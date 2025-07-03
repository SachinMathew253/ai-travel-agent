"""
Tests for the main travel planning system.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from core.system import TravelPlanningSystem
from utils.config import config

class TestTravelPlanningSystem:
    """Test cases for the main TravelPlanningSystem class."""
    
    @pytest.fixture
    def travel_system(self):
        """Create a TravelPlanningSystem instance for testing."""
        with patch.object(config, 'GOOGLE_API_KEY', 'test-api-key'):
            return TravelPlanningSystem()
    
    def test_system_initialization(self, travel_system):
        """Test system initialization."""
        assert travel_system.session_service is not None
        assert travel_system.agents is not None
        assert travel_system.runner is not None
        assert len(travel_system.agents) == 5  # 4 specialists + 1 coordinator
    
    def test_agent_creation(self, travel_system):
        """Test that all required agents are created."""
        expected_agents = ['weather', 'flight', 'hotel', 'activity', 'coordinator']
        for agent_name in expected_agents:
            assert agent_name in travel_system.agents
    
    def test_get_system_status(self, travel_system):
        """Test system status reporting."""
        status = travel_system.get_system_status()
        assert 'system' in status
        assert 'version' in status
        assert 'status' in status
        assert 'agents' in status
        assert status['system'] == "Travel Planning System"
        assert len(status['agents']) == 5

if __name__ == "__main__":
    pytest.main([__file__])
