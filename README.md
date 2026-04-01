# AutoInvoice AI – Agentic Invoice Generator & Sender

**AutoInvoice AI** is an **agentic automation tool** built with AI to **generate, customize, and send invoices automatically** — in just **~35 seconds per client**.
It pulls data from **forms**, **Google Sheets**, or **Excel files**, creates **PDF invoices**, and emails them directly to clients.

Ideal for **marketing agencies**, **e-commerce**, **SaaS**, and **software houses** looking to save hours on manual billing.

---

## ✨ Features

- 🧠 **AI-Powered Automation:** Uses **OpenAI Agents SDK** with **GPT-4o-mini** and **3 specialized agents** (Validation → Template → Delivery) for end-to-end invoice processing
- 📊 **Multiple Data Sources:** Input via **web form**, **Google Sheets**, or **Excel upload**
- 🧾 **PDF Generation:** Creates styled invoices using **Jinja2 templates** and **pdfkit**
- 📧 **Email Delivery:** Sends invoices via **Gmail SMTP** with attachments
- ⚙️ **Scalable MVP:** Handles 2–5 clients in demo mode (~35 sec/invoice)
- 🖥️ **Real-Time Progress:** **Streamlit UI** shows live status — *Fetching → Generating → Sending*
- 📦 **Download Options:** Download individual PDFs or all invoices as a **ZIP**
- 🛡️ **Robust Error Handling:** Graceful fallbacks for template loading, JSON parsing, and email sending

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, OpenAI Agents SDK, Python 3.12+ |
| **Frontend** | Streamlit |
| **AI Model** | OpenAI GPT-4o-mini via OpenAI Agents SDK |
| **Templates** | Jinja2 |
| **PDF Generation** | pdfkit + wkhtmltopdf |
| **Email** | smtplib (Gmail SMTP + MIME) |
| **Data Processing** | Pandas, Requests |
| **Automation Workflow** | n8n |

---

## ⚙️ Installation

### Prerequisites

- Python **3.12+**
- Git
- Gmail account with **App Password** (for email sending)

---

### 1. Clone the Repository

```bash
git clone https://github.com/Shahzain-Ali/agentic-invoice-generator.git
cd agentic-invoice-generator
```

### 2. Install Dependencies

```bash
uv sync
```

---

### 3. Setup wkhtmltopdf (for PDF Generation)

> wkhtmltopdf converts HTML to PDF. Required by pdfkit.

#### Windows

1. Download from [wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)
   - Select: **Windows (MSVC 2015)** → `wkhtmltox-0.12.6-1.msvc2015-win64.exe`
2. Run the `.exe` as **Administrator**
3. Tick **"Modify PATH"** → Install
4. Verify installation:
   ```bash
   wkhtmltopdf --version
   ```

#### macOS

1. Install via Homebrew:
   ```bash
   brew install wkhtmltopdf
   ```
2. Verify installation:
   ```bash
   wkhtmltopdf --version
   ```

> Don't have Homebrew? Install it first:
> ```bash
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
> ```

---

### 4. Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in your actual values:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GMAIL_EMAIL=your_email@gmail.com
   GMAIL_APP_PASSWORD=your_16_digit_app_password
   GOOGLE_SHEET_ID=your_google_sheet_id
   GOOGLE_CREDENTIALS_PATH=credentials.json
   WKHTMLTOPDF_PATH=C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
   API_URL=http://localhost:8000
   ```

> **How to get Gmail App Password:**
> Google Account → Security → 2-Step Verification → App Passwords → Generate

---

## 🚦 Usage

### Run Backend (FastAPI)

```bash
uvicorn backend.api.main:app --reload --port 8000
```

### Run Frontend (Streamlit)

```bash
streamlit run frontend/userInterface.py
```

### In the Streamlit UI

1. Fill the form **or** connect to Google Sheets **or** upload an Excel file
2. Click **"Process & Deliver Invoices"**
3. Watch live progress (Fetching → Generating → Sending)
4. Download PDFs individually or all invoices as a ZIP

---

## 📺 Demo

[Project Demo Video](https://youtube.com/your-video-link) *(Coming Soon)* — *Coming Soon*

---

## 📜 License

This project is licensed under the **MIT License**.
© 2025 Shahzain Ali

---

## 💬 Connect

- 💻 GitHub: [Shahzain Ali](https://github.com/Shahzain-Ali)
- 📧 Email: alishahzain604@gmail.com
