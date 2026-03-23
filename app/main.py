import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, HTTPException
from google.cloud import firestore
from app.models import InvoiceResponse
from app.vision import extract_invoice_data

app = FastAPI(title="InvoiceFlow", version="1.0.0")
db = firestore.Client()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/invoice/upload", response_model=InvoiceResponse)
async def upload_invoice(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or PDF files are accepted.")

    contents = await file.read()

    try:
        extracted = extract_invoice_data(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    invoice_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    doc = {
        "id": invoice_id,
        "vendor": extracted["vendor"],
        "total_amount": extracted["total_amount"],
        "invoice_date": extracted["invoice_date"],
        "raw_text": extracted["raw_text"],
        "created_at": now,
        "status": "processed"
    }

    db.collection("invoices").document(invoice_id).set(doc)

    return InvoiceResponse(**doc)

@app.get("/invoice/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: str):
    doc = db.collection("invoices").document(invoice_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return InvoiceResponse(**doc.to_dict())
