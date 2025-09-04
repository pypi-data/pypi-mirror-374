# MBX AI

A comprehensive Python library for building intelligent AI applications with Large Language Models (LLMs), structured responses, tool integration, and agent-based thinking.

## 🚀 Features

- **🔗 Multiple AI Client Types**: OpenRouter integration with tool-enabled and MCP-enabled variants
- **🤖 Intelligent Agent System**: Dialog-based thinking with question generation, quality iteration, and conversation memory
- **🛠️ Tool Integration**: Easy function registration with automatic schema generation
- **🔌 MCP Support**: Full Model Context Protocol (MCP) client and server implementation
- **📋 Structured Responses**: Type-safe responses using Pydantic models
- **🔄 Quality Iteration**: Built-in response improvement through AI-powered quality checks
- **💬 Conversation Memory**: Persistent dialog sessions with history management
- **⚡ Automatic Retry**: Built-in retry logic with exponential backoff for robust connections

## 📦 Installation

```bash
pip install mbxai
```

## 🏗️ Architecture Overview

MBX AI provides four main client types, each building upon the previous:

1. **OpenRouterClient** - Basic LLM interactions with structured responses
2. **ToolClient** - Adds function calling capabilities
3. **MCPClient** - Adds Model Context Protocol server integration
4. **AgentClient** - Adds intelligent dialog-based thinking (wraps any of the above)

| Client | Structured Responses | Function Calling | MCP Integration | Agent Thinking |
|--------|---------------------|------------------|-----------------|----------------|
| OpenRouterClient | ✅ | ❌ | ❌ | ❌ |
| ToolClient | ✅ | ✅ | ❌ | ❌ |
| MCPClient | ✅ | ✅ | ✅ | ❌ |
| AgentClient | ✅ | ✅* | ✅* | ✅ |

*AgentClient capabilities depend on the wrapped client

## 🚀 Quick Start

### Basic OpenRouter Client

```python
import os
from mbxai import OpenRouterClient
from pydantic import BaseModel, Field

# Initialize client
client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))

# Simple chat
response = client.create([
    {"role": "user", "content": "What is the capital of France?"}
])
print(response.choices[0].message.content)

# Structured response
class CityInfo(BaseModel):
    name: str = Field(description="City name")
    population: int = Field(description="Population count")
    country: str = Field(description="Country name")

response = client.parse(
    messages=[{"role": "user", "content": "Tell me about Paris"}],
    response_format=CityInfo
)
city = response.choices[0].message.parsed
print(f"{city.name}, {city.country} - Population: {city.population:,}")
```

### Tool Client with Automatic Schema Generation

```python
import os
from mbxai import ToolClient, OpenRouterClient

# Initialize clients
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
tool_client = ToolClient(openrouter_client)

# Define a function - schema is auto-generated!
def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get weather information for a location.
    
    Args:
        location: The city or location name
        unit: Temperature unit (celsius or fahrenheit)
    """
    return {
        "location": location,
        "temperature": 22,
        "unit": unit,
        "condition": "Sunny"
    }

# Register tool (schema automatically generated from function signature)
tool_client.register_tool(
    name="get_weather",
    description="Get current weather for a location",
    function=get_weather
    # No schema needed - automatically generated!
)

# Use the tool
response = tool_client.chat([
    {"role": "user", "content": "What's the weather like in Tokyo?"}
])
print(response.choices[0].message.content)
```

### MCP Client for Server Integration

```python
import os
from mbxai import MCPClient, OpenRouterClient

# Initialize MCP client
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
mcp_client = MCPClient(openrouter_client)

# Register MCP server (automatically loads all tools)
mcp_client.register_mcp_server("data-analysis", "http://localhost:8000")

# Chat with MCP tools available
response = mcp_client.chat([
    {"role": "user", "content": "Analyze the sales data from the server"}
])
print(response.choices[0].message.content)
```

### Agent Client - Intelligent Dialog System

The AgentClient provides an intelligent thinking process with question generation, quality improvement, and conversation memory.

```python
import os
from mbxai import AgentClient, OpenRouterClient
from pydantic import BaseModel, Field

class TravelPlan(BaseModel):
    destination: str = Field(description="Travel destination")
    duration: str = Field(description="Trip duration")
    activities: list[str] = Field(description="Recommended activities")
    budget: str = Field(description="Estimated budget")

# Initialize agent
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
agent = AgentClient(openrouter_client, max_iterations=2)

# Agent with questions (interactive mode)
response = agent.agent(
    prompt="Plan a vacation for me",
    final_response_structure=TravelPlan,
    ask_questions=True
)

if response.has_questions():
    print("Agent Questions:")
    for q in response.questions:
        print(f"- {q.question}")
    
    # Answer questions
    from mbxai import AnswerList, Answer
    answers = AnswerList(answers=[
        Answer(key="destination_preference", answer="Mountain destination"),
        Answer(key="budget_range", answer="$2000-3000"),
        Answer(key="duration", answer="5 days")
    ])
    
    # Continue with answers
    final_response = agent.agent(
        prompt="Continue with the travel planning",
        final_response_structure=TravelPlan,
        agent_id=response.agent_id,
        answers=answers
    )
    
    plan = final_response.final_response
    print(f"Destination: {plan.destination}")
    print(f"Duration: {plan.duration}")
else:
    # Direct response
    plan = response.final_response
    print(f"Destination: {plan.destination}")
```

### Agent with Tool Integration

