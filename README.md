# RISA - Real Estate Intelligence System & Analysis

A comprehensive real estate analysis platform using AI agents for market analysis, valuation, investment strategy, and policy simulation.

## 📁 Project Structure

```
Faranic_RealEstate/
├── src/                          # Source code
│   ├── agents/                   # AI Agents
│   │   ├── core/                 # Core functionality agents
│   │   │   ├── __init__.py           # Makes 'core' a Python package
│   │   │   ├── data_ingest_agent.py    # Data ingestion and processing
│   │   │   ├── market_cycle_agent.py   # Market cycle analysis
│   │   │   ├── query_understanding_agent.py # Understand user query
│   │   │   ├── generate_report_agent.py  # Generate final report
│   │   │   └── ...
│   │   ├── analysis/             # Specialized analysis agents
│   │   │   ├── valuation_analysis.py # Property valuation
│   │   │   ├── macro_analysis.py # Macroeconomic analysis
│   │   │   ├── rental_market.py  # Rental market analysis
│   │   │   ├── investment_strategy.py # Investment recommendations
│   │   │   └── policy_simulation.py # Policy impact simulation
│   │   └── routing/              # Orchestration and routing
│   │       └── orchestrator.py   # Main workflow orchestrator
│   ├── models/                   # Data models and state management
│   │   └── state.py             # RISA state management
│   ├── config/                   # Configuration files
│   │   └── llm_config.py        # LLM configuration
│   └── utils/                    # Utility functions
│       ├── data_processing/      # Data processing utilities
│       └── visualization/        # Visualization utilities
├── data/                         # Data storage
│   ├── raw/                     # Raw input data
│   ├── processed/               # Processed data
│   └── external/                # External data sources
├── output/                       # Generated outputs
│   ├── reports/                 # Analysis reports
│   └── visualizations/          # Charts and graphs
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── docs/                         # Documentation
├── examples/                     # Usage examples
├── scripts/                      # Utility scripts
├── logs/                         # Application logs
├── requirements.txt              # Python dependencies
└── .env                         # Environment variables
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Analysis**
   ```python
   from src.agents import orchestrator
   from src.models import RISAState
   
   # Initialize state
   state = RISAState(user_query="Analyze Tehran real estate market")
   
   # Run analysis
   result = orchestrator(state)
   ```

## 🏗️ Architecture

### Core Agents
- **Data Ingest**: Processes various data sources (PDFs, APIs, databases)
- **Query Understanding**: Interprets user queries and determines analysis requirements
- **Market Cycle**: Analyzes current market cycle phase
- **Generate Report**: Creates comprehensive analysis reports

### Analysis Agents
- **Valuation Analysis**: Property and market valuation
- **Macro Analysis**: Macroeconomic factors affecting real estate
- **Rental Market**: Rental market trends and analysis
- **Investment Strategy**: Investment recommendations and strategies
- **Policy Simulation**: Impact analysis of policy changes

### Orchestration
- **Orchestrator**: Manages workflow execution and agent coordination
- **Smart Orchestrator**: AI-guided routing and execution planning

## 🔧 Configuration

The system supports multiple LLM providers:
- OpenAI GPT models
- Google Gemini
- Custom LLM configurations

Configure in `src/config/llm_config.py` or via environment variables.

## 📊 Data Sources

- Real estate market data
- Economic indicators
- Policy documents
- Property listings
- Rental market data

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run all tests
python -m pytest tests/
```

