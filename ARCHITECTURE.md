# HomeWise AI - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                     (React Frontend - Port 3000)                │
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Chat Interface│  │Property Price│  │Buying Power Calc.  │  │
│  │               │  │  Estimator   │  │                    │  │
│  └───────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (Port 8000)                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  API Layer (main.py)                      │ │
│  │   /api/chat  |  /api/estimate-price  |  /api/buying-power│ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │          AGENT ORCHESTRATOR (orchestrator.py)             │ │
│  │                                                           │ │
│  │  • Intent Classification                                 │ │
│  │  • Agent Routing                                         │ │
│  │  • Response Coordination                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ▼                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │Price Agent   │  │Buying Power  │  │Market Insights Agent │ │
│  │              │  │    Agent     │  │                      │ │
│  │• RAG Search  │  │• Calculator  │  │• Trend Analysis      │ │
│  │• Domain API  │  │• RBA Rates   │  │• RAG Context         │ │
│  │• Comparables │  │• Serviceability│ │• Economic Data      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│                              ▼                                  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  RAG Engine  │  │External APIs │  │   Calculators        │ │
│  │              │  │              │  │                      │ │
│  │• ChromaDB    │  │• Domain.com  │  │• Buying Power        │ │
│  │• Embeddings  │  │• RBA         │  │• Stamp Duty          │ │
│  │• Vector      │  │• ABS         │  │• LVR/LMI             │ │
│  │  Search      │  │• CoreLogic   │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ PostgreSQL   │  │   Redis      │  │   Vector Store       │ │
│  │   (Future)   │  │  (Caching)   │  │   (ChromaDB)         │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Multi-Agent System Flow

```
User Query → Orchestrator → Intent Classification
                    │
                    ├─→ "price_estimation"
                    │   └→ Price Agent
                    │       ├─→ Parse Address
                    │       ├─→ RAG Search (Comparables)
                    │       ├─→ Domain API
                    │       ├─→ Calculate Estimate
                    │       └─→ Generate Explanation
                    │
                    ├─→ "buying_power"
                    │   └→ Buying Power Agent
                    │       ├─→ Get Current Rates (RBA)
                    │       ├─→ Calculate Max Loan
                    │       ├─→ Calculate Stamp Duty
                    │       ├─→ Assess Affordability
                    │       └─→ Generate Recommendations
                    │
                    ├─→ "market_insights"
                    │   └→ Market Insights Agent
                    │       ├─→ Get Market Data
                    │       ├─→ Get Economic Indicators
                    │       ├─→ RAG Search (Insights)
                    │       └─→ Generate Analysis
                    │
                    └─→ "general"
                        └→ Conversational Response
```

## RAG (Retrieval-Augmented Generation) Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Ingestion                          │
│                                                             │
│  Property Data ──→ Text Splitting ──→ Embedding ──→ Store  │
│  Market Insights ─→ Chunking ──────→ Vectors ───→ ChromaDB │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Query Processing                        │
│                                                             │
│  User Query ──→ Embed ──→ Similarity Search ──→ Retrieve   │
│                                                  Top K Docs │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Response Generation                      │
│                                                             │
│  Context + Query ──→ LLM (GPT-4) ──→ Natural Language      │
│                                       Response              │
└─────────────────────────────────────────────────────────────┘
```

## Buying Power Calculation Flow

```
User Inputs
  ├─ Deposit
  ├─ Annual Income
  ├─ Monthly Expenses
  ├─ Dependents
  └─ Employment Type
        ▼
┌─────────────────────────────────────┐
│  Calculate Maximum Loan             │
│  ├─ Calculate Surplus Income        │
│  ├─ Apply Employment Multiplier     │
│  ├─ Stress Test (Rate + 3%)         │
│  ├─ Apply Serviceability Rules      │
│  └─ Check Income Multiple Cap (6x)  │
└─────────────────────────────────────┘
        ▼
┌─────────────────────────────────────┐
│  Calculate Property Affordability   │
│  ├─ Max Property = Loan + Deposit   │
│  ├─ Calculate LVR                   │
│  ├─ Estimate LMI (if LVR > 80%)     │
│  ├─ Calculate Stamp Duty (by state) │
│  └─ Total Upfront Costs             │
└─────────────────────────────────────┘
        ▼
┌─────────────────────────────────────┐
│  Generate Recommendations           │
│  ├─ Affordability Rating            │
│  ├─ Debt-to-Income Ratio            │
│  ├─ Personalized Advice             │
│  └─ Natural Language Explanation    │
└─────────────────────────────────────┘
```

## Property Price Estimation Flow

```
User Input: Address + Property Details
        ▼
┌─────────────────────────────────────┐
│  Parse Address                      │
│  └─ Extract: Suburb, State, etc.    │
└─────────────────────────────────────┘
        ▼
┌─────────────────────────────────────┐
│  Multi-Source Data Gathering        │
│  ├─ RAG: Similar Properties         │
│  ├─ Domain API: Recent Sales        │
│  └─ Suburb Statistics               │
└─────────────────────────────────────┘
        ▼
┌─────────────────────────────────────┐
│  Price Calculation                  │
│  ├─ Domain Estimate (40% weight)    │
│  ├─ Suburb Median (30% weight)      │
│  │   └─ Adjust for bedrooms         │
│  └─ Comparables (30% weight)        │
└─────────────────────────────────────┘
        ▼
