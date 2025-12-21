import sys
import os

# Add parent directory to path so we can import from fetchers and parsers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetchers.fetch import scrapeMultiplePages
from parsers.parser import parseMultiplePdfs, prepareTextForLLM
from summarizer import summarizeMultipleDocuments

def runCompletePipeline(max_documents=None, save_to_file=False, summarize=True):
    """
    Complete pipeline: Scrape -> Parse -> Prepare for LLM -> Summarize
    
    Args:
        max_documents: Limit number of documents to process (None = all)
        save_to_file: Whether to save extracted text to files
        summarize: Whether to generate AI summaries
    
    Returns:
        Tuple of (llm_ready_documents, summaries)
    """
    print("\n" + "="*70)
    print("CITYSCOPE COMPLETE PIPELINE")
    print("="*70)
    
    # STEP 1: Scrape all DocumentIds
    print("\n[STEP 1/3] Scraping DocumentIds from eSCRIBE portal...")
    print("-"*70)
    
    document_ids = scrapeMultiplePages()
    
    if not document_ids:
        print("\n✗ No documents found. Exiting.")
        return []
    
    print(f"\n✓ Found {len(document_ids)} unique documents")
    
    # STEP 2: Parse PDFs and extract text
    print("\n[STEP 2/3] Parsing PDFs and extracting text...")
    print("-"*70)
    
    parsed_documents, failed = parseMultiplePdfs(document_ids, max_docs=max_documents)
    
    if not parsed_documents:
        print("\n✗ No documents parsed successfully. Exiting.")
        return []
    
    # STEP 3: Prepare for LLM
    print("\n[STEP 3/3] Preparing documents for LLM processing...")
    print("-"*70)
    
    llm_ready_documents = []
    
    for doc in parsed_documents:
        llm_doc = prepareTextForLLM(doc)
        llm_ready_documents.append(llm_doc)
        print(f"  ✓ {llm_doc['filename']} ({len(llm_doc['text'])} chars)")
    
    # Optional: Save to files for inspection
    if save_to_file:
        save_dir = 'extracted_texts'
        os.makedirs(save_dir, exist_ok=True)
        
        for doc in llm_ready_documents:
            filename = f"{save_dir}/doc_{doc['document_id']}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"DocumentId: {doc['document_id']}\n")
                f.write(f"Filename: {doc['filename']}\n")
                f.write(f"{'='*70}\n\n")
                f.write(doc['text'])
            print(f"  💾 Saved: {filename}")
    
    # STEP 4: Generate AI Summaries (optional)
    summaries = []
    if summarize and llm_ready_documents:
        print("\n[STEP 4/4] Generating AI summaries with Gemini...")
        print("-"*70)
        
        summaries, failed_summaries = summarizeMultipleDocuments(llm_ready_documents)
        
        # Save summaries if requested
        if save_to_file and summaries:
            summary_dir = 'summaries'
            os.makedirs(summary_dir, exist_ok=True)
            
            for summary in summaries:
                filename = f"{summary_dir}/summary_{summary['document_id']}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"DocumentId: {summary['document_id']}\n")
                    f.write(f"Filename: {summary['filename']}\n")
                    f.write(f"Compression: {summary['compression_ratio']}x\n")
                    f.write(f"{'='*70}\n\n")
                    f.write(summary['summary'])
                print(f"  💾 Saved summary: {filename}")
    
    # Final Summary
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    print(f"  Documents scraped: {len(document_ids)}")
    print(f"  Documents parsed: {len(parsed_documents)}")
    print(f"  Documents failed: {len(failed)}")
    print(f"  Ready for LLM: {len(llm_ready_documents)}")
    if summarize:
        print(f"  Summaries generated: {len(summaries)}")
    print("="*70 + "\n")
    
    return llm_ready_documents, summaries

def getDocumentStats(documents):
    """
    Get statistics about the parsed documents
    """
    if not documents:
        print("\nNo documents to analyze.")
        return
    
    total_words = sum(len(doc['text'].split()) for doc in documents)
    total_chars = sum(len(doc['text']) for doc in documents)
    avg_words = total_words // len(documents) if documents else 0
    
    print("\nDocument Statistics:")
    print(f"  Total documents: {len(documents)}")
    print(f"  Total words: {total_words:,}")
    print(f"  Total characters: {total_chars:,}")
    print(f"  Average words per doc: {avg_words:,}")
    print(f"  Shortest doc: {min(len(d['text'].split()) for d in documents):,} words")
    print(f"  Longest doc: {max(len(d['text'].split()) for d in documents):,} words")

def quickTest(num_docs=3):
    """
    Quick test with limited number of documents
    """
    print("\n🧪 Running quick test with first few documents...\n")
    documents, summaries = runCompletePipeline(max_documents=num_docs, save_to_file=True, summarize=True)
    
    if documents:
        getDocumentStats(documents)
        
        if summaries:
            print("\n📋 Sample Summary:")
            print("="*70)
            print(f"Document: {summaries[0]['filename']}")
            print("-"*70)
            print(summaries[0]['summary'])
            print("="*70)
        
        print("\n✅ Test successful! You can now:")
        print("  1. Check 'extracted_texts/' folder for full document text")
        print("  2. Check 'summaries/' folder for AI-generated summaries")
        print("  3. Integrate with Supabase to store summaries")
    
    return documents, summaries

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CityScope PDF Processing Pipeline')
    parser.add_argument('--test', action='store_true', help='Run quick test with 3 documents')
    parser.add_argument('--max', type=int, default=None, help='Maximum number of documents to process')
    parser.add_argument('--save', action='store_true', help='Save extracted text to files')
    parser.add_argument('--all', action='store_true', help='Process all documents')
    parser.add_argument('--no-summarize', action='store_true', help='Skip AI summarization')
    
    args = parser.parse_args()
    
    summarize = not args.no_summarize
    
    if args.test:
        # Quick test mode
        documents, summaries = quickTest()
    elif args.all:
        # Process all documents
        documents, summaries = runCompletePipeline(save_to_file=args.save, summarize=summarize)
        if documents:
            getDocumentStats(documents)
    else:
        # Custom number of documents
        documents, summaries = runCompletePipeline(max_documents=args.max, save_to_file=args.save, summarize=summarize)
        if documents:
            getDocumentStats(documents)
    
    # Return documents for further processing
    print("\n💡 Next step: Store these summaries in Supabase database!")
    print(f"   Documents processed: {len(documents) if documents else 0}")
    print(f"   Summaries generated: {len(summaries) if summaries else 0}")