from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def saveSummaryToDatabase(summary_data):
    """
    Save a meeting summary to Supabase
    Summary data already contains: title, date, summary from Gemini
    
    Args:
        summary_data: Dictionary with all required fields from summarizer
    
    Returns:
        Result from database insert
    """
    try:
        db_record = {
            'document_id': summary_data['document_id'],
            'meeting_title': summary_data['meeting_title'],
            'meeting_date': summary_data['meeting_date'],
            'summary': summary_data['summary'],
            'original_url': f"https://pub-london.escribemeetings.com/FileStream.ashx?DocumentId={summary_data['document_id']}",
        }
        
        # Insert into database (upsert to avoid duplicates)
        result = supabase.table('meeting_summaries').upsert(
            db_record,
            on_conflict='document_id'
        ).execute()
        
        print(f"  ✓ Saved to database: {db_record['meeting_title']}")
        return result
        
    except Exception as e:
        print(f"  ✗ Database error: {str(e)}")
        return None

def saveMultipleSummaries(summaries):
    """
    Save multiple summaries to database
    
    Args:
        summaries: List of summary dictionaries from summarizer
    
    Returns:
        Number of successfully saved records
    """
    print(f"\n{'='*70}")
    print(f"Saving {len(summaries)} summaries to Supabase...")
    print(f"{'='*70}\n")
    
    success_count = 0
    
    for summary in summaries:
        result = saveSummaryToDatabase(summary)
        if result:
            success_count += 1
    
    print(f"\n{'='*70}")
    print(f"Database Save Complete:")
    print(f"  ✓ Successful: {success_count}/{len(summaries)}")
    print(f"{'='*70}\n")
    
    return success_count

def getAllSummaries(limit=None):
    """Retrieve all summaries from database"""
    try:
        query = supabase.table('meeting_summaries').select('*').order('meeting_date', desc=True)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        return result.data
        
    except Exception as e:
        print(f"Error retrieving summaries: {str(e)}")
        return []

def getSummaryByDocumentId(document_id):
    """Get a specific summary by document ID"""
    try:
        result = supabase.table('meeting_summaries').select('*').eq('document_id', document_id).execute()
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"Error retrieving summary: {str(e)}")
        return None

def getRecentSummaries(days=30):
    """Get summaries from the last N days"""
    try:
        result = supabase.table('meeting_summaries').select('*').gte(
            'created_at', 
            f'now() - interval \'{days} days\''
        ).order('meeting_date', desc=True).execute()
        
        return result.data
        
    except Exception as e:
        print(f"Error retrieving recent summaries: {str(e)}")
        return []

def checkIfDocumentExists(document_id):
    """
    Check if a document already exists in database
    
    Args:
        document_id: The document ID to check
        
    Returns:
        Boolean - True if exists, False otherwise
    """
    try:
        result = supabase.table('meeting_summaries').select('document_id').eq('document_id', document_id).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"Error checking document existence: {str(e)}")
        return False

def testDatabaseConnection():
    """Test if Supabase connection is working"""
    print("\n🧪 Testing Supabase connection...")
    
    try:
        result = supabase.table('meeting_summaries').select('count', count='exact').execute()
        
        print(f"✓ Connection successful!")
        print(f"  Database has {result.count} records")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    if testDatabaseConnection():
        print("\n✅ Database ready!")
        
        recent = getAllSummaries(limit=5)
        if recent:
            print(f"\nMost recent {len(recent)} summaries:")
            for summary in recent:
                print(f"  - {summary.get('meeting_title', 'No title')} ({summary.get('meeting_date', 'No date')})")
    else:
        print("\n❌ Fix database connection before proceeding.")