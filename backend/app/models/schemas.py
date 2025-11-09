"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PropertyType(str, Enum):
    """Property type enumeration"""
    HOUSE = "house"
    APARTMENT = "apartment"
    TOWNHOUSE = "townhouse"
    UNIT = "unit"
    VILLA = "villa"
    LAND = "land"


class EmploymentType(str, Enum):
    """Employment type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CASUAL = "casual"
    SELF_EMPLOYED = "self_employed"
    CONTRACT = "contract"


class ConversationMessage(BaseModel):
    """Single message in conversation history"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message", min_length=1)
    conversation_history: Optional[List[ConversationMessage]] = Field(
        default=None,
        description="Previous conversation messages"
    )
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="AI assistant's response")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured data (prices, calculations, etc.)"
    )
    agent_used: Optional[str] = Field(
        default=None,
        description="Which specialized agent handled the request"
    )
    sources: List[str] = Field(
        default=[],
        description="Data sources used for the response"
    )
    timestamp: datetime = Field(default_factory=datetime.now)


class PropertyPriceRequest(BaseModel):
    """Request model for property price estimation"""
    address: str = Field(..., description="Full property address")
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = Field(None, ge=0, le=10)
    bathrooms: Optional[int] = Field(None, ge=0, le=10)
    parking: Optional[int] = Field(None, ge=0, le=10)
    land_size: Optional[float] = Field(None, description="Land size in square meters")


class PropertyPriceResponse(BaseModel):
    """Response model for property price estimation"""
    address: str
    estimated_price: float = Field(..., description="Estimated property value")
    price_range_min: float = Field(..., description="Minimum estimated value")
    price_range_max: float = Field(..., description="Maximum estimated value")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in estimation")
    comparable_properties: List[Dict[str, Any]] = Field(
        default=[],
        description="Similar properties used for comparison"
    )
    market_trends: Dict[str, Any] = Field(
        default={},
        description="Relevant market trend data"
    )
    sources: List[str] = Field(default=[], description="Data sources")
    explanation: str = Field(..., description="Natural language explanation")
    last_updated: datetime = Field(default_factory=datetime.now)


class BuyingPowerRequest(BaseModel):
    """Request model for buying power calculation"""
    deposit: float = Field(..., ge=0, description="Available deposit amount")
    annual_income: float = Field(..., ge=0, description="Annual gross income")
    monthly_expenses: float = Field(..., ge=0, description="Monthly expenses")
    other_income: Optional[float] = Field(0, ge=0, description="Other monthly income")
    dependents: int = Field(0, ge=0, le=20, description="Number of dependents")
    employment_type: EmploymentType
    existing_debts: Optional[float] = Field(0, ge=0, description="Existing debt repayments")


class BuyingPowerResponse(BaseModel):
    """Response model for buying power calculation"""
    max_loan_amount: float = Field(..., description="Maximum loan amount")
    max_property_price: float = Field(..., description="Maximum property price")
    monthly_repayment: float = Field(..., description="Estimated monthly repayment")
    interest_rate: float = Field(..., description="Current interest rate used")
    loan_to_value_ratio: float = Field(..., description="LVR percentage")
    stamp_duty: float = Field(..., description="Estimated stamp duty")
    total_upfront_costs: float = Field(..., description="Total upfront costs including deposit")
    affordability_rating: str = Field(..., description="Affordability assessment")
    recommendations: List[str] = Field(default=[], description="Personalized recommendations")
    explanation: str = Field(..., description="Natural language explanation")
    assumptions: Dict[str, Any] = Field(default={}, description="Calculation assumptions")


class MarketInsightsResponse(BaseModel):
    """Response model for market insights"""
    location: Optional[str] = None
    property_type: Optional[str] = None
    current_trends: Dict[str, Any] = Field(
        default={},
        description="Current market trends"
    )
    price_movements: Dict[str, Any] = Field(
        default={},
        description="Recent price movement data"
    )
    interest_rates: Dict[str, Any] = Field(
        default={},
        description="Current interest rate information"
    )
    economic_indicators: Dict[str, Any] = Field(
        default={},
        description="Relevant economic indicators"
    )
    forecast: Optional[str] = Field(
        None,
        description="Market forecast and predictions"
    )
    insights: str = Field(..., description="Natural language insights")
    sources: List[str] = Field(default=[], description="Data sources")
    last_updated: datetime = Field(default_factory=datetime.now)


class PropertyData(BaseModel):
    """Property data for RAG storage"""
    address: str
    suburb: str
    state: str
    postcode: str
    property_type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking: Optional[int] = None
    land_size: Optional[float] = None
    last_sale_price: Optional[float] = None
    last_sale_date: Optional[datetime] = None
    estimated_value: Optional[float] = None
    metadata: Dict[str, Any] = Field(default={})
