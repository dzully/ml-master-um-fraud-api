import json

import joblib
import numpy as np
import pandas as pd


with open('app/model/imputed_means.json', 'r') as json_file:
    imputed_means = json.load(json_file)


most_token_sent_encoder = joblib.load(
    'app/model/encoder_ERC20 most sent token type.pkl')
most_token_recieve_encoder = joblib.load(
    'app/model/encoder_ERC20_most_rec_token_type.pkl')
scaler = joblib.load('app/model/scaler.pkl')
model = joblib.load('app/model/Random Forest_model.joblib')


def data_preprocess(df, imputed_means, most_token_sent_encoder, most_token_recieve_encoder, scaler):

    irrelevant_columns = ['Address',
                          'Index']

    zero_mean_columns = ['ERC20 avg time between sent tnx',
                         'ERC20 avg time between rec tnx',
                         'ERC20 avg time between rec 2 tnx',
                         'ERC20 avg time between contract tnx',
                         'ERC20 min val sent contract',
                         'ERC20 max val sent contract',
                         'ERC20 avg val sent contract']

    # Strip name
    df.columns = df.columns.str.strip()

    # Drop irrelevant columns
    df = df.drop(irrelevant_columns, axis=1)
    df = df.drop(zero_mean_columns, axis=1)

    # mean impute on numerical columns
    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    for col in numeric_columns:
        if df[col].isna().any():
            df[col] = df[col].fillna(imputed_means[col])

    # Drop high correlation columns
    high_corr_columns = ['total transactions (including tnx to create contract',
                         'avg value sent to contract',
                         'total ether sent contracts',
                         'ERC20 max val rec',
                         'ERC20 avg val rec',
                         'ERC20 min val sent',
                         'ERC20 max val sent',
                         'ERC20 avg val sent',
                         'ERC20 uniq rec token name']
    df = df.drop(high_corr_columns, axis=1)

    categorical_columns = ['ERC20 most sent token type',
                           'ERC20_most_rec_token_type']

    # categorical impute with '0'
    for col in categorical_columns:
        df[col] = df[col].fillna('0')

    # categorical replace empty value with '0'
    for col in categorical_columns:
        df[col] = df[col].replace([' '], '0')

    # multi-encode
    df['ERC20 most sent token type'] = most_token_sent_encoder.transform(
        df['ERC20 most sent token type'])
    df['ERC20_most_rec_token_type'] = most_token_recieve_encoder.transform(
        df['ERC20_most_rec_token_type'])

    # scale all columns
    df_scaled = scaler.transform(df)

    df_scaled = pd.DataFrame(df_scaled, columns=df.columns)

    # final columns to retain after feature engineering
    final_columns = ['Time Diff between first and last (Mins)',
                     'min value received',
                     'min value sent to contract',
                     'max val sent to contract',
                     'total Ether sent',
                     'total ether received',
                     'total ether balance',
                     'ERC20 uniq sent addr.1',
                     'ERC20 uniq rec contract addr']

    return df_scaled[final_columns]


def g1_fraud_prediction(df):
    # copy
    df_copy = df.copy()

    # run the preprocess funtion to get the data suitable for prediction
    df_copy = data_preprocess(
        df_copy, imputed_means, most_token_sent_encoder, most_token_recieve_encoder, scaler)

    # ger prediction
    y = model.predict(df_copy)

    # append result
    fraud_predict = np.where(y == 1, 'yes', 'no')
    df['Potential Fraud'] = fraud_predict

    return df
