"""
Python wrapper for Go BM25 library using ctypes.

This module provides Python bindings for the high-performance BM25 ranking
algorithm implementation written in Go.
"""

import ctypes
import json
import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# Load the shared library
def _load_library():
    """Load the Go shared library."""
    # Get the directory where this Python file is located
    current_dir = Path(__file__).parent
    
    # Try to find the shared library
    lib_paths = [
        current_dir / "libbm25.so",      # Linux
        current_dir / "libbm25.dylib",   # macOS
        current_dir / "libbm25.dll",     # Windows
    ]
    
    for lib_path in lib_paths:
        if lib_path.exists():
            return ctypes.CDLL(str(lib_path))
    
    raise FileNotFoundError(f"Could not find BM25 shared library in {current_dir}")

try:
    _lib = _load_library()
except Exception as e:
    print(f"Warning: Could not load BM25 library: {e}")
    _lib = None

# Define function signatures
if _lib:
    _lib.HelloBM25.restype = ctypes.c_char_p
    _lib.NewBM25Index.argtypes = [ctypes.c_int, ctypes.c_int]
    _lib.NewBM25Index.restype = ctypes.c_longlong
    _lib.AddDocument.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_char_p]
    _lib.AddDocument.restype = ctypes.c_int
    _lib.Search.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_int]
    _lib.Search.restype = ctypes.c_char_p
    _lib.CreateEnglishSmartTokenizer.restype = ctypes.c_longlong
    _lib.CreateSmartTokenizer.argtypes = [ctypes.c_char_p]
    _lib.CreateSmartTokenizer.restype = ctypes.c_longlong
    _lib.TokenizeText.argtypes = [ctypes.c_longlong, ctypes.c_char_p]
    _lib.TokenizeText.restype = ctypes.c_char_p
    
    # Batch search functions
    _lib.BatchSearch.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong, ctypes.c_int]
    _lib.BatchSearch.restype = ctypes.c_char_p
    
    # GetMatches function
    _lib.GetMatches.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_char_p]
    _lib.GetMatches.restype = ctypes.c_char_p
    
    # Save/Load functions
    _lib.SaveIndex.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_int]
    _lib.SaveIndex.restype = ctypes.c_int
    _lib.LoadIndex.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_int]
    _lib.LoadIndex.restype = ctypes.c_int
    _lib.GetTokenizedDocuments.argtypes = [ctypes.c_longlong]
    _lib.GetTokenizedDocuments.restype = ctypes.c_char_p
    # Free function for memory management
    _lib.free.argtypes = [ctypes.c_void_p]
    _lib.free.restype = None
    
    # IDF functions
    _lib.GetTermIDF.argtypes = [ctypes.c_longlong, ctypes.c_char_p]
    _lib.GetTermIDF.restype = ctypes.c_double
    _lib.GetAllTermIDFs.argtypes = [ctypes.c_longlong]
    _lib.GetAllTermIDFs.restype = ctypes.c_char_p
    _lib.GetTermIDFsSorted.argtypes = [ctypes.c_longlong, ctypes.c_char_p]
    _lib.GetTermIDFsSorted.restype = ctypes.c_char_p
    _lib.GetTermStats.argtypes = [ctypes.c_longlong, ctypes.c_char_p]
    _lib.GetTermStats.restype = ctypes.c_char_p

class TermMatch:
    """Represents a term match found in a document."""
    
    def __init__(self, term: str, frequency: int, position: int):
        """
        Initialize a term match.
        
        Args:
            term: The term that was matched
            frequency: Frequency of the term in the document
            position: Position of the term in the document
        """
        self._term = term
        self._frequency = frequency
        self._position = position
    
    @property
    def term(self) -> str:
        """Get the matched term."""
        return self._term
    
    @property
    def frequency(self) -> int:
        """Get the frequency of the term in the document."""
        return self._frequency
    
    @property
    def position(self) -> int:
        """Get the position of the term in the document."""
        return self._position
    
    def __repr__(self) -> str:
        return f"TermMatch(term='{self._term}', frequency={self._frequency}, position={self._position})"

class BatchSearchResult:
    """Represents the result of a batch search operation."""
    
    def __init__(self, query: str, results: List[Dict[str, Any]]):
        """
        Initialize a batch search result.
        
        Args:
            query: The search query
            results: List of search results for this query
        """
        self._query = query
        self._results = results
    
    @property
    def query(self) -> str:
        """Get the search query."""
        return self._query
    
    @property
    def results(self) -> List[Dict[str, Any]]:
        """Get the search results."""
        return self._results

