from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from root of flask-backend
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file!")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def saveSummaryToDatabase(summary_data, full_document=None):
    """
    Save a meeting summary to Supabase
    
    Args:
        summary_data: Dictionary with summary info (from summarizer)
        full_document: Optional full document data (from parser)
    
    Returns:
        Result from database insert
    """
    try:
        # Prepare data for database
        db_record = {
            'document_id': summary_data['document_id'],
            'filename': summary_data['filename'],
            'summary': summary_data['summary'],
            'original_url': f"https://pub-london.escribemeetings.com/FileStream.ashx?DocumentId={summary_data['document_id']}",
        }
        
        # Add optional fields if available
        if full_document:
            db_record['raw_text'] = full_document.get('text', '')
            # Try to extract meeting title from metadata
            if full_document.get('metadata'):
                db_record['meeting_title'] = full_document['metadata'].get('title', '')
        
        # Insert into database (upsert to avoid duplicates)
        result = supabase.table('meeting_summaries').upsert(
            db_record,
            on_conflict='document_id'
        ).execute()
        
        print(f"  ✓ Saved to database: {summary_data['filename']}")
        return result
        
    except Exception as e:
        print(f"  ✗ Database error: {str(e)}")
        return None

def saveMultipleSummaries(summaries, full_documents=None):
    """
    Save multiple summaries to database
    
    Args:
        summaries: List of summary dictionaries
        full_documents: Optional list of full document data
    
    Returns:
        Number of successfully saved records
    """
    print(f"\n{'='*70}")
    print(f"Saving {len(summaries)} summaries to Supabase...")
    print(f"{'='*70}\n")
    
    success_count = 0
    
    # Create a lookup dict for full documents
    doc_lookup = {}
    if full_documents:
        doc_lookup = {doc['document_id']: doc for doc in full_documents}
    
    for summary in summaries:
        doc_id = summary['document_id']
        full_doc = doc_lookup.get(doc_id)
        
        result = saveSummaryToDatabase(summary, full_doc)
        if result:
            success_count += 1
    
    print(f"\n{'='*70}")
    print(f"Database Save Complete:")
    print(f"  ✓ Successful: {success_count}/{len(summaries)}")
    print(f"{'='*70}\n")
    
    return success_count

def getAllSummaries(limit=None):
    """
    Retrieve all summaries from database
    
    Args:
        limit: Optional limit on number of results
    
    Returns:
        List of summary records
    """
    try:
        query = supabase.table('meeting_summaries').select('*').order('created_at', desc=True)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        return result.data
        
    except Exception as e:
        print(f"Error retrieving summaries: {str(e)}")
        return []

def getSummaryByDocumentId(document_id):
    """
    Get a specific summary by document ID
    """
    try:
        result = supabase.table('meeting_summaries').select('*').eq('document_id', document_id).execute()
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"Error retrieving summary: {str(e)}")
        return None

def checkIfDocumentExists(document_id):
    """
    Check if a document already exists in database
    """
    try:
        result = supabase.table('meeting_summaries').select('document_id').eq('document_id', document_id).execute()
        return len(result.data) > 0
        
    except Exception as e:
        return False

def getRecentSummaries(days=30):
    """
    Get summaries from the last N days
    """
    try:
        result = supabase.table('meeting_summaries').select('*').gte(
            'created_at', 
            f'now() - interval \'{days} days\''
        ).order('created_at', desc=True).execute()
        
        return result.data
        
    except Exception as e:
        print(f"Error retrieving recent summaries: {str(e)}")
        return []

def testDatabaseConnection():
    """
    Test if Supabase connection is working
    """
    print("\n🧪 Testing Supabase connection...")
    
    try:
        # Try to query the table
        result = supabase.table('meeting_summaries').select('count', count='exact').execute()
        
        print(f"✓ Connection successful!")
        print(f"  Database has {result.count} records")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check SUPABASE_URL and SUPABASE_KEY in .env file")
        print("  2. Verify the table 'meeting_summaries' exists")
        print("  3. Check your Supabase project is running")
        return False

# Example usage
if __name__ == "__main__":
    # Test the connection
    if testDatabaseConnection():
        print("\n✅ Database ready!")
        
        # Show recent summaries
        recent = getAllSummaries(limit=5)
        if recent:
            print(f"\nMost recent {len(recent)} summaries:")
            for summary in recent:
                print(f"  - {summary['filename']} (ID: {summary['document_id']})")
        else:
            print("\nNo summaries in database yet. Run the pipeline to add some!")
    else:
        print("\n❌ Fix database connection before proceeding.")