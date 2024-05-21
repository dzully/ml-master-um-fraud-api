import os
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import Client, create_client

from model import generate_excel

app = FastAPI()
load_dotenv()

origins = [
    "http://localhost",
    "http://localhost:3005",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/v1/{item_id}")
def read_root(item_id: str):
    generate_result = generate_excel(item_id, supabase)
    return {"fileName": generate_result}
