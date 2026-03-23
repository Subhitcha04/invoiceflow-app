import re
from google.cloud import vision
from google.cloud.vision_v1 import types

def extract_invoice_data(image_bytes: bytes) -> dict:
    client = vision.ImageAnnotatorClient()
    image = types.Image(content=image_bytes)
    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API error: {response.error.message}")

    raw_text = response.text_annotations[0].description if response.text_annotations else ""

    vendor = None
    total = None
    date = None

    lines = raw_text.split("\n")

    # Simple heuristic extraction — first non-empty line is often vendor
    for line in lines[:5]:
        if line.strip():
            vendor = line.strip()
            break

    # Look for total amount pattern
    for line in lines:
        match = re.search(r'(total|amount due|balance due)[^\d]*([\d,]+\.?\d*)', line, re.IGNORECASE)
        if match:
            total = match.group(2)
            break

    # Look for date pattern
    for line in lines:
        match = re.search(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}', line)
        if match:
            date = match.group(0)
            break

    return {
        "vendor": vendor,
        "total_amount": total,
        "invoice_date": date,
        "raw_text": raw_text
    }