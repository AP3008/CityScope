from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file!")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def saveSummaryToDatabase(summary_data, document_metadata=None):
    """
    Save a meeting summary to Supabase (WITHOUT raw_text)
    
    Args:
        summary_data: Dictionary with summary info (from summarizer)
        document_metadata: Dictionary with meeting_title and meeting_date
    
    Returns:
        Result from database insert
    """
    try:
        # Prepare data for database (NO raw_text)
        db_record = {
            'document_id': summary_data['document_id'],
            'summary': summary_data['summary'],
            'original_url': f"https://pub-london.escribemeetings.com/FileStream.ashx?DocumentId={summary_data['document_id']}",
        }
        
        # Add metadata if available
        if document_metadata:
            db_record['meeting_title'] = document_metadata.get('meeting_title', summary_data.get('filename', 'Unknown Meeting'))
            if document_metadata.get('meeting_date'):
                db_record['meeting_date'] = document_metadata['meeting_date'].strftime('%Y-%m-%d')
        else:
            db_record['meeting_title'] = summary_data.get('filename', 'Unknown Meeting')
        
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

def saveMultipleSummaries(summaries, documents_metadata):
    """
    Save multiple summaries to database
    
    Args:
        summaries: List of summary dictionaries
        documents_metadata: List of document metadata (meeting_title, meeting_date)
    
    Returns:
        Number of successfully saved records
    """
    print(f"\n{'='*70}")
    print(f"Saving {len(summaries)} summaries to Supabase...")
    print(f"{'='*70}\n")
    
    success_count = 0
    
    # Create a lookup dict for metadata
    metadata_lookup = {}
    if documents_metadata:
        metadata_lookup = {doc['document_id']: doc for doc in documents_metadata}
    
    for summary in summaries:
        doc_id = summary['document_id']
        metadata = metadata_lookup.get(doc_id)
        
        result = saveSummaryToDatabase(summary, metadata)
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
        query = supabase.table('meeting_summaries').select('*').order('created_at', desc=True)
        
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
        ).order('created_at', desc=True).execute()
        
        return result.data
        
    except Exception as e:
        print(f"Error retrieving recent summaries: {str(e)}")
        return []

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
    else:
        print("\n❌ Fix database connection before proceeding.")