from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class TextSearchRequest(BaseModel):
    query: str
    category: str | None = None
    tags: list[str] | None = None
    sort_by: Literal["relevance", "date"] = "relevance"
    limit: int = Field(default=50, ge=1, le=10000)
    score_threshold: float = Field(default=0.20, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    filename: str
    path: str
    score: float
    category: str | None = None
    tags: list[str] = []
    uploaded_at: str = ""


class SearchResponse(BaseModel):
    total: int
    results: list[SearchResult]


class FilterOptions(BaseModel):
    categories: list[str]
    tags: list[str]
