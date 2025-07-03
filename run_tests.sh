#!/bin/bash

# Test runner script for the modular travel planning system

echo "🧪 Running Travel Planning System Tests"
echo "====================================="

# Activate virtual environment
source myenv/bin/activate

# Set Python path to include src directory
export PYTHONPATH="./src"

# Run tests based on arguments
if [ "$1" = "all" ] || [ -z "$1" ]; then
    echo "🔄 Running all tests..."
    python -m pytest tests/ -v
elif [ "$1" = "agents" ]; then
    echo "🔄 Running agent tests..."
    python -m pytest tests/test_agents.py -v
elif [ "$1" = "servers" ]; then
    echo "🔄 Running server tests..."
    python -m pytest tests/test_servers.py -v
elif [ "$1" = "system" ]; then
    echo "🔄 Running system tests..."
    python -m pytest tests/test_system.py -v
elif [ "$1" = "web" ]; then
    echo "🔄 Running web tests..."
    python -m pytest tests/test_web.py -v
elif [ "$1" = "integration" ]; then
    echo "🔄 Running integration tests..."
    python -m pytest tests/integration/ -v
else
    echo "Usage: ./run_tests.sh [all|agents|servers|system|web|integration]"
    exit 1
fi
