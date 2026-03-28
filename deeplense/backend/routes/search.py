import os
import tempfile
import logging
import time

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from models.schemas import TextSearchRequest, SearchResponse, SearchResult
from services import clip_service, qdrant_service
from services.advanced_search_service import hybrid_search, log_search_quality

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/text", response_model=SearchResponse)
async def search_by_text(request: TextSearchRequest):
    try:
        start_time = time.time()
        
        # Build filters dict
        filters = None
        if request.category or request.tags:
            filters = {}
            if request.category:
                filters["category"] = request.category
            if request.tags:
                filters["tags"] = request.tags

        # Use advanced hybrid search
        raw_results = hybrid_search(
            query=request.query,
            filters=filters,
            score_threshold=request.score_threshold,
            limit=200,
            use_query_enhancement=True,
            use_keyword_scoring=True,
            use_metadata_boost=True,
        )
        
        # Deduplicate results
        deduplicated_results = qdrant_service.deduplicate_results(raw_results)

        results = []
        for item in deduplicated_results:
            results.append(
                SearchResult(
                    filename=item.get("filename", ""),
                    path=item.get("path", ""),
                    score=round(item.get("combined_score", item.get("score", 0.0)), 4),
                    category=item.get("category"),
                    tags=item.get("tags", []),
                    uploaded_at=str(item.get("uploaded_at", "")),
                )
            )

        if request.sort_by == "date":
            results.sort(key=lambda r: r.uploaded_at, reverse=True)

        duration_ms = (time.time() - start_time) * 1000
        log_search_quality(request.query, raw_results, duration_ms)

        return SearchResponse(total=len(results), results=results)
    except Exception as e:
        logger.error("Text search failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/image", response_model=SearchResponse)
async def search_by_image(
    file: UploadFile = File(...), 
    score_threshold: float = 0.20,
    category: str | None = None,
    tags: list[str] | None = Query(default=None)
):
    tmp_path = None
    try:
        start_time = time.time()
        
        suffix = os.path.splitext(file.filename or "upload.jpg")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Get image embedding
        embedding = clip_service.embed_image(tmp_path)
        
        # Build filters dict
        filters = None
        if category or tags:
            filters = {}
            if category:
                filters["category"] = category
            if tags:
                filters["tags"] = tags
        
        # Use advanced hybrid search with original image query
        # (for image search, we use the embedding directly but enhance metadata understanding)
        raw_results = qdrant_service.search_all(
            embedding,
            filters=filters,
            score_threshold=score_threshold
        )
        
        # Re-rank for diversity and apply metadata boost
        from services.advanced_search_service import compute_metadata_boost, _rerank_for_diversity
        
        if raw_results:
            metadata_boost = compute_metadata_boost(
                "image search",
                raw_results,
                category_filter=category,
                tags_filter=tags
            )
            
            for r in raw_results:
                filename = r.get("filename", "")
                r["metadata_boost"] = metadata_boost.get(filename, 0)
                r["combined_score"] = r.get("score", 0) + (r.get("metadata_boost", 0) * 0.1)
            
            raw_results.sort(key=lambda x: x["combined_score"], reverse=True)
            raw_results = _rerank_for_diversity(raw_results, limit=200)
        
        # Deduplicate results
        deduplicated_results = qdrant_service.deduplicate_results(raw_results)

        results = []
        for item in deduplicated_results:
            results.append(
                SearchResult(
                    filename=item.get("filename", ""),
                    path=item.get("path", ""),
                    score=round(item.get("combined_score", item.get("score", 0.0)), 4),
                    category=item.get("category"),
                    tags=item.get("tags", []),
                    uploaded_at=str(item.get("uploaded_at", "")),
                )
            )

        duration_ms = (time.time() - start_time) * 1000
        query_desc = f"image_search ({file.filename})"
        log_search_quality(query_desc, raw_results, duration_ms)

        return SearchResponse(total=len(results), results=results)
    except Exception as e:
        logger.error("Image search failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Image search failed: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning("Failed to cleanup temp file: %s", e)
