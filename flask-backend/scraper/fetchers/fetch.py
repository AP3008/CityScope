from bs4 import BeautifulSoup
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrapePage():
    pageToScrape = requests.get("https://pub-london.escribemeetings.com/?MeetingViewId=1&Expanded=Audit%20Committee", verify=False)
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    pdfLinks = []
    baseUrl = 'https://pub-london.escribemeetings.com/'


    for link in soup.find_all('a',href=True):
        href = link.get('href','')
        if 'FileStream.ashx' in href:
            url = link['href']
            if url.startswith('https://'):
                pdfLinks.append(url)
            else: 
                url = baseUrl + url
                pdfLinks.append(url)
            print(f'PDF Found: {url}')



scrapePage() 