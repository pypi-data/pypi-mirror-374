#!/usr/bin/env python3

import bm25s
from bm25.bm25s_compat import BM25
import math

# Test with a simple corpus
corpus = [
    "medical diagnosis heart disease treatment",
    "heart disease symptoms and treatment options",
    "diabetes management and blood sugar control",
    "cancer treatment chemotherapy radiation therapy",
    "heart attack emergency medical response"
]

# Test query
query = "heart disease treatment"

print("=== BM25S vs Go-BM25 Comparison ===\n")

# Test with bm25s
print("1. Testing with bm25s library:")
corpus_tokens = bm25s.tokenize(corpus)
retriever = bm25s.BM25(corpus=corpus)
retriever.index(corpus_tokens)

query_tokens = bm25s.tokenize(query)
docs, scores = retriever.retrieve(query_tokens, k=5)

print(f"Query: {query}")
print(f"Query tokens: {query_tokens}")
print(f"Method: {retriever.method}")
print(f"K1: {retriever.k1}")
print(f"B: {retriever.b}")
print("\nResults:")
for i, (doc, score) in enumerate(zip(docs[0], scores[0])):
    print(f"  {i+1}. Score: {score:.4f} - {doc}")

print("\n" + "="*50 + "\n")

# Test with our Go implementation
print("2. Testing with Go-BM25 implementation:")
bm25_go = BM25(corpus)

print(f"Query: {query}")
print(f"Query tokens: {bm25_go._tokenizer.tokenize(query)}")
print(f"K1: {bm25_go.k1}")
print(f"B: {bm25_go.b}")
print(f"Epsilon: {bm25_go.epsilon}")

# Let's debug what's happening
print(f"Corpus tokens: {[bm25_go._tokenizer.tokenize(doc) for doc in corpus]}")
print(f"Index size: {len(bm25_go._documents)}")

# Try different return formats
print("\nTrying different return formats:")
try:
    results_dict = bm25_go.retrieve(query, k=5, return_as='dict')
    print(f"Dict results: {results_dict}")
except Exception as e:
    print(f"Dict error: {e}")

try:
    results_tuple = bm25_go.retrieve(query, k=5, return_as='tuple')
    print(f"Tuple results: {results_tuple}")
    print(f"Tuple length: {len(results_tuple)}")
    for i, (doc, score) in enumerate(results_tuple):
        print(f"  {i+1}. Score: {score:.4f} - {doc}")
except Exception as e:
    print(f"Tuple error: {e}")

print("\n" + "="*50 + "\n")

# Let's also check the IDF values for specific terms
print("3. IDF Comparison for key terms:")
key_terms = ["heart", "disease", "treatment", "medical"]

for term in key_terms:
    # bm25s IDF
    bm25s_idf = retriever.idf.get(term, 0.0)
    
    # Go BM25 IDF
    try:
        go_idf = bm25_go.get_term_idf(term)
        print(f"Term '{term}':")
        print(f"  bm25s IDF: {bm25s_idf:.4f}")
        print(f"  Go-BM25 IDF: {go_idf:.4f}")
        print(f"  Difference: {abs(bm25s_idf - go_idf):.4f}")
        print()
    except Exception as e:
        print(f"Term '{term}': Error getting IDF - {e}")

# Let's check document statistics
print("4. Document Statistics:")
print(f"Total documents: {len(corpus)}")
print(f"Average document length (bm25s): {retriever.avg_doc_len:.2f}")
print(f"Average document length (Go-BM25): {bm25_go.avg_doc_len:.2f}")

# Check individual document lengths
print("\nDocument lengths:")
for i, doc in enumerate(corpus):
    bm25s_len = len(corpus_tokens[i])
    go_len = len(bm25_go._tokenizer.tokenize(doc))
    print(f"  Doc {i+1}: bm25s={bm25s_len}, Go-BM25={go_len}, diff={abs(bm25s_len - go_len)}")
