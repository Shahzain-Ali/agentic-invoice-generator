from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel,set_default_openai_api, set_default_openai_client
from pydantic import BaseModel
from agents.run import RunConfig
from agents import enable_verbose_stdout_logging
import json, re, os
from pprint import pprint
import asyncio
from typing import Optional,Any, Dict
import pdfkit # type: ignore
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread
from jinja2 import Environment, FileSystemLoader # type: ignore
from agent_prompts.prompts import (invoice_validation_agent_prompt,
                                     invoice_template_agent_prompt,
                                     invoice_delivery_agent_prompt
                                     )
from dotenv import load_dotenv
# from pdf2image import convert_from_path

enable_verbose_stdout_logging()

load_dotenv()

# Set up Gemini API key and client
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError('API key is not set in the environment variable')

gemini_api_key = os.getenv('GEMINI_API_KEY')
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash',
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
)

def validate_invoice_data(data_json: str) -> str:
    """Validate invoice user input data."""

    try:
        data = json.loads(data_json)

        # ✅ Validate client_information fields
        client_info = data.get("client_information", {})
        required_client_fields = ["client_name", "address", "country", "due_date"]
        for field in required_client_fields:
            if field not in client_info:
                raise ValueError(f"Missing required client field: {field}")

        # ✅ Email optional but validate when present
        email = client_info.get("email", "")
        if email:
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
                raise ValueError("Invalid email format")

        # ✅ Due Date must follow ISO format YYYY-MM-DD
        try:
            datetime.strptime(client_info["due_date"], "%Y-%m-%d")
            datetime.strptime(client_info["current_date"], "%Y-%m-%d")
        except Exception:
            raise ValueError("Invalid due_date format, use YYYY-MM-DD")

        # ✅ Validate items list
        items = data.get("items", [])
        if not isinstance(items, list) or len(items) == 0:
            raise ValueError("Items array must be non-empty")

        subtotal = 0
        for item in items:
            if not all(k in item for k in ["description", "rate_per_hour", "hours"]):
                raise ValueError("Item missing required fields")

            if item.get("hours", 0) <= 0:
                raise ValueError("Hours must be greater than 0")

            if not isinstance(item["rate_per_hour"], (int, float)):
                raise ValueError("rate_per_hour must be a number")

            if not isinstance(item["hours"], (int, float)):
                raise ValueError("hours must be a number")

            # ✅ Auto add price if missing
            item["price"] = round(item["rate_per_hour"] * item["hours"], 2)
            subtotal += item["price"]

        # ✅ Assign subtotal & grand_total if missing
        data["subtotal"] = round(subtotal, 2)
        # Default: No tax included yet → grand_total = subtotal
        data["grand_total"] = round(subtotal, 2)


        invoice_validate_data_returns = json.dumps(data)
        print("invoice_validate_data_returns\n")
        pprint(invoice_validate_data_returns)
        return data

    except ValueError as e:
        raise ValueError(str(e))
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

    
@function_tool
def render_invoice_template(data_json: str, design_id: int) -> str:
    """Render invoice HTML based on design_id."""

    print("✅ Function Started")

    print("📌 Raw data_json:", data_json)
    print("📌 Design ID:", design_id)

    # Parse inner JSON
    try:
        data = json.loads(data_json)
        print("✅ Parsed JSON:", data)
    except Exception as e:
        print("❌ JSON Parse Error:", e)
        return json.dumps({"error": "Invalid JSON in data_json"})

    # Resolve template name
    design_map = {1: "invoice.html"}
    template_name = design_map.get(design_id, "invoice.html")
    print("📌 Template Chosen:", template_name)

    # Load template
    try:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(template_name)
        print("✅ Template loaded successfully")
    except Exception as e:
        print("❌ Template Load Error:", e)
        return json.dumps({"error": "Template not found"})

    # Render HTML
    try:
        html_content = template.render(**data)
        # pprint(html_content)
        print("✅ HTML Rendered Successfully ✅")
    except Exception as e:
        print("❌ HTML Render Error:", e)
        return json.dumps({"error": "Template rendering failed"})

    return json.dumps({"html_content": html_content})



@function_tool
def generate_pdf_tool(html_content: str, data_json: str) -> str:
    """Generate PDF from HTML content and return paths as JSON."""
    try:
        data = json.loads(data_json)
        client_info = data.get("client_information", {})
        client_name = client_info.get("client_name", "invoice").replace(" ", "_")
        pdf_path = f"invoices/{client_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        os.makedirs("invoices", exist_ok=True)

        # Configure wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

        # PDF generation options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }

        pdfkit.from_string(html_content, pdf_path, configuration=config, options=options)
        return json.dumps({"status": "success", "pdf_path": pdf_path})
    except Exception as e:
        return json.dumps({"error": "Failed to generate PDF", "details": str(e)})
    
