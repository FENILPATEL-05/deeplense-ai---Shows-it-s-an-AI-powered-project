#!/usr/bin/env python3
"""
Deeplense Database Initialization and Health Check Script
Ensures all services are properly initialized and ready to use.
"""

import sys
import os
import time
import subprocess

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "deeplense", "backend"))

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    except Exception:
        return False
    finally:
        sock.close()


def check_postgres() -> bool:
    """Check if PostgreSQL is running"""
    if check_port("localhost", 5432):
        logger.info("✓ PostgreSQL is running on port 5432")
        return True
    else:
        logger.error("✗ PostgreSQL is NOT running on port 5432")
        return False


def check_qdrant() -> bool:
    """Check if Qdrant is running"""
    if check_port("localhost", 6333):
        logger.info("✓ Qdrant is running on port 6333")
        return True
    else:
        logger.error("✗ Qdrant is NOT running on port 6333")
        logger.error("Start Qdrant with: cd /home/fenil/Deeplense && QDRANT_STORAGE_PATH=./storage ./qdrant")
        return False


def init_databases():
    """Initialize PostgreSQL and Qdrant databases"""
    try:
        logger.info("Initializing databases...")
        from services import postgres_service, qdrant_service
        
        # Initialize PostgreSQL
        logger.info("Creating PostgreSQL tables...")
        postgres_service.init_db()
        logger.info("✓ PostgreSQL initialized")
        
        # Initialize Qdrant
        logger.info("Creating Qdrant collection...")
        qdrant_service.create_collection_if_not_exists()
        logger.info("✓ Qdrant initialized")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        return False


def check_services():
    """Check all required services"""
    logger.info("=" * 60)
    logger.info("Deeplense Services Health Check")
    logger.info("=" * 60)
    
    services_ok = True
    
    # Check PostgreSQL
    if not check_postgres():
        services_ok = False
        logger.warning("Please start PostgreSQL before running Deeplense")
    
    # Check Qdrant
    if not check_qdrant():
        services_ok = False
        logger.warning("Please start Qdrant before running Deeplense")
        logger.warning("  Option 1: docker run -d -p 6333:6333 -v ./storage:/qdrant/storage qdrant/qdrant:latest")
        logger.warning("  Option 2: Download and run from https://qdrant.tech/")
    
    if not services_ok:
        logger.error("Some services are not running!")
        return False
    
    # Initialize databases if services are running
    logger.info("")
    if not init_databases():
        return False
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ All services are ready!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Backend:  cd deeplense/backend && source venv/bin/activate && python main.py")
    logger.info("2. Frontend: cd deeplense/frontend && npm run dev")
    logger.info("3. Access:   http://localhost:3000")
    logger.info("")
    
    return True


if __name__ == "__main__":
    success = check_services()
    sys.exit(0 if success else 1)
