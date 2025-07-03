"""
Activity MCP server implementation.
"""
import random
import json
from mcp_servers.base_server import BaseMCPServer
from utils.config import config

class ActivityServer(BaseMCPServer):
    """Activity and attraction MCP server."""
    
    def __init__(self):
        super().__init__(
            name="Activity Server",
            port=config.ACTIVITY_SERVER_PORT,
            description="Provides activity recommendations and booking services"
        )
    
    def register_tools(self):
        """Register activity-related tools."""
        
        @self.mcp.tool()
        def recommend_activities(city: str, category: str) -> str:
            """Recommend activities in a city based on category"""
            try:
                activities_by_category = {
                    "general": [
                        "City Walking Tour", "Museum Visit", "Local Food Tour",
                        "Historic Sites Tour", "Shopping District", "Central Park"
                    ],
                    "culture": [
                        "Art Museum", "History Museum", "Theater Show",
                        "Cultural Center", "Local Music Venue", "Heritage Site"
                    ],
                    "adventure": [
                        "Hiking Trail", "Bike Tour", "Water Sports",
                        "Rock Climbing", "Zip Line", "Adventure Park"
                    ],
                    "food": [
                        "Cooking Class", "Food Market Tour", "Wine Tasting",
                        "Local Restaurant Tour", "Street Food Walk", "Brewery Tour"
                    ],
                    "family": [
                        "Zoo", "Aquarium", "Amusement Park",
                        "Children's Museum", "Park Playground", "Family Beach"
                    ]
                }
                
                base_activities = activities_by_category.get(category.lower(), activities_by_category["general"])
                
                activities = []
                for i in range(random.randint(4, 8)):
                    activity = {
                        "name": random.choice(base_activities),
                        "description": f"Experience the best of {city} with this amazing activity",
                        "duration_hours": random.randint(1, 8),
                        "price_usd": random.randint(20, 150),
                        "rating": round(random.uniform(3.5, 5.0), 1),
                        "difficulty": random.choice(["Easy", "Moderate", "Challenging"]),
                        "age_requirement": random.choice(["All Ages", "12+", "18+"])
                    }
                    activities.append(activity)
                
                result = {
                    "city": city,
                    "category": category,
                    "activities": sorted(activities, key=lambda x: x["rating"], reverse=True)
                }
                
                self.logger.info(f"Activity recommendations generated for {city} - {category}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error recommending activities: {str(e)}")
                return json.dumps({"error": f"Failed to recommend activities: {str(e)}"})

        @self.mcp.tool()
        def book_activity(city: str, activity_name: str, date: str, participants: int = 1) -> str:
            """Book an activity in the specified city"""
            try:
                result = {
                    "status": "success",
                    "message": f"Activity '{activity_name}' booked in {city} for {date}",
                    "activity_name": activity_name,
                    "city": city,
                    "date": date,
                    "participants": participants,
                    "total_price_usd": random.randint(50, 300) * participants,
                    "booking_reference": f"ACT{random.randint(100000, 999999)}",
                    "meeting_point": f"{random.choice(['City Center', 'Hotel Lobby', 'Main Square', 'Tourist Information'])}",
                    "meeting_time": f"{random.randint(8, 16):02d}:{random.choice(['00', '30'])}",
                    "duration_hours": random.randint(2, 6),
                    "contact_phone": f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                }
                
                self.logger.info(f"Activity booked: {result}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error booking activity: {str(e)}")
                return json.dumps({"error": f"Failed to book activity: {str(e)}"})

        @self.mcp.tool()
        def get_activity_categories(city: str) -> str:
            """Get available activity categories for a city"""
            try:
                categories = [
                    {
                        "name": "General",
                        "description": "Popular attractions and general sightseeing",
                        "activity_count": random.randint(15, 25)
                    },
                    {
                        "name": "Culture",
                        "description": "Museums, theaters, and cultural experiences",
                        "activity_count": random.randint(8, 15)
                    },
                    {
                        "name": "Adventure",
                        "description": "Outdoor activities and adventure sports",
                        "activity_count": random.randint(10, 20)
                    },
                    {
                        "name": "Food",
                        "description": "Culinary experiences and food tours",
                        "activity_count": random.randint(12, 18)
                    },
                    {
                        "name": "Family",
                        "description": "Family-friendly activities and attractions",
                        "activity_count": random.randint(10, 16)
                    }
                ]
                
                result = {
                    "city": city,
                    "categories": categories
                }
                
                self.logger.info(f"Activity categories retrieved for {city}")
                return json.dumps(result)
            except Exception as e:
                self.logger.error(f"Error getting activity categories: {str(e)}")
                return json.dumps({"error": f"Failed to get activity categories: {str(e)}"})

def main():
    """Main function to run the activity server."""
    server = ActivityServer()
    server.run()

if __name__ == "__main__":
    main()