from typing import Dict
import json
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@function_tool
def send_email_tool(email_to: str, pdf_path: str) -> str:
    print("-------------------------------- send_email_tool called!!!!! ---------------------")
    """Send invoice PDF to client email with static message."""
    try:
        msg = MIMEMultipart()
        msg['From'] = "your-email@gmail.com"  # Tumhara email
        msg['To'] = email_to
        msg['Subject'] = "The Agentive Corporation – Invoice Attached ✅"
        body = "Your invoice is attached. Please pay by due date."
        msg.attach(MIMEText(body, 'plain'))

        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name="invoice.pdf")
            part['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
            msg.attach(part)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            app_password = os.getenv("GMAIL_APP_PASSWORD")
            if not app_password:
                raise ValueError("❌ GMAIL_APP_PASSWORD missing from environment!")

            server.login("alishahzain604@gmail.com", app_password)  # App password .env se lo
            server.send_message(msg)

        return json.dumps({"status": "success", "message": "Email sent"})
    except Exception as e:
        return json.dumps({"error": "Failed to send email", "details": str(e)})
    

class DeliveryOutput(BaseModel):
    status: str
    pdf_path: str

invoice_delivery_agent = Agent(
    name="Invoice Delivery Agent",
    instructions=invoice_delivery_agent_prompt,
    tools=[generate_pdf_tool,send_email_tool],
)

# class TemplateOutput(BaseModel):
#     invoice_number: str
#     html_content: str

invoice_template_agent = Agent(
    name="Invoice Template Agent",
    instructions=invoice_template_agent_prompt,
    tools=[render_invoice_template],
    handoffs=[invoice_delivery_agent],
)

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


invoice_validation_agent = Agent(
    name="Invoice Validation Agent",
    instructions=invoice_validation_agent_prompt,
    handoffs=[invoice_template_agent],
)


# async def generate_invoice(user_data):
#     """Generate invoice PDF and return paths to PDF and preview."""
#     prompt = f"""Process this invoice data: {user_data}"""
#     result = await Runner.run(invoice_validation_agent, prompt,run_config=config)
#     print("Final Output:\n" )
#     # pprint(result.to_input_list())
#     print("Final Output:\n", result.final_output)

from google.oauth2.service_account import Credentials
import gspread

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
client = gspread.authorize(creds)
google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
if not google_sheet_id:
    raise ValueError("GOOGLE_SHEET_ID missing in .env file!")

sheet = client.open_by_key(google_sheet_id).worksheet("Form responses 1")
data = sheet.get_all_records()  # Sab rows ek list mein aa jayengi

if not google_sheet_id:
    raise ValueError("GOOGLE_SHEET_ID missing in .env file!")

sheet = client.open_by_key(google_sheet_id).sheet1
data = sheet.get_all_records()  # Sab rows ek list mein aa jayengi

# Helper function — sheet ke record ko schema me convert karta hai
def format_google_sheet_row(row: dict) -> dict:
    """Convert Google Sheet flat data into structured invoice schema."""
    return {
        "client_information": {
            "client_name": row.get("client_name", "").strip(),
            "address": row.get("address", "").strip(),
            "email": row.get("email", "").strip(),
            "company_name": row.get("company_name", "").strip(),
            "country": row.get("country", "").strip(),
            "current_date": row.get("current_date", "").strip(),
            "due_date": row.get("due_date", "").strip()
        },
        "items": [
            {
                "description": row.get("description", "").strip(),
                "rate_per_hour": float(row.get("rate_per_hour", 0)),
                "hours": float(row.get("hours", 0))
            }
        ],
        "subtotal": float(row.get("subtotal", 0)),
        "grand_total": float(row.get("grand_total", 0))
    }

async def process_client(client_data):
    formatted_data = format_google_sheet_row(client_data)
    print('Google Sheet Data:\n')
    pprint(formatted_data)

    # ✅ Convert to proper JSON string
    data_json = json.dumps(formatted_data)

    # ✅ Validate invoice data
    validate_data = validate_invoice_data(data_json)
    print('Validated Data:\n')
    pprint(validate_data)

    # ✅ Pass validated JSON to agent
    prompt = f"Process this invoice data: {validate_data}"
    result = await Runner.run(invoice_validation_agent, prompt, run_config=config)

    print(f"Processed: {result.final_output}")
    return result.final_output


async def process_all_clients():
    """Generate invoice PDF and return paths to PDF and preview."""
    data = sheet.get_all_records()
   
    
    for client in data:  # Har row (client) ke liye loop
        await process_client(client)
        await asyncio.sleep(1)  # Thodi der rukna, server overload na ho






 # data = [
    #         {
    #             "client_information": {
    #                 "client_name": "Shahzain Ali",
    #                 "address": "456 ABC Rd,Karachi",
    #                 "email": "shahzainalii859@gmail.com",
    #                 "company_name": "The Agentive Corporation",
    #                 "country": "Pakistan",
    #                 "current_date": "2025-10-26",
    #                 "due_date": "2025-10-29"
    #             },
    #             "items": [
    #                 {
    #                 "description": "AI Chatbot",
    #                 "rate_per_hour": 50.0,
    #                 "hours": 26.0
    #                 },
    #                 {
    #                 "description": "Customer Support Automation Agent",
    #                 "rate_per_hour": 50.0,
    #                 "hours": 56.0
    #                 }
    #             ],
    #             "subtotal": 0,
    #             "grand_total": 0
    #         },
    #         {
    #             "client_information": {
    #                 "client_name": "John Doe",
    #                 "address": "456 ABC Rd,USA",
    #                 "email": "shahzainalii859@gmail.com",
    #                 "company_name": "The Agentive Corporation",
    #                 "country": "Pakistan",
    #                 "current_date": "2025-10-26",
    #                 "due_date": "2025-10-29"
    #             },
    #             "items": [
    #                 {
    #                 "description": "AI Chatbot",
    #                 "rate_per_hour": 50.0,
    #                 "hours": 30.0
    #                 },
    #                 {
    #                 "description": "Customer Support Automation Agent",
    #                 "rate_per_hour": 50.0,
    #                 "hours": 58.0
    #                 }
    #             ],
    #             "subtotal": 0,
    #             "grand_total": 0
    #         }
    #     ]
    

