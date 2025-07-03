"""
Tests for the web interface.
"""
import pytest
from unittest.mock import Mock, patch
from web.app import create_app
from utils.config import config

class TestWebInterface:
    """Test cases for the web interface."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        with patch('src.web.app.travel_system') as mock_system:
            mock_system.get_system_status.return_value = {
                'system': 'Travel Planning System',
                'status': 'operational'
            }
            app = create_app()
            app.config['TESTING'] = True
            return app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()
    
    def test_index_page(self, client):
        """Test the main index page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Travel Planning' in response.data
    
    def test_about_page(self, client):
        """Test the about page."""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_health_check_endpoint(self, client):
        """Test the health check API endpoint."""
        with patch('src.web.app.travel_system') as mock_system:
            mock_system.get_system_status.return_value = {
                'status': 'operational'
            }
            response = client.get('/api/health')
            assert response.status_code == 200
            assert response.json['status'] == 'operational'
    
    def test_plan_api_endpoint_coordinated(self, client):
        """Test the planning API endpoint with coordinated workflow."""
        with patch('src.web.app.travel_system') as mock_system:
            mock_system.plan_trip_coordinated.return_value = {
                'status': 'success',
                'result': 'Mock travel plan'
            }
            
            response = client.post('/api/plan', 
                                 json={'workflow': 'coordinated', 'query': 'Test query'})
            assert response.status_code == 200
    
    def test_plan_api_endpoint_missing_data(self, client):
        """Test the planning API endpoint with missing data."""
        response = client.post('/api/plan', json={})
        assert response.status_code == 400

class TestWebConfiguration:
    """Test web interface configuration."""
    
    def test_default_port_configuration(self):
        """Test that the default port is correctly configured."""
        assert config.WEB_UI_PORT == 8080
    
    def test_template_directory_exists(self):
        """Test that template directory exists."""
        import os
        template_dir = os.path.join(os.path.dirname(__file__), '../src/web/templates')
        assert os.path.exists(template_dir)

if __name__ == "__main__":
    pytest.main([__file__])
