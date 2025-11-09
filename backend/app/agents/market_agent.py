"""
Market Insights Agent
"""
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.services.domain_api import DomainAPIService
from app.services.rba_api import RBAAPIService
from app.services.abs_api import ABSAPIService
from app.utils.rag_engine import RAGEngine


class MarketInsightsAgent:
    """Agent specialized in providing market insights and trends"""

    def __init__(self, rag_engine: RAGEngine):
        """Initialize market insights agent"""
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.4,
            openai_api_key=self.settings.openai_api_key
        )
        self.rag_engine = rag_engine
        self.domain_service = DomainAPIService()
        self.rba_service = RBAAPIService()
        self.abs_service = ABSAPIService()

    async def get_market_insights(
        self,
        location: Optional[str] = None,
        property_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive market insights

        Args:
            location: Specific location (suburb, state) or None for national
            property_type: Type of property or None for all types

        Returns:
            Market insights and analysis
        """
        # Parse location if provided
        suburb = None
        state = None
        if location:
            parts = [p.strip() for p in location.split(',')]
            if len(parts) >= 2:
                suburb = parts[0]
                state = parts[1]
            elif len(parts) == 1:
                # Could be state or suburb
                if len(parts[0]) <= 3:
                    state = parts[0]
                else:
                    suburb = parts[0]

        # Gather data from multiple sources
        rba_data = await self.rba_service.get_economic_summary()

        suburb_stats = None
        if suburb and state:
            suburb_stats = await self.domain_service.get_suburb_statistics(suburb, state)

        state_data = None
        if state:
            state_data = await self.abs_service.get_housing_statistics(state)

        # Get relevant insights from RAG
        query = f"market trends {location or 'Australia'} {property_type or ''}"
        market_insights_data = await self.rag_engine.search_market_insights(
            query=query,
            k=3,
            location=location
        )

        # Compile insights
        insights = {
            "location": location or "Australia",
            "property_type": property_type,
            "current_trends": self._compile_trends(suburb_stats, state_data),
            "price_movements": self._compile_price_movements(suburb_stats, state_data),
            "interest_rates": rba_data["cash_rate"],
            "economic_indicators": {
                "inflation": rba_data["inflation"],
                "housing_credit_growth": rba_data["housing_credit"]
            },
            "forecast": None,  # Would integrate with forecasting service
            "sources": ["Domain.com.au", "RBA", "ABS", "Historical Data"]
        }

        # Generate natural language insights
        insights_text = await self._generate_insights(
            location=location,
            property_type=property_type,
            data=insights
        )

        insights["insights"] = insights_text

        return insights

    def _compile_trends(
        self,
        suburb_stats: Optional[Dict[str, Any]],
        state_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compile current market trends"""
        trends = {}

        if suburb_stats:
            trends["suburb_median"] = suburb_stats.get("medianPrice")
            trends["annual_growth"] = suburb_stats.get("annualGrowth")
            trends["quarterly_growth"] = suburb_stats.get("quarterlyGrowth")
            trends["days_on_market"] = suburb_stats.get("daysOnMarket")
            trends["sales_volume"] = suburb_stats.get("numberOfSales")

        if state_data:
            trends["state_median"] = state_data.get("median_house_price")
            trends["rental_yield"] = state_data.get("rental_yield")
            trends["ownership_rate"] = state_data.get("home_ownership_rate")

        if not trends:
            # National averages
            trends["national_median"] = 850000
            trends["annual_growth"] = 6.5
            trends["market_conditions"] = "balanced"

        return trends

    def _compile_price_movements(
        self,
        suburb_stats: Optional[Dict[str, Any]],
        state_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compile price movement data"""
        movements = {}

        if suburb_stats:
            annual_growth = suburb_stats.get("annualGrowth", 0)
            quarterly_growth = suburb_stats.get("quarterlyGrowth", 0)

            movements["trend"] = "rising" if annual_growth > 2 else "falling" if annual_growth < -2 else "stable"
            movements["annual_change_percent"] = annual_growth
            movements["quarterly_change_percent"] = quarterly_growth

            # Calculate momentum
            if quarterly_growth > annual_growth / 4:
                movements["momentum"] = "accelerating"
            elif quarterly_growth < annual_growth / 4:
                movements["momentum"] = "decelerating"
            else:
                movements["momentum"] = "steady"

        return movements

    async def _generate_insights(
        self,
        location: Optional[str],
        property_type: Optional[str],
        data: Dict[str, Any]
    ) -> str:
        """Generate natural language market insights"""

        trends = data["current_trends"]
        price_movements = data["price_movements"]
        interest_rates = data["interest_rates"]

        prompt = f"""
        You are an expert property market analyst. Provide insightful market commentary.

        Location: {location or "Australia (National)"}
        Property Type: {property_type or "All properties"}

        Current Trends:
        {self._format_dict(trends)}

        Price Movements:
        {self._format_dict(price_movements)}

        Interest Rates:
        - Current RBA Cash Rate: {interest_rates.get('current_rate')}%
        - Previous Rate: {interest_rates.get('previous_rate')}%

        Provide a 5-6 sentence market commentary that:
        1. Summarizes the current market state (hot/cool/balanced)
        2. Explains recent price movements and trends
        3. Discusses the impact of interest rates
        4. Provides forward-looking insights
        5. Offers practical advice for buyers/investors

        Be professional, insightful, and balanced in your analysis.
        """

        response = await self.llm.ainvoke(prompt)
        return response.content

    def _format_dict(self, d: Dict[str, Any]) -> str:
        """Format dictionary for prompt"""
        if not d:
            return "No data available"

        return "\n".join(f"- {k}: {v}" for k, v in d.items())

    async def answer_market_question(self, question: str) -> str:
        """
        Answer specific market-related questions using RAG

        Args:
            question: User's market question

        Returns:
            Answer based on market data
        """
        # Use RAG to get contextual answer
        answer = await self.rag_engine.query_with_context(
            question=question,
            context_type="market",
            k=3
        )

        return answer
