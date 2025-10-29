from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from ..agents.runner import process_all_clients # type:ignore
from pprint import pprint


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
    print('---------------------- Processed All Clients Results✅ -------------------------------')
    print(results)
    return {
        "status": "success",
        "processed_clients": len(results),
        "details": results
    }




