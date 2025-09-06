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

query = "heart disease treatment"

print("=== Parameter and Score Comparison ===\n")

# Test with bm25s (default parameters)
print("1. bm25s (default parameters):")
corpus_tokens = bm25s.tokenize(corpus)
retriever = bm25s.BM25(corpus=corpus)
retriever.index(corpus_tokens)

query_tokens = bm25s.tokenize(query)
docs, scores = retriever.retrieve(query_tokens, k=5)

print(f"Method: {retriever.method}")
print(f"K1: {retriever.k1}")
print(f"B: {retriever.b}")
print("Results:")
for i, (doc, score) in enumerate(zip(docs[0], scores[0])):
    print(f"  {i+1}. Score: {score:.4f} - {doc}")

print("\n" + "="*50 + "\n")

# Test with bm25s using same parameters as Go
print("2. bm25s (matching Go parameters K1=1.2, B=0.75):")
retriever2 = bm25s.BM25(corpus=corpus, k1=1.2, b=0.75)
retriever2.index(corpus_tokens)
docs2, scores2 = retriever2.retrieve(query_tokens, k=5)

print(f"Method: {retriever2.method}")
print(f"K1: {retriever2.k1}")
print(f"B: {retriever2.b}")
print("Results:")
for i, (doc, score) in enumerate(zip(docs2[0], scores2[0])):
    print(f"  {i+1}. Score: {score:.4f} - {doc}")

print("\n" + "="*50 + "\n")

# Test with Go implementation
print("3. Go-BM25 implementation:")
bm25_go = BM25(corpus)

# Let's try to get results using the working direct method
import bm25
index = bm25.new_bm25_index(100, 1000)
for i, doc in enumerate(corpus):
    index.add_document(f"doc_{i}", doc)

query_tokens_go = bm25_go._tokenizer.tokenize(query)
query_text = " ".join(query_tokens_go)
results = index.search(query_text, 5)

print(f"K1: {bm25_go.k1}")
print(f"B: {bm25_go.b}")
print(f"Epsilon: {bm25_go.epsilon}")
print(f"Query tokens: {query_tokens_go}")
print("Results:")
for i, result in enumerate(results):
    doc_idx = int(result['DocID'].split('_')[1])
    print(f"  {i+1}. Score: {result['Score']:.4f} - {corpus[doc_idx]}")

print("\n" + "="*50 + "\n")

# Let's also check the IDF calculation differences
print("4. IDF Calculation Comparison:")
print("bm25s IDF formula: log(1 + (N - n + 0.5) / (n + 0.5))")
print("Go-BM25 IDF formula: log((N - n + epsilon) / (n + epsilon))")

# Calculate IDF manually for comparison
N = len(corpus)
for term in ["heart", "disease", "treatment"]:
    # Count documents containing this term
    n = sum(1 for doc_tokens in corpus_tokens if term in doc_tokens)
    
    # bm25s formula
    bm25s_idf = math.log(1 + (N - n + 0.5) / (n + 0.5))
    
    # Go formula (with epsilon=0.25)
    go_idf = math.log((N - n + 0.25) / (n + 0.25))
    
    print(f"Term '{term}' (appears in {n}/{N} docs):")
    print(f"  bm25s IDF: {bm25s_idf:.4f}")
    print(f"  Go-BM25 IDF: {go_idf:.4f}")
    print(f"  Difference: {abs(bm25s_idf - go_idf):.4f}")
    print()
