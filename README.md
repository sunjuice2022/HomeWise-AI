# HomeWise AI - Property Price & Buying Power Chatbot

## Project Overview

HomeWise AI is a conversational AI chatbot that empowers Australian home buyers and property investors with accurate, data-driven insights. The system uses AI to estimate real-time property values, understand their financial capacity, and make informed decisions about buying or investing in properties.

## Core Technologies

- **RAG (Retrieval-Augmented Generation)**: For accurate property data retrieval
- **Multi-Agent Orchestration**: Specialized agents for different tasks
- **External APIs**: Integration with domain.com.au, realestate.com.au, ABS, RBA, CoreLogic
- **LangChain**: For agent orchestration and RAG implementation
- **FastAPI**: Backend API framework
- **React**: Frontend web interface
- **OpenAI GPT-4**: Primary LLM for conversational interface

## Features

- 🏠 **Real-time Property Price Estimation**: Instant market price estimates for any Australian address
- 💰 **Buying Power Calculator**: Personalized affordability analysis based on deposit, income, and financial situation
- 📊 **Market Insights**: Natural, conversational explanations about housing market trends
- 🤖 **Multi-Agent System**: Specialized AI agents working together for accurate responses
- 📈 **Real-time Data**: Integration with trusted Australian property and economic data sources

## Project Structure

```
HomeWiseAI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Configuration settings
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py     # Multi-agent orchestrator
│   │   │   ├── price_agent.py      # Property price estimation agent
│   │   │   ├── buying_power_agent.py # Affordability calculation agent
│   │   │   ├── market_agent.py     # Market insights agent
│   │   │   └── data_retrieval_agent.py # RAG-based data retrieval
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── domain_api.py       # Domain.com.au integration
│   │   │   ├── realestate_api.py   # RealEstate.com.au integration
│   │   │   ├── abs_api.py          # ABS data integration
│   │   │   ├── rba_api.py          # RBA data integration
│   │   │   └── corelogic_api.py    # CoreLogic integration
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py          # Pydantic models
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── rag_engine.py       # RAG implementation
│   │       └── calculators.py      # Financial calculators
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── PropertySearch.jsx
│   │   │   └── BuyingPowerForm.jsx
│   │   ├── App.jsx
│   │   ├── index.js
│   │   └── styles/
│   ├── package.json
│   └── .env.example
├── data/
│   └── knowledge_base/             # Vector store for RAG
├── docker-compose.yml
└── README.md
```

## Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- OpenAI API Key
- API keys for property data providers (Domain, RealEstate.com.au, CoreLogic)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python -m app.main
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your backend URL
npm start
```

### Docker Setup

```bash
docker-compose up -d
```

## Environment Variables

### Backend (.env)

```
OPENAI_API_KEY=your_openai_api_key
DOMAIN_API_KEY=your_domain_api_key
REALESTATE_API_KEY=your_realestate_api_key
CORELOGIC_API_KEY=your_corelogic_api_key
DATABASE_URL=postgresql://user:password@localhost/homewise
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment
```

### Frontend (.env)

```
REACT_APP_API_URL=http://localhost:8000
```

## Usage

1. Start the backend server: `cd backend && python -m app.main`
2. Start the frontend: `cd frontend && npm start`
3. Open browser to `http://localhost:3000`
4. Start chatting with HomeWise AI!

### Example Conversations

**Property Price Estimation:**
- "What's the current market price for 123 Smith Street, Melbourne VIC 3000?"
- "How much is a 3-bedroom house in Bondi worth?"

**Buying Power:**
- "I have a $100,000 deposit and earn $85,000 per year. What can I afford?"
- "Can I buy a property in Sydney with $150k deposit and $120k household income?"

**Market Insights:**
- "What's happening in the Brisbane property market?"
- "How are interest rates affecting property prices?"

## API Endpoints

### POST /api/chat
Send a message to the chatbot and receive AI-powered responses.

### POST /api/estimate-price
Get property price estimation for a specific address.

### POST /api/calculate-buying-power
Calculate affordability based on financial parameters.

### GET /api/market-insights
Get current market trends and insights.

## Architecture

The system uses a multi-agent architecture:

1. **Orchestrator Agent**: Routes queries to appropriate specialized agents
2. **Price Estimation Agent**: Calculates property values using RAG and real-time data
3. **Buying Power Agent**: Analyzes financial capacity and affordability
4. **Market Insights Agent**: Provides contextual market information
5. **Data Retrieval Agent**: Fetches real-time data from external sources

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Formatting

```bash
black backend/app
flake8 backend/app
```

## License

MIT License

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## Support

For issues and questions, please open a GitHub issue or contact support@homewise.ai
