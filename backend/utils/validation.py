from datetime import datetime
import json
from pprint import pprint
import re


def validate_invoice_data(data_json: str) -> str:
    """Validate invoice user input data."""
    print("\n\n-------------------------------- Validate Ivoice date tool called!!!!! ---------------------\n")

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
        due_date = client_info.get("due_date")
        current_date = client_info.get("current_date")

        if not due_date or not current_date:
           raise ValueError("Missing due_date or current_date")

        try:
           datetime.strptime(due_date, "%Y-%m-%d")
           datetime.strptime(current_date, "%Y-%m-%d")
        except ValueError:
           raise ValueError("Invalid date format — must be YYYY-MM-DD")

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