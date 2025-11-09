"""
Main FastAPI application for HomeWise AI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.config import get_settings
from app.models.schemas import (
    ChatRequest, ChatResponse,
    PropertyPriceRequest, PropertyPriceResponse,
    BuyingPowerRequest, BuyingPowerResponse,
    MarketInsightsResponse
)
from app.agents.orchestrator import AgentOrchestrator


settings = get_settings()

# Initialize orchestrator as global variable
orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global orchestrator
    # Startup
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    yield
    # Shutdown
    await orchestrator.cleanup()


# Initialize FastAPI app
app = FastAPI(
    title="HomeWise AI API",
    description="AI-powered property price estimation and buying power chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to HomeWise AI API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.app_env
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles conversational queries

    This endpoint routes the user's message through the multi-agent orchestrator
    which determines the appropriate specialized agent to handle the request.
    """
    try:
        response = await orchestrator.process_message(
            message=request.message,
            conversation_history=request.conversation_history or []
        )

        return ChatResponse(
            message=response["message"],
            data=response.get("data"),
            agent_used=response.get("agent_used"),
            sources=response.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/estimate-price", response_model=PropertyPriceResponse)
async def estimate_price(request: PropertyPriceRequest):
    """
    Estimate property price for a given address

    Uses RAG and real-time data from multiple sources to provide
    accurate property price estimations.
    """
    try:
        result = await orchestrator.estimate_property_price(
            address=request.address,
            property_type=request.property_type,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            parking=request.parking,
            land_size=request.land_size
        )

        return PropertyPriceResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate-buying-power", response_model=BuyingPowerResponse)
async def calculate_buying_power(request: BuyingPowerRequest):
    """
    Calculate user's buying power and affordability

    Analyzes financial parameters to determine what the user can afford,
    including loan amount, monthly repayments, and property price range.
    """
    try:
        result = await orchestrator.calculate_buying_power(
            deposit=request.deposit,
            annual_income=request.annual_income,
            monthly_expenses=request.monthly_expenses,
            other_income=request.other_income,
            dependents=request.dependents,
            employment_type=request.employment_type,
            existing_debts=request.existing_debts
        )

        return BuyingPowerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-insights", response_model=MarketInsightsResponse)
async def get_market_insights(location: str = None, property_type: str = None):
    """
    Get current market insights and trends

    Provides analysis of market conditions, trends, and factors
    affecting property prices in specific locations or Australia-wide.
    """
    try:
        result = await orchestrator.get_market_insights(
            location=location,
            property_type=property_type
        )

        return MarketInsightsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "message": "An internal error occurred",
            "detail": str(exc) if settings.debug else "Internal server error"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
