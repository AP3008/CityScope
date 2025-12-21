import sys
import os

# Add parent directory to path so we can import from fetchers and parsers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetchers.fetch import scrapeMultiplePages
from parsers.parser import parseMultiplePdfs, prepareTextForLLM

def runCompletePipeline(max_documents=None, save_to_file=False):
    """
    Complete pipeline: Scrape -> Parse -> Prepare for LLM
    
    Args:
        max_documents: Limit number of documents to process (None = all)
        save_to_file: Whether to save extracted text to files
    
    Returns:
        List of documents ready for LLM processing
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
    
    # Final Summary
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    print(f"  Documents scraped: {len(document_ids)}")
    print(f"  Documents parsed: {len(parsed_documents)}")
    print(f"  Documents failed: {len(failed)}")
    print(f"  Ready for LLM: {len(llm_ready_documents)}")
    print("="*70 + "\n")
    
    return llm_ready_documents

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
    documents = runCompletePipeline(max_documents=num_docs, save_to_file=True)
    
    if documents:
        getDocumentStats(documents)
        
        print("\n✅ Test successful! You can now:")
        print("  1. Check 'extracted_texts/' folder for saved text files")
        print("  2. Integrate with Gemini LLM for summarization")
        print("  3. Store summaries in Supabase")
    
    return documents

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CityScope PDF Processing Pipeline')
    parser.add_argument('--test', action='store_true', help='Run quick test with 3 documents')
    parser.add_argument('--max', type=int, default=None, help='Maximum number of documents to process')
    parser.add_argument('--save', action='store_true', help='Save extracted text to files')
    parser.add_argument('--all', action='store_true', help='Process all documents')
    
    args = parser.parse_args()
    
    if args.test:
        # Quick test mode
        documents = quickTest()
    elif args.all:
        # Process all documents
        documents = runCompletePipeline(save_to_file=args.save)
        if documents:
            getDocumentStats(documents)
    else:
        # Custom number of documents
        documents = runCompletePipeline(max_documents=args.max, save_to_file=args.save)
        if documents:
            getDocumentStats(documents)
    
    # Return documents for further processing (e.g., LLM summarization)
    print("\n💡 Next step: Pass these documents to your LLM summarizer!")
    print(f"   Example: summarizer.summarizeDocuments(documents)")