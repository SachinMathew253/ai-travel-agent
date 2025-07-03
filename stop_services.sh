#!/bin/bash

# Stop all MCP servers and clean up

echo "🛑 Stopping Multi-Agent Travel Planning System..."

# Function to stop a server by PID file
stop_server() {
    local server_name=$1
    local log_name=$(echo "${server_name}" | tr '[:upper:]' '[:lower:]')
    local pid_file="${log_name}_server.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔻 Stopping $server_name (PID: $pid)..."
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force killing $server_name..."
                kill -9 "$pid"
            fi
            echo "✅ $server_name stopped"
        else
            echo "ℹ️  $server_name was not running"
        fi
        rm -f "$pid_file"
    else
        echo "ℹ️  No PID file found for $server_name"
    fi
}

# Stop all servers
stop_server "Weather"
stop_server "Flight" 
stop_server "Hotel"
stop_server "Activity"

# Kill any remaining server processes
echo ""
echo "🧹 Cleaning up any remaining server processes..."
pkill -f "run_.*_server.py" 2>/dev/null
pkill -f "run_web_app.py" 2>/dev/null
pkill -f ".*_wrapper.sh" 2>/dev/null

# Clean up any remaining wrapper scripts
rm -f *_wrapper.sh 2>/dev/null

# Kill any remaining processes on our ports
for port in 8000 8001 8002 8003 5000; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "🔻 Killing process on port $port (PID: $pid)"
        kill -9 "$pid" 2>/dev/null
    fi
done

# Clean up log files (optional)
echo ""
echo "🗑️  Cleaning up log files..."
rm -f *_server.log
rm -f *.pid

echo ""
echo "✅ All services stopped successfully!"
