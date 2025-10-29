from datetime import datetime, timedelta


# Helper function — sheet ke record ko schema me convert karta hai

def format_google_sheet_row(row: dict) -> dict:
    """Convert Google Sheet flat data into structured invoice schema."""

    def parse_date(value):
        """Handle Excel serial, blank, or proper date strings safely."""
        if isinstance(value, (float, int)):
            return datetime.fromordinal(datetime(1899, 12, 30).toordinal() + int(value)).strftime("%Y-%m-%d")
        elif not value or str(value).strip() == "":
            # Default: today’s date
            return datetime.today().strftime("%Y-%m-%d")
        else:
            # Ensure correct format
            try:
                return datetime.strptime(str(value), "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                return datetime.today().strftime("%Y-%m-%d")

    current_date = parse_date(row.get("current_date"))
    due_date = parse_date(row.get("due_date"))

    return {
        "client_information": {
            "client_name": row.get("client_name", "").strip(),
            "address": row.get("address", "").strip(),
            "email": row.get("email", "").strip(),
            "company_name": row.get("company_name", "").strip(),
            "country": row.get("country", "").strip(),
            "current_date": current_date,
            "due_date": due_date
        },
        "items": [
            {
                "description": row.get("description", "").strip(),
                "rate_per_hour": float(row.get("rate_per_hour", 0) or 0),
                "hours": float(row.get("hours", 0) or 0)
            }
        ],
        "subtotal": float(row.get("subtotal", 0) or 0),
        "grand_total": float(row.get("grand_total", 0) or 0)
    }
