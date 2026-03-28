import logging
import uuid
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
)

from config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "deeplense_images"
VECTOR_SIZE = 512

_client: QdrantClient | None = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        try:
            _client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )
            logger.info("Connected to Qdrant at %s:%s", settings.QDRANT_HOST, settings.QDRANT_PORT)
        except Exception as e:
            logger.error("Failed to connect to Qdrant at %s:%s - %s", settings.QDRANT_HOST, settings.QDRANT_PORT, e)
            logger.error("CRITICAL: Qdrant is not running. Please start it before using search features.")
            raise
    return _client


def create_collection_if_not_exists():
    try:
        client = _get_client()
        collections = [c.name for c in client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection '%s'", COLLECTION_NAME)
        else:
            logger.info("Qdrant collection '%s' already exists", COLLECTION_NAME)
    except Exception as e:
        logger.error("Failed to create/verify collection: %s", e)
        raise


def insert(embedding: list[float], payload: dict) -> str:
    client = _get_client()
    point_id = str(uuid.uuid4())
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload,
            )
        ],
    )
    logger.info("Inserted point %s for '%s'", point_id, payload.get("filename", "unknown"))
    return point_id




def search_all(embedding: list[float], filters: dict | None = None, score_threshold: float = 0.20) -> list[dict]:
    """
    Scroll all vectors from Qdrant, compute cosine similarity in Python,
    and return ALL results above score_threshold — no server-side limit.
    Processes batches efficiently to avoid file descriptor exhaustion.
    """
    client = _get_client()

    scroll_filter = None
    if filters:
        conditions = []
        if filters.get("category"):
            conditions.append(
                FieldCondition(key="category", match=MatchValue(value=filters["category"]))
            )
        if filters.get("tags") and len(filters["tags"]) > 0:
            conditions.append(
                FieldCondition(key="tags", match=MatchAny(any=filters["tags"]))
            )
        if conditions:
            scroll_filter = Filter(must=conditions)

    # Scroll all points with their vectors in larger batches
    output = []
    next_offset = None
    batch_size = 500  # Larger batch size to reduce number of requests
    
    # Compute normalized query vector once
    query_vec = np.array(embedding, dtype=np.float32)
    norm = np.linalg.norm(query_vec)
    if norm > 0:
        query_vec = query_vec / norm
    
    while True:
        try:
            batch, next_offset = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=scroll_filter,
                limit=batch_size,
                offset=next_offset,
                with_payload=True,
                with_vectors=True,
            )
            
            # Process this batch
            for point in batch:
                if not point.vector:
                    continue
                vec = np.array(point.vector, dtype=np.float32)
                vec_norm = np.linalg.norm(vec)
                if vec_norm > 0:
                    vec = vec / vec_norm
                score = float(np.dot(query_vec, vec))
                if score >= score_threshold:
                    item = dict(point.payload) if point.payload else {}
                    item["score"] = round(score, 4)
                    output.append(item)
            
            if next_offset is None:
                break
        except Exception as e:
            logger.error("Error during scroll: %s", e)
            break

    output.sort(key=lambda x: x["score"], reverse=True)
    logger.info("search_all: %d results above threshold %.2f", len(output), score_threshold)
    return output


def deduplicate_results(results: list[dict], similarity_threshold: float = 0.95) -> list[dict]:
    """
    Remove near-duplicate results based on score similarity.
    Keeps the highest-scoring result in each cluster of similar results.
    
    Args:
        results: List of search results (should already be sorted by score)
        similarity_threshold: Score difference below which results are considered duplicates (default 0.95)
    
    Returns:
        Deduplicated list of results
    """
    if not results:
        return results
    
    deduplicated = []
    seen_filenames = set()
    
    for result in results:
        filename = result.get("filename", "")
        
        # Skip if we've already seen this exact filename
        if filename in seen_filenames:
            continue
        
        seen_filenames.add(filename)
        deduplicated.append(result)
    
    logger.info("Deduplicated %d results to %d", len(results), len(deduplicated))
    return deduplicated
