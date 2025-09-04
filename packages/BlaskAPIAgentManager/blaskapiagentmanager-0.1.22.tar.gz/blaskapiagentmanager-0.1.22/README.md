# BlaskAPIAgentManager

BlaskAPIAgentManager is a Python library that provides a sophisticated pipeline for interacting with the Blask API based on Swagger specifications. It automates API discovery, planning, and execution to retrieve relevant data based on natural language queries.

## Features

- **Automatic API Planning**: Intelligently plans the right API calls based on natural language queries
- **API Call Orchestration**: Executes API calls in the optimal order with proper parameters
- **Data Enrichment**: Automatically enriches data by resolving IDs to human-readable names
- **Result Synthesis**: Summarizes API responses into coherent, user-friendly answers
- **RAG Enhancement**: Can enhance Retrieval-Augmented Generation answers with live API data

## Installation

### Quick Install with pip

```bash
pip install BlaskAPIAgentManager
```

### Install with uv (Recommended)

For a faster, more reliable installation, you can use [uv](https://github.com/astral-sh/uv), a Python packaging tool for fast installation:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install BlaskAPIAgentManager with uv
uv pip install BlaskAPIAgentManager
```

### Local Development Installation

For local development or contributing to the project:

1. Clone the repository:
```bash
git clone https://gitlab.private.blask.com/blask/ml-ai/blaskapiagentmanager
cd blaskapiagentmanager
```

2. Create and activate a virtual environment:

Using standard venv:
```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

Using uv (recommended):
```bash
# Create virtual environment
uv venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

3. Install the package in development mode:
```bash
# Using standard pip
pip install -e .

# Using uv (recommended)
uv pip install -e .
```

## Configuration

Create a `.env` file in your project root with the following variables:

```
BLASK_USERNAME=your_username
BLASK_PASSWORD=your_password
OPENROUTER_API_KEY=your_openrouter_api_key
SWAGGER_JSON_URL=link_to_swagger_json
LOGIN_URL=link_to_login
BASE_URL=base_api_url
```

## Usage

### Basic Usage

```python
from BlaskAPIAgentManager import BlaskPipeline

# Initialize the pipeline
pipeline = BlaskPipeline()

# Process a natural language query
result = pipeline.process_query("What are the top 5 performing countries by GGR in the last 3 months?")

# Print the summary
print(result["summary"])

# Access the raw data
api_data = result["data"]
```

## Components

- **BlaskAPIAgentManager**: The name of the Python package.
- **BlaskPipeline**: Main orchestrator that manages the entire workflow from query to summarized result.
- **BlaskAPIAgent**: Core agent for authenticating and interacting with the Blask API.
- **PlannerTool**: Plans the sequence of API calls based on natural language queries.
- **ProcessorTool**: Processes raw API responses by filtering, sorting, and aggregating data.

## Development

To contribute to this project:

1. Clone the repository
2. Create and activate a virtual environment (see Local Development Installation section)
3. Install development dependencies:
```bash
uv pip install -e ".[dev]"
```
4. Set up environment variables for testing:
   - Create a `.env` file in the project root with your Blask API credentials
   - Tests will skip API-dependent tests if credentials are not available

5. Run tests:
```bash
# Run all tests
python -m unittest discover

# Run specific test files
python -m unittest tests.test_basic
python -m unittest tests.test_api_agents
```

Note that tests in `test_api_agents.py` require valid API credentials and will be skipped if they're not available.

## License

MIT

## Support

For support, please contact [elijah@blask.com](mailto:elijah@blask.com). 
