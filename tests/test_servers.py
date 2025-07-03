"""
Tests for MCP server functionality.
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, patch
from mcp_servers.weather_server import WeatherServer
from mcp_servers.flight_server import FlightServer
from mcp_servers.hotel_server import HotelServer
from mcp_servers.activity_server import ActivityServer

class TestWeatherServer:
    """Test cases for the Weather MCP server."""
    
    def test_weather_server_initialization(self):
        """Test weather server initialization."""
        server = WeatherServer()
        assert server.name == "Weather Server"
        assert server.port == 8000  # Default port
        assert "weather" in server.description.lower()
    
    def test_weather_server_tools_registration(self):
        """Test that weather tools are registered."""
        server = WeatherServer()
        server.register_tools()
        # Tools would be registered with the MCP instance
        assert server.mcp is not None

class TestFlightServer:
    """Test cases for the Flight MCP server."""
    
    def test_flight_server_initialization(self):
        """Test flight server initialization."""
        server = FlightServer()
        assert server.name == "Flight Server"
        assert server.port == 8001  # Default port
        assert "flight" in server.description.lower()
    
    def test_flight_server_tools_registration(self):
        """Test that flight tools are registered."""
        server = FlightServer()
        server.register_tools()
        assert server.mcp is not None

class TestHotelServer:
    """Test cases for the Hotel MCP server."""
    
    def test_hotel_server_initialization(self):
        """Test hotel server initialization."""
        server = HotelServer()
        assert server.name == "Hotel Server"
        assert server.port == 8002  # Default port
        assert "hotel" in server.description.lower()
    
    def test_hotel_server_tools_registration(self):
        """Test that hotel tools are registered."""
        server = HotelServer()
        server.register_tools()
        assert server.mcp is not None

class TestActivityServer:
    """Test cases for the Activity MCP server."""
    
    def test_activity_server_initialization(self):
        """Test activity server initialization."""
        server = ActivityServer()
        assert server.name == "Activity Server"
        assert server.port == 8003  # Default port
        assert "activity" in server.description.lower()
    
    def test_activity_server_tools_registration(self):
        """Test that activity tools are registered."""
        server = ActivityServer()
        server.register_tools()
        assert server.mcp is not None

class TestServerPorts:
    """Test server port configurations."""
    
    def test_unique_ports(self):
        """Test that all servers use unique ports."""
        weather = WeatherServer()
        flight = FlightServer()
        hotel = HotelServer()
        activity = ActivityServer()
        
        ports = [weather.port, flight.port, hotel.port, activity.port]
        assert len(ports) == len(set(ports)), "All servers should use unique ports"
    
    def test_port_range(self):
        """Test that ports are in expected range."""
        weather = WeatherServer()
        flight = FlightServer()
        hotel = HotelServer()
        activity = ActivityServer()
        
        for server in [weather, flight, hotel, activity]:
            assert 8000 <= server.port <= 8099, f"Port {server.port} should be in range 8000-8099"

if __name__ == "__main__":
    pytest.main([__file__])
