"""
Configuration management for the travel planning system.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the travel planning system."""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # Server Ports
    WEATHER_SERVER_PORT = int(os.getenv("WEATHER_SERVER_PORT", "8000"))
    FLIGHT_SERVER_PORT = int(os.getenv("FLIGHT_SERVER_PORT", "8001"))
    HOTEL_SERVER_PORT = int(os.getenv("HOTEL_SERVER_PORT", "8002"))
    ACTIVITY_SERVER_PORT = int(os.getenv("ACTIVITY_SERVER_PORT", "8003"))
    WEB_UI_PORT = int(os.getenv("WEB_UI_PORT", "8080"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # MCP Server URLs
    @property
    def WEATHER_SERVER_URL(self) -> str:
        return f"http://localhost:{self.WEATHER_SERVER_PORT}/mcp"
    
    @property
    def FLIGHT_SERVER_URL(self) -> str:
        return f"http://localhost:{self.FLIGHT_SERVER_PORT}/mcp"
    
    @property
    def HOTEL_SERVER_URL(self) -> str:
        return f"http://localhost:{self.HOTEL_SERVER_PORT}/mcp"
    
    @property
    def ACTIVITY_SERVER_URL(self) -> str:
        return f"http://localhost:{self.ACTIVITY_SERVER_PORT}/mcp"
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return status."""
        issues = []
        
        if not self.GOOGLE_API_KEY or self.GOOGLE_API_KEY == "PLACEHOLDER_API_KEY":
            issues.append("GOOGLE_API_KEY not set or is placeholder")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "weather_port": self.WEATHER_SERVER_PORT,
                "flight_port": self.FLIGHT_SERVER_PORT,
                "hotel_port": self.HOTEL_SERVER_PORT,
                "activity_port": self.ACTIVITY_SERVER_PORT,
                "web_port": self.WEB_UI_PORT,
                "log_level": self.LOG_LEVEL,
                "api_key_set": bool(self.GOOGLE_API_KEY and self.GOOGLE_API_KEY != "PLACEHOLDER_API_KEY")
            }
        }

# Global config instance
config = Config()
