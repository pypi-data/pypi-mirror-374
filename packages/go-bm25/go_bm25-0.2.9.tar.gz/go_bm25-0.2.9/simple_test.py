#!/usr/bin/env python3

from bm25.bm25s_compat import BM25

# Test with a simple corpus
corpus = [
    "heart disease treatment",
    "diabetes management",
    "cancer therapy"
]

print("Testing Go-BM25 implementation:")
bm25_go = BM25(corpus)

print(f"Corpus: {corpus}")
print(f"Index documents: {bm25_go._documents}")
print(f"Doc IDs: {bm25_go._doc_ids}")

# Test search directly
query = "heart disease"
print(f"\nQuery: {query}")
print(f"Query tokens: {bm25_go._tokenizer.tokenize(query)}")

# Try direct search on the index
try:
    results = bm25_go._index.search(query, 5)
    print(f"Direct search results: {results}")
except Exception as e:
    print(f"Direct search error: {e}")

# Try retrieve method
try:
    results = bm25_go.retrieve(query, k=5, return_as='tuple')
    print(f"Retrieve results: {results}")
except Exception as e:
    print(f"Retrieve error: {e}")

# Check if index has any documents
try:
    doc_count = bm25_go._index.get_document_count()
    print(f"Document count: {doc_count}")
except Exception as e:
    print(f"Document count error: {e}")
