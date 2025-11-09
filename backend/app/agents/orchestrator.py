"""
Multi-Agent Orchestrator
Routes queries to specialized agents and coordinates responses
"""
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
import re

from app.config import get_settings
from app.utils.rag_engine import RAGEngine
from app.agents.price_agent import PriceEstimationAgent
from app.agents.buying_power_agent import BuyingPowerAgent
from app.agents.market_agent import MarketInsightsAgent


class AgentOrchestrator:
    """
    Orchestrator that routes user queries to appropriate specialized agents
    """

    def __init__(self):
        """Initialize orchestrator and all agents"""
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.5,
            openai_api_key=self.settings.openai_api_key
        )

        # Initialize RAG engine
        self.rag_engine = RAGEngine()

        # Initialize specialized agents
        self.price_agent: Optional[PriceEstimationAgent] = None
        self.buying_power_agent: Optional[BuyingPowerAgent] = None
        self.market_agent: Optional[MarketInsightsAgent] = None

    async def initialize(self):
        """Initialize all components"""
        # Initialize RAG engine
        await self.rag_engine.initialize()

        # Initialize agents
        self.price_agent = PriceEstimationAgent(self.rag_engine)
        self.buying_power_agent = BuyingPowerAgent()
        self.market_agent = MarketInsightsAgent(self.rag_engine)

        # Optionally seed RAG with sample data
        await self._seed_sample_data()

    async def cleanup(self):
        """Cleanup resources"""
        pass

    async def _seed_sample_data(self):
        """Seed RAG engine with sample property and market data"""
        # Add sample property data
        sample_properties = [
            {
                "address": "123 Smith Street, Melbourne, VIC 3000",
                "suburb": "Melbourne",
                "state": "VIC",
                "postcode": "3000",
                "property_type": "Apartment",
                "bedrooms": 2,
                "bathrooms": 2,
                "parking": 1,
                "last_sale_price": 750000,
                "estimated_value": 820000
            },
            {
                "address": "45 Beach Road, Bondi, NSW 2026",
                "suburb": "Bondi",
                "state": "NSW",
                "postcode": "2026",
                "property_type": "House",
                "bedrooms": 4,
                "bathrooms": 3,
                "parking": 2,
                "land_size": 520,
                "last_sale_price": 2100000,
                "estimated_value": 2450000
            }
        ]

        for prop in sample_properties:
            self.rag_engine.add_property_data(prop)

        # Add sample market insights
        sample_insights = [
            {
                "title": "Melbourne Market Update Q4 2024",
                "location": "Melbourne, VIC",
                "date": "2024-10-01",
                "content": """
                The Melbourne property market has shown resilience in Q4 2024,
                with median house prices rising 2.3% quarterly. Strong population
                growth and limited supply continue to support prices, despite
                higher interest rates. Apartments are seeing renewed interest
                from first-home buyers taking advantage of stamp duty concessions.
                """,
                "key_points": [
                    "2.3% quarterly price growth",
                    "Strong population growth driving demand",
                    "First-home buyer activity increasing",
                    "Apartment market showing strength"
                ]
            },
            {
                "title": "Interest Rate Impact on Property Market",
                "location": "Australia",
                "date": "2024-11-01",
                "content": """
                The RBA's cash rate at 4.35% is influencing buyer behavior across
                Australia. While higher rates have moderated price growth in some
                areas, well-located properties continue to attract strong competition.
                Buyers with larger deposits are better positioned in the current market.
                """,
                "key_points": [
                    "RBA cash rate at 4.35%",
                    "Price growth moderation in outer suburbs",
                    "Strong competition for quality properties",
                    "Larger deposits provide competitive advantage"
                ]
            }
        ]

        for insight in sample_insights:
            self.rag_engine.add_market_insight(insight)

    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process user message and route to appropriate agent

        Args:
            message: User's message
            conversation_history: Previous conversation messages

        Returns:
            Agent response with data and metadata
        """
        # Classify the intent
        intent = await self._classify_intent(message, conversation_history or [])

        # Route to appropriate agent
        if intent["type"] == "price_estimation":
            response = await self._handle_price_estimation(message, intent)
        elif intent["type"] == "buying_power":
            response = await self._handle_buying_power(message, intent)
        elif intent["type"] == "market_insights":
            response = await self._handle_market_insights(message, intent)
        elif intent["type"] == "general":
            response = await self._handle_general_query(message)
        else:
            response = await self._handle_general_query(message)

        return response

    async def _classify_intent(
        self,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Classify user intent using LLM

        Returns:
            Intent classification with extracted parameters
        """
        # Build context from conversation history
        context = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-3:]  # Last 3 messages
        ]) if conversation_history else ""

        prompt = f"""
        Classify the following user query into one of these intents:
        1. price_estimation - User wants to know the price/value of a property
        2. buying_power - User wants to know what they can afford or calculate borrowing capacity
        3. market_insights - User wants market trends, insights, or general market information
        4. general - General questions or conversational queries

        Also extract relevant parameters:
        - address (for price_estimation)
        - financial_params (deposit, income, expenses for buying_power)
        - location (for market_insights)

        Conversation context:
        {context}

        User query: {message}

        Respond in this exact format:
        INTENT: [intent_type]
        PARAMS: [extracted parameters as key-value pairs]
        """

        response = await self.llm.ainvoke(prompt)
        content = response.content

        # Parse response
        intent_match = re.search(r'INTENT:\s*(\w+)', content)
        intent_type = intent_match.group(1).lower() if intent_match else "general"

        # Extract parameters based on intent
        params = {}

        if intent_type == "price_estimation":
            # Try to extract address
            address_patterns = [
                r'\d+\s+[\w\s]+(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Lane|Ln|Court|Ct)',
                r'at\s+([\w\s,]+)',
                r'for\s+([\w\s,]+)'
            ]
            for pattern in address_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    params["address"] = match.group(0).replace("at ", "").replace("for ", "")
                    break

        elif intent_type == "buying_power":
            # Extract financial figures
            deposit_match = re.search(r'\$?([\d,]+)k?\s*(?:deposit|down payment)', message, re.IGNORECASE)
            income_match = re.search(r'\$?([\d,]+)k?\s*(?:income|salary|earn)', message, re.IGNORECASE)

            if deposit_match:
                deposit_str = deposit_match.group(1).replace(',', '')
                params["deposit"] = float(deposit_str) * 1000 if 'k' in message.lower() else float(deposit_str)

            if income_match:
                income_str = income_match.group(1).replace(',', '')
                params["income"] = float(income_str) * 1000 if 'k' in message.lower() else float(income_str)

        elif intent_type == "market_insights":
            # Extract location
            location_match = re.search(r'(?:in|at|for)\s+([\w\s,]+?)(?:\s+market|\s+property|$)', message, re.IGNORECASE)
            if location_match:
                params["location"] = location_match.group(1).strip()

        return {
            "type": intent_type,
            "params": params,
            "original_message": message
        }

    async def _handle_price_estimation(
        self,
        message: str,
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle price estimation queries"""
        address = intent["params"].get("address")

        if not address:
            return {
                "message": "I'd be happy to estimate a property price for you! Could you please provide the full address? For example: '123 Smith Street, Melbourne VIC 3000'",
                "agent_used": "orchestrator",
                "data": None
            }

        # Call price estimation agent
        result = await self.price_agent.estimate_price(address)

        return {
            "message": result["explanation"],
            "agent_used": "price_estimation",
            "data": result,
            "sources": result.get("sources", [])
        }

    async def _handle_buying_power(
        self,
        message: str,
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle buying power queries"""
        params = intent["params"]

        # Check if we have minimum required parameters
        if not params.get("deposit") or not params.get("income"):
            return {
                "message": """I can help you calculate your buying power! To give you an accurate estimate, I'll need some information:

1. How much deposit do you have saved?
2. What's your annual income?
3. What are your monthly expenses? (optional)
4. Do you have any dependents? (optional)

For example: "I have a $100,000 deposit and earn $85,000 per year" """,
                "agent_used": "orchestrator",
                "data": None
            }

        # Call buying power agent with available params
        result = await self.buying_power_agent.calculate_buying_power(
            deposit=params.get("deposit", 100000),
            annual_income=params.get("income", 80000),
            monthly_expenses=params.get("expenses", 3000),
            other_income=params.get("other_income", 0),
            dependents=params.get("dependents", 0),
            employment_type=params.get("employment_type", "full_time"),
            existing_debts=params.get("existing_debts", 0)
        )

        return {
            "message": result["explanation"],
            "agent_used": "buying_power",
            "data": result,
            "sources": ["RBA", "Mortgage Calculator"]
        }

    async def _handle_market_insights(
        self,
        message: str,
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle market insights queries"""
        location = intent["params"].get("location")

        result = await self.market_agent.get_market_insights(location=location)

        return {
            "message": result["insights"],
            "agent_used": "market_insights",
            "data": result,
            "sources": result.get("sources", [])
        }

    async def _handle_general_query(self, message: str) -> Dict[str, Any]:
        """Handle general conversational queries"""
        prompt = f"""
        You are HomeWise AI, a friendly Australian property expert and chatbot.
        Answer the following question naturally and helpfully.

        If the user is asking how you can help, explain that you can:
        1. Estimate property prices for any Australian address
        2. Calculate their buying power and what they can afford
        3. Provide market insights and trends
        4. Answer questions about the property market

        User question: {message}

        Provide a helpful, friendly response:
        """

        response = await self.llm.ainvoke(prompt)

        return {
            "message": response.content,
            "agent_used": "general",
            "data": None,
            "sources": []
        }

    # Direct method calls for API endpoints

    async def estimate_property_price(
        self,
        address: str,
        property_type: Optional[str] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[int] = None,
        parking: Optional[int] = None,
        land_size: Optional[float] = None
    ) -> Dict[str, Any]:
        """Direct property price estimation"""
        return await self.price_agent.estimate_price(
            address=address,
            property_type=property_type,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking=parking,
            land_size=land_size
        )

    async def calculate_buying_power(
        self,
        deposit: float,
        annual_income: float,
        monthly_expenses: float,
        other_income: float = 0,
        dependents: int = 0,
        employment_type: str = "full_time",
        existing_debts: float = 0
    ) -> Dict[str, Any]:
        """Direct buying power calculation"""
        return await self.buying_power_agent.calculate_buying_power(
            deposit=deposit,
            annual_income=annual_income,
            monthly_expenses=monthly_expenses,
            other_income=other_income,
            dependents=dependents,
            employment_type=employment_type,
            existing_debts=existing_debts
        )

    async def get_market_insights(
        self,
        location: Optional[str] = None,
        property_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Direct market insights retrieval"""
        return await self.market_agent.get_market_insights(
            location=location,
            property_type=property_type
        )