┌─────────────────────────────────────┐
│  Generate Response                  │
│  ├─ Estimated Price ± Range         │
│  ├─ Confidence Score                │
│  ├─ Market Trends                   │
│  └─ Natural Language Explanation    │
└─────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│  User    │
└────┬─────┘
     │ HTTP Request
     ▼
┌──────────┐
│ Frontend │ React Components
│  (React) │
└────┬─────┘
     │ API Call
     ▼
┌──────────┐
│ FastAPI  │ Routing & Validation
│    API   │
└────┬─────┘
     │
     ▼
┌──────────┐
│Orchestr- │ Intent Classification
│  ator    │ & Routing
└────┬─────┘
     │
     ├──────────┬──────────┬──────────┐
     ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│ Price   ││ Buying  ││ Market  ││ General │
│ Agent   ││ Power   ││ Insights││ Chat    │
│         ││ Agent   ││ Agent   ││         │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘
     │          │          │          │
     │ ┌────────┴──────────┴──────────┘
     │ │
     ▼ ▼
┌──────────────────────────────────────┐
│   Supporting Services & Utils        │
│  ┌──────┐ ┌──────┐ ┌──────────────┐ │
│  │ RAG  │ │ APIs │ │ Calculators  │ │
│  └──────┘ └──────┘ └──────────────┘ │
└──────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│          Data Storage                │
│  ┌──────┐ ┌──────┐ ┌──────────────┐ │
│  │Vector│ │Cache │ │   Database   │ │
│  │ DB   │ │      │ │              │ │
│  └──────┘ └──────┘ └──────────────┘ │
└──────────────────────────────────────┘
```

## Technology Stack Details

### Backend Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Web Framework | FastAPI | High-performance async API |
| AI Orchestration | LangChain | Agent coordination & RAG |
| LLM | OpenAI GPT-4 | Natural language processing |
| Vector DB | ChromaDB | Semantic search |
| Embeddings | OpenAI text-embedding-3-small | Text vectorization |
| Validation | Pydantic | Request/response validation |
| Server | Uvicorn | ASGI server |

### Frontend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18 | UI framework |
| UI Library | Material-UI (MUI) | Component library |
| HTTP Client | Axios | API communication |
| State | React Hooks | State management |
| Styling | Emotion (via MUI) | CSS-in-JS |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containers | Docker | Application containerization |
| Orchestration | Docker Compose | Multi-container management |
| Database | PostgreSQL | Relational data (future) |
| Cache | Redis | Response caching |

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Security Layers                       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  1. API Key Management                            │ │
│  │     • Environment Variables                       │ │
│  │     • Never in Code                               │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  2. Input Validation                              │ │
│  │     • Pydantic Models                             │ │
│  │     • Type Checking                               │ │
│  │     • Range Validation                            │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  3. CORS Configuration                            │ │
│  │     • Allowed Origins                             │ │
│  │     • Credentials Handling                        │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  4. Error Handling                                │ │
│  │     • Safe Error Messages                         │ │
│  │     • Debug Mode Control                          │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Load balancer ready
- Database connection pooling
- Redis for distributed caching

### Vertical Scaling
- Async/await for I/O operations
- Vector similarity search optimization
- Efficient data structures
- Response caching

### Performance Optimizations
- RAG vector indexing
- API response caching
- Connection pooling
- Lazy loading in frontend
- Code splitting

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Production Deployment                   │
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │  Load       │      │   CDN       │                 │
│  │  Balancer   │      │             │                 │
│  └──────┬──────┘      └──────┬──────┘                 │
│         │                     │                        │
│         ▼                     ▼                        │
│  ┌─────────────────┐   ┌─────────────────┐           │
│  │  Backend        │   │  Frontend       │           │
│  │  (Containers)   │   │  (Static)       │           │
│  │  ├─ API 1       │   │                 │           │
│  │  ├─ API 2       │   └─────────────────┘           │
│  │  └─ API N       │                                  │
│  └────────┬────────┘                                  │
│           │                                           │
│           ▼                                           │
│  ┌─────────────────────────────────────┐             │
│  │         Data Layer                  │             │
│  │  ┌────────┐  ┌────────┐  ┌────────┐│             │
│  │  │  DB    │  │ Redis  │  │ Vector ││             │
│  │  │        │  │        │  │   DB   ││             │
│  │  └────────┘  └────────┘  └────────┘│             │
│  └─────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Development Workflow

```
┌─────────────────────────────────────────────────────────┐
│  Local Development                                      │
│                                                         │
│  Developer ──→ Code Change                             │
│      │                                                  │
│      ├──→ Backend (Python)                             │
│      │    └─ Hot Reload (uvicorn --reload)             │
│      │                                                  │
│      └──→ Frontend (React)                             │
│           └─ Hot Reload (npm start)                    │
│                                                         │
│  Docker Compose ──→ Full Stack Testing                 │
│      └─ All services in containers                     │
└─────────────────────────────────────────────────────────┘
```

---

This architecture is designed to be:
- **Scalable**: Stateless design, horizontal scaling ready
- **Maintainable**: Clear separation of concerns, modular design
- **Extensible**: Easy to add new agents, APIs, and features
- **Performant**: Async operations, caching, vector search
- **Secure**: Environment-based config, input validation, CORS
