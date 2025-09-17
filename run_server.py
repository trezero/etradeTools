#!/usr/bin/env python3
"""Main entry point for AI Trading Assistant web server."""

import sys
import os
import asyncio
import uvicorn

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Import the FastAPI app
from etrade_python_client.web.main import app, config_manager

def main():
    """Main entry point."""
    print("🚀 Starting AI Trading Assistant...")
    print(f"📍 Project root: {project_root}")
    
    # Run the FastAPI server
    uvicorn.run(
        "etrade_python_client.web.main:app",
        host=config_manager.get_web_app_host(),
        port=config_manager.get_web_app_port(),
        reload=config_manager.is_debug_enabled(),
        log_level="info"
    )

if __name__ == "__main__":
    main()