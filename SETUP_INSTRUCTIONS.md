# Deeplense Development Setup

This guide will help you set up Deeplense from scratch for development.

## System Requirements

### Minimum Requirements
- **CPU**: Dual-core processor
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 10GB free space (for models and databases)
- **GPU**: Optional but recommended (NVIDIA with CUDA for faster embeddings)

### Software Requirements
- **OS**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.8 or higher
- **Node.js**: 18.0 or higher
- **PostgreSQL**: 12 or higher
- **Git**: Latest version

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/FENILPATEL-05/deeplense-ai---Shows-it-s-an-AI-powered-project.git
cd deeplense
```

### 2. Set Up PostgreSQL

#### On Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### On macOS
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Create Database and User
```bash
sudo -u postgres psql
```

In the PostgreSQL prompt:
```sql
CREATE USER deeplense_user WITH PASSWORD 'secure_password';
CREATE DATABASE deeplense OWNER deeplense_user;
ALTER DATABASE deeplense OWNER TO deeplense_user;
\q
```

### 3. Set Up Python Backend

```bash
cd deeplense/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download CLIP model (this may take a few minutes)
python3 -c "from transformers import CLIPModel, CLIPProcessor; CLIPModel.from_pretrained('openai/clip-vit-base-patch32'); CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')"
```

### 4. Set Up Frontend

```bash
cd deeplense/frontend

# Install dependencies
npm install

# Build Tailwind CSS
npm run build
```

### 5. Configure Environment Variables

Create `.env` files in appropriate directories:

#### Backend `.env` (deeplense/backend/.env)
```env
# Database
DATABASE_URL=postgresql://deeplense_user:secure_password@localhost:5432/deeplense
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=deeplense_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=deeplense

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_PATH=../../storage

# CLIP Configuration
CLIP_MODEL=openai/clip-vit-base-patch32
DEVICE=cuda  # or cpu

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

#### Frontend `.env.local` (deeplense/frontend/.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 6. Initialize the System

```bash
cd /path/to/deeplense

# Verify connections and create tables
python3 init_deeplense.py
```

### 7. Download Qdrant Vector Database

```bash
# Download Qdrant (Linux/macOS)
curl -L https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-x86_64-unknown-linux-musl -o qdrant
chmod +x qdrant

# Or on macOS:
curl -L https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-x86_64-apple-darwin -o qdrant
chmod +x qdrant
```

## Running the Application

### Terminal 1: Start Qdrant Vector Database
```bash
cd /path/to/deeplense
QDRANT_STORAGE_PATH=./storage ./qdrant
```
Wait for: `"version":"1.7.0"` in output

### Terminal 2: Initialize Services
```bash
cd /path/to/deeplense

# Activate Python environment
source deeplense/backend/venv/bin/activate

# Run initialization
python3 init_deeplense.py
```

### Terminal 3: Start Backend Server
```bash
cd /path/to/deeplense/deeplense/backend

# Activate environment
source venv/bin/activate

# Start server
python main.py
```

Expected output: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 4: Start Frontend Server
```bash
cd /path/to/deeplense/deeplense/frontend

# Start development server
npm run dev
```

Expected output: `localhost:3000`

### Terminal 5 (Optional): Start Image Processing Watcher
```bash
cd /path/to/deeplense/deeplense/pipeline

# Activate environment
source ../backend/venv/bin/activate

# Start watcher
python watcher.py
```

## Verify Everything Works

1. **Open Browser**: Navigate to http://localhost:3000
2. **Search Interface**: Should see search bar and filters
3. **Test Search**: Try searching (will have no results until images are indexed)
4. **Index Images**: 
   ```bash
   # Copy images to inbox
   cp /path/to/images/*.jpg deeplense/images/inbox/
   
   # Bulk index
   cd deeplense/pipeline
   source ../backend/venv/bin/activate
   python bulk_index.py
   ```

## Troubleshooting Installation

### Issue: PostgreSQL Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql
```

### Issue: Port Already in Use
```bash
# Find what's using the port
lsof -i :8000  # For backend
lsof -i :3000  # For frontend
lsof -i :6333  # For Qdrant

# Kill the process
kill -9 <PID>
```

### Issue: CLIP Model Download Fails
```bash
# Pre-download models manually
python3 << 'EOF'
from transformers import CLIPModel, CLIPProcessor, AutoTokenizer
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch32")

print("Models downloaded successfully!")
EOF
```

### Issue: npm Dependency Conflicts
```bash
# Clear cache and reinstall
cd deeplense/frontend
rm -rf node_modules
rm package-lock.json
npm cache clean --force
npm install
```

### Issue: Python Dependencies Error
```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Reinstall requirements
pip install -r deeplense/backend/requirements.txt
```

## Development Tips

### Enable Debug Mode (Backend)
Edit `deeplense/backend/config.py`:
```python
DEBUG = True
```

### Enable Hot Reload (Frontend)
Already enabled with `npm run dev`

### View Logs
```bash
# Backend logs
# Displayed in Terminal 3

# Frontend logs
# Displayed in Terminal 4

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Qdrant logs
# Displayed in Terminal 1
```

### Access Databases

#### PostgreSQL
```bash
psql -U deeplense_user -d deeplense -h localhost
```

#### Qdrant API
```bash
curl http://localhost:6333/health
```

## Next Steps

1. **Add Sample Images**: Copy images to `deeplense/images/inbox/`
2. **Index Images**: Run `bulk_index.py` in pipeline
3. **Test Search**: Use the frontend or API endpoints
4. **Explore Features**: Try different search queries and filters

---

For more information, see [README.md](README.md) or visit
[GitHub Repository](https://github.com/FENILPATEL-05/deeplense-ai---Shows-it-s-an-AI-powered-project)
