import os
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import generate_excel
from supabase import Client, create_client

app = FastAPI()
load_dotenv()

origins = [
    "http://localhost",
    "http://localhost:3005",
    "https://fraud-analysis-w7g6j5rusa-as.a.run.app/"
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/v1/{item_id}")
def read_root(item_id: str):
    generate_result = generate_excel(item_id, supabase)
    return {"fileName": generate_result}
