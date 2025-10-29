import streamlit as st
import requests
import pandas as pd # type:ignore
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import json


load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Smart Invoice Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .header-subtitle {
        color: #e0e7ff;
        font-size: 1.1rem;
        text-align: center;
    }
    
    /* Section styling */
    # .section-box {
    #     background: white;
    #     color: black;
    #     padding: 2rem;
    #     border-radius: 10px;
    #     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    #     margin-bottom: 1.5rem;
    # }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #5568d3;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid #e5e7eb;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 6px;
        border: 1px solid #d1d5db;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        color: black !important;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 500;
    }
            
    /* Success message styling */
    .success-banner {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">💼 The Agentive Corporation – Smart Invoice Generator</h1>
        <p class="header-subtitle">Generate and email client invoices automatically with AI</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_results' not in st.session_state:
    st.session_state.generated_results = None
if 'sheet_data' not in st.session_state:
    st.session_state.sheet_data = None
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None

# Input method tabs
tab1, tab2, tab3 = st.tabs(["🧾 Manual Form Entry", "📊 Google Sheet Integration", "📁 Upload Excel File"])

# Manual Form Entry Tab
with tab1:
    # st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("📝 Enter Client Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input("Client Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="john@example.com")
        company_name = st.text_input("Company Name", placeholder="Acme Corp")
        address = st.text_area("Address", placeholder="123 Main St, City, State", height=100)
    
    with col2:
        country = st.text_input("Country", placeholder="United States")
        due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=30))
        current_date = st.date_input("Current Date", value=datetime.now() + timedelta(days=30))
        rate = st.number_input("Rate per Hour ($)", min_value=0.0, value=50.0, step=5.0)
        hours = st.number_input("Hours Worked", min_value=0.0, value=40.0, step=0.5)
    
    description = st.text_area("Description of Services", placeholder="Web development services, consulting, etc.", height=100)
    
    # st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Generate Invoice (Manual)", key="manual_generate"):
        if not all([client_name, email, company_name, address, country, description]):
            st.error("⚠️ Please fill in all required fields!")
        else:
            manual_data = {
                "method": "manual",
                "data": [{
                    "client_name": client_name,
                    "email": email,
                    "company_name": company_name,
                    "address": address,
                    "country": country,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "current_date": current_date.strftime("%Y-%m-%d"),
                    "description": description,
                    "rate_per_hour": rate,
                    "hours": hours
                }]
            }
            
            with st.spinner("Processing invoice... please wait ⏳"):
                try:
                    response = requests.post(
                        "http://localhost:8000/generate_invoices",
                        json=manual_data,
                        timeout=None
                    )
                
                    if response.status_code == 200:
                        st.session_state.generated_results = response.json()
                        print("Data Successfully Recieved From FastAPI:\n",st.session_state.generated_results)
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")

# Google Sheet Integration Tab
with tab2:
    # st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("📊 Connect to Google Sheets")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sheet_id = st.text_input(
            "Google Sheet ID",
            placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            help="Enter the ID from your Google Sheets URL"
        )
    
    with col2:
        st.write("")
        st.write("")
        fetch_button = st.button("📥 Fetch Data", key="fetch_sheet")
    
    if fetch_button and sheet_id:
        with st.spinner("Fetching data from Google Sheets... ⏳"):
            try:
               scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
               creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
               client = gspread.authorize(creds)
               google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
               if not google_sheet_id:
                   raise ValueError("GOOGLE_SHEET_ID missing in .env file!")

               sheet = client.open_by_key(google_sheet_id).worksheet("Form responses 1")
               data = sheet.get_all_records()  # Sab rows ek list mein aa jayengi

                # Convert to DataFrame
               st.session_state.sheet_data = pd.DataFrame(data)
               st.success("✅ Data fetched successfully!")

            except Exception as e:
                st.error(f"❌ Error fetching data: {str(e)}")
    
    if st.session_state.sheet_data is not None:
        st.dataframe(st.session_state.sheet_data, use_container_width=True)
        
        if st.button("🚀 Generate Invoices (Google Sheet)", key="sheet_generate"):
            sheet_data_json = {
                "method": "google_sheet",
                "sheet_id": sheet_id,
                "data": st.session_state.sheet_data.to_dict('records')
            }
            
            with st.spinner("Processing invoices... please wait ⏳"):
                try:
                    response = requests.post(
                        "http://localhost:8000/generate_invoices",
                        json=sheet_data_json,
                        timeout=None
                    )
                    if response.status_code == 200:
                        st.session_state.generated_results = response.json()
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
    
    # st.markdown('</div>', unsafe_allow_html=True)

# Excel Upload Tab
with tab3:
    # st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("📁 Upload Excel File")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx)",
        type=['xlsx'],
        help="Upload an Excel file with client information"
    )
    
    if uploaded_file is not None:
        try:
            st.session_state.excel_data = pd.read_excel(uploaded_file)
            st.success(f"✅ File uploaded successfully! Found {len(st.session_state.excel_data)} rows.")
            st.dataframe(st.session_state.excel_data, use_container_width=True)
            
            if st.button("🚀 Generate Invoices (Excel)", key="excel_generate"):
                excel_data_json = {
                    "method": "excel",
                    "data": st.session_state.excel_data.to_dict('records')
                }
                
                with st.spinner("Processing invoices... please wait ⏳"):
                    try:
                        response = requests.post(
                            "http://localhost:8000/generate_invoices",
                            json=excel_data_json,
                            timeout=60
                        )
                        if response.status_code == 200:
                            st.session_state.generated_results = response.json()
                        else:
                            st.error(f"❌ Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    # st.markdown('</div>', unsafe_allow_html=True)

# Display Results
if st.session_state.generated_results:
    st.markdown("---")
    results = st.session_state.generated_results
    
    st.markdown("""
        <div class="success-banner">
            <h3 style="margin: 0; color: #065f46;">✅ All invoices processed successfully!</h3>
            <p style="margin: 0.5rem 0 0 0; color: #047857;">
                Processed {} client(s) successfully
            </p>
        </div>
    """.format(results.get('processed_clients', 0)), unsafe_allow_html=True)
    
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("📋 Processing Summary")
    
    if 'details' in results and results['details']:
        cleaned_details = []
        for d in results['details']:
           # Remove Markdown fences and parse JSON
            try:
               d_clean = d.replace("```json", "").replace("```", "").strip()
               parsed = json.loads(d_clean)
               cleaned_details.append(parsed)
            except Exception as e:
               print("Error parsing detail item:", e, d)

        if cleaned_details:
            details_df = pd.DataFrame(cleaned_details)
        else:
            details_df = pd.DataFrame()
        
        if not details_df.empty:
            print('Details Available:\n',details_df)
            column_order = ['client_name', 'email', 'status', 'pdf_path']
            display_columns = [col for col in column_order if col in details_df.columns]
            details_df = details_df[display_columns]
            
            # Column rename only if columns exist
            details_df.columns = [col.replace('_', ' ').title() for col in details_df.columns]
            
            st.dataframe(details_df, use_container_width=True, hide_index=True)
        else:
            st.info("No client details available yet.")
    else:
        st.info("No details available in the response.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add a reset button
    if st.button("🔄 Generate New Invoices"):
        st.session_state.generated_results = None
        st.session_state.sheet_data = None
        st.session_state.excel_data = None
        st.rerun()

# Footer
st.markdown("""
    <div class="footer">
        © 2025 The Agentive Corporation | Powered by AI
    </div>
""", unsafe_allow_html=True)