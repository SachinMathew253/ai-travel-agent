"""
Agent configurations for the travel planning system.
"""
import threading
import time
from typing import Dict
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPServerParams
from google.adk.models import Gemini
from google.genai.types import GenerateContentConfig, AutomaticFunctionCallingConfig
from utils.config import config
from utils.logging import setup_logging

logger = setup_logging(__name__)

class ToolsetConnectionPool:
    """Connection pool for MCP toolsets to prevent async context issues."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.pools: Dict[str, list] = {}
        self.lock = threading.Lock()
        self.connection_count: Dict[str, int] = {}
    
    def get_toolset(self, service_name: str, url: str) -> MCPToolset:
        """Get a toolset from the pool or create a new one."""
        with self.lock:
            if service_name not in self.pools:
                self.pools[service_name] = []
                self.connection_count[service_name] = 0
            
            pool = self.pools[service_name]
            
            # Try to reuse an existing connection
            if pool:
                toolset = pool.pop()
                logger.debug(f"Reused existing toolset for {service_name}")
                return toolset
            
            # Create new connection if under limit
            if self.connection_count[service_name] < self.max_connections:
                try:
                    params = StreamableHTTPServerParams(url=url)
                    toolset = MCPToolset(connection_params=params)
                    self.connection_count[service_name] += 1
                    logger.info(f"Created new pooled toolset for {service_name} at {url} (count: {self.connection_count[service_name]})")
                    return toolset
                except Exception as e:
                    logger.error(f"Failed to create pooled toolset for {service_name}: {str(e)}")
                    raise
            else:
                logger.warning(f"Maximum connections reached for {service_name}, creating temporary connection")
                # Create a temporary connection that won't be pooled
                params = StreamableHTTPServerParams(url=url)
                return MCPToolset(connection_params=params)
    
    def return_toolset(self, service_name: str, toolset: MCPToolset):
        """Return a toolset to the pool."""
        with self.lock:
            if service_name in self.pools:
                pool = self.pools[service_name]
                if len(pool) < self.max_connections // 2:  # Keep some connections ready
                    pool.append(toolset)
                    logger.debug(f"Returned toolset to {service_name} pool")
                else:
                    # Pool is full, close this connection
                    self._close_toolset(toolset)
                    self.connection_count[service_name] -= 1
    
    def _close_toolset(self, toolset: MCPToolset):
        """Safely close a toolset."""
        try:
            # Check if we're in an async context
            try:
                # If we're in an async context, schedule the async close
                import asyncio
                loop = asyncio.get_running_loop()
                # Create a task to close the toolset asynchronously
                if hasattr(toolset, 'close') and callable(toolset.close):
                    # If it's a coroutine, schedule it
                    if asyncio.iscoroutinefunction(toolset.close):
                        loop.create_task(toolset.close())
                    else:
                        toolset.close()
                elif hasattr(toolset, 'cleanup'):
                    toolset.cleanup()
            except RuntimeError:
                # No event loop running, try sync cleanup
                if hasattr(toolset, 'cleanup'):
                    toolset.cleanup()
                elif hasattr(toolset, 'close') and not asyncio.iscoroutinefunction(getattr(toolset, 'close', None)):
                    toolset.close()
                # For async close methods outside async context, we'll just log a warning
                elif hasattr(toolset, 'close'):
                    logger.warning("Cannot close async toolset outside async context - potential resource leak")
        except Exception as e:
            logger.warning(f"Error closing toolset: {e}")
    
    def cleanup_all(self):
        """Clean up all pooled connections."""
        with self.lock:
            for service_name, pool in self.pools.items():
                logger.info(f"Cleaning up {len(pool)} connections for {service_name}")
                for toolset in pool:
                    self._close_toolset(toolset)
                pool.clear()
                self.connection_count[service_name] = 0
            self.pools.clear()

# Global connection pool
_connection_pool = ToolsetConnectionPool()

class AgentFactory:
    """Factory class for creating travel planning agents with connection pooling."""
    
    _toolsets_cache = {}
    _lock = threading.Lock()
    _creation_timestamps = {}
    _cache_ttl = 300  # 5 minutes TTL for cached toolsets
    
    @staticmethod
    def _get_or_create_toolset(service_name: str, url: str) -> MCPToolset:
        """Get or create a toolset with proper caching and connection pooling."""
        with AgentFactory._lock:
            # Check cache first with TTL validation
            current_time = time.time()
            if service_name in AgentFactory._toolsets_cache:
                creation_time = AgentFactory._creation_timestamps.get(service_name, 0)
                if current_time - creation_time < AgentFactory._cache_ttl:
                    logger.debug(f"Using cached toolset for {service_name}")
                    return AgentFactory._toolsets_cache[service_name]
                else:
                    # Cache expired, remove old entry
                    logger.info(f"Cache expired for {service_name}, creating new toolset")
                    old_toolset = AgentFactory._toolsets_cache.pop(service_name, None)
                    if old_toolset and hasattr(old_toolset, 'cleanup'):
                        try:
                            old_toolset.cleanup()
                        except Exception as e:
                            logger.warning(f"Error cleaning up expired toolset: {e}")
            
            # Try to get from connection pool
            try:
                toolset = _connection_pool.get_toolset(service_name, url)
                AgentFactory._toolsets_cache[service_name] = toolset
                AgentFactory._creation_timestamps[service_name] = current_time
                logger.info(f"Created new MCPToolset for {service_name} at {url}")
                return toolset
            except Exception as e:
                logger.error(f"Failed to create toolset for {service_name}: {str(e)}")
                raise
    
    @staticmethod
    def create_weather_agent() -> LlmAgent:
        """Create a weather specialist agent."""
        weather_toolset = AgentFactory._get_or_create_toolset("weather", config.WEATHER_SERVER_URL)
        
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
        flight_toolset = AgentFactory._get_or_create_toolset("flight", config.FLIGHT_SERVER_URL)
        
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
        hotel_toolset = AgentFactory._get_or_create_toolset("hotel", config.HOTEL_SERVER_URL)
        
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
        activity_toolset = AgentFactory._get_or_create_toolset("activity", config.ACTIVITY_SERVER_URL)
        
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
        weather_toolset = AgentFactory._get_or_create_toolset("weather", config.WEATHER_SERVER_URL)
        flight_toolset = AgentFactory._get_or_create_toolset("flight", config.FLIGHT_SERVER_URL)
        hotel_toolset = AgentFactory._get_or_create_toolset("hotel", config.HOTEL_SERVER_URL)
        activity_toolset = AgentFactory._get_or_create_toolset("activity", config.ACTIVITY_SERVER_URL)
        
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

    @staticmethod
    def cleanup_toolsets():
        """Clean up cached toolsets and connection pool."""
        with AgentFactory._lock:
            for name, toolset in AgentFactory._toolsets_cache.items():
                try:
                    # Return to pool instead of immediately closing
                    _connection_pool.return_toolset(name, toolset)
                    logger.info(f"Returned toolset for {name} to pool")
                except Exception as e:
                    logger.error(f"Error returning toolset for {name} to pool: {str(e)}")
            AgentFactory._toolsets_cache.clear()
            AgentFactory._creation_timestamps.clear()
            
            # Also cleanup the global connection pool
            _connection_pool.cleanup_all()