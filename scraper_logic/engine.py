from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


from config import SELECTORS


def get_page_html(window, url):

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=chrome_options)
    try:
        browser.get(url)
        try:
            wait = WebDriverWait(browser, 5)
            cookie_btn = wait.until(EC.element_to_be_clickable(
                (By.ID, SELECTORS.cookie_btn)))
            cookie_btn.click()
            window.new_status.emit("Successfully bypassed cookies.")
            print("Successfully bypassed cookies.")
        except Exception:
            window.new_status.emit("Cookie button not present")
            print("Cookie button not present")
        time.sleep(2)
        return browser.page_source
    finally:
        window.new_status.emit("finished scraping html")
        print("finished scraping html")
        browser.quit()
