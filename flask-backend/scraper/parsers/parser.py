import fitz  # PyMuPDF
import requests
import urllib3
from io import BytesIO
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetchPdfFromUrl(document_id):
    """
    Fetch a PDF directly into memory without saving to disk
    Returns the PDF content as bytes
    """
    base_url = "https://pub-london.escribemeetings.com/FileStream.ashx?DocumentId="
    url = f"{base_url}{document_id}"
    
    try:
        print(f"  Fetching DocumentId={document_id}...", end=' ')
        response = requests.get(url, verify=False, timeout=60)
        
        if response.status_code == 200:
            file_size = len(response.content) / 1024  # KB
            print(f"✓ ({file_size:.1f} KB)")
            return response.content
        else:
            print(f"✗ Failed (Status: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None

def extractTextFromPdfBytes(pdf_bytes):
    """
    Extract text from PDF bytes (in-memory)
    """
    try:
        # Open PDF from memory using BytesIO
        pdf_stream = BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        
        full_text = []
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text.append(text)
        
        doc.close()
        
        # Join all pages with double newline
        return '\n\n'.join(full_text)
        
    except Exception as e:
        print(f"    ✗ Error parsing PDF: {str(e)}")
        return None

def extractMetadataFromPdfBytes(pdf_bytes):
    """
    Extract metadata from PDF bytes (in-memory)
    """
    try:
        pdf_stream = BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        metadata = doc.metadata
        doc.close()
        return metadata
    except Exception as e:
        print(f"    ✗ Error extracting metadata: {str(e)}")
        return None

def getFilenameFromResponse(document_id):
    """
    Get the actual filename from the Content-Disposition header
    """
    base_url = "https://pub-london.escribemeetings.com/FileStream.ashx?DocumentId="
    url = f"{base_url}{document_id}"
    
    try:
        response = requests.head(url, verify=False, timeout=10)
        content_disposition = response.headers.get('content-disposition', '')
        
        if 'filename=' in content_disposition:
            filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename_match:
                return filename_match.group(1).strip().replace('"', '')
    except:
        pass
    
    return f"doc_{document_id}.pdf"

def parsePdfFromDocumentId(document_id):
    """
    Complete pipeline: Fetch PDF and extract text
    Returns a dictionary with all extracted data
    """
    # Fetch the PDF
    pdf_bytes = fetchPdfFromUrl(document_id)
    
    if not pdf_bytes:
        return None
    
    # Extract text
    print(f"    Extracting text...", end=' ')
    text = extractTextFromPdfBytes(pdf_bytes)
    
    if not text:
        print("✗ No text extracted")
        return None
    
    print(f"✓ ({len(text)} characters)")
    
    # Extract metadata
    metadata = extractMetadataFromPdfBytes(pdf_bytes)
    filename = getFilenameFromResponse(document_id)
    
    return {
        'document_id': document_id,
        'filename': filename,
        'text': text,
        'text_length': len(text),
        'metadata': metadata,
        'word_count': len(text.split()),
    }

def parseMultiplePdfs(document_ids, max_docs=None):
    """
    Parse multiple PDFs from a list of DocumentIds
    Returns a list of parsed documents
    """
    if max_docs:
        document_ids = list(document_ids)[:max_docs]
    
    parsed_documents = []
    failed_documents = []
    
    print(f"\n{'='*60}")
    print(f"Parsing {len(document_ids)} PDFs...")
    print(f"{'='*60}\n")
    
    for idx, doc_id in enumerate(document_ids, 1):
        print(f"[{idx}/{len(document_ids)}] DocumentId={doc_id}")
        
        result = parsePdfFromDocumentId(doc_id)
        
        if result:
            parsed_documents.append(result)
            print(f"    ✓ Complete: {result['word_count']} words extracted\n")
        else:
            failed_documents.append(doc_id)
            print(f"    ✗ Failed to parse\n")
    
    print(f"{'='*60}")
    print(f"Parsing Summary:")
    print(f"  ✓ Successful: {len(parsed_documents)}")
    print(f"  ✗ Failed: {len(failed_documents)}")
    print(f"{'='*60}\n")
    
    return parsed_documents, failed_documents

def cleanText(text):
    """
    Clean extracted text for LLM processing
    - Remove excessive whitespace
    - Remove page numbers and headers/footers
    - Keep paragraph structure
    """
    if not text:
        return ""
    
    # Remove multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove common header/footer patterns (customize as needed)
    text = re.sub(r'Page \d+ of \d+', '', text)
    
    return text.strip()

def prepareTextForLLM(parsed_document, max_chars=None):
    """
    Prepare extracted text for LLM input
    Optionally truncate if too long
    """
    text = cleanText(parsed_document['text'])
    
    if max_chars and len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Document truncated...]"
    
    return {
        'document_id': parsed_document['document_id'],
        'filename': parsed_document['filename'],
        'text': text,
        'metadata': parsed_document['metadata'],
    }