```python
from mbxai import AgentClient, ToolClient, OpenRouterClient

# Setup tool-enabled agent
openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY"))
tool_client = ToolClient(openrouter_client)
agent = AgentClient(tool_client)

# Register tools via agent (proxy method)
def search_flights(origin: str, destination: str, date: str) -> dict:
    """Search for flights between cities."""
    return {
        "flights": [
            {"airline": "Example Air", "price": "$450", "duration": "3h 15m"}
        ]
    }

agent.register_tool(
    name="search_flights",
    description="Search for flights between cities",
    function=search_flights
)

# Agent automatically uses tools when needed
class FlightInfo(BaseModel):
    flights: list[dict] = Field(description="Available flights")
    recommendation: str = Field(description="Flight recommendation")

response = agent.agent(
    prompt="Find flights from New York to Los Angeles for tomorrow",
    final_response_structure=FlightInfo,
    ask_questions=False
)

flight_info = response.final_response
print(f"Found {len(flight_info.flights)} flights")
print(f"Recommendation: {flight_info.recommendation}")
```

## 📚 Detailed Documentation

### OpenRouterClient

The base client for OpenRouter API integration with structured response support.

#### Key Features:
- **Multiple Models**: Support for GPT-4, Claude, Llama, and other models via OpenRouter
- **Structured Responses**: Type-safe responses using Pydantic models
- **Retry Logic**: Automatic retry with exponential backoff
- **Error Handling**: Comprehensive error handling with detailed logging

#### Methods:
- `create()` - Basic chat completion
- `parse()` - Chat completion with structured response

#### Configuration:
```python
client = OpenRouterClient(
    token="your-api-key",
    model="openai/gpt-4-turbo",  # or use OpenRouterModel enum
    max_retries=3,
    retry_initial_delay=1.0,
    retry_max_delay=10.0
)
```

### ToolClient

Extends OpenRouterClient with function calling capabilities.

#### Key Features:
- **Automatic Schema Generation**: Generate JSON schemas from Python function signatures
- **Tool Registration**: Simple function registration
- **Tool Execution**: Automatic tool calling and response handling
- **Error Recovery**: Graceful handling of tool execution errors

#### Usage:
```python
tool_client = ToolClient(openrouter_client)

# Register with automatic schema
tool_client.register_tool("function_name", "description", function)

# Register with custom schema
tool_client.register_tool("function_name", "description", function, custom_schema)
```

### MCPClient

Extends ToolClient with Model Context Protocol (MCP) server integration.

#### Key Features:
- **MCP Server Integration**: Connect to MCP servers and load their tools
- **Tool Discovery**: Automatically discover and register tools from MCP servers
- **HTTP Client Management**: Built-in HTTP client for MCP communication
- **Schema Conversion**: Convert MCP schemas to OpenAI function format

#### Usage:
```python
mcp_client = MCPClient(openrouter_client)
mcp_client.register_mcp_server("server-name", "http://localhost:8000")
```

### AgentClient

Wraps any client with intelligent dialog-based thinking capabilities.

#### Key Features:
- **Question Generation**: Automatically generates clarifying questions
- **Quality Iteration**: Improves responses through multiple AI review cycles
- **Conversation Memory**: Maintains conversation history across interactions
- **Flexible Configuration**: Configurable quality vs speed tradeoffs
- **Tool Proxy Methods**: Access underlying client's tool capabilities

#### Configuration Options:
```python
agent = AgentClient(
    ai_client=any_supported_client,
    max_iterations=2  # 0=fastest, 3+=highest quality
)
```

#### Dialog Flow:
1. **Question Generation** (if `ask_questions=True`)
2. **Answer Processing** (if questions were asked)
3. **Thinking Process** (analyze prompt and context)
4. **Quality Iteration** (improve response through AI review)
5. **Final Response** (generate structured output)

#### Session Management:
```python
# List active sessions
sessions = agent.list_sessions()

# Get session info
info = agent.get_session_info(agent_id)

# Delete session
agent.delete_session(agent_id)
```

## 🏃‍♂️ Advanced Examples

### Custom Model Registration

```python
from mbxai import OpenRouterClient, OpenRouterModel

# Register custom model
OpenRouterClient.register_model("CUSTOM_MODEL", "provider/model-name")

# Use custom model
client = OpenRouterClient(token="your-key", model="CUSTOM_MODEL")
```

### Conversation History and Context

```python
# Start a conversation
response1 = agent.agent("Tell me about quantum computing", ScienceExplanation)
agent_id = response1.agent_id

# Continue conversation with context
response2 = agent.agent(
    "How does it compare to classical computing?",
    ComparisonExplanation,
    agent_id=agent_id,
    ask_questions=False
)

# The agent remembers the previous conversation context
```

### Error Handling and Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

try:
    response = client.create(messages)
except OpenRouterAPIError as e:
    print(f"API Error: {e}")
except OpenRouterConnectionError as e:
    print(f"Connection Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
```

### Streaming Responses

```python
# Streaming with OpenRouterClient
response = client.create(messages, stream=True)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Streaming with ToolClient (tools execute before streaming)
response = tool_client.chat(messages, stream=True)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=mbxai --cov-report=html
```

## 🔧 Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mbxai.git
cd mbxai/packages
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
export OPENROUTER_API_KEY="your-api-key"
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔗 Links

- **Homepage**: [https://www.mibexx.de](https://www.mibexx.de)
- **Documentation**: [https://www.mibexx.de](https://www.mibexx.de)
- **Repository**: [https://github.com/yourusername/mbxai](https://github.com/yourusername/mbxai)

## 📊 Version Information

Current version: **2.1.3**

- Python 3.12+ required
- Built with modern async/await patterns
- Type-safe with Pydantic v2
- Compatible with OpenAI SDK v1.77+