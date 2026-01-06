from google import genai
import os
from dotenv import load_dotenv
import time
import json

load_dotenv(dotenv_path='../.env')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

client = genai.Client(api_key=GEMINI_API_KEY)

def extractMetadataAndSummarize(document_text, filename="", document_id=""):
    """
    Extract title, date, and create summary from document
    
    Returns:
        Dictionary with title, date, summary, or None if extraction fails
    """
    
    prompt = f"""You are analyzing City of London council meeting minutes.

TASK: Extract the meeting title, date, and create a concise summary.

DOCUMENT TEXT:
{document_text}

RESPOND IN THIS EXACT JSON FORMAT (no markdown, no code blocks, just raw JSON):
{{
  "meeting_title": "Full meeting title from the document",
  "meeting_date": "YYYY-MM-DD format",
  "summary": "First sentence describing the meeting topic. Then bullet points of major actions taken."
}}

RULES:
1. meeting_title: Extract the EXACT official meeting title (e.g., "Planning and Environment Committee")
2. meeting_date: Must be in YYYY-MM-DD format. If no date found, use null
3. summary: 
   - First sentence: What the meeting was about
   - Then use bullet points for major actions (use • symbol)
   - Focus ONLY on decisions affecting residents (taxes, construction, bylaws, services)
   - Ignore procedural items and attendance
   - Do NOT use asterisks, markdown, or formatting symbols
   - Keep each bullet point to 1-2 sentences maximum

IMPORTANT: If you cannot find a clear meeting title or date, set them to null.

Respond with ONLY the JSON, nothing else:"""

    try:
        print(f"  Extracting metadata and summarizing...", end=' ')
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Parse JSON response
        data = json.loads(response_text)
        
        # Validate required fields
        if not data.get('meeting_title') or not data.get('meeting_date'):
            print(f"✗ Missing title or date")
            return None
        
        # Validate date format
        if data['meeting_date'] == 'null' or not data['meeting_date']:
            print(f"✗ Invalid date")
            return None
        
        print(f"✓ ({len(data['summary'])} chars)")
        
        return {
            'document_id': document_id,
            'filename': filename,
            'meeting_title': data['meeting_title'],
            'meeting_date': data['meeting_date'],
            'summary': data['summary'],
            'original_length': len(document_text),
            'summary_length': len(data['summary']),
            'compression_ratio': round(len(document_text) / len(data['summary']), 1) if len(data['summary']) > 0 else 0
        }
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON Error: {str(e)}")
        print(f"Response was: {response_text[:200]}")
        return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None

def summarizeMultipleDocuments(documents, delay=2.0):
    """
    Process multiple documents with metadata extraction
    
    Args:
        documents: List of documents from parser
        delay: Delay between API calls (seconds)
    
    Returns:
        Tuple of (summaries, failed)
    """
    summaries = []
    failed = []
    
    print(f"\n{'='*70}")
    print(f"Processing {len(documents)} documents with Gemini...")
    print(f"{'='*70}\n")
    
    for idx, doc in enumerate(documents, 1):
        print(f"[{idx}/{len(documents)}] {doc['filename']}")
        
        result = extractMetadataAndSummarize(
            document_text=doc['text'],
            filename=doc['filename'],
            document_id=doc['document_id']
        )
        
        if result:
            summaries.append(result)
            print(f"  ✓ Title: {result['meeting_title'][:50]}")
            print(f"  ✓ Date: {result['meeting_date']}\n")
        else:
            failed.append({
                'document_id': doc['document_id'],
                'filename': doc['filename'],
                'error': 'Failed to extract title or date'
            })
            print(f"  ✗ Skipping document (no valid title/date)\n")
        
        # Rate limiting
        if idx < len(documents):
            time.sleep(delay)
    
    print(f"{'='*70}")
    print(f"Processing Complete:")
    print(f"  ✓ Successful: {len(summaries)}")
    print(f"  ✗ Skipped: {len(failed)}")
    print(f"{'='*70}\n")
    
    return summaries, failed

def testGeminiConnection():
    """Test if Gemini API is working"""
    print("\n🧪 Testing Gemini API connection...")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="Say 'Hello from Gemini!' if you're working."
        )
        
        print(f"✓ Connection successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    if testGeminiConnection():
        print("\n✅ Ready to process documents!")
        
        # Test with sample
        sample_text = """
        Planning and Environment Committee
        Meeting Date: January 15, 2024
        
        Motion: Approve $2.5M budget for new community center in North London.
        Vote: Passed 8-3
        
        Discussion: Proposed bylaw to restrict construction noise to 7am-7pm on weekdays.
        Decision: Referred to committee for further review.
        
        Announcement: Property tax increase of 2.5% for 2024 fiscal year.
        """
        
        print("\n🔍 Testing with sample...\n")
        result = extractMetadataAndSummarize(sample_text, "Test", "test_001")
        
        if result:
            print("\n" + "="*70)
            print("SAMPLE RESULT:")
            print("="*70)
            print(f"Title: {result['meeting_title']}")
            print(f"Date: {result['meeting_date']}")
            print(f"\n{result['summary']}")
            print("="*70)
    else:
        print("\n❌ Fix API connection before proceeding.")