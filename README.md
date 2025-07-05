# Faranic Real Estate Multi-Agent System 🏠

A sophisticated AI-powered real estate investment advisory system that leverages multiple specialized agents to provide comprehensive market analysis and investment recommendations. The system supports both English and Persian languages and focuses primarily on the Iranian real estate market, particularly Tehran.

## 🌟 Features

- **Multi-Agent Architecture**: Coordinated system of specialized AI agents
- **Bilingual Support**: Full support for English and Persian languages with RTL text rendering
- **Real-Time Analysis**: Live web research and market data integration
- **Knowledge Base Integration**: Leverages internal real estate knowledge and market principles
- **Interactive Web Interface**: Streamlit-based user interface with live report generation
- **Comprehensive Reports**: Institutional-grade investment analysis reports
- **Streaming Output**: Real-time report generation with live updates

## 🏗️ System Architecture

### Core Components

1. **Main Orchestrator** (`main.py`)
   - Coordinates the multi-agent workflow
   - Handles language detection and processing
   - Manages streaming report generation

2. **Specialized Agents**
   - **Query Understanding Agent**: Analyzes user queries and creates structured work orders
   - **Strategic Advisor**: Provides comprehensive investment strategies and market analysis
   - **Generate Report Agent**: Creates professional investment reports
   - **Field Researcher**: Conducts real-time web research for market data

3. **Web Interface** (`streamlit_app.py`)
   - Interactive Streamlit application
   - Persian language support with Vazirmatn font
   - Real-time report streaming

### Agent Workflow

```
User Query → Query Understanding → Strategic Advisor → Report Generation
                    ↓                      ↓
               Work Order            Field Research +
                                   Knowledge Base
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- Other API keys for web search services (Tavily, Exa, etc.)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Faranic_RealState
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create a .env file with your API keys
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
EXA_API_KEY=your_exa_api_key
# Add other required API keys
```

### Running the Application

#### Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```

#### Command Line Interface
```bash
python main.py
```

## 📊 Usage Examples

### English Query Example
```
"I am an investor looking to buy an apartment in Tehran. My budget is around $500,000. I am looking for a 2-bedroom, 2-bathroom apartment with a gym. I prefer a newer building."
```

### Persian Query Example
```
"عوامل کلیدی و تعیین‌کننده در شروع و پایان هر یک از اپیزودهای رونق شدید، رونق اندک، رکود اندک، رکود شدید و چرخش بازار کدامند؟"
```

## 🎯 Supported Query Types

- **Investment Strategy**: Comprehensive investment recommendations
- **Market Analysis**: Market trends and conditions analysis
- **Property Valuation**: Property assessment and pricing
- **Risk Assessment**: Investment risk evaluation
- **Comparative Analysis**: Regional and property comparisons
- **Policy Impact**: Analysis of regulatory and policy effects

## 📁 Project Structure

```
Faranic_RealState/
├── main.py                 # Main orchestrator
├── streamlit_app.py        # Web interface
├── requirements.txt        # Dependencies
├── src/
│   ├── agents/
│   │   ├── specialists/    # Core agent implementations
│   │   ├── analysis/       # Analysis tools and models
│   │   ├── utils/          # Utility functions and tools
│   │   └── prompts.py      # Agent prompts and templates
│   └── configs/            # Configuration files
├── data/
│   ├── raw/               # Raw data files
│   └── processed/         # Processed data and indices
└── tests/                 # Test files
```

## 🔧 Configuration

The system uses various configuration files and environment variables:

- **LLM Configuration**: OpenAI GPT-4 as the primary model
- **Search APIs**: Tavily, Exa, and other search services
- **Knowledge Base**: FAISS vector database for document retrieval
- **Language Support**: Automatic language detection and processing

## 📈 Key Technologies

- **LangChain**: Framework for building AI applications
- **LangGraph**: Multi-agent orchestration
- **Streamlit**: Web interface framework
- **FAISS**: Vector database for knowledge retrieval
- **OpenAI**: Primary language model
- **Pydantic**: Data validation and serialization
- **AsyncIO**: Asynchronous processing

## 🌍 Language Support

The system provides comprehensive bilingual support:

- **English**: Full functionality with international real estate focus
- **Persian/Farsi**: Complete RTL support with Persian-specific prompts and formatting
- **Automatic Detection**: Language detection based on input text
- **Localized Output**: Reports and responses in the detected language

## 📊 Output Formats

### Report Types
1. **Basic Reports**: Simple, easy-to-understand summaries
2. **Standard Reports**: Professional analysis with key metrics
3. **Sophisticated Reports**: Institutional-grade comprehensive analysis

### Report Sections
- Executive Summary
- Client Profile & Objectives
- Market Analysis & Principles
- Investment Recommendations
- Risk Assessment
- Next Steps & Disclaimers

## 🔍 Data Sources

The system integrates multiple data sources:
- Real-time web research
- Internal knowledge base (PDF documents)
- Market data APIs
- Government and institutional reports

## ⚠️ Important Notes

- The system is primarily designed for Iranian real estate market analysis
- Requires valid API keys for full functionality
- Real estate investments carry risks - reports are for informational purposes only
- Always consult with local legal and financial advisors

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions, please open an issue in the GitHub repository.

---

**Disclaimer**: This system provides informational analysis only and does not constitute financial advice. Real estate investments carry risks, and users should conduct their own due diligence and consult with qualified professionals before making investment decisions.
