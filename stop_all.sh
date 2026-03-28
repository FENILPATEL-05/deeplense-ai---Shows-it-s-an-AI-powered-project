#!/bin/bash

###############################################################################
# 🛑 Deeplense - Complete Shutdown Script
#
# Stops all Deeplense services and processes
# - Frontend (Next.js on port 3000)
# - Backend (FastAPI on port 8000)
# - Qdrant (Vector DB on port 6333)
# - Pipeline services (watcher, indexing)
# - PostgreSQL (if local)
#
# Usage:
#   bash stop_all.sh              # Stop all services
#   bash stop_all.sh --force      # Force kill all (less graceful)
###############################################################################

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
FORCE_KILL="${1:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counter for stopped services
STOPPED=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🛑 DEEPLENSE SHUTDOWN SCRIPT                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

###############################################################################
# Helper Functions
###############################################################################

stop_process() {
    local name=$1
    local port=$2
    local pid_pattern=$3
    
    # Try to find by port first (more reliable)
    if [ -n "$port" ]; then
        local pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo -n "  Stopping $name (port $port)..."
            if [ "$FORCE_KILL" == "--force" ]; then
                kill -9 $pids 2>/dev/null || true
            else
                kill -TERM $pids 2>/dev/null || true
                # Wait for graceful shutdown
                sleep 2
                # Force kill if still running
                kill -9 $pids 2>/dev/null || true
            fi
            sleep 1
            echo -e " ${GREEN}✓${NC}"
            ((STOPPED++))
            return 0
        fi
    fi
    
    # Try to find by process pattern
    if [ -n "$pid_pattern" ]; then
        local pids=$(pgrep -f "$pid_pattern" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo -n "  Stopping $name..."
            if [ "$FORCE_KILL" == "--force" ]; then
                pkill -9 -f "$pid_pattern" 2>/dev/null || true
            else
                pkill -TERM -f "$pid_pattern" 2>/dev/null || true
                sleep 2
                pkill -9 -f "$pid_pattern" 2>/dev/null || true
            fi
            sleep 1
            echo -e " ${GREEN}✓${NC}"
            ((STOPPED++))
            return 0
        fi
    fi
    
    echo -e "  $name - ${YELLOW}not running${NC}"
    return 1
}

###############################################################################
# Main Shutdown Sequence
###############################################################################

echo -e "${YELLOW}Stopping Deeplense Services...${NC}\n"

# 1. Stop Frontend (Next.js)
echo -e "${BLUE}1. Frontend Services${NC}"
stop_process "Frontend (Next.js)" "3000" "next" || true

# 2. Stop Backend (FastAPI/Uvicorn)
echo
echo -e "${BLUE}2. Backend Services${NC}"
stop_process "Backend (FastAPI)" "8000" "uvicorn.*main" || true

# 3. Stop Pipeline Services
echo
echo -e "${BLUE}3. Pipeline Services${NC}"
stop_process "Watcher (Auto-indexing)" "" "watcher.py" || true
stop_process "Bulk Index (Batch processing)" "" "bulk_index.py" || true
stop_process "Retry Handler (Error recovery)" "" "retry_handler.py" || true

# 4. Stop Qdrant
echo
echo -e "${BLUE}4. Vector Database${NC}"
stop_process "Qdrant (Vector DB)" "6333" "./qdrant" || true
stop_process "Qdrant (alt pattern)" "6333" "qdrant" || true

# 5. Stop PostgreSQL (if running locally)
echo
echo -e "${BLUE}5. Relational Database${NC}"
if command -v psql &> /dev/null; then
    # Check if postgres is running as user process (common dev setup)
    stop_process "PostgreSQL" "5432" "postgres" || true
fi

# 6. Cleanup Node processes (stranded npm/node)
echo
echo -e "${BLUE}6. Cleanup Orphaned Processes${NC}"
if pgrep -f "node.*3000" &>/dev/null; then
    echo -n "  Cleaning up orphaned Node.js..."
    pkill -9 -f "node.*3000" 2>/dev/null || true
    echo -e " ${GREEN}✓${NC}"
    ((STOPPED++))
fi

# 7. Kill any remaining by common patterns
if pgrep npm &>/dev/null; then
    pids=$(pgrep npm || true)
    if [ -n "$pids" ]; then
        echo -n "  Cleaning up npm processes..."
        pkill -9 npm 2>/dev/null || true
        echo -e " ${GREEN}✓${NC}"
        ((STOPPED++))
    fi
fi

###############################################################################
# Summary
###############################################################################

echo
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    SHUTDOWN COMPLETE                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

# Verify all ports are free
echo -e "${YELLOW}Verifying ports are free...${NC}\n"

check_port() {
    local port=$1
    local name=$2
    if lsof -i :$port &>/dev/null; then
        echo -e "  ${RED}✗${NC} Port $port ($name) - ${RED}STILL IN USE${NC}"
        return 1
    else
        echo -e "  ${GREEN}✓${NC} Port $port ($name) - free"
        return 0
    fi
}

check_port "3000" "Frontend"
check_port "8000" "Backend"
check_port "6333" "Qdrant"

echo
echo -e "${GREEN}Services stopped: $STOPPED${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "  • All services have been stopped"
echo "  • Ports 3000, 8000, 6333 should now be free"
echo "  • Restart with: bash start_all.sh"
echo

# Optional: Show what's still running on common ports
echo -e "${YELLOW}Active processes on Deeplense ports:${NC}"
echo -n "  Port 3000: "
lsof -i :3000 2>/dev/null | wc -l | tr -d '\n'
echo
echo -n "  Port 8000: "
lsof -i :8000 2>/dev/null | wc -l | tr -d '\n'
echo
echo -n "  Port 6333: "
lsof -i :6333 2>/dev/null | wc -l | tr -d '\n'
echo

exit 0
