from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel
from .prompts.validation_prompt import INVOICE_VALIDATION_PROMPT # type: ignore
from .prompts.delivery_prompt import INVOICE_DELIVERY_PROMPT # type: ignore
from .prompts.template_prompt import INVOICE_TEMPLATE_PROMPT # type: ignore
from backend.utils.formatters import format_google_sheet_row
from backend.utils.validation import validate_invoice_data
from agents import enable_verbose_stdout_logging
from agents.run import RunConfig
from dotenv import load_dotenv
from datetime import datetime
from pprint import pprint
import json, os
import asyncio

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
    model='gemini-2.5-flash',
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client, # type: ignore
)

# type: ignore


from typing import Dict
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from agents import function_tool

@function_tool
def send_email_tool(email_to: str, pdf_path: str) -> str:
    """Send invoice PDF to client email with static message."""
    print("\n\n-------------------------------- send_email_tool called!!!!! ---------------------")
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


# import pdfkit # type: ignore

# @function_tool
# def generate_pdf_tool(html_content: str, data_json: str) -> str:
#     """Generate PDF from HTML content and return paths as JSON."""
#     print("\n\n-------------------------------- PDF Generated tool called!!!!! ---------------------\n")
#     try:
#         data = json.loads(data_json)
#         client_info = data.get("client_information", {})
#         client_name = client_info.get("client_name", "invoice").replace(" ", "_")
#         pdf_path = f"invoices/{client_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         os.makedirs("invoices", exist_ok=True)

#         # Configure wkhtmltopdf
#         config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

#         # PDF generation options
#         options = {
#             'page-size': 'A4',
#             'margin-top': '0.75in',
#             'margin-right': '0.75in',
#             'margin-bottom': '0.75in',
#             'margin-left': '0.75in',
#             'encoding': "UTF-8",
#             'no-outline': None,
#             'enable-local-file-access': None
#         }

#         pdfkit.from_string(html_content, pdf_path, configuration=config, options=options)
#         return json.dumps({"status": "success", "pdf_path": pdf_path})
#     except Exception as e:
#         return json.dumps({"error": "Failed to generate PDF", "details": str(e)})

from weasyprint import HTML

@function_tool
def generate_pdf_tool(html_content: str, data_json: str) -> str:
    client_info = json.loads(data_json).get("client_information", {})
    client_name = client_info.get("client_name", "invoice").replace(" ", "_")
    pdf_path = f"invoices/{client_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    os.makedirs("invoices", exist_ok=True)

    HTML(string=html_content).write_pdf(pdf_path)
    return json.dumps({"status": "success", "pdf_path": pdf_path})


invoice_delivery_agent = Agent(
    name="Invoice Delivery Agent",
    instructions=INVOICE_DELIVERY_PROMPT,
    tools=[generate_pdf_tool, send_email_tool],
    # output_type=DeliveryOutput,
)


from jinja2 import Environment, FileSystemLoader

@function_tool
def render_invoice_template(data_json: str, design_id: int) -> str:
    """Render invoice HTML based on design_id."""
    print("\n\n-------------------------------- Render Ivoice Template tool called!!!!! ---------------------\n")

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



invoice_template_agent = Agent(
    name="Invoice Template Agent",
    instructions=INVOICE_TEMPLATE_PROMPT,
    tools=[render_invoice_template], 
    handoffs=[invoice_delivery_agent],
)



invoice_validation_agent = Agent(
    name="Invoice Validation Agent",
    instructions=INVOICE_VALIDATION_PROMPT,
    handoffs=[invoice_template_agent],
)



async def process_client(client_data):
    formatted_data = format_google_sheet_row(client_data)
    print('\n\nGoogle Sheet Data:-\n')
    pprint(formatted_data)

    # ✅ Convert to proper JSON string
    data_json = json.dumps(formatted_data)

    # ✅ Validate invoice data
    validate_data = validate_invoice_data(data_json)
    print('\n\nValidated Data:\n')
    pprint(validate_data)

    # ✅ Pass validated JSON to agent
    prompt = f"Process this invoice data: {validate_data}"
    result = await Runner.run(invoice_validation_agent, prompt, run_config=config)

    print(f"Processed: {result.final_output}")
    return result.final_output


async def process_all_clients(all_client_data):
    print("\n\nData_Recieved_From_Streamlit\n")
    pprint(all_client_data)
    
    print(f"🔹 Total Clients Found: {len(all_client_data)}")

    results = []
    for client in all_client_data:
        res = await process_client(client)
        results.append(res)
        print('Appending one by one Response in results:\n',res)
        await asyncio.sleep(1)

    return results



# async def generate_invoice(user_data):
#     """Generate invoice PDF and return paths to PDF and preview."""
#     prompt = f"""Process this invoice data: {user_data}"""
#     result = await Runner.run(invoice_validation_agent, prompt,run_config=config)
#     print("Final Output:\n" )
#     # pprint(result.to_input_list())
#     print("Final Output:\n", result.final_output)

# from google.oauth2.service_account import Credentials
# import gspread

# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
# client = gspread.authorize(creds)
# google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
# if not google_sheet_id:
#     raise ValueError("GOOGLE_SHEET_ID missing in .env file!")

# sheet = client.open_by_key(google_sheet_id).worksheet("Form responses 1")
# data = sheet.get_all_records()  # Sab rows ek list mein aa jayengi



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
    