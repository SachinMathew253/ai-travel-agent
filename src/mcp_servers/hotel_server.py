"""
Hotel MCP server implementation.
"""
import random
import json
from mcp_servers.base_server import BaseMCPServer
from utils.config import config

class HotelServer(BaseMCPServer):
    """Hotel booking and search MCP server."""
    
    def __init__(self):
        super().__init__(
            name="Hotel Server",
            port=config.HOTEL_SERVER_PORT,
            description="Provides hotel search and booking services"
        )
    
    def register_tools(self):
        """Register hotel-related tools."""
        
        @self.mcp.tool()
        def book_hotel(city: str, checkin: str, checkout: str) -> str:
            """Book a hotel in the specified city"""
            try:
                hotel_names = [
                    "Grand Luxury Hotel", "City Center Inn", "Cozy Boutique Hotel",
                    "Business Plaza Hotel", "Riverside Resort", "Historic Manor"
                ]
                
                result = {
                    "status": "success",
                    "message": f"Hotel booked in {city} from {checkin} to {checkout}",
                    "hotel_name": random.choice(hotel_names),
                    "price_per_night_usd": random.randint(80, 400),
                    "rating": round(random.uniform(3.5, 5.0), 1),
                    "confirmation_number": f"HB{random.randint(100000, 999999)}",
                    "amenities": random.sample([
                        "Free WiFi", "Pool", "Gym", "Spa", "Restaurant", 
                        "Room Service", "Business Center", "Parking"
                    ], k=random.randint(3, 6))
                }
                
                self.logger.info(f"Hotel booked: {result}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error booking hotel: {str(e)}")
                return json.dumps({"error": f"Failed to book hotel: {str(e)}"})

        @self.mcp.tool()
        def search_hotels(city: str) -> str:
            """Search for hotels in the specified city"""
            try:
                hotel_names = [
                    "Grand Luxury Hotel", "City Center Inn", "Cozy Boutique Hotel",
                    "Business Plaza Hotel", "Riverside Resort", "Historic Manor",
                    "Modern Suites", "Boutique Palace", "Economy Lodge"
                ]
                
                hotels = []
                for i in range(random.randint(4, 8)):
                    hotel = {
                        "name": random.choice(hotel_names),
                        "price_per_night_usd": random.randint(60, 500),
                        "rating": round(random.uniform(3.0, 5.0), 1),
                        "amenities": random.sample([
                            "Free WiFi", "Pool", "Gym", "Spa", "Restaurant", 
                            "Room Service", "Business Center", "Parking", "Pet Friendly"
                        ], k=random.randint(2, 7)),
                        "distance_from_center_km": round(random.uniform(0.5, 15.0), 1)
                    }
                    hotels.append(hotel)
                
                result = {
                    "city": city,
                    "hotels": sorted(hotels, key=lambda x: x["rating"], reverse=True)
                }
                
                self.logger.info(f"Hotel search completed for {city}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error searching hotels: {str(e)}")
                return json.dumps({"error": f"Failed to search hotels: {str(e)}"})

        @self.mcp.tool()
        def get_hotel_details(hotel_name: str, city: str) -> str:
            """Get detailed information about a specific hotel"""
            try:
                result = {
                    "hotel_name": hotel_name,
                    "city": city,
                    "rating": round(random.uniform(3.5, 5.0), 1),
                    "price_range_usd": f"{random.randint(80, 200)}-{random.randint(300, 600)}",
                    "amenities": [
                        "Free WiFi", "Pool", "Fitness Center", "Restaurant",
                        "Room Service", "Concierge", "Business Center"
                    ],
                    "room_types": [
                        "Standard Room", "Deluxe Room", "Suite", "Executive Suite"
                    ],
                    "check_in_time": "15:00",
                    "check_out_time": "11:00",
                    "cancellation_policy": "Free cancellation up to 24 hours before check-in",
                    "contact": {
                        "phone": f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                        "email": f"reservations@{hotel_name.lower().replace(' ', '')}.com"
                    }
                }
                
                self.logger.info(f"Hotel details retrieved for {hotel_name} in {city}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error getting hotel details: {str(e)}")
                return json.dumps({"error": f"Failed to get hotel details: {str(e)}"})

def main():
    """Main function to run the hotel server."""
    server = HotelServer()
    server.run()

if __name__ == "__main__":
    main()
