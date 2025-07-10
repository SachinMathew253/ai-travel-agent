#!/usr/bin/env python3
"""
Entry point for the FastAPI web server.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web.fastapi_app import run_fastapi_server

if __name__ == "__main__":
    run_fastapi_server()
