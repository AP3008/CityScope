import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fetchers.fetch import scrapeMultiplePages
from parsers.parser import parseMultiplePdfs, prepareTextForLLM
from summarizer import summarizeMultipleDocuments
from database import saveMultipleSummaries

def runCompletePipeline(max_documents=None, save_to_file=False, summarize=True, save_to_db=True):
    print("\n" + "="*70)
    print("CITYSCOPE COMPLETE PIPELINE")
    print("="*70)
    
    # STEP 1: Scrape
    print("\n[STEP 1/5] Scraping DocumentIds...")
    print("-"*70)
    
    all_documents = scrapeMultiplePages()

    if not all_documents:
        print("\n✗ No documents found.")
        return [], []

    all_documents.sort(key=lambda x: int(x['document_id']), reverse=True)
    recent_docs = all_documents[:max_documents] if max_documents else all_documents[:30]
    document_ids = [doc['document_id'] for doc in recent_docs]

    print(f"📋 Processing {len(document_ids)} documents")
    
    # STEP 2: Parse PDFs
    print("\n[STEP 2/5] Parsing PDFs...")
    print("-"*70)
    
    parsed_documents, failed = parseMultiplePdfs(document_ids, max_docs=None)
    
    if not parsed_documents:
        print("\n✗ No documents parsed.")
        return [], []
    
    # STEP 3: Prepare for LLM
    print("\n[STEP 3/5] Preparing for LLM...")
    print("-"*70)
    
    llm_ready_documents = []
    for doc in parsed_documents:
        llm_doc = prepareTextForLLM(doc)
        llm_ready_documents.append(llm_doc)
        print(f"  ✓ {llm_doc['filename']} ({len(llm_doc['text'])} chars)")
    
    # STEP 4: Summarize
    summaries = []
    if summarize and llm_ready_documents:
        print("\n[STEP 4/5] Generating summaries...")
        print("-"*70)
        
        summaries, failed_summaries = summarizeMultipleDocuments(llm_ready_documents)
    
    # STEP 5: Save to database
    if save_to_db and summaries:
        print("\n[STEP 5/5] Saving to Supabase...")
        print("-"*70)
        
        saved_count = saveMultipleSummaries(summaries, recent_docs)
        print(f"  ✓ Saved {saved_count} summaries")
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print(f"  Summaries generated: {len(summaries)}")
    print("="*70 + "\n")
    
    return llm_ready_documents, summaries

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, default=5)
    parser.add_argument('--save', action='store_true')
    
    args = parser.parse_args()
    
    runCompletePipeline(max_documents=args.max, save_to_file=args.save)