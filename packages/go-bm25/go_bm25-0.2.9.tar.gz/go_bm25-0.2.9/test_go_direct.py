#!/usr/bin/env python3

import bm25

# Test the Go implementation directly
print("Testing Go BM25 implementation directly:")

# Create index
index = bm25.new_bm25_index(100, 1000)
print(f"Created index: {index}")

# Add documents
doc1 = "heart disease treatment"
doc2 = "diabetes management"
doc3 = "cancer therapy"

print(f"Adding document 1: {doc1}")
result1 = index.add_document("doc_0", doc1)
print(f"Add result 1: {result1}")

print(f"Adding document 2: {doc2}")
result2 = index.add_document("doc_1", doc2)
print(f"Add result 2: {result2}")

print(f"Adding document 3: {doc3}")
result3 = index.add_document("doc_2", doc3)
print(f"Add result 3: {result3}")

# Check document count
doc_count = index.get_document_count()
print(f"Document count: {doc_count}")

# Try search
query = "heart disease"
print(f"\nSearching for: {query}")
results = index.search(query, 5)
print(f"Search results: {results}")

# Try with tokenizer
tokenizer = bm25.new_english_smart_tokenizer()
print(f"\nUsing tokenizer:")
query_tokens = tokenizer.tokenize(query)
print(f"Query tokens: {query_tokens}")

results2 = index.search(query, 5)
print(f"Search results with tokenizer: {results2}")
