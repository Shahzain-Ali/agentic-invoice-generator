from pydantic import BaseModel
from typing import Optional


class Item(BaseModel):
    description: str
    rate_per_hour: float
    hours: float
    price: float



class ClientInformation(BaseModel):
    client_name: str
    email: str = ""  # Empty if missing
    company_name: Optional[str] = None
    address: str
    country: str
    due_date: str  # ISO format


class InvoiceData(BaseModel):
    invoice_number: str
    date: str  # ISO format
    client_information: ClientInformation
    items: list[Item]
    subtotal: float
    grand_total: float

    class Config:
        extra = "ignore"  # Allow extra fields
# print(invoice_validation_agent_prompt)



# class DeliveryOutput(BaseModel):
#     client_name: str
#     email: str
#     status: str
#     pdf_path: str
#     agent_output:str

# class TemplateOutput(BaseModel):
#     invoice_number: str
#     html_content: str