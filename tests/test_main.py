from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("app.main.extract_invoice_data")
@patch("app.main.get_db")
def test_upload_invoice(mock_get_db, mock_extract):
    mock_extract.return_value = {
        "vendor": "Acme Corp",
        "total_amount": "1500.00",
        "invoice_date": "01/06/2025",
        "raw_text": "Acme Corp\nTotal 1500.00"
    }
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    with open("tests/sample_invoice.png", "rb") as f:
        response = client.post(
            "/invoice/upload",
            files={"file": ("sample_invoice.png", f, "image/jpeg")}
        )
    assert response.status_code == 200
    assert response.json()["vendor"] == "Acme Corp"

@patch("app.main.get_db")
def test_get_invoice_not_found(mock_get_db):
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    mock_get_db.return_value = mock_db

    response = client.get("/invoice/nonexistent-id")
    assert response.status_code == 404