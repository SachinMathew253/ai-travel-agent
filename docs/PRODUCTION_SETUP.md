# Production Setup Guide

## 🔑 Getting Your Google API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key (starts with "AIza...")

## 🚀 Quick Start

### 1. Set Your API Key
```bash
export GOOGLE_API_KEY="AIza...your-actual-key-here"
```

### 2. Start the System
```bash
cd /Users/sachinmathew/personal/ai_agent
./start_system.sh
```

### 3. Access the Web Interface
Open your browser to: http://localhost:8080

### 4. Test the System
```bash
python test_system.py
```

## 🌐 Using the Web Interface

1. **Fill out the travel form:**
   - Origin city (e.g., "London")
   - Destination city (e.g., "Paris")
   - Departure and return dates
   - Number of travelers
   - Budget preference
   - Interests (comma-separated)

2. **Choose workflow type:**
   - **Coordinated** (recommended) - Uses the main coordinator agent
   - **Sequential** - Runs agents one after another
   - **Parallel** - Runs multiple agents simultaneously

3. **Get comprehensive results:**
   - Weather forecasts
   - Flight options
   - Hotel recommendations
   - Activity suggestions
   - Budget estimates

## 📡 API Usage

### Endpoint: POST /api/plan

```bash
curl -X POST http://localhost:8080/api/plan \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": "coordinated",
    "query": "Plan a romantic weekend in Paris from London, departing July 15th 2025"
  }'
```

### Response Format:
```json
{
  "status": "success",
  "workflow_type": "coordinated",
  "result": "Complete travel plan with weather, flights, hotels, and activities..."
}
```

## 🛠️ System Management

### Check Server Status:
```bash
lsof -i :8000 -i :8001 -i :8002 -i :8003 -i :8080
```

### View Logs:
```bash
tail -f weather_server.log flight_server.log hotel_server.log activity_server.log
```

### Stop All Services:
```bash
./stop_services.sh
```

### Restart System:
```bash
./stop_services.sh && ./start_system.sh
```

## 🔧 Troubleshooting

### If servers don't start:
```bash
# Check port availability
lsof -i :8000
# Kill conflicting processes if needed
sudo kill -9 <PID>
```

### If API calls fail:
1. Verify your API key is valid
2. Check you have sufficient quota
3. Ensure internet connectivity

### If MCP servers aren't responding:
```bash
# Restart individual servers
python weather_server.py &
python flight_server.py &
python hotel_server.py &
python activity_server.py &
```

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   API Endpoint  │
│   (Port 8080)   │    │   (Port 8080)   │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │  Coordinator Agent   │
          │   (Google ADK)       │
          └──────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌───────┐    ┌──────────┐    ┌──────────┐
│Weather│    │ Flights  │    │ Hotels   │
│ MCP   │    │   MCP    │    │   MCP    │
│:8000  │    │  :8001   │    │  :8002   │
└───────┘    └──────────┘    └──────────┘
                     │
                ┌────▼────┐
                │Activities│
                │   MCP   │
                │  :8003  │
                └─────────┘
```

## 🎯 Success Indicators

When everything is working correctly, you should see:

1. **All servers responding:**
   ```
   ✅ Weather Server: Port 8000 is responding
   ✅ Flight Server: Port 8001 is responding  
   ✅ Hotel Server: Port 8002 is responding
   ✅ Activity Server: Port 8003 is responding
   ✅ Web Interface: All endpoints OK
   ```

2. **AI responses include:**
   - Real weather data for destinations
   - Flight search results and pricing
   - Hotel recommendations with ratings
   - Activity suggestions based on interests
   - Comprehensive travel itineraries

## 🚀 You're Ready to Go!

Your multi-agent travel planning system is now fully operational and ready to provide intelligent, comprehensive travel planning assistance!
