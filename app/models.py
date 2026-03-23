from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InvoiceResponse(BaseModel):
    id: str
    vendor: Optional[str] = None
    total_amount: Optional[str] = None
    invoice_date: Optional[str] = None
    raw_text: str
    created_at: datetime
    status: str