import pytest
import threading
import time
import os
import uvicorn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from unittest.mock import patch, MagicMock

# ── Start a real FastAPI server in a background thread ──
def run_server():
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

@pytest.fixture(scope="module", autouse=True)
def start_server():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2)  # Wait for server to start
    yield

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=options)
    yield d
    d.quit()

def test_homepage_loads(driver):
    driver.get("http://127.0.0.1:8001/")
    assert "InvoiceFlow" in driver.title or "InvoiceFlow" in driver.page_source

def test_upload_button_present(driver):
    driver.get("http://127.0.0.1:8001/")
    wait = WebDriverWait(driver, 10)
    btn = wait.until(EC.presence_of_element_located((By.ID, "uploadBtn")))
    assert btn is not None
    assert btn.text == "Upload Invoice"

def test_file_input_present(driver):
    driver.get("http://127.0.0.1:8001/")
    file_input = driver.find_element(By.ID, "fileInput")
    assert file_input is not None

def test_upload_invoice_e2e(driver):
    driver.get("http://127.0.0.1:8001/")
    wait = WebDriverWait(driver, 10)

    # Upload the sample invoice
    file_input = driver.find_element(By.ID, "fileInput")
    sample_path = os.path.abspath("tests/sample_invoice.jpg")
    file_input.send_keys(sample_path)

    # Click upload
    btn = driver.find_element(By.ID, "uploadBtn")
    btn.click()

    # Wait for result to appear
    time.sleep(3)
    result = driver.find_element(By.ID, "result")
    assert result.text != ""  # Some response came back