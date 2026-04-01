from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from ..agents.runner import process_all_clients # type:ignore
from pprint import pprint
import json


app = FastAPI(title="Automated Invoice Generator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.post("/generate_invoices")
async def generate_invoices_endpoint(request: Request):
    body = await request.json()  # JSON body lo
    print("📄 Starting invoice generation from Google Sheet...\n")
    pprint(body)

    # Sheet data nikalo
    all_client_data = body.get("data", [])

    results = await process_all_clients(all_client_data)

    # Pretty print results
    print('\n' + '='*70)
    print(f'✅ INVOICE PROCESSING COMPLETE - {len(results)} clients processed')
    print('='*70 + '\n')

    for idx, result in enumerate(results, 1):
        try:
            # Clean the JSON string (remove ```json wrapper)
            clean_result = result.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_result)

            print(f"[{idx}] {data.get('client_name', 'Unknown')}")
            print(f"    📧 {data.get('email', 'N/A')}")
            print(f"    {data.get('status', 'Unknown')}")
            print(f"    📄 {data.get('pdf_path', 'N/A')}")
            print()
        except Exception as e:
            print(f"[{idx}] Error parsing result: {e}")
            print()

    print('='*70 + '\n')

    return {
        "status": "success",
        "processed_clients": len(results),
        "details": results
    }