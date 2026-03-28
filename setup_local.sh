#!/bin/bash

# Deeplense Local Setup Script (No Docker)

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         Deeplense Local Setup - No Docker                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check PostgreSQL
if nc -z localhost 5432 2>/dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running on port 5432"
else
    echo -e "${RED}✗${NC} PostgreSQL is NOT running"
    echo "Please start PostgreSQL first"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Step 1: Download Qdrant"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ ! -f "qdrant" ]; then
    echo "Downloading Qdrant..."
    curl -L https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-x86_64-unknown-linux-gnu -o qdrant
    chmod +x qdrant
    echo -e "${GREEN}✓${NC} Qdrant downloaded"
else
    echo -e "${GREEN}✓${NC} Qdrant binary already exists"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Step 2: Create Storage Directory"
echo "═══════════════════════════════════════════════════════════"
echo ""

mkdir -p storage
echo -e "${GREEN}✓${NC} Storage directory ready at ./storage"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "ALL READY! Next Steps:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Open 4 terminals and run:"
echo ""
echo -e "${YELLOW}Terminal 1 - Start Qdrant:${NC}"
echo "  cd /home/fenil/Deeplense"
echo "  ./qdrant --storage-path ./storage"
echo ""
echo -e "${YELLOW}Terminal 2 - Initialize (run once PostgreSQL & Qdrant are ready):${NC}"
echo "  cd /home/fenil/Deeplense"
echo "  python3 init_deeplense.py"
echo ""
echo -e "${YELLOW}Terminal 3 - Start Backend:${NC}"
echo "  cd /home/fenil/Deeplense/deeplense/backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo -e "${YELLOW}Terminal 4 - Start Frontend:${NC}"
echo "  cd /home/fenil/Deeplense/deeplense/frontend"
echo "  npm run dev"
echo ""
echo -e "${GREEN}Then access: http://localhost:3000${NC}"
echo ""
