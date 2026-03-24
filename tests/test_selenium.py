import pytest
import threading
import time
import os
import socket
import uvicorn
from PIL import Image
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# ---------- Server ----------
def run_server():
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")


def wait_for_server(host="127.0.0.1", port=8001, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("Server did not start in time")


@pytest.fixture(scope="module", autouse=True)
def start_server():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    wait_for_server()  # ✅ robust readiness check
    yield


# ---------- Driver ----------
@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")  # ✅ modern headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # ✅ CRITICAL FIX: use system chromedriver (from CI setup)
    service = Service()

    d = webdriver.Chrome(service=service, options=options)
    yield d
    d.quit()

def create_test_image():
    img = Image.new("RGB", (200, 100), color="white")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    img.save(temp_file.name, format="JPEG")

    return temp_file.name
# ---------- Tests ----------
BASE_URL = "http://127.0.0.1:8001"


def test_homepage_loads(driver):
    driver.get(BASE_URL + "/")
    assert "InvoiceFlow" in driver.title or "InvoiceFlow" in driver.page_source


def test_upload_button_present(driver):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)

    btn = wait.until(
        EC.presence_of_element_located((By.ID, "uploadBtn"))
    )

    assert btn is not None
    assert btn.text.strip().lower() == "upload invoice"


def test_file_input_present(driver):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)

    file_input = wait.until(
        EC.presence_of_element_located((By.ID, "fileInput"))
    )

    assert file_input is not None


def test_upload_invoice_e2e(driver):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)

    # Upload file
    file_input = wait.until(
        EC.presence_of_element_located((By.ID, "fileInput"))
    )

    sample_path = create_test_image()

    file_input.send_keys(sample_path)

    # Click upload
    btn = wait.until(
        EC.element_to_be_clickable((By.ID, "uploadBtn"))
    )
    btn.click()

    # Wait for result
    result = wait.until(
        EC.presence_of_element_located((By.ID, "result"))
    )

    assert result.text.strip() != ""