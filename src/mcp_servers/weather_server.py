"""
Weather MCP server implementation with OpenWeatherMap API integration.
"""
import json
import requests
from typing import Optional
from datetime import datetime
from mcp_servers.base_server import BaseMCPServer
from utils.config import config

class WeatherServer(BaseMCPServer):
    """Weather information MCP server with OpenWeatherMap API integration."""
    
    def __init__(self):
        super().__init__(
            name="Weather Server",
            port=config.WEATHER_SERVER_PORT,
            description="Provides weather information and forecasts using OpenWeatherMap API"
        )
        self.base_url_v3 = "https://api.openweathermap.org/data/3.0"
        self.base_url_v2 = "https://api.openweathermap.org/data/2.5"
        self.geocoding_url = "https://api.openweathermap.org/geo/1.0"
        self.api_key = config.OPENWEATHER_API_KEY
        self.use_one_call_api = True  # Try One Call API first, fallback to basic API
        
        if not self.api_key:
            self.logger.warning("OpenWeatherMap API key not configured. Set OPENWEATHER_API_KEY environment variable.")
        else:
            self.logger.info("OpenWeatherMap API key configured. Testing API access...")
    
    def _make_api_request(self, endpoint: str, params: dict, use_v3: bool = True) -> Optional[dict]:
        """Make a request to the OpenWeatherMap API with fallback to v2.5 API."""
        if not self.api_key:
            return {"error": "OpenWeatherMap API key not configured"}
        
        params['appid'] = self.api_key
        
        # Try One Call API 3.0 first if available
        if use_v3 and self.use_one_call_api:
            url = f"{self.base_url_v3}/{endpoint}"
        else:
            url = f"{self.base_url_v2}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # If v3 API fails with 401/403, fall back to v2.5 and disable v3 for future calls
            if use_v3 and response.status_code in [401, 403]:
                self.logger.warning("One Call API 3.0 not accessible. Falling back to basic API.")
                self.use_one_call_api = False
                return self._make_api_request(endpoint.replace('onecall', 'weather'), params, use_v3=False)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse API response: {str(e)}")
            return {"error": "Invalid API response format"}
    
    def _get_coordinates(self, city: str) -> Optional[tuple]:
        """Get coordinates for a city using geocoding API."""
        params = {
            'q': city,
            'limit': 1,
            'appid': self.api_key
        }
        
        url = f"{self.geocoding_url}/direct"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result and len(result) > 0:
                return result[0]['lat'], result[0]['lon'], result[0]['name'], result[0].get('country', '')
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Geocoding request failed: {str(e)}")
            return None
    
    def register_tools(self):
        """Register weather-related tools."""
        
        @self.mcp.tool()
        def get_current_weather(city: str) -> str:
            """Get comprehensive current weather data for a city using One Call API 3.0"""
            try:
                if not city or not isinstance(city, str):
                    self.logger.error(f"Invalid city input: {city}")
                    return json.dumps({"error": "Invalid city name"})
                
                # Get coordinates for the city
                coord_result = self._get_coordinates(city)
                if not coord_result:
                    return json.dumps({"error": f"Could not find coordinates for city: {city}"})
                
                lat, lon, city_name, country = coord_result
                
                # Use One Call API 3.0 for comprehensive weather data
                params = {
                    'lat': lat,
                    'lon': lon,
                    'units': 'metric',
                    'exclude': 'minutely,hourly,daily,alerts'  # Only get current weather
                }
                
                weather_data = self._make_api_request("onecall", params)
                
                if isinstance(weather_data, dict) and "error" in weather_data:
                    return json.dumps(weather_data)
                
                current = weather_data.get('current', {})
                
                # Extract comprehensive current weather information
                result = {
                    "city": city_name,
                    "country": country,
                    "coordinates": {"lat": lat, "lon": lon},
                    "timezone": weather_data.get('timezone', ''),
                    "timezone_offset": weather_data.get('timezone_offset', 0),
                    "current": {
                        "datetime": datetime.fromtimestamp(current.get('dt', 0)).isoformat(),
                        "sunrise": datetime.fromtimestamp(current.get('sunrise', 0)).isoformat() if current.get('sunrise') else None,
                        "sunset": datetime.fromtimestamp(current.get('sunset', 0)).isoformat() if current.get('sunset') else None,
                        "temperature_c": round(current.get('temp', 0), 1),
                        "feels_like_c": round(current.get('feels_like', 0), 1),
                        "pressure_hpa": current.get('pressure', 0),
                        "humidity_percent": current.get('humidity', 0),
                        "dew_point_c": round(current.get('dew_point', 0), 1),
                        "uv_index": current.get('uvi', 0),
                        "clouds_percent": current.get('clouds', 0),
                        "visibility_m": current.get('visibility', 0),
                        "wind": {
                            "speed_ms": current.get('wind_speed', 0),
                            "direction_deg": current.get('wind_deg', 0),
                            "gust_ms": current.get('wind_gust', 0)
                        },
                        "weather": {
                            "main": current.get('weather', [{}])[0].get('main', ''),
                            "description": current.get('weather', [{}])[0].get('description', ''),
                            "icon": current.get('weather', [{}])[0].get('icon', '')
                        },
                        "precipitation": {
                            "rain_1h": current.get('rain', {}).get('1h', 0) if current.get('rain') else 0,
                            "snow_1h": current.get('snow', {}).get('1h', 0) if current.get('snow') else 0
                        }
                    }
                }
                
                self.logger.info(f"Current weather fetched for {city_name}: {result['current']['weather']['description']}, {result['current']['temperature_c']}°C")
                return json.dumps(result)
                
            except Exception as e:
                self.logger.error(f"Error in get_current_weather for {city}: {str(e)}")
                return json.dumps({"error": f"Failed to fetch current weather: {str(e)}"})

        @self.mcp.tool()
        def get_weather_forecast(city: str, days: int = 7) -> str:
            """Get comprehensive weather forecast using One Call API 3.0 (up to 8 days)"""
            try:
                if not city or not isinstance(city, str):
                    self.logger.error(f"Invalid city input: {city}")
                    return json.dumps({"error": "Invalid city name"})
                
                if not isinstance(days, int) or days < 1 or days > 8:
                    self.logger.error(f"Invalid days input: {days}")
                    return json.dumps({"error": "Days must be between 1 and 8 for One Call API 3.0"})
                
                # Get coordinates for the city
                coord_result = self._get_coordinates(city)
                if not coord_result:
                    return json.dumps({"error": f"Could not find coordinates for city: {city}"})
                
                lat, lon, city_name, country = coord_result
                
                # Use One Call API 3.0 for comprehensive forecast
                params = {
                    'lat': lat,
                    'lon': lon,
                    'units': 'metric',
                    'exclude': 'minutely'  # Include current, hourly, daily, and alerts
                }
                
                forecast_data = self._make_api_request("onecall", params)
                
                if isinstance(forecast_data, dict) and "error" in forecast_data:
                    return json.dumps(forecast_data)
                
                # Process daily forecast
                daily_forecasts = []
                daily_data = forecast_data.get('daily', [])[:days]
                
                for i, day_data in enumerate(daily_data):
                    daily_forecast = {
                        "day": i + 1,
                        "date": datetime.fromtimestamp(day_data.get('dt', 0)).strftime('%Y-%m-%d'),
                        "sunrise": datetime.fromtimestamp(day_data.get('sunrise', 0)).isoformat() if day_data.get('sunrise') else None,
                        "sunset": datetime.fromtimestamp(day_data.get('sunset', 0)).isoformat() if day_data.get('sunset') else None,
                        "moon_phase": day_data.get('moon_phase', 0),
                        "summary": day_data.get('summary', ''),
                        "temperature": {
                            "min_c": round(day_data.get('temp', {}).get('min', 0), 1),
                            "max_c": round(day_data.get('temp', {}).get('max', 0), 1),
                            "morning_c": round(day_data.get('temp', {}).get('morn', 0), 1),
                            "day_c": round(day_data.get('temp', {}).get('day', 0), 1),
                            "evening_c": round(day_data.get('temp', {}).get('eve', 0), 1),
                            "night_c": round(day_data.get('temp', {}).get('night', 0), 1)
                        },
                        "feels_like": {
                            "morning_c": round(day_data.get('feels_like', {}).get('morn', 0), 1),
                            "day_c": round(day_data.get('feels_like', {}).get('day', 0), 1),
                            "evening_c": round(day_data.get('feels_like', {}).get('eve', 0), 1),
                            "night_c": round(day_data.get('feels_like', {}).get('night', 0), 1)
                        },
                        "weather": {
                            "main": day_data.get('weather', [{}])[0].get('main', ''),
                            "description": day_data.get('weather', [{}])[0].get('description', ''),
                            "icon": day_data.get('weather', [{}])[0].get('icon', '')
                        },
                        "pressure_hpa": day_data.get('pressure', 0),
                        "humidity_percent": day_data.get('humidity', 0),
                        "dew_point_c": round(day_data.get('dew_point', 0), 1),
                        "wind": {
                            "speed_ms": day_data.get('wind_speed', 0),
                            "direction_deg": day_data.get('wind_deg', 0),
                            "gust_ms": day_data.get('wind_gust', 0)
                        },
                        "clouds_percent": day_data.get('clouds', 0),
                        "uv_index": day_data.get('uvi', 0),
                        "precipitation": {
                            "probability": day_data.get('pop', 0),
                            "rain_mm": day_data.get('rain', 0),
                            "snow_mm": day_data.get('snow', 0)
                        }
                    }
                    daily_forecasts.append(daily_forecast)
                
                # Include current weather and some hourly data (next 24 hours)
                current = forecast_data.get('current', {})
                hourly_24h = forecast_data.get('hourly', [])[:24]
                
                result = {
                    "city": city_name,
                    "country": country,
                    "coordinates": {"lat": lat, "lon": lon},
                    "timezone": forecast_data.get('timezone', ''),
                    "current": {
                        "temperature_c": round(current.get('temp', 0), 1),
                        "weather_description": current.get('weather', [{}])[0].get('description', ''),
                        "uv_index": current.get('uvi', 0)
                    },
                    "forecast_days": len(daily_forecasts),
                    "daily_forecast": daily_forecasts,
                    "next_24h_summary": {
                        "hourly_count": len(hourly_24h),
                        "temp_range": {
                            "min_c": round(min([h.get('temp', 0) for h in hourly_24h], default=0), 1),
                            "max_c": round(max([h.get('temp', 0) for h in hourly_24h], default=0), 1)
                        }
                    }
                }
                
                # Include weather alerts if available
                alerts = forecast_data.get('alerts', [])
                if alerts:
                    result["weather_alerts"] = [
                        {
                            "sender": alert.get('sender_name', ''),
                            "event": alert.get('event', ''),
                            "start": datetime.fromtimestamp(alert.get('start', 0)).isoformat(),
                            "end": datetime.fromtimestamp(alert.get('end', 0)).isoformat(),
                            "description": alert.get('description', '')[:200] + "..." if len(alert.get('description', '')) > 200 else alert.get('description', '')
                        }
                        for alert in alerts[:3]  # Limit to first 3 alerts
                    ]
                
                self.logger.info(f"Comprehensive forecast fetched for {city_name} ({len(daily_forecasts)} days)")
                return json.dumps(result)
                
            except Exception as e:
                self.logger.error(f"Error in get_weather_forecast for {city}: {str(e)}")
                return json.dumps({"error": f"Failed to fetch forecast: {str(e)}"})

        @self.mcp.tool()
        def get_weather_by_coordinates(latitude: float, longitude: float) -> str:
            """Get comprehensive current weather by geographic coordinates using One Call API 3.0"""
            try:
                if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
                    return json.dumps({"error": "Invalid coordinates. Latitude and longitude must be numbers."})
                
                if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                    return json.dumps({"error": "Invalid coordinates. Latitude must be -90 to 90, longitude -180 to 180."})
                
                params = {
                    'lat': latitude,
                    'lon': longitude,
                    'units': 'metric',
                    'exclude': 'minutely,hourly,daily,alerts'  # Only current weather
                }
                
                weather_data = self._make_api_request("onecall", params)
                
                if isinstance(weather_data, dict) and "error" in weather_data:
                    return json.dumps(weather_data)
                
                current = weather_data.get('current', {})
                
                result = {
                    "coordinates": {"lat": latitude, "lon": longitude},
                    "timezone": weather_data.get('timezone', ''),
                    "timezone_offset": weather_data.get('timezone_offset', 0),
                    "current": {
                        "datetime": datetime.fromtimestamp(current.get('dt', 0)).isoformat(),
                        "sunrise": datetime.fromtimestamp(current.get('sunrise', 0)).isoformat() if current.get('sunrise') else None,
                        "sunset": datetime.fromtimestamp(current.get('sunset', 0)).isoformat() if current.get('sunset') else None,
                        "temperature_c": round(current.get('temp', 0), 1),
                        "feels_like_c": round(current.get('feels_like', 0), 1),
                        "pressure_hpa": current.get('pressure', 0),
                        "humidity_percent": current.get('humidity', 0),
                        "dew_point_c": round(current.get('dew_point', 0), 1),
                        "uv_index": current.get('uvi', 0),
                        "clouds_percent": current.get('clouds', 0),
                        "visibility_m": current.get('visibility', 0),
                        "wind": {
                            "speed_ms": current.get('wind_speed', 0),
                            "direction_deg": current.get('wind_deg', 0),
                            "gust_ms": current.get('wind_gust', 0)
                        },
                        "weather": {
                            "main": current.get('weather', [{}])[0].get('main', ''),
                            "description": current.get('weather', [{}])[0].get('description', ''),
                            "icon": current.get('weather', [{}])[0].get('icon', '')
                        },
                        "precipitation": {
                            "rain_1h": current.get('rain', {}).get('1h', 0) if current.get('rain') else 0,
                            "snow_1h": current.get('snow', {}).get('1h', 0) if current.get('snow') else 0
                        }
                    }
                }
                
                self.logger.info(f"Weather fetched for coordinates {latitude}, {longitude}")
                return json.dumps(result)
                
            except Exception as e:
                self.logger.error(f"Error in get_weather_by_coordinates: {str(e)}")
                return json.dumps({"error": f"Failed to fetch weather: {str(e)}"})

        @self.mcp.tool()
        def get_weather_overview(city: str, date: str = None) -> str:
            """Get AI-generated weather overview with human-readable summary"""
            try:
                if not city or not isinstance(city, str):
                    self.logger.error(f"Invalid city input: {city}")
                    return json.dumps({"error": "Invalid city name"})
                
                # Get coordinates for the city
                coord_result = self._get_coordinates(city)
                if not coord_result:
                    return json.dumps({"error": f"Could not find coordinates for city: {city}"})
                
                lat, lon, city_name, country = coord_result
                
                # Prepare parameters for weather overview
                params = {
                    'lat': lat,
                    'lon': lon,
                    'units': 'metric'
                }
                
                # Add date if provided (format: YYYY-MM-DD)
                if date:
                    params['date'] = date
                
                overview_data = self._make_api_request("onecall/overview", params)
                
                if isinstance(overview_data, dict) and "error" in overview_data:
                    return json.dumps(overview_data)
                
                result = {
                    "city": city_name,
                    "country": country,
                    "coordinates": {"lat": lat, "lon": lon},
                    "date": overview_data.get('date', ''),
                    "timezone": overview_data.get('tz', ''),
                    "units": overview_data.get('units', 'metric'),
                    "weather_overview": overview_data.get('weather_overview', '')
                }
                
                self.logger.info(f"Weather overview fetched for {city_name}")
                return json.dumps(result)
                
            except Exception as e:
                self.logger.error(f"Error in get_weather_overview for {city}: {str(e)}")
                return json.dumps({"error": f"Failed to fetch weather overview: {str(e)}"})

        @self.mcp.tool()
        def get_weather(city: str) -> str:
            """Get current weather for a city (works with basic OpenWeatherMap API)"""
            try:
                if not city or not isinstance(city, str):
                    self.logger.error(f"Invalid city input: {city}")
                    return json.dumps({"error": "Invalid city name"})
                
                # Try One Call API first
                if self.use_one_call_api:
                    return self.get_current_weather(city)
                
                # Fall back to basic weather API
                params = {
                    'q': city,
                    'units': 'metric'
                }
                
                weather_data = self._make_api_request("weather", params, use_v3=False)
                
                if isinstance(weather_data, dict) and "error" in weather_data:
                    return json.dumps(weather_data)
                
                # Extract basic weather information
                result = {
                    "city": weather_data.get('name', city),
                    "country": weather_data.get('sys', {}).get('country', ''),
                    "weather": {
                        "main": weather_data.get('weather', [{}])[0].get('main', ''),
                        "description": weather_data.get('weather', [{}])[0].get('description', ''),
                        "icon": weather_data.get('weather', [{}])[0].get('icon', '')
                    },
                    "temperature_c": round(weather_data.get('main', {}).get('temp', 0), 1),
                    "feels_like_c": round(weather_data.get('main', {}).get('feels_like', 0), 1),
                    "pressure_hpa": weather_data.get('main', {}).get('pressure', 0),
                    "humidity_percent": weather_data.get('main', {}).get('humidity', 0),
                    "wind": {
                        "speed_ms": weather_data.get('wind', {}).get('speed', 0),
                        "direction_deg": weather_data.get('wind', {}).get('deg', 0)
                    },
                    "clouds_percent": weather_data.get('clouds', {}).get('all', 0),
                    "visibility_m": weather_data.get('visibility', 0),
                    "timestamp": datetime.fromtimestamp(weather_data.get('dt', 0)).isoformat()
                }
                
                self.logger.info(f"Weather fetched for {city}: {result['weather']['description']}, {result['temperature_c']}°C")
                return json.dumps(result)
                
            except Exception as e:
                self.logger.error(f"Error in get_weather for {city}: {str(e)}")
                return json.dumps({"error": f"Failed to fetch weather: {str(e)}"})

def main():
    """Main function to run the weather server."""
    server = WeatherServer()
    server.run()

if __name__ == "__main__":
    main()
