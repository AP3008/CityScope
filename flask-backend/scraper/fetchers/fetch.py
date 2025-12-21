from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def setupDriver(headless=True):
    """
    Setup Chrome WebDriver with appropriate options
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')  # Run without opening browser window
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    # Install and setup ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def expandAllMeetings(driver):
    expand_selectors = [
        "//a[contains(@class, 'expand')]",
        "//a[contains(@class, 'collapsed')]",
        "//button[contains(@class, 'expand')]",
        "//div[contains(@class, 'expandable')]//a",
        "//*[contains(@onclick, 'expand')]",
        "//a[contains(text(), '+')]",
        "//span[contains(@class, 'toggle')]",
    ]
    
    expanded_count = 0
    
    for selector in expand_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            print(f"  Found {len(elements)} elements for selector: {selector[:50]}...")
            
            for element in elements:
                try:
                    # Check if element is visible and clickable
                    if element.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(0.3)
                        element.click()
                        expanded_count += 1
                        time.sleep(0.5)  # Wait for content to load
                except Exception as e:
                    # Element might not be clickable, skip it
                    pass
        except Exception as e:
            # Selector didn't work, try next one
            pass
    
    print(f"  ✓ Expanded {expanded_count} sections")
    
    # Extra wait for any dynamic content to finish loading
    time.sleep(2)

def extractDocumentIdsWithSelenium(url="https://pub-london.escribemeetings.com/", expand=True):
    """
    Use Selenium to scrape DocumentIds from dynamically loaded content
    """
    print(f"{'='*60}")
    print(f"Launching browser to scrape: {url}")
    print(f"{'='*60}\n")
    
    driver = setupDriver(headless=True)  # Set to False to see the browser
    document_ids = set()
    
    try:
        # Load the page
        print("Loading page...")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("  ✓ Page loaded")
        
        # Expand all collapsed sections if requested
        if expand:
            expandAllMeetings(driver)
        
        # Scroll to bottom to trigger any lazy loading
        print("\nScrolling to load all content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 5
        
        while scroll_attempts < max_scrolls:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Calculate new scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
            scroll_attempts += 1
            print(f"  Scroll {scroll_attempts}/{max_scrolls}")
        
        print("  ✓ Finished scrolling")
        
        # Get the fully loaded page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract all DocumentIds
        print("\nExtracting DocumentIds...")
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            if 'FileStream.ashx' in href and 'DocumentId=' in href:
                match = re.search(r'DocumentId=(\d+)', href)
                if match:
                    doc_id = match.group(1)
                    document_ids.add(doc_id)
                    
                    link_text = link.get_text(strip=True)
                    print(f"  Found: DocumentId={doc_id} | {link_text[:60]}")
        
        print(f"\n✓ Extracted {len(document_ids)} unique DocumentIds")
        
    except Exception as e:
        print(f"✗ Error during scraping: {str(e)}")
    
    finally:
        driver.quit()
        print("Browser closed")
    
    return document_ids

def scrapeMultiplePages():
    """
    Scrape multiple committee pages
    """
    pages = [
        "https://pub-london.escribemeetings.com/",
        "https://pub-london.escribemeetings.com/?View=List",
    ]
    
    all_document_ids = set()
    
    for page_url in pages:
        doc_ids = extractDocumentIdsWithSelenium(page_url, expand=True)
        all_document_ids.update(doc_ids)
        print(f"\nRunning total: {len(all_document_ids)} unique documents\n")
    
    for ids in all_document_ids:
        print(ids)
    return all_document_ids

