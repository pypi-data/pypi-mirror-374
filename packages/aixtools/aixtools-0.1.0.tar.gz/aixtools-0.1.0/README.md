# AiXplore-tools

AiXplore-tools (`axitools` for short) is a Python library to support AI agent development and debugging. It serves two main purposes:

1. **Utility Library**: A collection of utility functions and classes for agent projects
2. **Debugging Tool**: A Streamlit app (`log_view`) for visualizing and debugging agent applications by viewing messages logged by `ObjectLogger`


## `.venv`

```
# Create a new environment
uv venv .venv
source .venv/bin/activate

# Add packages
uv add pydantic-ai
uv add mcp[cli]
uv add chainlit
uv add streamlit

# Add langchain
uv add langchain-chroma
uv add langchain-ollama
uv add langchain-openai

# Other packages
uv add colorlog
uv add pandas
uv add rich
uv add ruff
uv add watchdog
uv add ipykernel

# Install this code as a package
uv pip install -e .
```

## Installation

Installing the package from GitHub, you can use `uv add` (prefered)
```
uv add https://github.com/your-org/aixtools.git
```

or using the `pip` commamnd
```
uv pip install https://github.com/your-org/aixtools.git
```

Remember to set up your [`.env` file](#environment-configuration).

### Updating

This package is in active development and changes often.

You'll want to force uv to re-install or update it to the latest commit, even if the version hasn’t changed.

```
uv add --upgrade https://github.com/your-org/aixtools.git
```

### Example: Creatng a new project

```
# Create a new project
uv init MyNewProject
cd MyNewProject

# Add a virtual environemnt and activate it
uv venv .venv
source .venv/bin/activate

# Add this package
uv add https://github.com/your-org/aixtools.git
```

### Environment Configuration

AIXtools requires specific environment variables to be set for proper operation, especially when working with different model providers.

Here is a [template of an `.env`](./.env_template) file you can use as reference.

#### Setting Up Environment Variables

1. Create a `.env` file in your project root based on the template below:

```
# Model family (azure, openai, or ollama)
MODEL_FAMILY=azure
VDB_EMBEDDINGS_MODEL_FAMILY=azure

MODEL_TIMEOUT=120

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your_endpoint.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_API_KEY=your_secret_key
AZURE_MODEL_NAME=gpt-4o
AZURE_OPENAI_PROVIDER_ID=azure
AZURE_VDB_EMBEDDINGS_MODEL_NAME=text-embedding-3-small

# OpenAI
OPENAI_MODEL_NAME=gpt-4.5-preview
OPENAI_API_KEY=openai_api_key
OPENAI_VDB_EMBEDDINGS_MODEL_NAME=text-embedding-3-small

# Ollama models
OLLAMA_MODEL_NAME=llama3.2:3b-instruct-fp16
OLLAMA_LOCAL_URL=http://localhost:11434/v1
OLLAMA_VDB_EMBEDDINGS_MODEL_NAME=snowflake-arctic-embed2:latest
```

2. Configure the variables according to your needs:
   - Set `MODEL_FAMILY` to your preferred model provider (`azure`, `openai`, or `ollama`)
   - Provide the appropriate API keys and endpoints for your chosen provider
   - Adjust model names and timeouts as needed

#### Important Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MODEL_FAMILY` | The model provider to use (azure, openai, ollama) | Yes |
| `MODEL_TIMEOUT` | Timeout in seconds for model requests | Yes |
| `AZURE_*` | Azure OpenAI configuration (if using Azure) | If MODEL_FAMILY=azure |
| `OPENAI_*` | OpenAI configuration (if using OpenAI) | If MODEL_FAMILY=openai |
| `OLLAMA_*` | Ollama configuration (if using Ollama) | If MODEL_FAMILY=ollama |

## Debugging tools: `log_view` and `ObjectLogger`

The `ObjectLogger` provides a simple logging facility, these logs can then be visualized with `log_view` app.


### `ObjectLogger`

The `ObjectLogger` class allows you to log objects to a file for later analysis. This is particularly useful for debugging agent interactions.

`ObjectLogger` simply serializes objects to a pickle file. It first removes unserializeable parts of the objects (e.g. like `async` managers).

#### Basic Usage

```python
from aixtools.utils.log_objects import ObjectLogger

# Create a logger as a context manager
with ObjectLogger() as logger:
    # Log any pickleable object
    logger.log({"message": "Hello, world!"})
    
    # Log agent responses or any other objects
    logger.log(agent_response)
```

#### Logging Agent Interactions

The function `run_agent` logs each node from the agent run, roughtly it looks like this:

```python
async def run_agent(agent: Agent, prompt: str | list[str]):
    nodes = []
    async with agent.iter(prompt) as agent_run:
        with ObjectLogger(debug=debug) as agent_logger:
            async for node in agent_run:
                agent_logger.log(node)
                nodes.append(node)
            result = agent_run.result
    return result.data, nodes
```

#### Saving Multiple Objects

```python
from aixtools.utils.log_objects import save_objects_to_logfile

# Save a list of objects to a log file
objects = [obj1, obj2, obj3]
save_objects_to_logfile(objects)
```

### log_view App

The `log_view` app allows you to visualize and analyze the objects logged by `ObjectLogger`.

It is a simple Streamlit app that you can run locally and view the log files.

#### Running the App

You can run the app using the command-line script installed with the package:

```bash
log_view
```

Or specify a custom log directory:

```bash
log_view /path/to/logs
```

#### Features

The log_view app provides several features for analyzing logged objects:

- **Log File Selection**: Choose from available log files
- **Filtering**: Filter nodes by text, type, attributes, or regex patterns
- **Visualization**: Expand/collapse nodes to view details
- **Export**: Export filtered nodes to JSON

#### Example Workflow

1. Log agent interactions using `ObjectLogger`
2. Run the `log_view` app to analyze the logs
3. Filter and explore the logged objects
4. Export interesting findings for further analysis

## Additional Utilities

AIXtools provides several other utilities to support agent development:

### PersistedDict

A dictionary that persists to a file on disk as JSON or pickle:

```python
from aixtools.utils.persisted_dict import PersistedDict

# Create a persisted dictionary
data = PersistedDict("data.json")

# Use it like a regular dictionary
data["key"] = "value"  # Automatically saved to disk
```

## Agent Utilities

Functions for creating and running agents with different model providers:

```python
from aixtools.agents.agent import get_agent, run_agent

# Create an agent with the default model (from MODEL_FAMILY)
agent = get_agent(system_prompt="You are a helpful assistant.")

# Create an agent with a specific model
from aixtools.agents.agent import get_model_openai
model = get_model_openai()
agent = get_agent(system_prompt="You are a helpful assistant.", model=model)

# Run the agent
result, nodes = await run_agent(agent, "Tell me about AI")
```

### Batch Processing

Run multiple agent queries simultaneously:

```python
from aixtools.agents.agent_batch import agent_batch, AgentQueryParams

# Create query parameters
query_parameters = [
    AgentQueryParams(prompt="What is the meaning of life"),
    AgentQueryParams(prompt="Who is the prime minister of Canada")
]

# Run queries in batches
async for result in agent_batch(query_parameters):
    print(result)
```

## Project Structure

```
aixtools/
├── __init__.py           # Package initialization
├── log_view.py           # Entry point for log_view app
├── agents/               # Agent-related functionality
│   ├── agent.py          # Core agent functions
│   └── agent_batch.py    # Batch processing for agents
├── log_view/             # Log viewer application
│   ├── app.py            # Main Streamlit application
│   ├── display.py        # Node display utilities
│   ├── export.py         # Export functionality
│   ├── filters.py        # Node filtering
│   ├── log_utils.py      # Log file utilities
│   └── node_utils.py     # Node processing utilities
└── utils/                # Utility functions and classes
    ├── config.py         # Configuration utilities
    ├── log_objects.py    # Object logging functionality
    ├── persisted_dict.py # Persistent dictionary
    └── utils.py          # General utilities

## Logging

The logging system is configured using a standard Python `dictConfig` schema. By default, it will look for a `logging.yaml` or `logging.json` file in your project's root directory. You can also specify a custom path using the `LOGGING_CONFIG_PATH` environment variable.

If no configuration file is found, a default colorized console logger will be used.

### Example `logging.yaml`

```yaml
version: 1
disable_existing_loggers: false
formatters:
  default:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  color:
    "()": "colorlog.ColoredFormatter"
    "format": "%(log_color)s%(levelname)-8s%(reset)s [%(name)s] %(message)s"
handlers:
  console:
    class: colorlog.StreamHandler
    formatter: color
    level: DEBUG
  file:
    class: logging.handlers.RotatingFileHandler
    formatter: default
    filename: app.log
    maxBytes: 10485760 # 10MB
    backupCount: 5
    level: INFO
root:
  handlers: [console, file]
  level: DEBUG
loggers:
  aixtools:
    level: INFO
```