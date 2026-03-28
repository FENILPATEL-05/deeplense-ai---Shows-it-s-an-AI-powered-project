"""
Advanced Search Service for Deeplense
Implements professional search engine features:
1. Hybrid search (semantic + keyword/BM25)
2. Smart query enhancement
3. Metadata-boosted scoring
4. Result re-ranking for diversity
"""

import logging
import math
from typing import Optional
import numpy as np
from collections import defaultdict

from services import clip_service, qdrant_service, postgres_service

logger = logging.getLogger(__name__)

# ============================================================================
# Query Enhancement
# ============================================================================

QUERY_SYNONYMS = {
    "dog": ["puppy", "canine", "doggo", "pup"],
    "cat": ["kitten", "feline", "kitty"],
    "car": ["automobile", "vehicle", "truck"],
    "bird": ["avian", "fowl"],
    "tree": ["plant", "forest", "foliage"],
    "house": ["building", "home", "residence"],
    "person": ["human", "people", "face"],
    "landscape": ["scenery", "nature", "vista"],
    "sunset": ["sunrise", "dawn", "dusk"],
    "food": ["eating", "cuisine", "meal"],
}

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "being"
}


def enhance_query(query: str) -> str:
    """
    Enhance search query for better results:
    - Add synonyms
    - Remove stop words intelligently
    - Improve structure
    """
    words = query.lower().split()
    enhanced_words = []
    
    for word in words:
        enhanced_words.append(word)
        # Add synonyms for key words (not stop words)
        if word not in STOP_WORDS and word in QUERY_SYNONYMS:
            enhanced_words.extend(QUERY_SYNONYMS[word][:2])  # Add top 2 synonyms
    
    enhanced_query = " ".join(enhanced_words)
    logger.debug("Query enhancement: '%s' -> '%s'", query, enhanced_query)
    return enhanced_query


# ============================================================================
# BM25 Keyword Search (Ranking)
# ============================================================================

class BM25:
    """BM25 ranking algorithm for keyword search"""
    
    def __init__(self, corpus: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.avg_doc_length = sum(len(doc.split()) for doc in corpus) / max(len(corpus), 1)
        self.idf = self._compute_idf(corpus)
    
    def _compute_idf(self, corpus: list[str]) -> dict:
        """Compute IDF for all terms"""
        idf = {}
        for doc in corpus:
            for word in set(doc.lower().split()):
                idf[word] = idf.get(word, 0) + 1
        
        n = len(corpus)
        for word in idf:
            idf[word] = math.log((n - idf[word] + 0.5) / (idf[word] + 0.5) + 1)
        return idf
    
    def score(self, query: str, doc_idx: int) -> float:
        """Compute BM25 score for document"""
        doc = self.corpus[doc_idx]
        doc_length = len(doc.split())
        query_words = query.lower().split()
        
        score = 0.0
        for word in query_words:
            if word not in self.idf:
                continue
            
            word_count = doc.lower().split().count(word)
            idf = self.idf[word]
            normalized_tf = (self.k1 + 1) * word_count
            length_norm = self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)
            score += idf * normalized_tf / (word_count + length_norm)
        
        return score


def compute_keyword_scores(
    query: str,
    results: list[dict]
) -> dict[str, float]:
    """
    Compute BM25 scores for keyword matching
    Returns: {filename: bm25_score, ...}
    """
    # Extract text from results (filename + category + tags)
    corpus = []
    filename_map = {}
    
    for r in results:
        filename = r.get("filename", "")
        category = r.get("category", "")
        tags = " ".join(r.get("tags", []))
        doc_text = f"{filename} {category} {tags}"
        
        corpus.append(doc_text)
        filename_map[len(corpus) - 1] = filename
    
    if not corpus:
        return {}
    
    bm25 = BM25(corpus)
    keyword_scores = {}
    
    for idx, filename in filename_map.items():
        keyword_scores[filename] = bm25.score(query, idx)
    
    # Normalize to 0-1
    if keyword_scores:
        max_score = max(keyword_scores.values())
        if max_score > 0:
            keyword_scores = {k: v / max_score for k, v in keyword_scores.items()}
    
    logger.debug("Computed keyword scores for %d results", len(keyword_scores))
    return keyword_scores


# ============================================================================
# Metadata Boosting
# ============================================================================

def compute_metadata_boost(
    query: str,
    results: list[dict],
    category_filter: Optional[str] = None,
    tags_filter: Optional[list[str]] = None
) -> dict[str, float]:
    """
    Compute metadata boost scores:
    - +0.2 if category matches filter
    - +0.1 for each matching tag
    """
    boost_scores = {}
    query_lower = query.lower()
    
    for r in results:
        filename = r.get("filename", "")
        boost = 0.0
        
        # Category match bonus
        if category_filter:
            if r.get("category", "").lower() == category_filter.lower():
                boost += 0.2
        
        # Tag match bonus
        if tags_filter:
            result_tags = r.get("tags", [])
            matching_tags = sum(1 for tag in tags_filter if tag in result_tags)
            boost += matching_tags * 0.1
        
        # Query term in metadata bonus
        category = r.get("category", "").lower()
        tags_str = " ".join(r.get("tags", [])).lower()
        
        if category in query_lower:
            boost += 0.15
        if tags_str and any(word in tags_str for word in query_lower.split()):
            boost += 0.1
        
        boost_scores[filename] = boost
    
    logger.debug("Computed metadata boost for %d results", len(boost_scores))
    return boost_scores


# ============================================================================
# Hybrid Search Orchestration
# ============================================================================

