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
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setupDriver(headless=True):
    """Setup Chrome WebDriver with appropriate options"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def expandAllMeetings(driver):
    """Find and click all expand/collapse buttons"""
    print("\nExpanding all meeting sections...")
    
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
            
            for element in elements:
                try:
                    if element.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(0.3)
                        element.click()
                        expanded_count += 1
                        time.sleep(0.5)
                except Exception as e:
                    pass
        except Exception as e:
            pass
    
    print(f"  ✓ Expanded {expanded_count} sections")
    time.sleep(2)

def extractDateFromText(text):
    """
    Try to extract a date from text
    Returns datetime object or None
    """
    # Common date patterns
    patterns = [
        r'(\w+ \d{1,2}, \d{4})',  # January 15, 2024
        r'(\d{1,2}/\d{1,2}/\d{4})',  # 01/15/2024
        r'(\d{4}-\d{2}-\d{2})',  # 2024-01-15
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                date_str = match.group(1)
                # Try different parsing formats
                for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
            except:
                continue
    
    return None

def extractDocumentsWithMetadata(url="https://pub-london.escribemeetings.com/", expand=True):
    """
    Scrape DocumentIds along with meeting metadata (date, title)
    Returns list of dictionaries with document info
    """
    print(f"{'='*60}")
    print(f"Launching browser to scrape: {url}")
    print(f"{'='*60}\n")
    
    driver = setupDriver(headless=True)
    documents = []
    
    try:
        print("Loading page...")
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("  ✓ Page loaded")
        
        if expand:
            expandAllMeetings(driver)
        
        # Scroll to load all content
        print("\nScrolling to load all content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 5
        
        while scroll_attempts < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
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
        
        # Extract all PDFs with metadata
        print("\nExtracting documents with metadata...")
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            if 'FileStream.ashx' in href and 'DocumentId=' in href:
                match = re.search(r'DocumentId=(\d+)', href)
                if match:
                    doc_id = match.group(1)
                    link_text = link.get_text(strip=True)
                    
                    # Try to find meeting date and title from parent elements
                    parent = link.parent
                    meeting_info = parent.get_text(strip=True) if parent else ""
                    
                    # Extract date if possible
                    meeting_date = extractDateFromText(meeting_info)
                    
                    doc_info = {
                        'document_id': doc_id,
                        'link_text': link_text,
                        'meeting_date': meeting_date,
                        'meeting_info': meeting_info[:100]  # First 100 chars for context
                    }
                    
                    documents.append(doc_info)
                    
                    date_str = meeting_date.strftime('%Y-%m-%d') if meeting_date else 'No date'
                    print(f"  Found: DocumentId={doc_id} | Date: {date_str} | {link_text[:50]}")
        
        print(f"\n✓ Extracted {len(documents)} documents with metadata")
        
    except Exception as e:
        print(f"✗ Error during scraping: {str(e)}")
    
    finally:
        driver.quit()
        print("Browser closed")
    
    return documents

def getRecentDocuments(documents, limit=30):
    """
    Get the most recent documents
    
    Args:
        documents: List of document dictionaries with metadata
        limit: Number of recent documents to return
    
    Returns:
        List of most recent document IDs
    """
    # Separate documents with dates from those without
    with_dates = [doc for doc in documents if doc['meeting_date'] is not None]
    without_dates = [doc for doc in documents if doc['meeting_date'] is None]
    
    # Sort by date (most recent first)
    with_dates_sorted = sorted(with_dates, key=lambda x: x['meeting_date'], reverse=True)
    
    # For documents without dates, sort by DocumentId (higher = more recent)
    without_dates_sorted = sorted(without_dates, key=lambda x: int(x['document_id']), reverse=True)
    
    # Combine: dated documents first, then undated
    all_sorted = with_dates_sorted + without_dates_sorted
    
    # Take the most recent N documents
    recent = all_sorted[:limit]
    
    print(f"\n📋 Selected {len(recent)} most recent documents:")
    for doc in recent[:5]:  # Show first 5
        date_str = doc['meeting_date'].strftime('%Y-%m-%d') if doc['meeting_date'] else 'Unknown date'
        print(f"  - {date_str}: {doc['link_text'][:60]}")
    
    if len(recent) > 5:
        print(f"  ... and {len(recent) - 5} more")
    
    # Return just the document IDs
    return [doc['document_id'] for doc in recent]

def scrapeMultiplePages():
    """Scrape multiple pages and return recent documents"""
    pages = [
        "https://pub-london.escribemeetings.com/",
        "https://pub-london.escribemeetings.com/?View=List",
    ]
    
    all_documents = []
    
    for page_url in pages:
        docs = extractDocumentsWithMetadata(page_url, expand=True)
        # Avoid duplicates
        existing_ids = {doc['document_id'] for doc in all_documents}
        new_docs = [doc for doc in docs if doc['document_id'] not in existing_ids]
        all_documents.extend(new_docs)
        print(f"\nRunning total: {len(all_documents)} unique documents\n")
    
    return all_documents

if __name__ == "__main__":
    # Scrape all documents with metadata
    all_documents = scrapeMultiplePages()
    
    # Get the 30 most recent
    recent_doc_ids = getRecentDocuments(all_documents, limit=30)
    
    print(f"\n{'='*60}")
    print(f"Ready to process {len(recent_doc_ids)} recent documents")
    print(f"{'='*60}")