class BM25Index:
    """High-performance BM25 index with Go backend."""
    
    def __init__(self, doc_capacity: int = 1000, term_capacity: int = 10000):
        """
        Initialize a new BM25 index.
        
        Args:
            doc_capacity: Maximum number of documents the index can hold
            term_capacity: Maximum number of unique terms the index can hold
        """
        if _lib is None:
            raise RuntimeError("BM25 library not available")
        
        self._handle = _lib.NewBM25Index(doc_capacity, term_capacity)
        self._doc_capacity = doc_capacity
        self._term_capacity = term_capacity
    
    def add_document(self, doc_id: str, content: str) -> bool:
        """
        Add a document to the index.
        
        Args:
            doc_id: Unique identifier for the document
            content: Text content of the document
            
        Returns:
            True if the document was added successfully, False otherwise
        """
        if _lib is None:
            return False
        
        result = _lib.AddDocument(
            self._handle,
            doc_id.encode('utf-8'),
            content.encode('utf-8')
        )
        return result == 0
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of search results, each containing 'doc_id' and 'score'
        """
        if _lib is None:
            return []
        
        result_ptr = _lib.Search(
            self._handle,
            query.encode('utf-8'),
            limit
        )
        
        if result_ptr is None:
            return []
        
        result_str = ctypes.string_at(result_ptr).decode('utf-8')
          # Free the C string
        
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return []
    
    def clear(self):
        """Clear all documents from the index."""
        # For now, we'll create a new index
        # In a full implementation, we'd add a Clear method to the Go library
        self._handle = _lib.NewBM25Index(self._doc_capacity, self._term_capacity)
    
    def batch_search(self, queries: List[str], tokenizer, limit: int = 10) -> List[BatchSearchResult]:
        """
        Perform batch search on multiple queries.
        
        Args:
            queries: List of search queries
            tokenizer: Tokenizer to use for the queries
            limit: Maximum number of results per query
            
        Returns:
            List of BatchSearchResult objects
        """
        if _lib is None:
            return []
        
        # Convert queries to JSON
        queries_json = json.dumps(queries)
        
        # Get tokenizer handle
        tokenizer_handle = getattr(tokenizer, '_handle', None)
        if tokenizer_handle is None:
            return []
        
        result_ptr = _lib.BatchSearch(
            self._handle,
            queries_json.encode('utf-8'),
            tokenizer_handle,
            limit
        )
        
        if result_ptr is None:
            return []
        
        result_str = ctypes.string_at(result_ptr).decode('utf-8')
        
        
        try:
            batch_results = json.loads(result_str)
            return [BatchSearchResult(query, results) for query, results in batch_results]
        except json.JSONDecodeError:
            return []
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the index."""
        # This would need to be implemented in the Go library
        return 0
    
    def get_term_count(self) -> int:
        """Get the total number of unique terms in the index."""
        # This would need to be implemented in the Go library
        return 0
    
    def get_average_document_length(self) -> float:
        """Get the average document length in the index."""
        # This would need to be implemented in the Go library
        return 0.0
    
    def get_matches(self, tokens: List[str], doc_id: str) -> List[TermMatch]:
        """
        Get term matches for specific tokens in a document.
        
        Args:
            tokens: List of tokens to search for
            doc_id: Document ID to search in
            
        Returns:
            List of TermMatch objects
        """
        if _lib is None:
            return []
        
        # Convert tokens to JSON
        tokens_json = json.dumps(tokens)
        
        result_ptr = _lib.GetMatches(
            self._handle,
            tokens_json.encode('utf-8'),
            doc_id.encode('utf-8')
        )
        
        if result_ptr is None:
            return []
        
        result_str = ctypes.string_at(result_ptr).decode('utf-8')
        
        
        try:
            matches_data = json.loads(result_str)
            matches = []
            for match_data in matches_data:
                match = TermMatch(
                    match_data['term'],
                    match_data['frequency'],
                    match_data['position']
                )
                matches.append(match)
            return matches
        except (json.JSONDecodeError, KeyError):
            return []
    
    def save(self, path: str, include_documents: bool = True) -> bool:
        """
        Save the index to a file.
        
        Args:
            path: File path to save to
            include_documents: Whether to include document content in the save
            
        Returns:
            True if successful, False otherwise
        """
        if _lib is None:
            return False
        
        result = _lib.SaveIndex(
            self._handle,
            path.encode('utf-8'),
            1 if include_documents else 0
        )
        return result == 0
    
    def load(self, path: str, load_corpus: bool = True) -> bool:
        """
        Load an index from a file.
        
        Args:
            path: File path to load from
            load_corpus: Whether to load document content
            
        Returns:
            True if successful, False otherwise
        """
        if _lib is None:
            return False
        
        result = _lib.LoadIndex(
            self._handle,
            path.encode('utf-8'),
            1 if load_corpus else 0
        )
        return result == 0
    
    def get_tokenized_documents(self) -> List[List[str]]:
        """
        Get all tokenized documents from the index.
        
        Returns:
            List of tokenized documents (list of token lists)
        """
        if _lib is None:
            return []
        
        result_ptr = _lib.GetTokenizedDocuments(self._handle)
        
        if result_ptr is None:
            return []
        
        result_str = ctypes.string_at(result_ptr).decode('utf-8')
        
        
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return []
    
    def get_term_idf(self, term: str) -> float:
        """
        Get the IDF (Inverse Document Frequency) value for a specific term.
        
        Args:
            term: The term to get IDF for
            
        Returns:
            IDF value for the term, or 0.0 if term doesn't exist
        """
        if _lib is None:
            return 0.0
        
        return _lib.GetTermIDF(self._handle, term.encode('utf-8'))
    
    def get_all_term_idfs(self) -> List[Dict[str, Any]]:
        """
        Get all term-IDF pairs from the index.
        
        Returns:
            List of dictionaries containing 'term', 'idf', and 'docCount'
        """
        if _lib is None:
            return []
        
        result_ptr = _lib.GetAllTermIDFs(self._handle)
        
        if result_ptr is None:
            return []
        
        result_str = ctypes.string_at(result_ptr).decode('utf-8')
        
        
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return []
    
    def get_term_idfs_sorted(self, sort_by: str = "idf") -> List[Dict[str, Any]]:
        """
        Get all term-IDF pairs sorted by the specified criteria.
        
        Args:
            sort_by: Sort criteria - "idf" (default), "term", or "docCount"
            
        Returns:
            List of dictionaries containing 'term', 'idf', and 'docCount', sorted
        """
        if _lib is None:
            return []
        
        result_ptr = _lib.GetTermIDFsSorted(
            self._handle, 
            sort_by.encode('utf-8')
        )
        
        if result_ptr is None:
            return []
        
        result_str = ctypes.string_at(result_ptr).decode('utf-8')
        
        
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return []
    
    def get_term_stats(self, term: str) -> Dict[str, int]:
        """
        Get statistics for a specific term.
        
        Args:
            term: The term to get statistics for
            
        Returns:
            Dictionary containing 'docCount' and 'totalFreq'
        """
        if _lib is None:
            return {"docCount": 0, "totalFreq": 0}
        
        result_ptr = _lib.GetTermStats(self._handle, term.encode('utf-8'))
        
        if result_ptr is None:
            return {"docCount": 0, "totalFreq": 0}
        
        result_str = ctypes.string_at(result_ptr).decode('utf-8')
        
        
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {"docCount": 0, "totalFreq": 0}

