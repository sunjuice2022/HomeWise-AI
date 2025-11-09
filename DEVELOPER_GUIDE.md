# Developer Guide - HomeWise AI

This guide provides detailed information for developers working on the HomeWise AI project.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Key Concepts](#key-concepts)
5. [Adding New Features](#adding-new-features)
6. [Testing](#testing)
7. [API Development](#api-development)
8. [Frontend Development](#frontend-development)
9. [Troubleshooting](#troubleshooting)

## Project Overview

HomeWise AI uses a multi-agent architecture with RAG (Retrieval-Augmented Generation) to provide property insights. The system consists of:

- **Backend**: FastAPI with LangChain for AI orchestration
- **Frontend**: React with Material-UI
- **AI**: OpenAI GPT-4 with specialized agents
- **Data**: ChromaDB for vector storage, PostgreSQL for relational data

## Development Setup

### Prerequisites

```bash
# Check versions
python --version  # Should be 3.9+
node --version    # Should be 16+
docker --version  # Optional but recommended
```

### Initial Setup

```bash
# 1. Clone repository (if needed)
git clone <repository-url>
cd HomeWiseAI

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY

cp frontend/.env.example frontend/.env
# Edit if needed
```

### Running Locally

#### Option 1: Docker (Recommended)

```bash
docker-compose up -d
```

#### Option 2: Manual

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m app.main
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

## Project Structure

```
backend/
├── app/
│   ├── agents/           # AI agents
│   │   ├── orchestrator.py      # Main orchestrator
│   │   ├── price_agent.py       # Price estimation
│   │   ├── buying_power_agent.py # Affordability
│   │   └── market_agent.py      # Market insights
│   ├── services/         # External API integrations
│   │   ├── domain_api.py        # Domain.com.au
│   │   ├── rba_api.py           # Reserve Bank
│   │   └── abs_api.py           # Bureau of Statistics
│   ├── utils/            # Utilities
│   │   ├── rag_engine.py        # Vector search
│   │   └── calculators.py       # Financial calculations
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx         # Chat UI
│   │   ├── PropertySearch.jsx        # Price estimator
│   │   └── BuyingPowerCalculator.jsx # Calculator
│   ├── App.js            # Main app
│   └── index.js          # Entry point
└── package.json
```

## Key Concepts

### 1. Multi-Agent System

The system uses specialized agents coordinated by an orchestrator:

```python
# backend/app/agents/orchestrator.py

async def process_message(self, message: str):
    # 1. Classify intent
    intent = await self._classify_intent(message)

    # 2. Route to appropriate agent
    if intent["type"] == "price_estimation":
        return await self.price_agent.estimate_price(...)
    elif intent["type"] == "buying_power":
        return await self.buying_power_agent.calculate(...)
    # ...
```

### 2. RAG (Retrieval-Augmented Generation)

RAG enhances AI responses with relevant data:

```python
# backend/app/utils/rag_engine.py

# Add data
rag_engine.add_property_data({
    "address": "123 Main St",
    "price": 850000,
    # ...
})

# Search
results = await rag_engine.search_similar_properties(
    query="3 bedroom house in Melbourne",
    k=5
)
```

### 3. Pydantic Models

All API requests/responses use Pydantic for validation:

```python
# backend/app/models/schemas.py

class PropertyPriceRequest(BaseModel):
    address: str
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = Field(None, ge=0, le=10)
```

## Adding New Features

### Adding a New Agent

1. **Create Agent File**

```python
# backend/app/agents/new_agent.py

from langchain_openai import ChatOpenAI
from app.config import get_settings

class NewAgent:
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.3
        )

    async def process(self, input_data):
        # Your agent logic here
        response = await self.llm.ainvoke(prompt)
        return response.content
```

2. **Register in Orchestrator**

```python
# backend/app/agents/orchestrator.py

def __init__(self):
    # ...existing code...
    self.new_agent = NewAgent()

async def _classify_intent(self, message):
    # Add new intent type
    if "keyword" in message.lower():
        return {"type": "new_feature", "params": {}}
```

3. **Add API Endpoint**

```python
# backend/app/main.py

@app.post("/api/new-feature")
async def new_feature(request: NewFeatureRequest):
    result = await orchestrator.new_agent.process(request)
    return NewFeatureResponse(**result)
```

### Adding External API Integration

1. **Create Service**

```python
# backend/app/services/new_api.py

import httpx
from app.config import get_settings

class NewAPIService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.new_api_key

    async def fetch_data(self, params):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.example.com/data",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params=params
            )
            return response.json()
```

2. **Add Configuration**

```python
# backend/app/config.py

class Settings(BaseSettings):
    # ...existing settings...
    new_api_key: str = ""
```

3. **Update .env.example**

```bash
# backend/.env.example
NEW_API_KEY=your-new-api-key
```

### Adding Frontend Component

1. **Create Component**

```jsx
// frontend/src/components/NewFeature.jsx

import React, { useState } from 'react';
import { Paper, TextField, Button } from '@mui/material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const NewFeature = () => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    const response = await axios.post(
      `${API_URL}/api/new-feature`,
      { input }
    );
    setResult(response.data);
  };

  return (
    <Paper>
      <TextField value={input} onChange={e => setInput(e.target.value)} />
      <Button onClick={handleSubmit}>Submit</Button>
      {result && <div>{JSON.stringify(result)}</div>}
    </Paper>
  );
};

export default NewFeature;
```

2. **Add to App**

```jsx
// frontend/src/App.js

import NewFeature from './components/NewFeature';

function App() {
  return (
    // ...
    <Tab label="New Feature" />
    // ...
    <TabPanel value={activeTab} index={3}>
      <NewFeature />
    </TabPanel>
  );
}
```

## Testing

### Backend Testing

```bash
cd backend
source venv/bin/activate

# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_agents.py -v
```

### Create Test Files

```python
# backend/tests/test_agents.py

import pytest
from app.agents.price_agent import PriceEstimationAgent
from app.utils.rag_engine import RAGEngine

@pytest.mark.asyncio
async def test_price_estimation():
    rag = RAGEngine()
    await rag.initialize()

    agent = PriceEstimationAgent(rag)
    result = await agent.estimate_price("123 Test St, Melbourne VIC 3000")

    assert result["estimated_price"] > 0
    assert "address" in result
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm test

# With coverage
npm test -- --coverage
```

## API Development

### Adding New Endpoint

1. **Define Request/Response Models**

```python
# backend/app/models/schemas.py

class NewRequest(BaseModel):
    param1: str
    param2: int = Field(ge=0)

class NewResponse(BaseModel):
    result: str
    data: Dict[str, Any]
```

2. **Create Endpoint**

```python
# backend/app/main.py

@app.post("/api/new-endpoint", response_model=NewResponse)
async def new_endpoint(request: NewRequest):
    """
    Endpoint description

    - **param1**: Description
    - **param2**: Description
    """
    try:
        result = await orchestrator.process_new_request(request)
        return NewResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

3. **Test Endpoint**

```bash
# Using curl
curl -X POST http://localhost:8000/api/new-endpoint \
  -H "Content-Type: application/json" \
  -d '{"param1": "value", "param2": 42}'

# Or visit Swagger UI
open http://localhost:8000/docs
```

### API Best Practices

- Use Pydantic models for validation
- Add proper error handling
- Document with docstrings
- Use async/await for I/O operations
- Return appropriate HTTP status codes
- Add request/response examples in docstrings

## Frontend Development

### Component Structure

```jsx
// Standard component template

import React, { useState, useEffect } from 'react';
import { Paper, Box, Typography } from '@mui/material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const MyComponent = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch data on mount
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/endpoint`);
      setData(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Typography>Loading...</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Paper>
      {/* Your component UI */}
    </Paper>
  );
};

export default MyComponent;
```

### Styling with MUI

```jsx
// Use sx prop for inline styles
<Box sx={{
  p: 2,              // padding
  m: 1,              // margin
  bgcolor: '#fff',   // background color
  borderRadius: 2    // border radius
}}>
  Content
</Box>

// Use theme
import { useTheme } from '@mui/material/styles';

const theme = useTheme();
<Box sx={{ color: theme.palette.primary.main }}>
```

## Troubleshooting

### Common Issues

#### Backend Won't Start

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
cd backend
python -m app.main  # Use -m flag
```

**Problem**: `OpenAI API key not found`

**Solution**:
```bash
# Check .env file
cat backend/.env | grep OPENAI_API_KEY

# Set manually
export OPENAI_API_KEY=sk-your-key
```

#### Frontend Issues

**Problem**: `Cannot connect to backend`

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check REACT_APP_API_URL in .env
cat frontend/.env
```

**Problem**: CORS errors

**Solution**:
```python
# backend/app/config.py
cors_origins: str = "http://localhost:3000,http://localhost:3001"
```

#### RAG/Vector Store Issues

**Problem**: ChromaDB errors

**Solution**:
```bash
# Clear and reinitialize
rm -rf backend/data/chroma_db
# Restart backend - will reinitialize
```

### Debug Mode

Enable debug logging:

```python
# backend/app/main.py

import logging
logging.basicConfig(level=logging.DEBUG)

# In agents
print(f"Debug: {variable}")
```

```jsx
// frontend
console.log('Debug:', variable);
```

## Code Style

### Python (Backend)

```python
# Use type hints
def calculate_price(deposit: float, income: float) -> Dict[str, Any]:
    pass

# Use async/await for I/O
async def fetch_data() -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Use Pydantic models
class Request(BaseModel):
    field: str

# Document functions
def function(param: str) -> str:
    """
    Brief description

    Args:
        param: Parameter description

    Returns:
        Return value description
    """
    pass
```

### JavaScript (Frontend)

```jsx
// Use functional components
const MyComponent = () => {
  // Component logic
};

// Use descriptive names
const handleSubmit = async () => {
  // Handler logic
};

// Destructure props
const MyComponent = ({ data, onUpdate }) => {
  // ...
};
```

## Deployment

### Production Build

```bash
# Backend - use production server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend - build static files
cd frontend
npm run build
# Serve build/ directory with nginx or similar
```

### Environment Variables

Production:
```bash
# backend/.env
APP_ENV=production
DEBUG=false
OPENAI_API_KEY=sk-real-key
DATABASE_URL=postgresql://...
```

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [React Documentation](https://react.dev/)
- [Material-UI Documentation](https://mui.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## Getting Help

1. Check this guide and [QUICKSTART.md](QUICKSTART.md)
2. Review [ARCHITECTURE.md](ARCHITECTURE.md)
3. Check API docs at http://localhost:8000/docs
4. Review error logs
5. Create an issue on GitHub

---

Happy coding! 🚀
