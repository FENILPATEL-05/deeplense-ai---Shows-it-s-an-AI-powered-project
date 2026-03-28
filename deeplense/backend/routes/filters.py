import logging

from fastapi import APIRouter
from models.schemas import FilterOptions
from services import postgres_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["filters"])


@router.get("/filters", response_model=FilterOptions)
async def get_filters():
    data = postgres_service.get_filters()
    return FilterOptions(categories=data["categories"], tags=data["tags"])