class SmartTokenizer:
    """Smart tokenizer with language-specific rules."""
    
    def __init__(self, language: str = "en"):
        """
        Initialize a smart tokenizer.
        
        Args:
            language: Language code for tokenization rules
        """
        if _lib is None:
            raise RuntimeError("BM25 library not available")
        
        self._handle = _lib.CreateSmartTokenizer(language.encode('utf-8'))
        self._language = language
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into a list of tokens.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        if _lib is None:
            return []
        
        result_ptr = _lib.TokenizeText(self._handle, text.encode('utf-8'))
        
        if result_ptr is None:
            return []
        
        result_str = ctypes.string_at(result_ptr).decode('utf-8')
        
        
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return []

class DefaultTokenizer:
    """Simple default tokenizer."""
    
    def __init__(self):
        """Initialize a default tokenizer."""
        pass
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text using simple whitespace splitting.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        return text.split()

# Convenience functions
def hello_bm25() -> str:
    """Get a hello message from the BM25 library."""
    if _lib is None:
        return "BM25 library not available"
    
    result_ptr = _lib.HelloBM25()
    if result_ptr is None:
        return "Error getting hello message"
    
    result = ctypes.string_at(result_ptr).decode('utf-8')
    
    return result

def new_bm25_index(doc_capacity: int = 1000, term_capacity: int = 10000) -> BM25Index:
    """Create a new BM25 index."""
    return BM25Index(doc_capacity, term_capacity)

def new_english_smart_tokenizer() -> SmartTokenizer:
    """Create a new English smart tokenizer."""
    if _lib is None:
        raise RuntimeError("BM25 library not available")
    
    handle = _lib.CreateEnglishSmartTokenizer()
    tokenizer = SmartTokenizer.__new__(SmartTokenizer)
    tokenizer._handle = handle
    tokenizer._language = "en"
    return tokenizer

def new_smart_tokenizer(language: str) -> SmartTokenizer:
    """Create a new smart tokenizer for the specified language."""
    return SmartTokenizer(language)

def new_default_tokenizer() -> DefaultTokenizer:
    """Create a new default tokenizer."""
    return DefaultTokenizer()

def batch_search(index: BM25Index, queries: List[str], tokenizer, limit: int = 10) -> List[BatchSearchResult]:
    """Perform batch search on multiple queries."""
    return index.batch_search(queries, tokenizer, limit)
