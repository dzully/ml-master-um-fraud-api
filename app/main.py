import joblib
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import Client, create_client

from app.api import generate_upload_link_excel, generate_upload_local_excel

app = FastAPI()
load_dotenv()

origins = [
    "http://localhost",
    "http://localhost:3005",
    "https://fraud-analysis-w7g6j5rusa-as.a.run.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url: str = "https://yivpgyutmjubrdxywcbt.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlpdnBneXV0bWp1YnJkeHl3Y2J0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTYyMTgwNjQsImV4cCI6MjAzMTc5NDA2NH0.6pGdyzPV0mIikeVdxa6-Fl5WaM41K4IXZoaBRrWKQ7I"
supabase: Client = create_client(url, key)

logistic_model = joblib.load('app/model/Logistic Regression_model.joblib')
random_forest_model = joblib.load('app/model/Random Forest_model.joblib')
svm_model = joblib.load('app/model/Support Vector Machines (SVM)_model.joblib')

# Define the feature names
feature_names = [
    'Time Diff between first and last (Mins)',
    'min value received',
    'min value sent to contract',
    'max val sent to contract',
    'total Ether sent',
    'total ether received',
    'total ether balance',
    'ERC20 uniq sent addr',
    'ERC20 uniq rec contract addr',
    'ERC20 most sent token type',
    'ERC20_most_rec_token_type'
]


@app.get("/")
def read_root():
    return {"Hello": "World"}


class LocalItem(BaseModel):
    fileName: str


@app.post("/api/v1/upload-local")
def read_root(item: LocalItem):
    generate_result = generate_upload_local_excel(item.fileName, supabase)
    return {"fileName": generate_result}


class Item(BaseModel):
    link: str


@app.post("/api/v1/upload-link")
def read_root(item: Item):
    generate_result = generate_upload_link_excel(item.link, supabase)
    return {"fileName": generate_result}


class FormItem(BaseModel):
    time_diff: float
    min_val_received: float
    min_val_sent_to_contract: float
    max_val_sent_to_contract: float
    total_ether_sent: float
    total_ether_received: float
    total_ether_balance: float
    erc20_uniq_sent_addr: int
    erc20_uniq_rec_contract_addr: int


@app.post('/api/v1/form-predict')
def predict_fraud(
    item: FormItem
):
    time_diff = item.time_diff
    min_val_received = item.min_val_received
    min_val_sent_to_contract = item.min_val_sent_to_contract
    max_val_sent_to_contract = item.max_val_sent_to_contract
    total_ether_sent = item.total_ether_sent
    total_ether_received = item.total_ether_received
    total_ether_balance = item.total_ether_balance
    erc20_uniq_sent_addr = item.erc20_uniq_sent_addr
    erc20_uniq_rec_contract_addr = item.erc20_uniq_rec_contract_addr

    print(time_diff, min_val_received,
          min_val_sent_to_contract, max_val_sent_to_contract)
    # Create feature array
    features = np.array([[time_diff, min_val_received, min_val_sent_to_contract, max_val_sent_to_contract,
                          total_ether_sent, total_ether_received, total_ether_balance,
                          erc20_uniq_sent_addr, erc20_uniq_rec_contract_addr]])

    # Make predictions using loaded models
    logistic_pred = logistic_model.predict(features)[0]
    random_forest_pred = random_forest_model.predict(features)[0]
    svm_pred = svm_model.predict(features)[0]

    return {
        "logistic_regression": "fraud" if logistic_pred == 1 else "not fraud",
        "random_forest": "fraud" if random_forest_pred == 1 else "not fraud",
        "svm": "fraud" if svm_pred == 1 else "not fraud"
    }
