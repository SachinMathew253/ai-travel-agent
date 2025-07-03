#!/usr/bin/env python3
"""
Entry point for the weather server.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_servers.weather_server import main

if __name__ == "__main__":
    main()
