# AutoInvoice AI – Agentic Invoice Generator & Sender

**AutoInvoice AI** is an **agentic automation tool** built with AI to **generate, customize, and send invoices automatically** — in just **~35 seconds per client**.  
It pulls data from **forms**, **Google Sheets**, or **Excel files**, creates **PDF invoices**, and emails them directly to clients.  

Ideal for **marketing agencies**, **e-commerce**, **SaaS**, and **software houses** looking to save hours on manual billing.

---

## ✨ Features

- 🧠 **AI-Powered Automation:** Uses **OpenAI Agents SDK** + **Gemini 2.0 Flash** for intelligent data handling.  
- 📊 **Multiple Data Sources:** Input via **web form**, **Google Sheets**, or **Excel upload**.  
- 🧾 **PDF Generation:** Creates styled invoices using **Jinja2 templates** and **pdfkit**.  
- 📧 **Email Delivery:** Sends invoices via **Gmail SMTP** with attachments.  
- ⚙️ **Scalable MVP:** Handles 2–5 clients in demo mode (~35 sec/invoice).  
- 🖥️ **Real-Time Progress:** **Streamlit UI** shows live status — *Fetching → Generating → Sending*.  
- 📦 **Download Options:** Download individual PDFs or all invoices as a **ZIP**.  
- 🛡️ **Robust Error Handling:** Graceful fallbacks for template loading, JSON parsing, and email sending.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | FastAPI, OpenAI Agents SDK, Python 3.12+ |
| **Frontend** | Streamlit |
| **AI Model** | Google Gemini 2.0 Flash (Free Tier) |
| **Templates** | Jinja2 |
| **PDF Generation** | pdfkit + wkhtmltopdf |
| **Email** | smtplib (Gmail SMTP + MIME) |
| **Data Processing** | Pandas, Requests |
| **Automation Workflow** | n8n |
| **Others** | os, json, datetime, zipfile, io |

---

## ⚙️ Installation

### 🧾 Prerequisites
- Python **3.12+**
- Git
- Gmail account with **App Password** (for email sending)

---

### 1️⃣ Clone the Repository

> git clone https://github.com/Shahzain-Ali/AutoInvoice-AI.git

- cd autoinvoice-ai

### 2️⃣ Install Dependencies
- uv sync

### Example pyproject.toml:

> dependencies = [
    "streamlit",
    "fastapi",
    "uvicorn",
    "openai",
    "pdfkit",
    "jinja2",
    "openai-agents>=0.4.1",
    "gspread>=6.2.1",
    "google-auth>=2.41.1",
    "requests>=2.32.5",
]
<br><br>


## 3️⃣ Setup wkhtmltopdf (for PDF generation)
> wkhtmltopdf converts HTML to PDF. Required for pdfkit.

### Windows 

- Download: wkhtmltopdf.org/downloads.html
→ Windows (MSVC 2015) → wkhtmltox-0.12.6-1.msvc2015-win64.exe
Install:

- Run .exe as Administrator
Tick "Modify PATH" → Install


- Code Path:
pythonr"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

- Test: CMD → wkhtmltopdf --version


### macOS 

- Terminal → Run:
bashbrew install wkhtmltopdf

- Code Path:
python"/usr/local/bin/wkhtmltopdf"

- Test: wkhtmltopdf --version

- No Homebrew? Install: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

## 4️⃣ Environment Setup

- Create a .env file in the root directory:
```
GEMINI_API_KEY=#########
GMAIL_APP_PASSWORD=your16digitcode
GOOGLE_SHEET_ID=###########
```
> (Get App Password from Google Account > Security > App passwords)

# 🚦 Usage
## ▶️ Run Backend (FastAPI)
> uvicorn backend.api.main:app --reload --port 8000

## 💻 Run Frontend (Streamlit)
> streamlit run frontend\userInterface.py

## 🧩 In the Streamlit UI

1) Fill form or connect to Google Sheets or Upload Excel file 

2) Click “Generate Invoices”

3) Watch live progress (fetching → generating → sending)

4) Download PDFs or all invoices in ZIP format

## 📺 Demo Flow
[AutoIvoice-AI Project Demo Video]()

## 📜 License

This project is licensed under the MIT License.  
© 2025 Shahzain Ali

## 💬 Connect

> 💻 GitHub: [Shahzain Ali](https://github.com/Shahzain-Ali)

> 📧 Email: alishahzain604@gmail.com
