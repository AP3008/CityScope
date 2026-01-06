import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fetchers.fetch import scrapeMultiplePages
from parsers.parser import parseMultiplePdfs, prepareTextForLLM
from summarizer import summarizeMultipleDocuments
from database import saveMultipleSummaries, checkIfDocumentExists

def runCompletePipeline(max_documents=5, save_to_file=False, summarize=True, save_to_db=True, check_duplicates=True):
    """
    Complete pipeline with duplicate checking and batch processing
    
    Args:
        max_documents: Maximum number of NEW documents to process (default: 5)
        save_to_file: Whether to save extracted text to files
        summarize: Whether to generate AI summaries
        save_to_db: Whether to save summaries to Supabase
        check_duplicates: Whether to skip documents already in database
    
    Returns:
        Tuple of (llm_ready_documents, summaries)
    """
    print("\n" + "="*70)
    print("CITYSCOPE COMPLETE PIPELINE")
    print("="*70)
    
    # STEP 1: Scrape Document IDs
    print("\n[STEP 1/6] Scraping DocumentIds from eSCRIBE portal...")
    print("-"*70)
    
    all_documents = scrapeMultiplePages()

    if not all_documents:
        print("\n✗ No documents found. Exiting.")
        return [], []

    # Sort by document_id (higher = newer)
    all_documents.sort(key=lambda x: int(x['document_id']), reverse=True)

    print(f"📋 Found {len(all_documents)} total documents")
    
    # STEP 2: Filter out duplicates if requested
    documents_to_process = []
    skipped_count = 0
    
    if check_duplicates:
        print("\n[STEP 2/6] Checking for existing documents in database...")
        print("-"*70)
        
        for doc in all_documents:
            if len(documents_to_process) >= max_documents:
                break
                
            doc_id = doc['document_id']
            
            if checkIfDocumentExists(doc_id):
                print(f"  ⊘ Skipping DocumentId={doc_id} (already in database)")
                skipped_count += 1
            else:
                documents_to_process.append(doc)
                print(f"  ✓ DocumentId={doc_id} (new)")
        
        print(f"\n  New documents to process: {len(documents_to_process)}")
        print(f"  Duplicates skipped: {skipped_count}")
    else:
        documents_to_process = all_documents[:max_documents]
    
    if not documents_to_process:
        print("\n✓ No new documents to process. Database is up to date!")
        return [], []
    
    document_ids = [doc['document_id'] for doc in documents_to_process]
    
    # STEP 3: Parse PDFs and extract text
    print(f"\n[STEP 3/6] Parsing {len(document_ids)} PDFs...")
    print("-"*70)
    
    parsed_documents, failed = parseMultiplePdfs(document_ids, max_docs=None)
    
    if not parsed_documents:
        print("\n✗ No documents parsed successfully. Exiting.")
        return [], []
    
    # STEP 4: Prepare for LLM
    print("\n[STEP 4/6] Preparing documents for LLM processing...")
    print("-"*70)
    
    llm_ready_documents = []
    for doc in parsed_documents:
        llm_doc = prepareTextForLLM(doc)
        llm_ready_documents.append(llm_doc)
        print(f"  ✓ {llm_doc['filename'][:50]} ({len(llm_doc['text'])} chars)")
    
    # STEP 5: Extract metadata and generate summaries
    summaries = []
    if summarize and llm_ready_documents:
        print("\n[STEP 5/6] Extracting metadata and generating summaries...")
        print("-"*70)
        
        summaries, failed_summaries = summarizeMultipleDocuments(llm_ready_documents)
        
        if failed_summaries:
            print(f"\n⚠️  Skipped {len(failed_summaries)} documents (missing title/date)")
    
    # STEP 6: Save to Supabase
    if save_to_db and summaries:
        print("\n[STEP 6/6] Saving summaries to Supabase...")
        print("-"*70)
        
        saved_count = saveMultipleSummaries(summaries)
        print(f"  ✓ Saved {saved_count} new summaries to database")
    
    # Final Summary
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    print(f"  Documents found: {len(all_documents)}")
    print(f"  Already in database: {skipped_count}")
    print(f"  New documents processed: {len(parsed_documents)}")
    print(f"  Summaries generated: {len(summaries)}")
    print(f"  Failed/Skipped: {len(failed_summaries) if summarize else 0}")
    print("="*70 + "\n")
    
    return llm_ready_documents, summaries

def quickTest(num_docs=3):
    """Quick test with limited documents"""
    print("\n🧪 Running quick test...\n")
    documents, summaries = runCompletePipeline(max_documents=num_docs, check_duplicates=True, save_to_db=True)
    
    if summaries:
        print("\n📋 Sample Summary:")
        print("="*70)
        print(f"Title: {summaries[0]['meeting_title']}")
        print(f"Date: {summaries[0]['meeting_date']}")
        print("-"*70)
        print(summaries[0]['summary'])
        print("="*70)
        
        print("\n✅ Test successful!")
        print("  Check your Supabase database for the summaries")
    elif documents:
        print("\n✅ Test complete! All documents were already in database.")
    
    return documents, summaries

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CityScope PDF Processing Pipeline')
    parser.add_argument('--test', action='store_true', help='Run quick test with 3 documents')
    parser.add_argument('--max', type=int, default=5, help='Maximum number of NEW documents to process (default: 5)')
    parser.add_argument('--save', action='store_true', help='Save extracted text to files')
    parser.add_argument('--no-check', action='store_true', help='Disable duplicate checking')
    
    args = parser.parse_args()
    
    check_dups = not args.no_check
    
    if args.test:
        documents, summaries = quickTest()
    else:
        documents, summaries = runCompletePipeline(
            max_documents=args.max, 
            save_to_file=args.save,
            check_duplicates=check_dups
        )
    
    print("\n💡 Next steps:")
    print("  • View summaries at http://localhost:3000")
    print("  • Check Supabase dashboard for stored data")
    print(f"  • {len(summaries) if summaries else 0} new summaries added")