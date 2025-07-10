"""
FastAPI web interface for the travel planning system (async-native).
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from core.system import TravelPlanningSystem
from utils.config import config
from utils.logging import setup_logging

logger = setup_logging(__name__)

# Pydantic models for request validation
class CoordinatedPlanRequest(BaseModel):
    workflow: str = "coordinated"
    query: str

class StructuredPlanRequest(BaseModel):
    workflow: str
    origin: str = ""
    destination: str = ""
    departure_date: str = ""
    return_date: str = ""
    travelers: int = 1
    budget: str = "moderate"
    interests: List[str] = []

# FastAPI app
app = FastAPI(
    title="AI Travel Planning System",
    description="Multi-agent travel planning system with weather, flights, hotels, and activities",
    version="1.0.0"
)

# Templates
templates = Jinja2Templates(directory="src/web/templates")

# Global travel system instance
travel_system: Optional[TravelPlanningSystem] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the travel system on startup."""
    global travel_system
    try:
        travel_system = TravelPlanningSystem()
        logger.info("Travel planning system initialized for FastAPI interface")
    except Exception as e:
        logger.error(f"Failed to initialize travel system: {e}")
        travel_system = None

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global travel_system
    if travel_system:
        try:
            from core.agents import AgentFactory
            AgentFactory.cleanup_toolsets()
            logger.info("Travel system cleanup completed")
        except Exception as e:
            logger.error(f"Error during shutdown cleanup: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with travel planning form."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page with system information."""
    system_status = travel_system.get_system_status() if travel_system else {"status": "not_initialized"}
    return templates.TemplateResponse("about.html", {"request": request, "system_status": system_status})

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    if travel_system:
        status = travel_system.get_system_status()
        return JSONResponse(status)
    else:
        raise HTTPException(status_code=503, detail="Travel system not initialized")

@app.post("/api/plan")
async def plan_trip(request: CoordinatedPlanRequest):
    """API endpoint for coordinated travel planning."""
    try:
        if not travel_system:
            raise HTTPException(status_code=503, detail="Travel system not initialized")
        
        # Use the async method directly without the context manager
        result = await travel_system.plan_trip_coordinated(request.query)
        
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"Error in travel planning API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plan-structured")
async def plan_trip_structured(request: StructuredPlanRequest):
    """API endpoint for structured travel planning (sequential/parallel)."""
    try:
        if not travel_system:
            raise HTTPException(status_code=503, detail="Travel system not initialized")
        
        travel_request = {
            'origin': request.origin,
            'destination': request.destination,
            'departure_date': request.departure_date,
            'return_date': request.return_date,
            'travelers': request.travelers,
            'budget': request.budget,
            'interests': request.interests
        }
        
        # Use the async method directly without the context manager
        if request.workflow == 'sequential':
            result = await travel_system.plan_trip_sequential(travel_request)
        elif request.workflow == 'parallel':
            result = await travel_system.plan_trip_parallel(travel_request)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown workflow: {request.workflow}")
        
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"Error in structured travel planning API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plan", response_class=HTMLResponse)
async def plan_result(request: Request, query: str = "", result: str = ""):
    """Display travel plan results."""
    return templates.TemplateResponse("result.html", {
        "request": request, 
        "query": query, 
        "result": result
    })

@app.post("/plan", response_class=HTMLResponse)
async def plan_trip_form(request: Request):
    """Handle travel planning form submission."""
    try:
        # Get form data
        form_data = await request.form()
        workflow = form_data.get("workflow_type", "coordinated")  # Changed from "workflow" to "workflow_type"
        
        # Extract individual form fields
        origin = form_data.get("origin", "")
        destination = form_data.get("destination", "")
        departure_date = form_data.get("departure_date", "")
        return_date = form_data.get("return_date", "")
        travelers = int(form_data.get("travelers", 1))
        budget = form_data.get("budget", "moderate")
        interests = form_data.get("interests", "").split(",") if form_data.get("interests") else []
        
        # Create a natural language query from the form data
        query = f"Plan a trip from {origin} to {destination} for {travelers} travelers"
        if departure_date:
            query += f" departing on {departure_date}"
        if return_date:
            query += f" and returning on {return_date}"
        query += f" with a {budget} budget"
        if interests:
            interests_clean = [i.strip() for i in interests if i.strip()]
            if interests_clean:
                query += f" with interests in {', '.join(interests_clean)}"
        
        logger.info(f"Form submission - workflow: {workflow}, query: {query}")
        
        if not travel_system:
            error_message = "Travel system not initialized. Please try again later."
            return templates.TemplateResponse("result.html", {
                "request": request,
                "query": query,
                "result": f"Error: {error_message}"
            })
        
        # Process the travel planning request
        try:
            if workflow == "coordinated":
                result = await travel_system.plan_trip_coordinated(query)
            else:
                # Handle structured planning
                travel_request = {
                    'origin': origin,
                    'destination': destination,
                    'departure_date': departure_date,
                    'return_date': return_date,
                    'travelers': travelers,
                    'budget': budget,
                    'interests': interests
                }
                
                if workflow == 'sequential':
                    result = await travel_system.plan_trip_sequential(travel_request)
                elif workflow == 'parallel':
                    result = await travel_system.plan_trip_parallel(travel_request)
                else:
                    result = await travel_system.plan_trip_coordinated(query)
        except Exception as e:
            logger.error(f"Travel planning failed, using fallback: {e}")
            # Fallback response when MCP servers are not accessible
            result = {
                'status': 'fallback',
                'workflow_type': workflow,
                'query': query,
                'message': f"I understand you want to plan a trip {query.lower()}. Unfortunately, our live booking and weather services are temporarily unavailable. Here's what I can help you with:\n\n"
                          f"🗺️ **Trip Overview**\n"
                          f"- Origin: {origin}\n"
                          f"- Destination: {destination}\n"
                          f"- Dates: {departure_date} to {return_date}\n"
                          f"- Travelers: {travelers}\n"
                          f"- Budget: {budget}\n"
                          f"- Interests: {', '.join(interests_clean) if interests_clean else 'General sightseeing'}\n\n"
                          f"🔧 **Recommendations**\n"
                          f"- Check flight prices on airline websites or travel booking sites\n"
                          f"- Look for hotels on booking platforms based on your budget preference\n"
                          f"- Research local attractions and activities related to your interests\n"
                          f"- Check weather forecasts closer to your travel date\n\n"
                          f"Please try again later when our services are restored for personalized recommendations and live booking assistance.",
                'recommendations': {
                    'flights': f"Search for flights from {origin} to {destination} on airline websites",
                    'hotels': f"Look for {budget} budget accommodations in {destination}",
                    'activities': f"Research activities related to: {', '.join(interests_clean) if interests_clean else 'sightseeing'}",
                    'weather': f"Check weather forecast for {destination} during your travel dates"
                }
            }
        
        # Format the result for display
        if isinstance(result, dict):
            # Convert dict result to a formatted string
            formatted_result = ""
            for key, value in result.items():
                if isinstance(value, dict):
                    formatted_result += f"\n{key.upper()}:\n"
                    for sub_key, sub_value in value.items():
                        formatted_result += f"  {sub_key}: {sub_value}\n"
                else:
                    formatted_result += f"{key}: {value}\n"
            result = formatted_result
        elif not isinstance(result, str):
            result = str(result)
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "query": query,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error in travel planning form submission: {e}")
        error_message = f"An error occurred while planning your trip: {str(e)}"
        return templates.TemplateResponse("result.html", {
            "request": request,
            "query": form_data.get("query", "") if 'form_data' in locals() else "",
            "result": error_message
        })

def run_fastapi_server():
    """Run the FastAPI server."""
    try:
        logger.info("Starting Travel Planning FastAPI Interface...")
        
        # Validate configuration
        config_status = config.validate()
        if not config_status["valid"]:
            logger.warning("Configuration issues detected:")
            for issue in config_status["issues"]:
                logger.warning(f"  - {issue}")
        
        logger.info("📋 Available endpoints:")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/ - Main interface")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/api/plan - Coordinated planning API")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/api/plan-structured - Structured planning API")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/about - About page")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/api/health - Health check")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/docs - API documentation")
        
        import uvicorn
        uvicorn.run(
            "web.app:app",
            host="0.0.0.0",
            port=config.WEB_UI_PORT,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start FastAPI server: {e}")
        raise

if __name__ == "__main__":
    run_fastapi_server()
