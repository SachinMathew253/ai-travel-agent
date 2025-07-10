#!/bin/bash

# Multi-Agent Travel Planning System Startup Script
echo "🚀 Starting Multi-Agent Travel Planning System..."

# Set the working directory
cd "$(dirname "$0")"

# Check if virtual environment exists and activate it
if [ -d "myenv" ]; then
    echo "📦 Activating virtual environment..."
    source myenv/bin/activate
else
    echo "❌ Virtual environment not found. Please run 'python -m venv myenv' first."
    exit 1
fi

# Check for .env file and Google API key
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found."
    echo "Creating a template .env file..."
    echo "Please edit .env and add your Google API key."
    cp /dev/null .env
    echo "GOOGLE_API_KEY=your-api-key-here" >> .env
    echo "FLASK_SECRET_KEY=travel-planning-secret-key-change-in-production" >> .env
    echo "WEATHER_SERVER_PORT=8000" >> .env
    echo "FLIGHT_SERVER_PORT=8001" >> .env
    echo "HOTEL_SERVER_PORT=8002" >> .env
    echo "ACTIVITY_SERVER_PORT=8003" >> .env
    echo "WEB_UI_PORT=8080" >> .env
    echo "LOG_LEVEL=INFO" >> .env
fi

# Load environment variables from .env file
set -a  # automatically export all variables
source .env
set +a

# Set Python path for modular structure
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Check if Google API key is set (and not the placeholder)
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-api-key-here" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not properly set in .env file."
    echo "Please edit the .env file and set your Google API key:"
    echo "GOOGLE_API_KEY=your-actual-api-key"
    echo "You can get an API key from: https://aistudio.google.com/app/apikey"
    echo ""
    echo "Continuing without valid API key - some features may not work..."
else
    echo "✅ Google API key loaded from .env file"
fi

# Check if required entry point files exist
echo "📋 Checking system requirements..."
for file in "run_weather_server.py" "run_flight_server.py" "run_hotel_server.py" "run_activity_server.py" "run_web_app.py"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file $file not found!"
        echo "Please ensure the modular system is properly set up."
        exit 1
    fi
done
echo "✅ All required entry point files found"

# Check for asyncio environment conflicts
echo "🔍 Checking for environment conflicts..."
if python -c "import asyncio; asyncio.get_event_loop()" 2>/dev/null; then
    echo "⚠️  Warning: Asyncio event loop detected in current environment"
    echo "   This may cause server startup issues."
    echo "   For best results, run this script in a fresh terminal session."
    echo ""
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    # Kill any background processes we started
    for pid_file in weather_server.pid flight_server.pid hotel_server.pid activity_server.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid"
            fi
            rm -f "$pid_file"
        fi
    done
    echo "👋 Goodbye!"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Function to start MCP servers in background
start_mcp_server() {
    local server_name=$1
    local server_file=$2
    local port=$3
    
    echo "🔧 Starting $server_name on port $port..."
    local log_name=$(echo "${server_name}" | tr '[:upper:]' '[:lower:]')
    
    # Create a wrapper script for each server to ensure clean environment
    local wrapper_script="${log_name}_wrapper.sh"
    cat > "$wrapper_script" << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
source myenv/bin/activate
export PYTHONPATH="./src"
exec python "$server_file"
EOF
    chmod +x "$wrapper_script"
    
    # Run the wrapper script in background
    ./"$wrapper_script" > "${log_name}_server.log" 2>&1 &
    local pid=$!
    echo "$pid" > "${log_name}_server.pid"
    
    # Wait a moment for server to start
    sleep 4
    
    # Check if server is running
    if kill -0 "$pid" 2>/dev/null; then
        echo "✅ $server_name started successfully (PID: $pid)"
        # Clean up wrapper script
        rm -f "$wrapper_script"
        return 0
    else
        echo "❌ Failed to start $server_name"
        echo "📋 Check ${log_name}_server.log for details"
        # Show last few lines of the log for debugging
        echo "   Last error lines:"
        tail -3 "${log_name}_server.log" | sed 's/^/   /'
        rm -f "$wrapper_script"
        return 1
    fi
}

# Start all MCP servers using new modular structure
echo ""
echo "🔧 Starting MCP Servers..."
start_mcp_server "Weather" "run_weather_server.py" ${WEATHER_SERVER_PORT:-8000}
start_mcp_server "Flight" "run_flight_server.py" ${FLIGHT_SERVER_PORT:-8001}
start_mcp_server "Hotel" "run_hotel_server.py" ${HOTEL_SERVER_PORT:-8002}
start_mcp_server "Activity" "run_activity_server.py" ${ACTIVITY_SERVER_PORT:-8003}

# Wait for all servers to be ready
echo ""
echo "⏳ Waiting for all servers to be ready..."
sleep 5

# Check server health by checking if processes are still running
echo ""
echo "🔍 Checking server health..."
all_servers_running=true

for server in "weather" "flight" "hotel" "activity"; do
    if [ -f "${server}_server.pid" ]; then
        pid=$(cat "${server}_server.pid")
        if kill -0 "$pid" 2>/dev/null; then
            # Capitalize server name for display
            display_name=$(echo "$server" | sed 's/./\U&/')
            echo "✅ ${display_name} server is running (PID: $pid)"
        else
            display_name=$(echo "$server" | sed 's/./\U&/')
            echo "❌ ${display_name} server is not running"
            all_servers_running=false
        fi
    else
        display_name=$(echo "$server" | sed 's/./\U&/')
        echo "❌ ${display_name} server PID file not found"
        all_servers_running=false
    fi
done

if [ "$all_servers_running" = true ]; then
    echo "🎉 All MCP servers are running successfully!"
else
    echo "⚠️  Some servers may not be running properly."
    echo "💡 Troubleshooting tips:"
    echo "   1. Check log files: *_server.log"
    echo "   2. Try running in a fresh terminal session"
    echo "   3. Ensure no other processes are using ports 8000-8003"
    echo "   4. Run individual servers manually: python run_weather_server.py"
    echo ""
    echo "   Common solutions:"
    echo "   - Open a new terminal window and try again"
    echo "   - Run: ./stop_services.sh && ./start_system.sh"
    echo "   - Check if ports are in use: lsof -i :8000-8003"
    echo ""
fi

echo ""
echo "🌐 Starting Web Interface..."
echo "📋 Available at: http://localhost:${WEB_UI_PORT:-8080}"
echo ""
echo "🛑 To stop all services, press Ctrl+C or run: ./stop_services.sh"
echo ""

# Start the web interface (this will run in foreground)
PYTHONPATH="${PWD}/src:${PYTHONPATH}" python run_web_app.py
