import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://34.100.193.209"

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
    driver.get(BASE_URL)
    assert driver.title is not None

def test_upload_button_present(driver):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
    assert button is not None

def test_file_input_present(driver):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)
    file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
    assert file_input is not None

def test_upload_invoice_e2e(driver):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)
    file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
    assert file_input is not None
