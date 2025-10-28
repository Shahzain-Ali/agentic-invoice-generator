from google.oauth2.service_account import Credentials
import gspread
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()
# Credentials load karo
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
client = gspread.authorize(creds)
google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
if not google_sheet_id:
    raise ValueError("GOOGLE_SHEET_ID missing in .env file!")

sheet = client.open_by_key(google_sheet_id).worksheet("Form responses 1")
data = sheet.get_all_records()  # Sab rows ek list mein aa jayengi



data = sheet.get_all_records()
print('Google Sheet Data:\n')
pprint(data)