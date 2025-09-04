# AutoGen Agent Development Guide

This guide shows you how to create AutoGen-based agents using the `AutoGenBasedAgent` base class. The base class handles all the boilerplate code for AutoGen integration, allowing you to focus on your agent's specific functionality.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding the Architecture](#understanding-the-architecture)
3. [Required Methods](#required-methods)
4. [Optional Methods](#optional-methods)
5. [Tool Development](#tool-development)
6. [MCP Integration](#mcp-integration)
7. [Configuration Options](#configuration-options)
8. [Advanced Examples](#advanced-examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

1. Install required dependencies:
```bash
pip install autogen-agentchat~=0.4.5
```

2. Set up your API keys in your environment:
```bash
export OPENAI_API_KEY="your-openai-key"
# OR
export GEMINI_API_KEY="your-gemini-key"
```

### Creating Your First Agent

Here's a minimal example of an AutoGen agent:

```python
from typing import Any, Dict, List
from agent_framework import AutoGenBasedAgent, create_basic_agent_server

class MyAgent(AutoGenBasedAgent):
    """My custom AutoGen agent."""
    
    def get_agent_prompt(self) -> str:
        """Return the system prompt for this agent."""
        return """You are a helpful assistant that can perform basic calculations.
        Always be polite and provide clear explanations of your work."""
    
    def get_agent_tools(self) -> List[callable]:
        """Return list of tool functions for this agent."""
        return [self.add]
    
    def get_agent_metadata(self) -> Dict[str, Any]:
        """Return agent-specific metadata."""
        return {
            "name": "My Math Agent",
            "description": "A simple agent that can add numbers",
            "version": "1.0.0"
        }
    
    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers together."""
        return a + b

# Start the server
if __name__ == "__main__":
    create_basic_agent_server(MyAgent, port=8000)
```

That's it! Your agent will be available at `http://localhost:8000/testapp`.

## Understanding the Architecture

### What the Base Class Provides

The `AutoGenBasedAgent` base class handles:

- ✅ **AutoGen Integration**: Complete setup and lifecycle management
- ✅ **Streaming Support**: Real-time message streaming with proper event handling
- ✅ **MCP Tools**: Integration with Model Context Protocol tools
- ✅ **Session Management**: Configuration, state saving/loading
- ✅ **Special Block Parsing**: Forms, option blocks, charts, tables
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Model Client Management**: Automatic model client setup

### What You Need to Provide

You only need to implement:

- 🎯 **Agent Prompt**: Your agent's system prompt
- 🎯 **Tools**: Functions your agent can call
- 🎯 **Metadata**: Agent description and capabilities
- 🎯 **AutoGen Agent Creation**: Choose and configure your AutoGen agent type
- 🔧 **MCP Configuration** (optional): External tool servers

## Required Methods

### 1. `get_agent_prompt(self) -> str`

Define your agent's personality and capabilities:

```python
def get_agent_prompt(self) -> str:
    return """You are a data analysis expert.
    
    You can:
    - Analyze datasets and create visualizations
    - Perform statistical calculations
    - Generate reports in various formats
    
    Always provide clear explanations and cite your sources.
    Use charts and tables when helpful for visualization."""
```

### 2. `get_agent_tools(self) -> List[callable]`

Return the functions your agent can use:

```python
def get_agent_tools(self) -> List[callable]:
    return [
        self.calculate_mean,
        self.calculate_variance,
        self.create_histogram,
        self.generate_report
    ]
```

### 3. `get_agent_metadata(self) -> Dict[str, Any]`

Provide information about your agent:

```python
def get_agent_metadata(self) -> Dict[str, Any]:
    return {
        "name": "Data Analysis Agent",
        "description": "Expert in statistical analysis and data visualization",
        "version": "2.1.0",
        "author": "Data Science Team",
        "capabilities": {
            "statistics": True,
            "visualization": True,
            "reporting": True,
            "data_processing": True
        },
        "supported_formats": ["CSV", "JSON", "Excel"],
        "output_types": ["charts", "tables", "reports"]
    }
```

### 4. `create_autogen_agent(self, tools, model_client, system_message) -> Any`

Create and configure your AutoGen agent. This gives you full control over which AutoGen agent type to use:

```python
from autogen_agentchat.agents import AssistantAgent

def create_autogen_agent(self, tools: List[callable], model_client: Any, system_message: str) -> AssistantAgent:
    """Create and configure the AutoGen agent."""
    return AssistantAgent(
        name="data_analyst",
        model_client=model_client,
        system_message=system_message,
        max_tool_iterations=500,  # Allow more tool calls for complex analysis
        reflect_on_tool_use=True,
        tools=tools,
        model_client_stream=True
    )
```

**Other AutoGen Agent Types:**

```python
from autogen_agentchat.agents import GroupChatManager, UserProxyAgent

# For group chat coordination
def create_autogen_agent(self, tools, model_client, system_message):
    return GroupChatManager(
        name="chat_manager",
        model_client=model_client,
        participants=[...],  # Your participant agents
        selector=lambda history: ...  # Your selection logic
    )

# For user proxy functionality  
def create_autogen_agent(self, tools, model_client, system_message):
    return UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",  # Or "ALWAYS" for interactive mode
        code_execution_config={"use_docker": False}
    )
```

## Optional Methods

### `get_mcp_server_params(self) -> List[StdioServerParams]`

Configure external MCP tool servers:

```python
from autogen_ext.tools.mcp import StdioServerParams

def get_mcp_server_params(self) -> List[StdioServerParams]:
    return [
        # Python execution server
        StdioServerParams(
            command='deno',
            args=[
                'run', '-N', '-R=node_modules', '-W=node_modules',
                '--node-modules-dir=auto',
                'jsr:@pydantic/mcp-run-python', 'stdio'
            ],
            read_timeout_seconds=120
        ),
        # File system server
        StdioServerParams(
            command='npx',
            args=['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
            read_timeout_seconds=60
        )
    ]
```



## Tool Development

### Creating Agent Tools

Agent tools are regular Python functions with docstrings:

```python
@staticmethod
def calculate_correlation(data1: List[float], data2: List[float]) -> float:
    """Calculate Pearson correlation coefficient between two datasets.
    
    Args:
        data1: First dataset
        data2: Second dataset
        
    Returns:
        Correlation coefficient between -1 and 1
    """
    # Your implementation here
    import statistics
    mean1, mean2 = statistics.mean(data1), statistics.mean(data2)
    
    numerator = sum((x - mean1) * (y - mean2) for x, y in zip(data1, data2))
    sum1 = sum((x - mean1) ** 2 for x in data1)
    sum2 = sum((y - mean2) ** 2 for y in data2)
    
    if sum1 == 0 or sum2 == 0:
        return 0.0
        
    return numerator / (sum1 * sum2) ** 0.5

def create_chart(self, chart_type: str, data: Dict[str, Any]) -> str:
    """Create a chart and return the chart configuration.
    
    Args:
        chart_type: Type of chart (bar, line, pie, etc.)
        data: Chart data and configuration
        
    Returns:
        Chart configuration as JSON string
    """
    chart_config = {
        "type": "chartjs",
        "chartConfig": {
            "type": chart_type,
            "data": data,
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": data.get("title", "Chart")}
                }
            }
        }
    }
    return f"```chart\n{json.dumps(chart_config, indent=2)}\n```"
```

### Tool Categories

#### 1. Data Processing Tools
```python
def clean_dataset(self, data: List[Dict], remove_nulls: bool = True) -> List[Dict]:
    """Clean and preprocess dataset."""
    pass

def filter_data(self, data: List[Dict], criteria: Dict[str, Any]) -> List[Dict]:
    """Filter data based on criteria."""
    pass
```

#### 2. Analysis Tools
```python
def descriptive_stats(self, data: List[float]) -> Dict[str, float]:
    """Calculate descriptive statistics."""
    pass

def run_hypothesis_test(self, sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
    """Perform statistical hypothesis test."""
    pass
```

#### 3. Visualization Tools
```python
def create_scatter_plot(self, x_data: List[float], y_data: List[float], **kwargs) -> str:
    """Create a scatter plot."""
    pass

def create_dashboard(self, charts: List[Dict]) -> str:
    """Create a multi-chart dashboard."""
    pass
```

## MCP Integration

### Available MCP Servers

The framework supports various MCP servers:

#### 1. Python Execution
```python
StdioServerParams(
    command='deno',
    args=['run', '-N', '-R=node_modules', '-W=node_modules', 
          '--node-modules-dir=auto', 'jsr:@pydantic/mcp-run-python', 'stdio'],
    read_timeout_seconds=120
)
```

#### 2. File System Access
```python
StdioServerParams(
    command='npx',
    args=['-y', '@modelcontextprotocol/server-filesystem', '/allowed/path'],
    read_timeout_seconds=60
)
```

#### 3. Database Access
```python
StdioServerParams(
    command='npx',
    args=['-y', '@modelcontextprotocol/server-sqlite', 'database.db'],
    read_timeout_seconds=90
)
```

#### 4. Custom MCP Server
```python
StdioServerParams(
    command='python',
    args=['-m', 'my_custom_mcp_server'],
    env={"API_KEY": os.getenv("MY_API_KEY")},
    read_timeout_seconds=120
)
```

### MCP Best Practices

1. **Always set appropriate timeouts** for MCP servers
2. **Handle MCP initialization failures gracefully**
3. **Use environment variables for sensitive configuration**
4. **Test MCP tools independently** before integrating

## Configuration Options

### Environment Variables

```bash
# API Keys
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"

# Agent Configuration
export AGENT_PORT="8000"
export AGENT_TYPE="MyCustomAgent"

# Model Selection
export OPENAI_API_MODEL="gpt-4"
export GEMINI_MODEL="gemini-pro"
```

### Session Configuration

Agents can be configured per session:

```python
# When initializing a session
session_config = {
    "system_prompt": "Custom prompt for this session",
    "model_name": "gpt-4",
    "model_config": {
        "temperature": 0.7,
        "max_tokens": 2000
    }
}
```

## Advanced Examples

### 1. Multi-Modal Agent with File Processing

```python
class DocumentAnalysisAgent(AutoGenBasedAgent):
    """Agent that can analyze documents and images."""
    
    def get_agent_prompt(self) -> str:
        return """You are a document analysis expert.
        You can analyze text documents, images, and data files.
        Provide detailed insights and create visualizations when helpful."""
    
    def get_agent_tools(self) -> List[callable]:
        return [
            self.extract_text_from_pdf,
            self.analyze_image,
            self.parse_csv_data,
            self.generate_summary,
            self.create_visualization
        ]
    
    def create_autogen_agent(self, tools: List[callable], model_client: Any, system_message: str):
        """Create an AssistantAgent optimized for document analysis."""
        return AssistantAgent(
            name="document_analyst",
            model_client=model_client,
            system_message=system_message,
            max_tool_iterations=300,  # More iterations for complex document analysis
            reflect_on_tool_use=True,
            tools=tools,
            model_client_stream=True
        )
    
    def get_mcp_server_params(self) -> List[StdioServerParams]:
        return [
            # File system access for document processing
            StdioServerParams(
                command='npx',
                args=['-y', '@modelcontextprotocol/server-filesystem', './documents'],
                read_timeout_seconds=60
            ),
            # Python for data processing
            StdioServerParams(
                command='deno',
                args=['run', '-N', '-R=node_modules', '-W=node_modules',
                      '--node-modules-dir=auto', 'jsr:@pydantic/mcp-run-python', 'stdio'],
                read_timeout_seconds=120
            )
        ]
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file."""
        # Implementation using PyPDF2 or similar
        pass
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image and extract information."""
        # Implementation using PIL/OpenCV
        pass
```

### 2. API Integration Agent

```python
class APIIntegrationAgent(AutoGenBasedAgent):
    """Agent that can interact with external APIs."""
    
    def get_agent_tools(self) -> List[callable]:
        return [
            self.fetch_weather_data,
            self.get_stock_prices,
            self.search_web,
            self.send_notification
        ]
    
    def create_autogen_agent(self, tools: List[callable], model_client: Any, system_message: str):
        """Create an AssistantAgent for API integration tasks."""
        return AssistantAgent(
            name="api_agent",
            model_client=model_client,
            system_message=system_message,
            max_tool_iterations=150,  # Moderate iterations for API calls
            reflect_on_tool_use=True,
            tools=tools,
            model_client_stream=True
        )
    
    def get_mcp_server_params(self) -> List[StdioServerParams]:
        return [
            # Web API access server
            StdioServerParams(
                command='npx',
                args=['-y', '@modelcontextprotocol/server-web-api'],
                env={
                    "WEATHER_API_KEY": os.getenv("WEATHER_API_KEY"),
                    "STOCK_API_KEY": os.getenv("STOCK_API_KEY")
                },
                read_timeout_seconds=30
            )
        ]
    
    async def fetch_weather_data(self, location: str) -> Dict[str, Any]:
        """Fetch current weather data for a location."""
        # Implementation using weather API
        pass
```

### 3. Code Generation Agent

```python
class CodeGenerationAgent(AutoGenBasedAgent):
    """Agent specialized in generating and executing code."""
    
    def get_agent_prompt(self) -> str:
        return """You are a senior software engineer and code generation expert.
        You can:
        - Generate code in multiple programming languages
        - Execute and test code
        - Debug and optimize existing code
        - Create documentation and tests
        
        Always write clean, well-documented code with proper error handling."""
    
    def get_agent_tools(self) -> List[callable]:
        return [
            self.generate_function,
            self.run_tests,
            self.optimize_code,
            self.create_documentation
        ]
    
    def create_autogen_agent(self, tools: List[callable], model_client: Any, system_message: str):
        """Create an AssistantAgent optimized for code generation."""
        return AssistantAgent(
            name="code_generator",
            model_client=model_client,
            system_message=system_message,
            max_tool_iterations=400,  # High iterations for complex coding tasks
            reflect_on_tool_use=True,
            tools=tools,
            model_client_stream=True
        )
    
    def get_mcp_server_params(self) -> List[StdioServerParams]:
        return [
            # Python execution
            StdioServerParams(
                command='deno',
                args=['run', '-N', '-R=node_modules', '-W=node_modules',
                      '--node-modules-dir=auto', 'jsr:@pydantic/mcp-run-python', 'stdio'],
                read_timeout_seconds=120
            ),
            # Git operations
            StdioServerParams(
                command='npx',
                args=['-y', '@modelcontextprotocol/server-git', './workspace'],
                read_timeout_seconds=60
            )
        ]
    
    def generate_function(self, specification: str, language: str = "python") -> str:
        """Generate a function based on specification."""
        # Implementation for code generation
        pass
```

## Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent should have a clear, focused purpose
- **Clear Prompts**: Write detailed system prompts that explain capabilities
- **Tool Organization**: Group related tools logically
- **Error Handling**: Always handle edge cases in tools

### 2. Tool Development

```python
# ✅ Good: Clear, documented tool with error handling
@staticmethod
def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers safely.
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        Result of a/b
        
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# ❌ Bad: Unclear, undocumented tool
def calc(x, y):
    return x / y  # No error handling!
```

### 3. Performance Optimization

- **Lazy Loading**: Initialize expensive resources only when needed
- **Caching**: Cache results of expensive operations
- **Async Operations**: Use async/await for I/O operations
- **Timeout Management**: Set appropriate timeouts for all operations

### 4. Testing Your Agent

```python
import pytest
from your_agent import YourAgent

@pytest.fixture
def agent():
    return YourAgent()

def test_agent_tools(agent):
    """Test that all tools work correctly."""
    tools = agent.get_agent_tools()
    assert len(tools) > 0
    
    # Test a specific tool
    result = agent.add(2, 3)
    assert result == 5

def test_agent_metadata(agent):
    """Test agent metadata."""
    metadata = agent.get_agent_metadata()
    assert "name" in metadata
    assert "description" in metadata
```

### 5. Deployment Considerations

- **Environment Variables**: Use environment variables for configuration
- **Resource Limits**: Set appropriate resource limits for production
- **Monitoring**: Implement logging and monitoring
- **Security**: Validate all inputs and limit file system access

## Troubleshooting

### Common Issues

#### 1. AutoGen Import Errors
```
ImportError: AutoGen dependencies are not installed
```
**Solution**: Install AutoGen properly:
```bash
pip install autogen-agentchat~=0.4.5
```

#### 2. MCP Tool Initialization Failures
```
Failed to initialize MCP tools: [Error details]
```
**Solutions**:
- Check if the MCP server command is available
- Verify environment variables are set correctly
- Increase timeout values for slow servers
- Check file permissions for file system servers

#### 3. Model Client Errors
```
Failed to create model client: No API keys found
```
**Solution**: Set up your API keys:
```bash
export OPENAI_API_KEY="your-key"
# OR
export GEMINI_API_KEY="your-key"
```

#### 4. Tool Execution Timeouts
```
Tool execution timed out
```
**Solutions**:
- Increase `read_timeout_seconds` for MCP servers
- Optimize tool implementations for better performance
- Add progress indicators for long-running operations

### Debugging Tips

1. **Enable Verbose Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Test Tools Independently**:
```python
# Test tools outside of the agent context
agent = YourAgent()
result = agent.your_tool(test_input)
print(f"Tool result: {result}")
```

3. **Check MCP Server Status**:
```python
# In your agent's __init__ method
logger.info(f"MCP tools initialized: {len(self._mcp_tools)} tools")
```

4. **Validate Configuration**:
```python
def validate_config(self):
    """Validate agent configuration."""
    assert self.get_agent_prompt(), "Agent prompt cannot be empty"
    assert self.get_agent_tools(), "Agent must have at least one tool"
    assert self.get_agent_metadata(), "Agent metadata is required"
```

## Getting Help

- **Framework Documentation**: Check the main AgentFramework documentation
- **AutoGen Documentation**: Refer to Microsoft AutoGen documentation
- **MCP Documentation**: See Model Context Protocol documentation
- **Community**: Join the AgentFramework community discussions

---

This guide should get you started with creating powerful AutoGen-based agents. The base class handles all the complexity, so you can focus on building amazing agent capabilities! 