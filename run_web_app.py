#!/usr/bin/env python3
"""
Entry point for the web application.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web.app import run_web_server

if __name__ == "__main__":
    run_web_server()
