"""
Weather MCP server implementation.
"""
import random
import json
from typing import Optional
from mcp_servers.base_server import BaseMCPServer
from utils.config import config

class WeatherServer(BaseMCPServer):
    """Weather information MCP server."""
    
    def __init__(self):
        super().__init__(
            name="Weather Server",
            port=config.WEATHER_SERVER_PORT,
            description="Provides weather information and forecasts"
        )
    
    def register_tools(self):
        """Register weather-related tools."""
        
        @self.mcp.tool()
        def get_weather(city: str) -> str:
            """Get the current weather for a city"""
            try:
                if not city or not isinstance(city, str):
                    self.logger.error(f"Invalid city input: {city}")
                    return json.dumps({"error": "Invalid city name"})
                
                # Mock weather data (replace with real API in production)
                conditions = ["sunny", "cloudy", "rainy", "snowy", "foggy"]
                temp = random.randint(5, 35)
                humidity = random.randint(30, 90)
                result = {
                    "city": city,
                    "condition": random.choice(conditions),
                    "temperature_c": temp,
                    "humidity_percent": humidity
                }
                self.logger.info(f"Weather fetched for {city}: {result}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error in get_weather for {city}: {str(e)}")
                return json.dumps({"error": f"Failed to fetch weather: {str(e)}"})

        @self.mcp.tool()
        def get_forecast(city: str, days: int) -> str:
            """Get a weather forecast for the next few days"""
            try:
                if not city or not isinstance(city, str):
                    self.logger.error(f"Invalid city input: {city}")
                    return json.dumps({"error": "Invalid city name"})
                
                if not isinstance(days, int) or days < 1 or days > 14:
                    self.logger.error(f"Invalid days input: {days}")
                    return json.dumps({"error": "Days must be between 1 and 14"})
                
                # Mock forecast data
                conditions = ["sunny", "cloudy", "rainy", "snowy", "partly cloudy"]
                forecast = []
                
                for day in range(days):
                    day_forecast = {
                        "day": day + 1,
                        "condition": random.choice(conditions),
                        "high_temp_c": random.randint(15, 35),
                        "low_temp_c": random.randint(5, 20),
                        "precipitation_chance": random.randint(0, 100)
                    }
                    forecast.append(day_forecast)
                
                result = {
                    "city": city,
                    "forecast_days": days,
                    "forecast": forecast
                }
                
                self.logger.info(f"Forecast fetched for {city} ({days} days)")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error in get_forecast for {city}: {str(e)}")
                return json.dumps({"error": f"Failed to fetch forecast: {str(e)}"})

def main():
    """Main function to run the weather server."""
    server = WeatherServer()
    server.run()

if __name__ == "__main__":
    main()
