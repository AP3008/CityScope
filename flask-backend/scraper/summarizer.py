from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv(dotenv_path='../.env')  # Goes up one level to flask-backend/.env

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)

def summarizeDocument(document_text, filename="", document_id=""):
    """
    Summarize a single city council document using Gemini
    
    Args:
        document_text: The full text of the document
        filename: Optional filename for context
        document_id: Optional document ID for reference
    
    Returns:
        Dictionary with summary and metadata
    """
    
    # Create the prompt
    prompt = f"""You are summarizing official City of London council meeting minutes for residents.

Document: {filename}

Instructions:
- Summarize this city council meeting minutes into 5-7 clear bullet points
- Use simple, non-bureaucratic language that any resident can understand
- Focus ONLY on decisions that directly affect residents (taxes, construction, bylaws, public services)
- Ignore procedural items, attendance, and administrative matters
- Each bullet point should be 1-2 sentences maximum
- Start each bullet with an action verb (Approved, Rejected, Discussed, Decided, etc.)

Meeting Minutes:
{document_text}

Summary:"""

    try:
        print(f"  Sending to Gemini API...", end=' ')
        
        # Use Gemini 2.5 Flash (free tier, large context window, stable)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        summary = response.text.strip()
        
        print(f"✓ ({len(summary)} characters)")
        
        return {
            'document_id': document_id,
            'filename': filename,
            'summary': summary,
            'original_length': len(document_text),
            'summary_length': len(summary),
            'compression_ratio': round(len(document_text) / len(summary), 1) if len(summary) > 0 else 0
        }
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return {
            'document_id': document_id,
            'filename': filename,
            'summary': None,
            'error': str(e)
        }

def summarizeMultipleDocuments(documents, delay=1.0):
    """
    Summarize multiple documents with rate limiting
    
    Args:
        documents: List of documents from parser (with 'text', 'filename', 'document_id')
        delay: Delay between API calls to respect rate limits (seconds)
    
    Returns:
        List of summaries
    """
    summaries = []
    failed = []
    
    print(f"\n{'='*70}")
    print(f"Summarizing {len(documents)} documents with Gemini...")
    print(f"{'='*70}\n")
    
    for idx, doc in enumerate(documents, 1):
        print(f"[{idx}/{len(documents)}] {doc['filename']}")
        
        result = summarizeDocument(
            document_text=doc['text'],
            filename=doc['filename'],
            document_id=doc['document_id']
        )
        
        if result.get('summary'):
            summaries.append(result)
            print(f"  ✓ Summary: {len(result['summary'])} chars, {result['compression_ratio']}x compression\n")
        else:
            failed.append(result)
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}\n")
        
        # Rate limiting - respect Gemini free tier (15 requests/min)
        if idx < len(documents):
            time.sleep(delay)
    
    print(f"{'='*70}")
    print(f"Summarization Complete:")
    print(f"  ✓ Successful: {len(summaries)}")
    print(f"  ✗ Failed: {len(failed)}")
    print(f"{'='*70}\n")
    
    return summaries, failed

def customPromptSummary(document_text, custom_prompt):
    """
    Use a custom prompt for summarization (for testing different approaches)
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{custom_prompt}\n\nDocument:\n{document_text}"
        )
        return response.text.strip()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def testGeminiConnection():
    """
    Test if Gemini API is working
    """
    print("\n🧪 Testing Gemini API connection...")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Say 'Hello from Gemini!' if you're working."
        )
        
        print(f"✓ Connection successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check your GEMINI_API_KEY in .env file")
        print("  2. Verify the API key is valid at https://makersuite.google.com/app/apikey")
        print("  3. Ensure you have internet connection")
        print("  4. Try listing available models with: client.models.list()")
        return False

def listAvailableModels():
    """
    List all available Gemini models
    """
    try:
        print("\n📋 Available Gemini models:")
        models = client.models.list()
        for model in models:
            print(f"  - {model.name}")
        return models
    except Exception as e:
        print(f"✗ Error listing models: {str(e)}")
        return []

# Example usage
if __name__ == "__main__":
    # Test the connection first
    if testGeminiConnection():
        print("\n✅ Ready to summarize documents!")
        
        # Example: Test with sample text
        sample_text = """
        City Council Meeting - January 15, 2024
        
        Motion: Approve $2.5M budget for new community center in North London.
        Vote: Passed 8-3
        
        Discussion: Proposed bylaw to restrict construction noise to 7am-7pm on weekdays.
        Decision: Referred to committee for further review.
        
        Announcement: Property tax increase of 2.5% for 2024 fiscal year.
        """
        
        print("\n📝 Testing with sample text...\n")
        result = summarizeDocument(sample_text, filename="Test Document", document_id="test_001")
        
        if result.get('summary'):
            print("\n" + "="*70)
            print("SAMPLE SUMMARY:")
            print("="*70)
            print(result['summary'])
            print("="*70)
    else:
        print("\n❌ Fix API connection before proceeding.")
        print("\nTrying to list available models...")
        listAvailableModels()