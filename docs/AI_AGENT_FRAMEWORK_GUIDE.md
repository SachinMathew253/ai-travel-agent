# AI Agent Framework: Complete Guide for Building Intelligent Systems

## Table of Contents
1. [Introduction](#introduction)
2. [High-Level Design Architecture](#high-level-design-architecture)
3. [Core Components](#core-components)
4. [Model Context Protocol (MCP) Integration](#model-context-protocol-mcp-integration)
5. [Agent Design Patterns](#agent-design-patterns)
6. [Tooling and Development](#tooling-and-development)
7. [Security Measures](#security-measures)
8. [Testing Framework](#testing-framework)
9. [Deployment and Operations](#deployment-and-operations)
10. [Best Practices](#best-practices)
11. [Extension Points](#extension-points)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

This framework provides a comprehensive foundation for building production-ready AI agent systems. Based on the travel planning agent reference implementation, it demonstrates scalable, modular architecture patterns that can be adapted for various domains.

### Key Features
- **Modular Agent Architecture**: Specialized agents for different domains
- **MCP Integration**: Standardized tool interface protocol
- **Event-Driven System**: Asynchronous communication patterns
- **Configuration Management**: Environment-based configuration
- **Comprehensive Testing**: Unit, integration, and end-to-end testing
- **Production Ready**: Logging, monitoring, and deployment patterns

---

## High-Level Design Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Web UI  │  REST API  │  CLI Interface  │  Direct Integration   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Agent Orchestration Layer                     │
├─────────────────────────────────────────────────────────────────┤
│           Coordinator Agent (Main Orchestrator)                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │ Weather     │ │ Flight      │ │ Hotel       │ │ Activity  │  │
│  │ Agent       │ │ Agent       │ │ Agent       │ │ Agent     │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Tool Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │ Weather     │ │ Flight      │ │ Hotel       │ │ Activity  │  │
│  │ MCP Server  │ │ MCP Server  │ │ MCP Server  │ │ MCP Server│  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   External Services Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  APIs  │  Databases  │  File Systems  │  Third-party Services   │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Separation of Concerns**: Each agent has a specific domain responsibility
2. **Loose Coupling**: Agents communicate through standardized MCP interfaces
3. **High Cohesion**: Related functionalities are grouped within agents
4. **Scalability**: Components can be scaled independently
5. **Testability**: Each layer can be tested in isolation
6. **Configurability**: Runtime behavior controlled through configuration

---

## Core Components

### 1. Agent Factory Pattern

The `AgentFactory` provides a centralized way to create and configure agents:

```python
class AgentFactory:
    """Factory for creating domain-specific agents."""
    
    @staticmethod
    def create_specialized_agent(domain: str, config: AgentConfig) -> LlmAgent:
        """Create an agent for a specific domain."""
        # Tool configuration
        tool_params = StreamableHTTPServerParams(url=config.tool_server_url)
        toolset = MCPToolset(connection_params=tool_params)
        
        return LlmAgent(
            name=f"{domain}_agent",
            instruction=config.instruction_prompt,
            tools=[toolset],
            model=config.llm_model,
            generate_content_config=config.generation_config
        )
```

### 2. System Orchestrator

The main system class that coordinates all components:

```python
class AgentSystem:
    """Main system orchestrator."""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.session_service = InMemorySessionService()
        self.agents = self._create_agents()
        self.runner = self._create_runner()
    
    def _create_agents(self) -> Dict[str, LlmAgent]:
        """Create all system agents."""
        pass
    
    def _create_runner(self) -> Runner:
        """Create the main system runner."""
        pass
```

### 3. Configuration Management

Centralized configuration with validation:

```python
class Config:
    """System configuration with validation."""
    
    def __init__(self):
        self.load_from_environment()
    
    def validate(self) -> ConfigValidationResult:
        """Validate all configuration parameters."""
        pass
    
    def load_from_environment(self):
        """Load configuration from environment variables."""
        pass
```

### 4. Logging Infrastructure

Structured logging with multiple outputs:

```python
def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """Configure structured logging for the system."""
    logger = logging.getLogger(name)
    
    # Configure formatters, handlers, and levels
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logger
```

---

## Model Context Protocol (MCP) Integration

### MCP Server Architecture

MCP servers provide standardized interfaces for external tools and services:

```python
class BaseMCPServer:
    """Base class for all MCP servers."""
    
    def __init__(self, name: str, port: int, description: str):
        self.name = name
        self.port = port
        self.mcp = FastMCP(name)
        self.logger = setup_logging(f"MCP.{name}")
    
    def register_tools(self):
        """Override to register domain-specific tools."""
        raise NotImplementedError
    
    def run(self):
        """Start the MCP server."""
        self.register_tools()
        self.mcp.run(port=self.port, transport="streamable-http")
```

### Creating Custom MCP Tools

#### Step 1: Define Tool Schema

```python
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    location: str
    date_range: Optional[str] = None
    
class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_count: int
    status: str
```

#### Step 2: Implement Tool Logic

```python
class CustomMCPServer(BaseMCPServer):
    
    def register_tools(self):
        @self.mcp.tool()
        def search_data(request: SearchRequest) -> SearchResponse:
            """Search for data based on criteria."""
            try:
                # Implement your search logic
                results = self._perform_search(request)
                return SearchResponse(
                    results=results,
                    total_count=len(results),
                    status="success"
                )
            except Exception as e:
                self.logger.error(f"Search failed: {e}")
                return SearchResponse(
                    results=[],
                    total_count=0,
                    status="error"
                )
    
    def _perform_search(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Implement the actual search logic."""
        pass
```

#### Step 3: Tool Registration

```python
def create_custom_toolset(server_url: str) -> MCPToolset:
    """Create a toolset for the custom MCP server."""
    params = StreamableHTTPServerParams(url=server_url)
    return MCPToolset(connection_params=params)
```

### MCP Best Practices

1. **Error Handling**: Always return structured error responses
2. **Validation**: Use Pydantic models for request/response validation
3. **Logging**: Log all tool calls and their results
4. **Timeout Management**: Implement reasonable timeouts for external calls
5. **Resource Management**: Properly manage connections and resources

---

## Agent Design Patterns

### 1. Specialist Agent Pattern

Each agent focuses on a single domain:

```python
class SpecialistAgent:
    """Pattern for domain-specific agents."""
    
    def __init__(self, domain: str, tools: List[MCPToolset]):
        self.domain = domain
        self.tools = tools
        self.instruction = self._create_instruction()
    
    def _create_instruction(self) -> str:
        """Create domain-specific instructions."""
        return f"""
        You are a {self.domain} specialist agent.
        Your responsibilities:
        1. Handle all {self.domain}-related queries
        2. Use available tools to gather information
        3. Provide accurate, helpful responses
        4. Escalate complex issues when necessary
        """
```

### 2. Coordinator Agent Pattern

Orchestrates multiple specialist agents:

```python
class CoordinatorAgent:
    """Pattern for orchestrating multiple agents."""
    
    def __init__(self, specialist_agents: Dict[str, LlmAgent]):
        self.specialists = specialist_agents
        self.all_tools = self._aggregate_tools()
        self.instruction = self._create_coordinator_instruction()
    
    def _create_coordinator_instruction(self) -> str:
        """Create coordinator-specific instructions."""
        return """
        You are a coordinator agent with access to multiple specialized tools.
        Your responsibilities:
        1. Analyze user requests to determine required tools
        2. Make appropriate tool calls immediately
        3. Synthesize results from multiple tools
        4. Provide comprehensive responses
        """
```

### 3. Pipeline Agent Pattern

For sequential processing workflows:

```python
class PipelineAgent:
    """Pattern for sequential processing workflows."""
    
    def __init__(self, stages: List[ProcessingStage]):
        self.stages = stages
    
    async def process(self, input_data: Any) -> Any:
        """Process data through the pipeline."""
        current_data = input_data
        for stage in self.stages:
            current_data = await stage.process(current_data)
        return current_data
```

---

## Tooling and Development

### Development Environment Setup

#### 1. Virtual Environment

```bash
# Create virtual environment
python -m venv agent_env
source agent_env/bin/activate  # On macOS/Linux
# or agent_env\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Environment Configuration

Create `.env` file:

```env
# API Keys
GOOGLE_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here

# Server Ports
WEATHER_SERVER_PORT=8000
FLIGHT_SERVER_PORT=8001
HOTEL_SERVER_PORT=8002
ACTIVITY_SERVER_PORT=8003
WEB_UI_PORT=8080

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
```

#### 3. Project Structure

```
project_root/
├── src/
│   ├── core/
│   │   ├── agents.py      # Agent definitions
│   │   ├── system.py      # System orchestrator
│   │   └── __init__.py
│   ├── mcp_servers/
│   │   ├── base_server.py # Base MCP server
│   │   ├── custom_server.py
│   │   └── __init__.py
│   ├── utils/
│   │   ├── config.py      # Configuration management
│   │   ├── logging.py     # Logging setup
│   │   └── __init__.py
│   └── web/
│       ├── app.py         # Web interface
│       └── templates/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
├── requirements.txt
├── setup.py
└── README.md
```

### Development Tools

#### 1. Code Quality

```bash
# Install development tools
pip install black isort flake8 mypy pytest

# Format code
black src/
isort src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

#### 2. Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

#### 3. Documentation

```bash
# Generate documentation
sphinx-build -b html docs/ docs/_build/

# Live reload documentation
sphinx-autobuild docs/ docs/_build/
```

---

## Security Measures

### 1. API Key Management

```python
class SecureConfig:
    """Secure configuration management."""
    
    def __init__(self):
        self.api_keys = self._load_secure_keys()
    
    def _load_secure_keys(self) -> Dict[str, str]:
        """Load API keys from secure storage."""
        # Use environment variables or secure vaults
        return {
            "google_api": os.getenv("GOOGLE_API_KEY"),
            "openai_api": os.getenv("OPENAI_API_KEY")
        }
    
    def validate_keys(self) -> bool:
        """Validate all required API keys are present."""
        required_keys = ["google_api", "openai_api"]
        return all(self.api_keys.get(key) for key in required_keys)
```

### 2. Input Validation

```python
from pydantic import BaseModel, validator

class UserRequest(BaseModel):
    """Validated user request model."""
    
    query: str
    user_id: str
    session_id: str
    
    @validator('query')
    def validate_query(cls, v):
        if len(v) > 1000:
            raise ValueError('Query too long')
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.isalnum():
            raise ValueError('Invalid user ID format')
        return v
```

### 3. Rate Limiting

```python
from functools import wraps
import time

class RateLimiter:
    """Rate limiting for API calls."""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = {}
    
    def limit(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            current_time = time.time()
            
            if self._is_rate_limited(user_id, current_time):
                raise RateLimitExceeded("Rate limit exceeded")
            
            return func(*args, **kwargs)
        return wrapper
```

### 4. Data Privacy

```python
class DataPrivacy:
    """Data privacy and PII protection."""
    
    @staticmethod
    def sanitize_logs(log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII from log data."""
        sensitive_fields = ['email', 'phone', 'ssn', 'credit_card']
        
        for field in sensitive_fields:
            if field in log_data:
                log_data[field] = '[REDACTED]'
        
        return log_data
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """Encrypt sensitive data."""
        # Implement encryption logic
        pass
```

### 5. Authentication and Authorization

```python
class AuthManager:
    """Authentication and authorization management."""
    
    def authenticate_user(self, token: str) -> Optional[User]:
        """Authenticate user from token."""
        try:
            # Validate JWT token
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return User.from_token_payload(payload)
        except jwt.InvalidTokenError:
            return None
    
    def authorize_action(self, user: User, action: str, resource: str) -> bool:
        """Check if user is authorized for action."""
        return user.has_permission(action, resource)
```

---

## Testing Framework

### 1. Test Structure

```python
# tests/conftest.py
import pytest
from src.core.system import AgentSystem
from src.utils.config import Config

@pytest.fixture
def test_config():
    """Test configuration fixture."""
    config = Config()
    config.GOOGLE_API_KEY = "test_key"
    return config

@pytest.fixture
def agent_system(test_config):
    """Agent system fixture."""
    return AgentSystem(test_config)
```

### 2. Unit Tests

```python
# tests/unit/test_agents.py
import pytest
from src.core.agents import AgentFactory

class TestAgentFactory:
    """Test agent factory functionality."""
    
    def test_create_weather_agent(self, test_config):
        """Test weather agent creation."""
        agent = AgentFactory.create_weather_agent()
        assert agent.name == "weather_agent"
        assert len(agent.tools) == 1
    
    def test_agent_instruction_format(self, test_config):
        """Test agent instruction format."""
        agent = AgentFactory.create_weather_agent()
        assert "weather specialist" in agent.instruction.lower()
```

### 3. Integration Tests

```python
# tests/integration/test_full_workflow.py
import pytest
from src.core.system import AgentSystem

class TestFullWorkflow:
    """Test complete system workflows."""
    
    @pytest.mark.asyncio
    async def test_travel_planning_workflow(self, agent_system):
        """Test complete travel planning workflow."""
        query = "Plan a trip to Paris for 3 days"
        
        response = await agent_system.process_query(query)
        
        assert response.status == "success"
        assert "paris" in response.content.lower()
        assert len(response.tool_calls) > 0
```

### 4. MCP Server Tests

```python
# tests/unit/test_mcp_servers.py
import pytest
from src.mcp_servers.weather_server import WeatherServer

class TestWeatherServer:
    """Test weather MCP server."""
    
    @pytest.fixture
    def weather_server(self):
        return WeatherServer("test_weather", 8000, "Test weather server")
    
    def test_get_weather_tool(self, weather_server):
        """Test weather tool registration."""
        weather_server.register_tools()
        
        # Test tool availability
        tools = weather_server.mcp.get_tools()
        tool_names = [tool.name for tool in tools]
        assert "get_weather" in tool_names
```

### 5. Performance Tests

```python
# tests/performance/test_response_times.py
import pytest
import time
from src.core.system import AgentSystem

class TestPerformance:
    """Test system performance."""
    
    def test_response_time_under_threshold(self, agent_system):
        """Test response time is under acceptable threshold."""
        start_time = time.time()
        
        response = agent_system.process_simple_query("What's the weather?")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response_time < 5.0  # 5 second threshold
```

---

## Deployment and Operations

### 1. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY templates/ templates/

EXPOSE 8080

CMD ["python", "-m", "src.web.app"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  agent-system:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - LOG_LEVEL=INFO
    depends_on:
      - weather-server
      - flight-server
  
  weather-server:
    build: .
    command: python run_weather_server.py
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
  
  flight-server:
    build: .
    command: python run_flight_server.py
    ports:
      - "8001:8001"
    environment:
      - LOG_LEVEL=INFO
```

### 3. Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-system
  template:
    metadata:
      labels:
        app: agent-system
    spec:
      containers:
      - name: agent-system
        image: agent-system:latest
        ports:
        - containerPort: 8080
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: google-api-key
```

### 4. Monitoring and Logging

```python
# src/utils/monitoring.py
import logging
from prometheus_client import Counter, Histogram, start_http_server

class SystemMonitoring:
    """System monitoring and metrics."""
    
    def __init__(self):
        self.request_counter = Counter('agent_requests_total', 'Total requests')
        self.response_time = Histogram('agent_response_seconds', 'Response time')
        
    def start_metrics_server(self, port: int = 9090):
        """Start Prometheus metrics server."""
        start_http_server(port)
        
    def record_request(self):
        """Record a request."""
        self.request_counter.inc()
        
    def record_response_time(self, time_seconds: float):
        """Record response time."""
        self.response_time.observe(time_seconds)
```

### 5. Health Checks

```python
# src/utils/health.py
class HealthChecker:
    """System health checking."""
    
    def __init__(self, system: AgentSystem):
        self.system = system
        
    async def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check agent availability
        for name, agent in self.system.agents.items():
            try:
                # Simple health check query
                response = await agent.process("health check")
                health_status["components"][name] = "healthy"
            except Exception as e:
                health_status["components"][name] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
        
        return health_status
```

---

## Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent should have one clear purpose
- **Clear Instructions**: Provide specific, actionable instructions
- **Tool Integration**: Immediately use tools when needed, don't ask for more info
- **Error Handling**: Gracefully handle tool failures and edge cases
- **Consistent Responses**: Maintain consistent response formats

### 2. MCP Tool Development

- **Schema Validation**: Always validate inputs and outputs
- **Error Responses**: Return structured error information
- **Documentation**: Document all tool functions clearly
- **Testing**: Test tools independently and in integration
- **Performance**: Optimize for response time and resource usage

### 3. System Architecture

- **Modularity**: Design for easy addition/removal of components
- **Configuration**: Make behavior configurable without code changes
- **Logging**: Log all important events and state changes
- **Monitoring**: Implement comprehensive monitoring and alerting
- **Scalability**: Design for horizontal scaling from the start

### 4. Code Quality

- **Type Hints**: Use type hints throughout the codebase
- **Documentation**: Maintain comprehensive documentation
- **Testing**: Achieve high test coverage (>80%)
- **Code Review**: Implement thorough code review processes
- **Standards**: Follow PEP 8 and established coding standards

### 5. Security

- **Input Validation**: Validate all inputs rigorously
- **Authentication**: Implement robust authentication
- **Authorization**: Use principle of least privilege
- **Encryption**: Encrypt sensitive data in transit and at rest
- **Auditing**: Log all security-relevant events

---

## Extension Points

### 1. Custom Agent Types

```python
class CustomAgentType(LlmAgent):
    """Template for custom agent types."""
    
    def __init__(self, config: CustomAgentConfig):
        super().__init__(
            name=config.name,
            instruction=config.instruction,
            tools=config.tools,
            model=config.model
        )
        
        # Custom initialization
        self.custom_behavior = config.custom_behavior
    
    def post_process_response(self, response: str) -> str:
        """Custom post-processing of responses."""
        # Implement custom logic
        return response
```

### 2. Plugin Architecture

```python
class PluginManager:
    """Manage system plugins."""
    
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin: Plugin):
        """Register a new plugin."""
        self.plugins[name] = plugin
        plugin.initialize()
    
    def execute_hooks(self, hook_name: str, *args, **kwargs):
        """Execute hooks for all plugins."""
        for plugin in self.plugins.values():
            if hasattr(plugin, hook_name):
                getattr(plugin, hook_name)(*args, **kwargs)
```

### 3. Custom Tool Integration

```python
class ExternalToolIntegration:
    """Template for integrating external tools."""
    
    def __init__(self, config: ToolConfig):
        self.config = config
        self.client = self._create_client()
    
    def _create_client(self):
        """Create client for external service."""
        pass
    
    def create_mcp_tool(self) -> MCPToolset:
        """Create MCP toolset for external tool."""
        pass
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Agent Not Responding

**Symptoms**: Agent doesn't respond to queries or responses are empty

**Possible Causes**:
- Missing API keys
- Tool server not running
- Network connectivity issues
- Invalid configuration

**Solutions**:
```bash
# Check API key configuration
echo $GOOGLE_API_KEY

# Verify tool servers are running
curl http://localhost:8000/health
curl http://localhost:8001/health

# Check system logs
tail -f logs/system.log

# Validate configuration
python -c "from src.utils.config import config; print(config.validate())"
```

#### 2. MCP Tool Errors

**Symptoms**: Tools returning errors or not being called

**Possible Causes**:
- Server not accessible
- Schema validation errors
- Tool registration issues

**Solutions**:
```python
# Test tool directly
from src.mcp_servers.weather_server import WeatherServer
server = WeatherServer("test", 8000, "test")
server.register_tools()

# Check tool registration
tools = server.mcp.get_tools()
print([tool.name for tool in tools])
```

#### 3. Performance Issues

**Symptoms**: Slow response times or high resource usage

**Possible Causes**:
- Inefficient tool calls
- Memory leaks
- Network latency

**Solutions**:
```python
# Profile code
import cProfile
cProfile.run('agent_system.process_query("test query")')

# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB")

# Check response times
import time
start = time.time()
response = agent_system.process_query("test")
print(f"Response time: {time.time() - start} seconds")
```

#### 4. Configuration Issues

**Symptoms**: Services not starting or behaving unexpectedly

**Solutions**:
```python
# Validate all configuration
from src.utils.config import Config
config = Config()
validation_result = config.validate()
print(validation_result)

# Check environment variables
import os
required_vars = ['GOOGLE_API_KEY', 'WEATHER_SERVER_PORT']
for var in required_vars:
    print(f"{var}: {os.getenv(var, 'NOT SET')}")
```

### Debugging Tools

1. **Logging Configuration**:
   ```python
   # Enable debug logging
   logging.getLogger().setLevel(logging.DEBUG)
   ```

2. **Interactive Debugging**:
   ```python
   # Add breakpoints
   import pdb; pdb.set_trace()
   ```

3. **System Status Checks**:
   ```python
   # Check all system components
   health_status = await health_checker.check_health()
   print(health_status)
   ```

---

## Conclusion

This framework provides a comprehensive foundation for building production-ready AI agent systems. The modular architecture, standardized interfaces, and extensive tooling support enable rapid development while maintaining high quality and security standards.

Key takeaways:
- Start with the core components and gradually add complexity
- Use the MCP protocol for standardized tool integration
- Implement comprehensive testing from the beginning
- Plan for security, monitoring, and deployment early
- Follow established patterns and best practices

For additional support and examples, refer to the reference implementation in the `src/` directory of this repository.

---

*Framework Version: 1.0*  
*Last Updated: July 3, 2025*  
*For questions and contributions, please refer to the project documentation.*
