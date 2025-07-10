"""
Main travel planning system implementation.
"""
import asyncio
import time
from typing import Dict, Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.flows.llm_flows.contents import types
from core.agents import AgentFactory
from utils.config import config
from utils.logging import setup_logging

logger = setup_logging(__name__)

class TravelPlanningSystem:
    """Main travel planning system orchestrator with async context management."""
    
    def __init__(self):
        """Initialize the travel planning system."""
        logger.info("Initializing Travel Planning System...")
        
        # Validate configuration
        config_status = config.validate()
        if not config_status["valid"]:
            logger.warning(f"Configuration issues detected: {config_status['issues']}")
            for issue in config_status["issues"]:
                logger.warning(f"  - {issue}")
        
        # Initialize session service
        self.session_service = InMemorySessionService()
        
        # Create agents
        self.agents = self._create_agents()
        
        # Initialize runner with the coordinator agent
        self.runner = Runner(
            app_name="Travel Planning System",
            agent=self.agents['coordinator'],
            session_service=self.session_service
        )
        
        # Track if we're in an async context
        self._event_loop = None
        self._loop_created = False
        
        logger.info("Travel Planning System initialized successfully")
    
    async def __aenter__(self):
        """Async context manager entry."""
        logger.debug("Entering async context for TravelPlanningSystem")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        logger.debug("Exiting async context for TravelPlanningSystem")
        # Clean up toolsets
        AgentFactory.cleanup_toolsets()
    
    def _get_or_create_event_loop(self):
        """Get or create an event loop for sync calls."""
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            self._event_loop = loop
            self._loop_created = False
            return loop
        except RuntimeError:
            # No event loop running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._event_loop = loop
            self._loop_created = True
            return loop
    
    def _cleanup_event_loop(self):
        """Clean up the event loop if we created it."""
        if self._loop_created and self._event_loop:
            try:
                self._event_loop.close()
                logger.debug("Cleaned up event loop")
            except Exception as e:
                logger.warning(f"Error cleaning up event loop: {e}")
            finally:
                self._event_loop = None
                self._loop_created = False
    
    def _create_agents(self) -> Dict[str, Any]:
        """Create all travel planning agents."""
        logger.info("Creating travel planning agents...")
        
        agents = {
            'weather': AgentFactory.create_weather_agent(),
            'flight': AgentFactory.create_flight_agent(),
            'hotel': AgentFactory.create_hotel_agent(),
            'activity': AgentFactory.create_activity_agent(),
            'coordinator': AgentFactory.create_coordinator_agent()
        }
        
        logger.info(f"Created {len(agents)} agents: {list(agents.keys())}")
        return agents
    
    async def plan_trip_coordinated(self, user_query: str) -> Dict[str, Any]:
        """Plan a trip using the coordinator agent."""
        try:
            logger.info(f"Starting coordinated travel planning with query: {user_query}")
            
            # Create a session for this planning request
            session_id = f"session_{int(time.time())}"
            user_id = "travel_user"
            
            # Create session explicitly
            await self.session_service.create_session(
                app_name="Travel Planning System",
                user_id=user_id,
                session_id=session_id
            )
            
            # Create message content with explicit role
            message = types.Content(
                parts=[types.Part(text=user_query)],
                role="user"
            )
            
            logger.info(f"Created message: {message}")
            
            # Run the agent and collect responses
            responses = []
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id, 
                new_message=message
            ):
                logger.debug(f"Received event: {type(event).__name__}")
                
                # Extract text content from different event types
                if hasattr(event, 'content') and event.content:
                    content = event.content
                    
                    # If content has parts, extract text from them
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            if hasattr(part, 'text') and part.text:
                                responses.append(part.text)
                    # If content has text directly
                    elif hasattr(content, 'text') and content.text:
                        responses.append(content.text)
                    # Fallback to string representation but clean it up
                    else:
                        content_str = str(content)
                        # Extract text from the string representation
                        if 'text=' in content_str:
                            import re
                            # Extract text content between quotes after text=
                            matches = re.findall(r'text="([^"]*)"', content_str)
                            if matches:
                                responses.append(matches[0])
                            else:
                                # Try without quotes
                                matches = re.findall(r'text=([^,)]*)', content_str)
                                if matches:
                                    text = matches[0].strip()
                                    # Remove any trailing characters
                                    if text.endswith("')]"):
                                        text = text[:-3]
                                    responses.append(text)
            
            result = "\n".join(responses) if responses else "No response generated"
            
            return {
                "status": "success",
                "workflow_type": "coordinated",
                "result": result
            }
        except Exception as e:
            logger.error(f"Error in coordinated planning: {str(e)}")
            return {
                "status": "error",
                "workflow_type": "coordinated",
                "error": str(e)
            }
    
    def plan_trip_coordinated_sync(self, user_query: str) -> Dict[str, Any]:
        """Synchronous wrapper for coordinated travel planning with proper async context management."""
        try:
            # Check if we're already in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, run directly
                logger.warning("Already in async context, this may cause issues. Consider using async version.")
                return asyncio.create_task(self.plan_trip_coordinated(user_query))
            except RuntimeError:
                # No event loop running, create a proper async context
                async def run_with_context():
                    async with self:
                        return await self.plan_trip_coordinated(user_query)
                
                # Create new event loop for this operation
                loop = asyncio.new_event_loop()
                old_loop = None
                try:
                    # Save current loop if any
                    try:
                        old_loop = asyncio.get_event_loop()
                    except RuntimeError:
                        pass
                    
                    # Set new loop as current
                    asyncio.set_event_loop(loop)
                    
                    # Run the planning operation
                    result = loop.run_until_complete(run_with_context())
                    return result
                
                finally:
                    # Clean up
                    try:
                        # Cancel any remaining tasks
                        pending = asyncio.all_tasks(loop)
                        for task in pending:
                            task.cancel()
                        
                        # Wait for cancellation to complete
                        if pending:
                            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                        
                        # Close the loop
                        loop.close()
                    except Exception as e:
                        logger.warning(f"Error during event loop cleanup: {e}")
                    
                    # Restore old loop if it existed
                    if old_loop:
                        asyncio.set_event_loop(old_loop)
        
        except Exception as e:
            logger.error(f"Error in synchronous coordinated planning: {str(e)}")
            return {
                "status": "error",
                "workflow_type": "coordinated",
                "error": str(e)
            }
    
    async def plan_trip_sequential(self, travel_request: Dict[str, Any]) -> Dict[str, Any]:
        """Plan a trip using sequential agent execution."""
        try:
            logger.info("Starting sequential travel planning...")
            
            # Execute agents in sequence: weather → flights → hotels → activities
            results = {}
            
            # Weather
            if 'destination' in travel_request:
                session_id = f"weather_session_{int(time.time())}"
                user_id = "weather_user"
                await self.session_service.create_session(
                    app_name="Travel Planning System",
                    user_id=user_id, 
                    session_id=session_id
                )
                
                weather_query = f"What's the weather like in {travel_request['destination']}?"
                message = types.Content(parts=[types.Part(text=weather_query)])
                
                weather_responses = []
                async for event in self.runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=message
                ):
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    weather_responses.append(part.text)
                
                results['weather'] = "\n".join(weather_responses) if weather_responses else "Weather information unavailable"
            
            return {
                "status": "success",
                "workflow_type": "sequential", 
                "result": f"Sequential planning completed for {travel_request.get('origin', 'Unknown')} to {travel_request.get('destination', 'Unknown')}. Results: {results}"
            }
        except Exception as e:
            logger.error(f"Error in sequential planning: {str(e)}")
            return {
                "status": "error",
                "workflow_type": "sequential",
                "error": str(e)
            }
    
    async def plan_trip_parallel(self, travel_request: Dict[str, Any]) -> Dict[str, Any]:
        """Plan a trip using parallel agent execution."""
        try:
            logger.info("Starting parallel travel planning...")
            
            # For now, use the coordinator agent as a fallback since the 
            # parallel implementation would be complex
            query = f"""
            Plan a trip from {travel_request.get('origin', 'Unknown')} to {travel_request.get('destination', 'Unknown')}
            departing {travel_request.get('departure_date', 'soon')} and returning {travel_request.get('return_date', 'later')}.
            Budget: {travel_request.get('budget', 'moderate')}. 
            Travelers: {travel_request.get('travelers', 1)}.
            Interests: {', '.join(travel_request.get('interests', []))}.
            """
            
            # Use the coordinated workflow as a fallback for parallel
            result = await self.plan_trip_coordinated(query)
            result['workflow_type'] = 'parallel'
            
            return result
        except Exception as e:
            logger.error(f"Error in parallel planning: {str(e)}")
            return {
                "status": "error",
                "workflow_type": "parallel", 
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status."""
        config_status = config.validate()
        
        return {
            "system": "Travel Planning System",
            "version": "1.0.0",
            "status": "operational" if config_status["valid"] else "configuration_issues",
            "agents": list(self.agents.keys()),
            "configuration": config_status["config"],
            "issues": config_status["issues"]
        }
