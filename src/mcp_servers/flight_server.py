"""
Flight MCP server implementation.
"""
import random
import json
from mcp_servers.base_server import BaseMCPServer
from utils.config import config

class FlightServer(BaseMCPServer):
    """Flight booking and search MCP server."""
    
    def __init__(self):
        super().__init__(
            name="Flight Server",
            port=config.FLIGHT_SERVER_PORT,
            description="Provides flight search and booking services"
        )
    
    def register_tools(self):
        """Register flight-related tools."""
        
        @self.mcp.tool()
        def book_flight(origin: str, destination: str, date: str) -> str:
            """Book a flight from origin to destination on the given date"""
            try:
                # Mock flight booking
                result = {
                    "status": "success",
                    "message": f"Flight booked from {origin} to {destination} on {date}",
                    "price_usd": random.randint(400, 800),
                    "flight_number": f"FL{random.randint(1000, 9999)}",
                    "departure_time": "08:30",
                    "arrival_time": "14:45",
                    "airline": random.choice(["United Airlines", "Delta", "American Airlines", "Lufthansa"])
                }
                self.logger.info(f"Flight booked: {result}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error booking flight: {str(e)}")
                return json.dumps({"error": f"Failed to book flight: {str(e)}"})

        @self.mcp.tool()
        def search_flights(origin: str, destination: str, date: str) -> str:
            """Search for flights from origin to destination on the given date"""
            try:
                # Mock flight search with multiple options
                airlines = ["United Airlines", "Delta", "American Airlines", "Lufthansa", "Southwest"]
                flights = []
                
                for i in range(random.randint(3, 6)):
                    flight = {
                        "flight_number": f"FL{random.randint(1000, 9999)}",
                        "airline": random.choice(airlines),
                        "price_usd": random.randint(350, 900),
                        "departure_time": f"{random.randint(6, 23):02d}:{random.choice(['00', '15', '30', '45'])}",
                        "arrival_time": f"{random.randint(8, 23):02d}:{random.choice(['00', '15', '30', '45'])}",
                        "duration": f"{random.randint(2, 12)}h {random.randint(0, 59)}m",
                        "stops": random.randint(0, 2)
                    }
                    flights.append(flight)
                
                result = {
                    "origin": origin,
                    "destination": destination,
                    "date": date,
                    "flights": sorted(flights, key=lambda x: x["price_usd"])
                }
                
                self.logger.info(f"Flight search completed: {origin} to {destination} on {date}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error searching flights: {str(e)}")
                return json.dumps({"error": f"Failed to search flights: {str(e)}"})

def main():
    """Main function to run the flight server."""
    server = FlightServer()
    server.run()

if __name__ == "__main__":
    main()
