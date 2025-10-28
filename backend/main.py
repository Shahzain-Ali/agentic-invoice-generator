from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agents_work.agents_work import process_all_clients
import json
from pprint import pprint


app = FastAPI(title="Automated Invoice Generator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Item(BaseModel):
    description: str
    rate_per_hour: float
    hours: float

class ClientInformation(BaseModel):
    client_name: str
    address: str
    email: str = ""  # Empty if missing
    company_name: Optional[str] = None
    country: str
    current_date:str
    due_date: str  # ISO format


class InvoiceData(BaseModel):
    client_information: ClientInformation
    items: list[Item]
    subtotal:int
    grand_total:int

    class Config:
        extra = "ignore"  # Allow extra fields

@app.post("/generate_invoice")
async def generate_invoice_endpoint(invoice_data: InvoiceData):
    print(f"Received invoice generation request:\n")
    invoice_schema = invoice_data.model_dump_json(indent=2)
    print(invoice_schema)
    result = await process_all_clients()




