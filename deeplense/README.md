# Deeplense — AI Image Search Platform

Deeplense is a production-ready, self-hosted image search platform powered by OpenAI CLIP embeddings. Search your image library using natural language or upload an image to find visually similar results. Built for small teams running on a local network.

## Architecture

- **Backend** — FastAPI serving search endpoints, CLIP embedding, and image files
- **Pipeline** — Python ingestion pipeline that watches a folder, generates CLIP embeddings, and indexes into Qdrant + PostgreSQL
- **Frontend** — Next.js 14 with TypeScript and Tailwind CSS, Google-inspired minimal UI with dark mode
- **Qdrant** — Vector database for similarity search (cosine distance, 512-dim CLIP vectors)
- **PostgreSQL** — Metadata storage for categories, tags, and filters

## Prerequisites

```bash
# System packages
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip nodejs npm postgresql postgresql-contrib

# Install Qdrant binary
wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz
tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz
```

## PostgreSQL Setup

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE deeplense;
CREATE USER deeplense_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE deeplense TO deeplense_user;
\q
```

Then connect and grant schema permissions:

```bash
sudo -u postgres psql -d deeplense
```

```sql
GRANT ALL ON SCHEMA public TO deeplense_user;
\q
```

## Running the Project (4 Terminals)

### Terminal 1 — Qdrant

```bash
./qdrant
```

Qdrant runs on `http://localhost:6333` by default.

### Terminal 2 — Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your PostgreSQL credentials and paths
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. Check health: `http://localhost:8000/health`

### Terminal 3 — Pipeline

```bash
cd pipeline
source ../backend/venv/bin/activate
pip install -r requirements.txt

# Index existing images (run once)
python bulk_index.py

# Watch for new images (keep running)
python watcher.py
```

### Terminal 4 — Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:3000`.

## Team Access on Local Network

```bash
# Find your IP
hostname -I
```

Team members open: `http://YOUR_IP:3000`

Update `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://YOUR_IP:8000
```

Update `backend/.env` if needed to ensure the processed images directory path is absolute.

## Adding New Images

```bash
# Copy images into the inbox folder
cp /path/to/new/images/* deeplense/images/inbox/
```

The pipeline watcher auto-detects new files and indexes them within seconds. Successfully processed images are moved to `images/processed/`. Failed images are moved to `images/failed/`.

## Bulk Indexing

To index images already in the `images/processed/` directory:

```bash
cd pipeline
python bulk_index.py
```

It skips already-indexed files automatically and prints progress as it goes.

## Project Structure

```
deeplense/
├── backend/              # FastAPI backend
│   ├── main.py           # App entrypoint, CORS, routers
│   ├── config.py         # Environment variable loading
│   ├── routes/           # API route handlers
│   │   ├── search.py     # POST /search/text, POST /search/image
│   │   ├── images.py     # GET /images/{filename}
│   │   └── filters.py    # GET /filters
│   ├── services/         # Business logic
│   │   ├── clip_service.py      # CLIP embedding (text + image)
│   │   ├── qdrant_service.py    # Vector DB operations
│   │   └── postgres_service.py  # Metadata DB operations
│   └── models/
│       └── schemas.py    # Pydantic request/response models
├── pipeline/             # Image ingestion pipeline
│   ├── watcher.py        # Filesystem watcher (watchdog)
│   ├── bulk_index.py     # Batch indexer for existing images
│   ├── processor.py      # Image processing logic
│   └── logger.py         # Logging configuration
├── frontend/             # Next.js 14 frontend
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── hooks/            # Custom hooks (useSearch)
│   ├── lib/              # API client
│   └── types/            # TypeScript types
└── images/               # Image storage
    ├── inbox/            # Drop new images here
    ├── processed/        # Successfully indexed images
    └── failed/           # Images that failed processing
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `QDRANT_HOST` | Qdrant server host | `localhost` |
| `QDRANT_PORT` | Qdrant server port | `6333` |
| `POSTGRES_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/deeplense` |
| `IMAGES_PROCESSED_DIR` | Path to processed images | `../images/processed` |
| `IMAGES_INBOX_DIR` | Path to inbox directory | `../images/inbox` |
| `IMAGES_FAILED_DIR` | Path to failed directory | `../images/failed` |

### Frontend (`frontend/.env.local`)

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

## Tech Stack

- **Backend**: Python 3.11, FastAPI, CLIP (ViT-B/32), Qdrant, PostgreSQL
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons
- **ML Model**: `openai/clip-vit-base-patch32` via HuggingFace Transformers
- **Vector DB**: Qdrant (512-dim cosine similarity)
- **Pipeline**: watchdog filesystem monitoring, PIL image processing
