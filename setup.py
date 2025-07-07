#!/usr/bin/env python3
"""
Setup script for Multi-Agent Travel Planning System
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"🔄 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_virtual_environment():
    """Create and setup virtual environment"""
    venv_path = Path("myenv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "myenv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install Python dependencies"""
    pip_cmd = "./myenv/bin/pip" if os.name != 'nt' else ".\\myenv\\Scripts\\pip.exe"
    
    return run_command(
        f"{pip_cmd} install -r requirements.txt",
        "Installing dependencies"
    )

def create_env_file():
    """Create .env file template"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    env_template = """# Multi-Agent Travel Planning System Configuration

# Required: Google API Key for Gemini AI
# Get your key from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your-google-api-key-here

# Required: OpenWeatherMap API Key for Weather Service
# Get your free API key from: https://openweathermap.org/api
# Free tier: 1,000 calls/day, current weather + 5-day forecast
OPENWEATHER_API_KEY=your-openweathermap-api-key-here

# Optional: Application Configuration
FLASK_ENV=development
LOG_LEVEL=INFO

# Optional: MCP Server Ports (defaults shown)
WEATHER_SERVER_PORT=8000
FLIGHT_SERVER_PORT=8001
HOTEL_SERVER_PORT=8002
ACTIVITY_SERVER_PORT=8003
WEB_APP_PORT=5000
"""
    
    try:
        env_file.write_text(env_template)
        print("✅ .env file template created")
        print("⚠️  Please edit .env and add your API keys:")
        print("   - Google API key for Gemini AI")
        print("   - OpenWeatherMap API key for weather data")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_logs_directory():
    """Create logs directory"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ Logs directory created")
    else:
        print("✅ Logs directory already exists")
    return True

def make_scripts_executable():
    """Make shell scripts executable"""
    scripts = ["start_system.sh", "stop_services.sh"]
    
    for script in scripts:
        if Path(script).exists():
            try:
                os.chmod(script, 0o755)
                print(f"✅ Made {script} executable")
            except Exception as e:
                print(f"⚠️  Could not make {script} executable: {e}")

def run_tests():
    """Run the test suite to verify installation"""
    python_cmd = "./myenv/bin/python" if os.name != 'nt' else ".\\myenv\\Scripts\\python.exe"
    
    return run_command(
        f'PYTHONPATH="./src" {python_cmd} -m pytest tests/ -v --tb=short',
        "Running test suite"
    )

def main():
    """Main setup function"""
    print("🚀 Multi-Agent Travel Planning System Setup")
    print("=" * 50)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating environment file", create_env_file),
        ("Creating logs directory", create_logs_directory),
        ("Making scripts executable", make_scripts_executable),
    ]
    
    for description, func in steps:
        if not func():
            print(f"\n❌ Setup failed at: {description}")
            return 1
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Google API key")
    print("2. Run: ./start_system.sh")
    print("3. Visit: http://localhost:5000")
    
    # Optionally run tests
    print("\n🧪 Running tests to verify installation...")
    if run_tests():
        print("\n✅ All tests passed! System is ready to use.")
    else:
        print("\n⚠️  Some tests failed, but setup is complete.")
        print("   You can still start the system and troubleshoot later.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
