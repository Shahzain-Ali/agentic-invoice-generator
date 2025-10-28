import streamlit as st
from datetime import datetime, date
import json
import pycountry
import requests

# Page config
st.set_page_config(
    page_title="Invoice Request Form",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
    }
    
    .form-header {
        background: linear-gradient(135deg, #1A73E8 0%, #0d47a1 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(26, 115, 232, 0.3);
    }
    
    .form-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .form-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        font-size: 1.1rem;
    }
    
    .section-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #1A73E8;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    .section-icon {
        font-size: 1.8rem;
        margin-right: 1rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0;
    }
    
    .item-block {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .item-title {
        font-weight: 600;
        color: #475569;
        font-size: 1.1rem;
    }
    
    .required-label {
        color: #dc2626;
        font-weight: 600;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1A73E8 0%, #0d47a1 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 4px 15px rgba(26, 115, 232, 0.4);
        transform: translateY(-2px);
    }
    
    div[data-testid="stDateInput"] {
        margin-bottom: 0;
    }
    
    .success-box {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .summary-table {
        margin-top: 1rem;
    }
    
    label {
        font-weight: 500;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'items' not in st.session_state:
    st.session_state['items'] = [{'id': 0}]
if 'item_counter' not in st.session_state:
    st.session_state['item_counter'] = 1

# Get country list
countries = sorted([country.name for country in pycountry.countries])
pakistan_index = countries.index("Pakistan")

# Header
st.markdown("""
<div class="form-header">
    <h1>📄 Invoice Request Form</h1>
    <p>Please fill out the form below to request an invoice for your services</p>
</div>
""", unsafe_allow_html=True)

# Add item button (before form)
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("➕ Add Another Item", use_container_width=True):
        st.session_state['items'].append({'id': st.session_state['item_counter']})
        st.session_state['item_counter'] += 1
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Form
with st.form("invoice_form", clear_on_submit=False):
    
    # Section 1: Client Information
    st.markdown("""
    <div class="section-container">
        <div class="section-header">
            <span class="section-icon">👤</span>
            <h2 class="section-title">Client Information</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input(
            "Client Name *",
            placeholder="Enter your full name",
            help="Required field"
        )
        company_name = st.text_input(
            "Company Name",
            placeholder="Enter company name (optional)"
        )
    
    with col2:
        email = st.text_input(
            "Email Address *",
            placeholder="your.email@example.com",
            help="Required field"
        )
        country = st.selectbox(
            "Country *",
            options=countries,
            index=pakistan_index,
            help="Select your country"
        )
    
    today = None  # No default date

    due_date = st.date_input(
        "Due Date",
        value=datetime.today(),
        help="Select deadline date (optional)",
    )

    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 2: Item Details
    st.markdown("""
    <div class="section-container">
        <div class="section-header">
            <span class="section-icon">📋</span>
            <h2 class="section-title">Services / Products</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    items_data = []
    
    # Access items list properly
    items_list = st.session_state['items']
    print("--------------- Items List -----------------\n")
    print(items_list)
    
    for idx, item in enumerate(items_list):
        st.markdown(f"""
        <div class="item-block">
            <div class="item-header">
                <span class="item-title">Item #{idx + 1}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        description = st.text_area(
            f"Service / Product Description *",
            key=f"desc_{item['id']}",
            placeholder="Describe the service or product provided",
            height=80,
            help="Required field"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            rate_per_hour = st.number_input(
                "Rate per Hour ($) *",
                key=f"rate_{item['id']}",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Required field"
            )
        
        with col2:
            hours = st.number_input(
                "Hours *",
                key=f"hours_{item['id']}",
                min_value=0.0,
                step=0.25,
                format="%.2f",
                help="Required field"
            )
        
        items_data.append({
            'description': description,
            'rate_per_hour': rate_per_hour,
            'hours': hours,
        })
        print("--------------- Items Data -----------------\n")
        print(items_data)
        
        if idx < len(items_list) - 1:
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 3: Optional Notes
    st.markdown("""
    <div class="section-container">
        <div class="section-header">
            <span class="section-icon">💬</span>
            <h2 class="section-title">Additional Notes</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    notes = st.text_area(
        "Additional Comments / Instructions",
        placeholder="Any special instructions or additional information...",
        height=120,
        help="Optional field"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.form_submit_button("✅ Submit Invoice Request", use_container_width=True)

# Form submission logic
if submit_button:
    errors = []
    
    # Validate required fields
    if not client_name or client_name.strip() == "":
        errors.append("Client Name is required")
    
    if not email or email.strip() == "":
        errors.append("Email is required")
    elif "@" not in email or "." not in email.split("@")[-1]:
        errors.append("Please enter a valid email address")
    
     # Validate items
    valid_items = []
    for idx, item in enumerate(items_data):
        if item['description'] and item['description'].strip():
            if item['rate_per_hour'] <= 0:
                errors.append(f"Item #{idx + 1}: Rate must be greater than 0")
            if item['hours'] <= 0:
                errors.append(f"Item #{idx + 1}: Hours must be greater than 0")
            if item['rate_per_hour'] > 0 and item['hours'] > 0:
                valid_items.append(item)
           
    if len(valid_items) == 0:
        errors.append("At least 1 service/product item is required")
    
    # Show errors or process submission
    if errors:
        for error in errors:
            st.error(f"❌ {error}")
    else:
        # Create JSON object
        submission_data = {                                                  
            "client_information": {
                "client_name": client_name,
                "email": email,
                "company_name": company_name if company_name else None,
                "country": country,
                "due_date": due_date.isoformat()
            },
            "items": valid_items,
            "notes": notes if notes else None,
            "submission_date": datetime.now().isoformat(),
            "total_amount": 0
        }

        # Print to console
        print("\n" + "="*50)
        print("INVOICE REQUEST SUBMITTED")
        print("="*50)
        print(json.dumps(submission_data, indent=2))
        print("="*50 + "\n")
        
        response = requests.post(
            "http://localhost:8000/generate_invoice",
            json=submission_data   # ✅ Correct
        )
        st.success("Invoice generated! Check response: " )
        
        # Summary table
        st.markdown("### 📊 Submission Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Client:** {client_name}  
            **Email:** {email}  
            **Company:** {company_name if company_name else 'N/A'}
            """)
        
        with col2:
            st.markdown(f"""
            **Country:** {country}  
            **Due Date:** {due_date}  
            **Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)
        
        st.markdown("---")
        st.markdown("### 📋 Items")
        
        for idx, item in enumerate(valid_items):
            st.markdown(f"""
            **Item #{idx + 1}**  
            Description: {item['description']}  
            """)
            st.markdown("")
        
        st.markdown
        if notes:
            st.markdown(f"**Notes:** {notes}")
        
        st.markdown("---")
        
        with st.expander("📄 View JSON Output"):
            st.json(submission_data)