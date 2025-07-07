"""
Agent configurations for the travel planning system.
"""
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPServerParams
from google.adk.models import Gemini
from google.genai.types import GenerateContentConfig, AutomaticFunctionCallingConfig
from utils.config import config
from utils.logging import setup_logging

logger = setup_logging(__name__)

class AgentFactory:
    """Factory class for creating travel planning agents."""
    
    @staticmethod
    def create_weather_agent() -> LlmAgent:
        """Create a weather specialist agent."""
        weather_params = StreamableHTTPServerParams(url=config.WEATHER_SERVER_URL)
        weather_toolset = MCPToolset(connection_params=weather_params)
        
        return LlmAgent(
            name="weather_agent",
            instruction=(
                "You are a weather specialist. Provide accurate weather information "
                "and forecasts for travel destinations. Always include temperature, "
                "conditions, and helpful travel advice based on weather."
            ),
            tools=[weather_toolset],
            model=Gemini(model_name="gemini-2.0-flash", api_key=config.GOOGLE_API_KEY)
        )
    
    @staticmethod
    def create_flight_agent() -> LlmAgent:
        """Create a flight booking specialist agent."""
        flight_params = StreamableHTTPServerParams(url=config.FLIGHT_SERVER_URL)
        flight_toolset = MCPToolset(connection_params=flight_params)
        
        return LlmAgent(
            name="flight_agent",
            instruction=(
                "You are a flight booking specialist. Help users search for and book "
                "flights. Provide clear information about prices, times, and airlines. "
                "Always offer multiple options when available."
            ),
            tools=[flight_toolset],
            model=Gemini(model_name="gemini-2.0-flash", api_key=config.GOOGLE_API_KEY)
        )
    
    @staticmethod
    def create_hotel_agent() -> LlmAgent:
        """Create a hotel booking specialist agent."""
        hotel_params = StreamableHTTPServerParams(url=config.HOTEL_SERVER_URL)
        hotel_toolset = MCPToolset(connection_params=hotel_params)
        
        return LlmAgent(
            name="hotel_agent",
            instruction=(
                "You are a hotel booking specialist. Help users find and book "
                "accommodations. Provide details about amenities, prices, and ratings. "
                "Consider the user's budget and preferences."
            ),
            tools=[hotel_toolset],
            model=Gemini(model_name="gemini-2.0-flash", api_key=config.GOOGLE_API_KEY)
        )
    
    @staticmethod
    def create_activity_agent() -> LlmAgent:
        """Create an activity specialist agent."""
        activity_params = StreamableHTTPServerParams(url=config.ACTIVITY_SERVER_URL)
        activity_toolset = MCPToolset(connection_params=activity_params)
        
        return LlmAgent(
            name="activity_agent",
            instruction=(
                "You are a local activities and attractions specialist. Recommend "
                "interesting activities, tours, and experiences based on the destination. "
                "Consider the user's interests and available time."
            ),
            tools=[activity_toolset],
            model=Gemini(model_name="gemini-2.0-flash", api_key=config.GOOGLE_API_KEY)
        )
    
    @staticmethod
    def create_coordinator_agent() -> LlmAgent:
        """Create the main coordinator agent with access to all tools."""
        # Create all tool connections
        weather_params = StreamableHTTPServerParams(url=config.WEATHER_SERVER_URL)
        weather_toolset = MCPToolset(connection_params=weather_params)
        
        flight_params = StreamableHTTPServerParams(url=config.FLIGHT_SERVER_URL)
        flight_toolset = MCPToolset(connection_params=flight_params)
        
        hotel_params = StreamableHTTPServerParams(url=config.HOTEL_SERVER_URL)
        hotel_toolset = MCPToolset(connection_params=hotel_params)
        
        activity_params = StreamableHTTPServerParams(url=config.ACTIVITY_SERVER_URL)
        activity_toolset = MCPToolset(connection_params=activity_params)
        
        all_tools = [weather_toolset, flight_toolset, hotel_toolset, activity_toolset]
        
        return LlmAgent(
            name="travel_coordinator",
            instruction=(
                "You are a travel planning coordinator that IMMEDIATELY uses tools when given travel requests. "
                "NEVER ask for more information - ALWAYS start by calling appropriate tools immediately. "
                
                "When given ANY travel query, you MUST IMMEDIATELY call tools: "
                "- For any city mentioned (like 'Paris'), IMMEDIATELY call get_weather(city_name) "
                "- For travel between cities (like 'London to Paris'), IMMEDIATELY call search_flights(origin, destination, date) "
                "- For any trip, IMMEDIATELY call search_hotels(city) for the destination "
                "- For any trip, IMMEDIATELY call recommend_activities(city, 'general') for the destination "
                
                "ALWAYS make these tool calls FIRST, then use the results to provide a comprehensive travel plan. "
                "Do NOT ask follow-up questions - use reasonable defaults and provide complete information."
            ),
            tools=all_tools,
            model=Gemini(model_name="gemini-2.0-flash", api_key=config.GOOGLE_API_KEY),
            generate_content_config=GenerateContentConfig(
                automatic_function_calling=AutomaticFunctionCallingConfig()
            )
        )
