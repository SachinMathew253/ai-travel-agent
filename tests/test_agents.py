"""
Tests for agent functionality.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from core.agents import AgentFactory
from utils.config import config

class TestAgentFactory:
    """Test cases for the AgentFactory class."""
    
    def test_create_weather_agent(self):
        """Test weather agent creation."""
        agent = AgentFactory.create_weather_agent()
        assert agent.name == "weather_agent"
        assert "weather specialist" in agent.instruction.lower()
        assert len(agent.tools) == 1
    
    def test_create_flight_agent(self):
        """Test flight agent creation."""
        agent = AgentFactory.create_flight_agent()
        assert agent.name == "flight_agent"
        assert "flight booking" in agent.instruction.lower()
        assert len(agent.tools) == 1
    
    def test_create_hotel_agent(self):
        """Test hotel agent creation."""
        agent = AgentFactory.create_hotel_agent()
        assert agent.name == "hotel_agent"
        assert "hotel booking" in agent.instruction.lower()
        assert len(agent.tools) == 1
    
    def test_create_activity_agent(self):
        """Test activity agent creation."""
        agent = AgentFactory.create_activity_agent()
        assert agent.name == "activity_agent"
        assert "activities" in agent.instruction.lower()
        assert len(agent.tools) == 1
    
    def test_create_coordinator_agent(self):
        """Test coordinator agent creation."""
        agent = AgentFactory.create_coordinator_agent()
        assert agent.name == "travel_coordinator"
        assert "coordinator" in agent.instruction.lower()
        assert len(agent.tools) == 4  # All four tool types
        assert agent.generate_content_config is not None

class TestAgentConfiguration:
    """Test agent configuration validity."""
    
    def test_api_key_configuration(self):
        """Test that agents are configured with API key."""
        # Test that the configuration has an API key set
        # Note: We don't test the actual model API key as it may not be exposed
        with patch.object(config, 'GOOGLE_API_KEY', 'test-api-key'):
            agent = AgentFactory.create_weather_agent()
            # Just verify the agent was created successfully with the mocked config
            assert agent is not None
            assert agent.name == "weather_agent"
    
    def test_tool_urls_configuration(self):
        """Test that tool URLs are properly configured."""
        assert config.WEATHER_SERVER_URL.endswith('/mcp')
        assert config.FLIGHT_SERVER_URL.endswith('/mcp')
        assert config.HOTEL_SERVER_URL.endswith('/mcp')
        assert config.ACTIVITY_SERVER_URL.endswith('/mcp')

if __name__ == "__main__":
    pytest.main([__file__])
