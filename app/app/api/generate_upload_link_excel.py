import datetime
import os

import pandas as pd
import requests
from supabase import Client

from app.utils.model import g1_fraud_prediction


def generate_upload_link_excel(csv_url: str, supabase: Client):
    requests_csv = requests.get(csv_url)
    url_content = requests_csv.content

    csv_file_name = 'upload_csv' + \
        datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.csv'
    csv_file = open(csv_file_name, 'wb')
    csv_file.write(url_content)
    csv_file.close()

    txn_df = pd.read_csv(csv_file_name, index_col=0)
    result = g1_fraud_prediction(txn_df)

    output_file_name = "output" + "-processed-" + \
        datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.xlsx'
    writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
    result.to_excel(writer, index=False, sheet_name='Sheet1')

    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Add a format for the cells to be highlighted
    highlight_format = workbook.add_format({'bg_color': 'yellow'})

    # Apply conditional formatting to the entire row
    for idx, value in enumerate(result['Potential Fraud']):
        if value == 'yes':
            for col_num, col_value in enumerate(result.iloc[idx]):
                if pd.isna(col_value):  # Check for NaN values
                    col_value = ''      # Replace NaN with empty string
                worksheet.write(idx + 1, col_num, col_value, highlight_format)

    writer.close()

    with open(csv_file_name, 'rb') as file:
        supabase.storage.from_(
            'upload_csv').upload(csv_file_name, file)

    with open(output_file_name, 'rb') as file:
        supabase.storage.from_(
            'processed_csv').upload(output_file_name, file)

    os.remove(csv_file_name)
    os.remove(output_file_name)

    return output_file_name
