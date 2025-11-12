#!/usr/bin/env python3
"""
Script to download DOCX files from PCI Security Standards website.
Scrapes the document library and downloads the appropriate DOCX based on detected language.
Enhanced with anti-detection techniques from pci_pdf_scraper.py
"""

import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time
import os
import random
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_language_option_value(language_code):
    """
    Maps language code to the select option value on the PCI website.
    Based on the HTML structure: English DOCX=1, French DOCX=5, etc.
    """
    language_map = {
        'EN': '1',  # English DOCX
        'FR': '5',  # French DOCX
        'DE': '7',  # German DOCX
        'ES': '13', # Spanish DOCX
        'PT': '11', # Portuguese DOCX
        'ZH': '3',  # Chinese DOCX
        'JA': '9'   # Japanese DOCX
    }
    return language_map.get(language_code.upper(), '1')  # Default to English


def download_docx_from_pciwebsite(language_code, download_path, doc_type='SAQ_D_Merchant'):
    """
    Downloads DOCX file from PCI website based on language and document type.

    Args:
        language_code (str): Language code (EN, FR, DE, ES, PT, ZH, JA)
        download_path (str): Path where the file should be downloaded
        doc_type (str): Document type identifier (default: SAQ_D_Merchant)

    Returns:
        str: Path to the downloaded file, or None if failed
    """
    # Configure WebDriver with anti-detection techniques from pci_pdf_scraper.py
    options = Options()

    # Set download directory
    prefs = {
        "download.default_directory": os.path.abspath(download_path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # Anti-detection configuration (from pci_pdf_scraper.py)
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--window-size=1920,1080')

    # Pool d'user-agents réalistes (from pci_pdf_scraper.py)
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    user_agent = random.choice(user_agents)
    options.add_argument(f"--user-agent={user_agent}")

    driver = webdriver.Chrome(options=options)

    # Application du module selenium-stealth (from pci_pdf_scraper.py)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    # Suppression manuelle des signatures WebDriver (from pci_pdf_scraper.py)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")

    try:
        logger.info(f"Navigating to PCI Security Standards document library...")
        url = "https://www.pcisecuritystandards.org/document_library/"
        driver.get(url)

        # Wait for page to load with increased timeout
        wait = WebDriverWait(driver, 30)

        # Wait for the document category dropdown to be present
        logger.info(f"Waiting for document library to load...")
        try:
            wait.until(
                EC.presence_of_element_located((By.ID, "document_category"))
            )
            logger.info(f"Document library loaded")
        except:
            logger.warning(f"Could not detect category dropdown, continuing anyway...")

        # Additional wait for dynamic content
        time.sleep(3)

        # Select the appropriate category based on doc_type
        # Use the Select class instead of JavaScript to avoid displayTab error
        logger.info(f"Selecting document category...")
        try:
            category_dropdown = driver.find_element(By.ID, "document_category")
            select = Select(category_dropdown)

            # Determine the category value based on doc_type
            # SAQ documents are in the "saqs" category
            category_value = "saqs"  # Default for SAQ documents

            logger.info(f"Setting category to: {category_value}")
            select.select_by_value(category_value)

            # Wait for the content to update (similar to pci_pdf_scraper.py)
            time.sleep(3)
            logger.info(f"Category selected: {category_value}")

        except Exception as e:
            logger.error(f"Error selecting category: {str(e)}")
            logger.info(f"Continuing anyway...")

        # Handle cookie consent overlay if present (RGPD compliance popup)
        logger.info(f"Checking for cookie consent overlay...")
        try:
            # Check if cookie overlay exists
            driver.find_element(By.ID, "ccc-overlay")
            logger.info(f"Cookie consent overlay detected, attempting to dismiss...")

            # Try multiple strategies to dismiss the overlay
            try:
                # Strategy 1: Look for accept button
                accept_button = driver.find_element(By.ID, "ccc-notify-accept")
                accept_button.click()
                logger.info(f"Clicked cookie accept button")
                time.sleep(1)
            except:
                try:
                    # Strategy 2: Look for dismiss button
                    dismiss_button = driver.find_element(By.ID, "ccc-notify-dismiss")
                    dismiss_button.click()
                    logger.info(f"Clicked cookie dismiss button")
                    time.sleep(1)
                except:
                    # Strategy 3: Remove overlay with JavaScript
                    logger.info(f"Removing cookie overlay with JavaScript...")
                    driver.execute_script("""
                        var overlay = document.getElementById('ccc-overlay');
                        if (overlay) overlay.remove();
                        var notify = document.getElementById('ccc-notify');
                        if (notify) notify.remove();
                        var module = document.getElementById('ccc-module');
                        if (module) module.remove();
                    """)
                    time.sleep(1)
        except:
            logger.info(f"No cookie consent overlay found, continuing...")

        # Wait for download buttons to appear (similar to pci_pdf_scraper.py)
        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[id^='download_btn_']"))
            )
            logger.info(f"Download buttons found")
        except Exception as e:
            logger.warning(f"No download buttons found: {e}")

        # Find the SAQ D Merchant row based on the HTML structure
        # The row id is "saqs_SAQ_D_Merchant_row"
        logger.info(f"Looking for {doc_type} document row...")
        row_id = f"saqs_{doc_type}_row"

        try:
            doc_row = wait.until(
                EC.presence_of_element_located((By.ID, row_id))
            )
            logger.info(f"Found document row: {row_id}")

            # Scroll element into view to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView(true);", doc_row)
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Could not find document row with ID '{row_id}'")
            logger.error(f"Exception details: {str(e)}")
            # Debug: print available IDs
            logger.info("Available document rows:")
            try:
                rows = driver.find_elements(By.CLASS_NAME, "document_row")
                logger.info(f"Total rows found: {len(rows)}")
                for row in rows[:30]:  # Print first 30
                    row_id_attr = row.get_attribute('id')
                    if row_id_attr:
                        logger.info(f"  - {row_id_attr}")
            except:
                pass
            return None

        # Find the language select dropdown within this row
        # The select is within the element with id "lang_select_38" (or similar)
        lang_select_cell = doc_row.find_element(By.CSS_SELECTOR, "[id^='lang_select_']")
        lang_dropdown = lang_select_cell.find_element(By.TAG_NAME, "select")

        logger.info(f"Found language dropdown")

        # Get the option value for the requested language
        option_value = get_language_option_value(language_code)
        logger.info(f"Selecting language option: {language_code} (value={option_value})")

        # Select the language option
        select = Select(lang_dropdown)
        select.select_by_value(option_value)

        # Wait a moment for the selection to register (matching pci_pdf_scraper.py timing)
        time.sleep(2)

        # Find and click the download button
        # The download button is within the element with id "download_btn_38" (or similar)
        download_cell = doc_row.find_element(By.CSS_SELECTOR, "[id^='download_btn_']")
        download_link = download_cell.find_element(By.CLASS_NAME, "download_doc")

        logger.info(f"Clicking download button...")

        # Try normal click first, fallback to JavaScript if intercepted
        try:
            download_link.click()
            logger.info(f"Download link clicked successfully")
        except Exception as click_error:
            logger.warning(f"Normal click failed: {click_error}")
            logger.info(f"Attempting JavaScript click as fallback...")
            try:
                # Remove any remaining overlays
                driver.execute_script("""
                    var overlay = document.getElementById('ccc-overlay');
                    if (overlay) overlay.remove();
                    var notify = document.getElementById('ccc-notify');
                    if (notify) notify.remove();
                    var module = document.getElementById('ccc-module');
                    if (module) module.remove();
                """)
                time.sleep(0.5)

                # Click using JavaScript
                driver.execute_script("arguments[0].click();", download_link)
                logger.info(f"JavaScript click executed successfully")
            except Exception as js_error:
                logger.error(f"JavaScript click also failed: {js_error}")
                # Last resort: navigate directly to the href
                try:
                    href = download_link.get_attribute('href')
                    if href:
                        logger.info(f"Navigating directly to download URL: {href}")
                        driver.get(href)
                    else:
                        raise Exception("Could not retrieve download URL")
                except Exception as nav_error:
                    logger.error(f"Direct navigation also failed: {nav_error}")
                    raise

        # Wait for download to complete
        # Check download directory for new file
        logger.info(f"Waiting for download to complete...")
        download_complete = False
        timeout = 30  # 30 seconds timeout
        start_time = time.time()

        while not download_complete and (time.time() - start_time) < timeout:
            time.sleep(1)
            # Check if any .docx file exists in download directory
            for file in os.listdir(download_path):
                if file.endswith('.docx') and not file.endswith('.crdownload'):
                    download_complete = True
                    downloaded_file = os.path.join(download_path, file)
                    logger.info(f"Download complete: {file}")
                    return downloaded_file

        if not download_complete:
            logger.error("Download timed out")
            return None

    except Exception as e:
        logger.error(f"Error during download: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        driver.quit()
        logger.info("Browser closed")


if __name__ == "__main__":
    # Test the function
    import sys

    language = sys.argv[1] if len(sys.argv) > 1 else 'EN'
    download_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    logger.info(f"Testing download for language: {language}")
    logger.info(f"Download directory: {download_dir}")

    result = download_docx_from_pciwebsite(language, download_dir)

    if result:
        logger.info(f"\nSuccess! File downloaded to: {result}")
    else:
        logger.error(f"\nFailed to download file")
        sys.exit(1)