def hybrid_search(
    query: str,
    filters: Optional[dict] = None,
    score_threshold: float = 0.20,
    limit: int = 200,
    use_query_enhancement: bool = True,
    use_keyword_scoring: bool = True,
    use_metadata_boost: bool = True,
) -> list[dict]:
    """
    Hybrid search combining:
    1. Semantic search (vector-based)
    2. Keyword search (BM25)
    3. Metadata boosting
    4. Smart result re-ranking
    """
    
    # Step 1: Enhance query
    enhanced_query = enhance_query(query) if use_query_enhancement else query
    logger.info("Performing hybrid search: '%s' (enhanced: '%s')", query, enhanced_query)
    
    # Step 2: Get semantic embeddings (use enhanced query for better understanding)
    try:
        semantic_embedding = clip_service.embed_text(enhanced_query)
    except Exception as e:
        logger.error("Failed to create semantic embedding: %s", e)
        raise
    
    # Step 3: Get semantic results from Qdrant
    try:
        semantic_results = qdrant_service.search_all(
            semantic_embedding,
            filters=filters,
            score_threshold=score_threshold
        )
    except Exception as e:
        logger.error("Semantic search failed: %s", e)
        raise
    
    if not semantic_results:
        logger.warning("No semantic results found")
        return []
    
    # Step 4: Compute keyword scores
    keyword_scores = {}
    if use_keyword_scoring:
        try:
            keyword_scores = compute_keyword_scores(enhanced_query, semantic_results)
        except Exception as e:
            logger.warning("Keyword scoring failed (continuing): %s", e)
    
    # Step 5: Compute metadata boost
    metadata_boost = {}
    if use_metadata_boost:
        try:
            category_filter = filters.get("category") if filters else None
            tags_filter = filters.get("tags") if filters else None
            metadata_boost = compute_metadata_boost(query, semantic_results, category_filter, tags_filter)
        except Exception as e:
            logger.warning("Metadata boost failed (continuing): %s", e)
    
    # Step 6: Combine scores
    combined_results = []
    for r in semantic_results:
        filename = r.get("filename", "")
        semantic_score = r.get("score", 0.0)  # Already 0-1 normalized
        keyword_score = keyword_scores.get(filename, 0.0)
        boost = metadata_boost.get(filename, 0.0)
        
        # Weighted combination (tuned for best quality)
        combined_score = (
            semantic_score * 0.60 +  # Semantic is primary
            keyword_score * 0.25 +   # Keywords support semantic
            boost * 0.15             # Metadata provides context
        )
        
        r["combined_score"] = combined_score
        r["semantic_score"] = semantic_score
        r["keyword_score"] = keyword_score
        r["metadata_boost"] = boost
        
        combined_results.append(r)
    
    # Step 7: Re-rank by combined score
    combined_results.sort(key=lambda x: x["combined_score"], reverse=True)
    
    # Step 8: Re-ranking for diversity (optional: avoid too many similar results)
    diverse_results = _rerank_for_diversity(combined_results, limit=limit)
    
    logger.info(
        "Hybrid search completed: %d semantic results -> %d final results",
        len(semantic_results),
        len(diverse_results)
    )
    
    return diverse_results


def _rerank_for_diversity(
    results: list[dict],
    limit: int = 200,
    diversity_threshold: float = 0.85
) -> list[dict]:
    """
    Rerank results to improve diversity:
    - Avoid returning very similar images (high vector similarity)
    - Keep diversity while maintaining relevance
    """
    if len(results) <= limit:
        return results
    
    selected = []
    vectors_selected = []
    
    for r in results:
        # Always include top results
        if len(selected) < max(5, limit // 4):
            selected.append(r)
            vectors_selected.append(np.array(r.get("vector", [])))
            continue
        
        # For rest, check similarity with already selected
        if len(vectors_selected) == 0:
            selected.append(r)
            vectors_selected.append(np.array(r.get("vector", [])))
            continue
        
        # Check if different enough from selected results
        result_vector = np.array(r.get("vector", []))
        if len(result_vector) == 0:
            # No vector, include to maintain diversity
            selected.append(r)
            continue
        
        # Compute max similarity with selected
        similarities = [
            np.dot(result_vector, v) / (np.linalg.norm(result_vector) * np.linalg.norm(v) + 1e-8)
            for v in vectors_selected
        ]
        max_similarity = max(similarities) if similarities else 0
        
        # Include if diverse enough
        if max_similarity < diversity_threshold:
            selected.append(r)
            vectors_selected.append(result_vector)
            if len(selected) >= limit:
                break
    
    logger.debug("Diversity reranking: %d results -> %d", len(results), len(selected))
    return selected


# ============================================================================
# Search Statistics & Monitoring
# ============================================================================

def log_search_quality(
    query: str,
    results: list[dict],
    duration_ms: float
):
    """Log search quality metrics for monitoring"""
    if not results:
        logger.info("Search quality: query='%s' duration=%.1fms results=0", query, duration_ms)
        return
    
    avg_semantic = np.mean([r.get("semantic_score", 0) for r in results[:10]])
    avg_keyword = np.mean([r.get("keyword_score", 0) for r in results[:10]])
    avg_boost = np.mean([r.get("metadata_boost", 0) for r in results[:10]])
    
    top_score = results[0].get("combined_score", 0)
    
    logger.info(
        "Search quality: query='%s' results=%d top_score=%.3f semantic=%.3f keyword=%.3f boost=%.3f duration=%.1fms",
        query, len(results), top_score, avg_semantic, avg_keyword, avg_boost, duration_ms
    )
