"""
Web interface for the travel planning system.
"""
import asyncio
from flask import Flask, render_template, request, jsonify
from core.system import TravelPlanningSystem
from utils.config import config
from utils.logging import setup_logging

logger = setup_logging(__name__)

# Create Flask app
app = Flask(__name__, template_folder='templates')
app.secret_key = 'your-secret-key-change-in-production'

# Global travel system instance
travel_system = None

def create_app():
    """Create and configure the Flask application."""
    global travel_system
    
    # Initialize the travel system at app creation time
    try:
        travel_system = TravelPlanningSystem()
        logger.info("Travel planning system initialized for web interface")
    except Exception as e:
        logger.error(f"Failed to initialize travel system: {e}")
        travel_system = None

    @app.route('/')
    def index():
        """Main page with travel planning form."""
        return render_template('index.html')

    @app.route('/about')
    def about():
        """About page with system information."""
        system_status = travel_system.get_system_status() if travel_system else {"status": "not_initialized"}
        return render_template('about.html', system_status=system_status)

    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        if travel_system:
            status = travel_system.get_system_status()
            return jsonify(status)
        else:
            return jsonify({"status": "system_not_initialized"}), 503

    @app.route('/api/plan', methods=['POST'])
    def plan_trip():
        """API endpoint for travel planning."""
        try:
            if not travel_system:
                return jsonify({"error": "Travel system not initialized"}), 503
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            workflow = data.get('workflow', 'coordinated')
            
            if workflow == 'coordinated':
                query = data.get('query', '')
                if not query:
                    return jsonify({"error": "Query is required for coordinated workflow"}), 400
                
                # Use asyncio.run() for cleaner async execution from sync code
                result = asyncio.run(travel_system.plan_trip_coordinated(query))
                
                return jsonify(result)
            
            elif workflow in ['sequential', 'parallel']:
                travel_request = {
                    'origin': data.get('origin', ''),
                    'destination': data.get('destination', ''),
                    'departure_date': data.get('departure_date', ''),
                    'return_date': data.get('return_date', ''),
                    'travelers': data.get('travelers', 1),
                    'budget': data.get('budget', 'moderate'),
                    'interests': data.get('interests', [])
                }
                
                # Use asyncio.run() for cleaner async execution from sync code
                if workflow == 'sequential':
                    result = asyncio.run(travel_system.plan_trip_sequential(travel_request))
                else: # parallel
                    result = asyncio.run(travel_system.plan_trip_parallel(travel_request))
                
                return jsonify(result)
            
            else:
                return jsonify({"error": f"Unknown workflow: {workflow}"}), 400
                
        except Exception as e:
            logger.error(f"Error in travel planning API: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/plan', methods=['POST'])
    def plan_trip_form():
        """Handle form submission from the web interface."""
        try:
            if not travel_system:
                return render_template('error.html', error="Travel system not initialized")
            
            # Get form data
            query = request.form.get('query', '').strip()
            origin = request.form.get('origin', '').strip()
            destination = request.form.get('destination', '').strip()
            departure_date = request.form.get('departure_date', '').strip()
            travelers = request.form.get('travelers', '1')
            budget = request.form.get('budget', 'moderate')
            
            # Build query if not provided directly
            if not query and origin and destination:
                query = f"Plan a trip from {origin} to {destination}"
                if departure_date:
                    query += f" departing {departure_date}"
                if travelers != '1':
                    query += f" for {travelers} travelers"
                query += f" with a {budget} budget."
            
            if not query:
                return render_template('error.html', error="Please provide either a query or complete trip details")
            
            # Use asyncio.run() for cleaner async execution from sync code
            result = asyncio.run(travel_system.plan_trip_coordinated(query))
            
            if result['status'] == 'success':
                return render_template('result.html', result=result['result'], query=query)
            else:
                return render_template('error.html', error=result.get('error', 'Unknown error'))
                
        except Exception as e:
            logger.error(f"Error in form-based travel planning: {e}")
            return render_template('error.html', error=str(e))

    return app

def run_web_server():
    """Run the web server."""
    try:
        logger.info("Starting Travel Planning Web Interface...")
        
        # Validate configuration
        config_status = config.validate()
        if not config_status["valid"]:
            logger.warning("Configuration issues detected:")
            for issue in config_status["issues"]:
                logger.warning(f"  - {issue}")
        
        # Initialize travel system
        global travel_system
        travel_system = TravelPlanningSystem()
        
        logger.info("📋 Available endpoints:")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/ - Main interface")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/api/plan - API endpoint")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/about - About page")
        logger.info(f"   • http://localhost:{config.WEB_UI_PORT}/api/health - Health check")
        
        app = create_app()
        app.run(
            host='0.0.0.0',
            port=config.WEB_UI_PORT,
            debug=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        raise

if __name__ == "__main__":
    run_web_server()
