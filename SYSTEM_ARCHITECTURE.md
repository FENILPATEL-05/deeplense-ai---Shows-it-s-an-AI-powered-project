# 🏗️ Deeplense System Architecture

## Overview

Deeplense is a production-ready AI image search engine combining semantic search (CLIP embeddings), keyword search (BM25), and intelligent filtering with category/tag metadata.

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                          │
│  - Search interface with filters                                 │
│  - Image results grid & lightbox                                 │
│  - Category & tag filtering                                      │
└─────────────┬───────────────────────────────────────────────────┘
              │ HTTP/JSON
┌─────────────▼───────────────────────────────────────────────────┐
│                   FastAPI Backend (8000)                         │
├─────────────────────────────────────────────────────────────────┤
│  Routes:                                                          │
│  ├── /search/text     - Semantic + keyword search               │
│  ├── /search/image    - Image search with hybrid ranking        │
│  ├── /filters         - Get available categories/tags           │
│  ├── /images/{name}   - Serve image files                       │
│  └── /admin/*         - Retry failed images                     │
├─────────────────────────────────────────────────────────────────┤
│  Services:                                                        │
│  ├── clip_service          - CLIP embeddings (text & image)    │
│  ├── qdrant_service        - Vector DB operations              │
│  ├── postgres_service      - Metadata DB operations            │
│  └── advanced_search_service - Hybrid search orchestration     │
└─────────────┬───┬──────────────┬────────────────────────────────┘
              │   │              │
         ┌────▼───▼──────────────▼────┐
         │   Qdrant (6333)            │
         │   Vector Storage           │
         │   - 5000+ embeddings       │
         │   - 512D vectors           │
         │   - Cosine distance        │
         │   - Payloads (category/    │
         │     tags/filename/path)    │
         └────────────────────────────┘
         
         ┌────────────────────────────┐
         │ PostgreSQL (5432)          │
         │ Metadata Store             │
         │ - Images table             │
         │ - Category/tags            │
         │ - Filenames                │
         │ - Upload timestamps        │
         └────────────────────────────┘
         
         ┌────────────────────────────┐
         │ Image Files                │
         │ /images/processed/         │
         │ /images/failed/            │
         │ /images/inbox/             │
         └────────────────────────────┘

         ┌────────────────────────────┐
         │ Pipeline Services          │
         │ ├── watcher.py             │
         │ ├── processor.py           │
         │ ├── bulk_index.py          │
         │ └── retry_handler.py       │
         └────────────────────────────┘
```

## Core Components

### 1. Frontend (Next.js + React)

**Key Files:**
- `app/search/page.tsx` - Main search interface
- `components/FilterButton.tsx` - Category/tag/quality filters
- `hooks/useSearch.ts` - Search state management
- `lib/api.ts` - API client

**Features:**
- Real-time search as you type
- Image upload & reverse search
- Category filtering (8 categories)
- Tag filtering (16 tags)
- Match quality slider (0.20 - 0.60)
- Sort by relevance or date
- Lightbox image viewer

### 2. Backend (FastAPI)

**API Endpoints:**
```
POST /search/text           - Text search with hybrid ranking
POST /search/image          - Image search with metadata boosting
GET  /filters               - Available categories & tags
GET  /images/               - List all indexed images
GET  /images/{filename}     - Serve image file
POST /admin/retry-failed    - Retry failed images
```

**Core Services:**

#### clip_service.py
- `embed_text(query)` - Get text embedding (512D)
- `embed_image(path)` - Get image embedding (512D)
- `classify_image(path)` - Zero-shot classification into 8 categories
- `extract_tags(path)` - Extract semantic tags (18 tags available)

#### qdrant_service.py
- `insert()` - Store embedding + metadata
- `search_all()` - Full-text scroll with cosine similarity
- `deduplicate_results()` - Remove duplicate filenames

#### postgres_service.py
- `init_db()` - Create tables & schema
- `insert_image()` - Store metadata
- `get_filters()` - Get categories/tags for UI
- `get_all_images()` - List images with pagination

#### advanced_search_service.py (New - Hybrid Search)
- `hybrid_search()` - Main search orchestration
- `enhance_query()` - Add synonyms to query
- `compute_keyword_scores()` - BM25 ranking
- `compute_metadata_boost()` - Category/tag scoring
- `log_search_quality()` - Search metrics

### 3. Image Processing Pipeline

**watcher.py** (Auto-indexing)
- Monitors `images/inbox/` folder
- Detects new images automatically
- Processes with CLIP classification
- Moves to `processed/` on success, `failed/` on error
- Retry failed images every 2 hours

**processor.py** (Single image)
- Runs CLIP embedding
- Runs CLIP zero-shot classification
- Runs semantic tag extraction
- Stores in both Qdrant + PostgreSQL

**bulk_index.py** (Batch indexing)
- Indexes all images in `inbox/` folder
- Progress reporting
- Error handling & categorization

**retry_handler.py** (Fault recovery)
- Retries images in `failed/` folder
- Multi-attempt retry with delays
- Fallback error handling

### 4. Databases

#### Qdrant (Vector Store)
- Collection: `deeplense_images`
- Vectors: 512-dimensional (CLIP)
- Distance: Cosine similarity
- Payload fields:
  - `filename`: Image filename
  - `path`: Local file path
  - `category`: One of 8 categories
  - `tags`: Array of semantic tags
  - `uploaded_at`: Timestamp

#### PostgreSQL (Metadata)
```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    path TEXT,
    category TEXT,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

## Search Architecture

### Traditional Vector Search (60% weight)
```
Query: "animals in nature"
    ↓
CLIP model
    ↓
512D embedding
    ↓
Qdrant cosine search
    ↓
Semantic Score (0.0-1.0)
```

### Keyword/BM25 Search (25% weight)
```
Query: "animals in nature"
    ↓
BM25 algorithm on metadata
- Scores exact term matches
- High IDF for rare words
- Normalizes by document length
    ↓
Keyword Score (0.0-1.0)
```

### Metadata Boosting (15% weight)
```
Filter: category="animals"
Filter: tags=["wildlife"]
    ↓
Boost scoring
- +0.2 if category matches
- +0.1 per matching tag
- +0.15 if query in category name
    ↓
Boost Score (0.0-1.0)
```

### Combined Score
```
Final Score = (Semantic × 0.6) + (Keyword × 0.25) + (Boost × 0.15)
```

### Result Diversity (Post-ranking)
- Avoids 95%+ similar vectors
- Keeps top 5 regardless of similarity
- Improves user experience with variety

## Data Flow

### Indexing Pipeline
```
1. Upload image → images/inbox/
2. Watcher detects new file
3. CLIP embedding generation (512D vector)
4. CLIP zero-shot classification (8 categories)
5. Semantic tag extraction (16 tags)
6. Store in Qdrant (vector + payload)
7. Store in PostgreSQL (metadata)
8. Move to images/processed/
```

### Search Pipeline
```
1. User enters query
2. Query enhancement (add synonyms)
3. CLIP text embedding
4. Semantic search in Qdrant
5. BM25 keyword scoring
6. Metadata boost calculation
7. Combined score ranking
8. Diversity reranking
9. Deduplication
10. Return top results
```

## Performance Characteristics

| Operation | Time | Throughput |
|-----------|------|------------|
| Text search | 100-500ms | ~5 queries/sec |
| Image search | 500-1500ms | ~2 queries/sec |
| Indexing (single) | 2-5s | ~200 images/hour |
| Bulk indexing | 2-5s per image | ~200 images/hour |
| CLIP embedding | 1-3s | GPU accelerated |

## Security & Limits

- CORS: Enabled for all origins (configure in production)
- File path: Directory traversal protection with `os.path.basename()`
- Query: Rate limiting (implement with aioredis if needed)
- Upload: Multipart file validation
- DB: Connection pooling with psycopg2

## Scalability Notes

**Current Setup (Single Machine):**
- 5000 images
- 512MB Qdrant index
- Suitable for small/medium deployments

**Scaling Considerations:**
- Qdrant: Supports distributed clusters
- PostgreSQL: Add replication/partitioning
- Backend: Horizontal scaling with load balancer
- CLIP: GPU sharing or inference optimization
- Images: Move to S3/cloud storage

## Configuration

Key settings in `config.py`:
```python
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
DATABASE_URL = "postgresql://user:password@localhost/deeplense"
CLIP_MODEL = "openai/clip-vit-base-patch32"
IMAGES_INBOX_DIR = "./deeplense/images/inbox"
```

## Monitoring & Debugging

**Logs:**
- Backend: `stdout` (FastAPI uvicorn)
- Pipeline: `logger.py` in pipeline/ directory
- Search: `log_search_quality()` metrics

**Health Checks:**
```bash
curl http://localhost:8000/health
```

**Debug Endpoints:**
- `/filters` - Check available categories/tags
- `/images/` - List all indexed images (paginated)
- `/admin/failed-images` - Check failed queue

## Testing the System

1. **Verify Setup:**
   ```bash
   python init_deeplense.py
   ```

2. **Index Test Images:**
   ```bash
   cp test_images/*.jpg deeplense/images/inbox/
   python deeplense/pipeline/bulk_index.py
   ```

3. **Test API:**
   ```bash
   curl -X POST http://localhost:8000/search/text \
     -H "Content-Type: application/json" \
     -d '{"query":"animal","limit":10}'
   ```

4. **Test UI:**
   - Open http://localhost:3000
   - Search, filter, and verify results

