#!/usr/bin/env python3
"""
Startup script for the Faranic Real Estate FastAPI backend
"""
import uvicorn
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print(f"Starting Faranic Real Estate API server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Log Level: {log_level}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"ReDoc Documentation: http://{host}:{port}/redoc")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "backend.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    ) 