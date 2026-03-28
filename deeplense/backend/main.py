import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import search, images, filters, admin
from services import postgres_service, qdrant_service, clip_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("Starting Deeplense API...")
    postgres_service.init_db()
    qdrant_service.create_collection_if_not_exists()
    clip_service.preload_model()
    logging.info("Deeplense API ready.")
    yield
    # Shutdown
    logging.info("Shutting down Deeplense API...")


app = FastAPI(title="Deeplense API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(search.router)
app.include_router(images.router)
app.include_router(filters.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Deeplense API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
