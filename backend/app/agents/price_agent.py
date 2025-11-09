"""
Property Price Estimation Agent
"""
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import re

from app.config import get_settings
from app.services.domain_api import DomainAPIService
from app.utils.rag_engine import RAGEngine


class PriceEstimationAgent:
    """Agent specialized in property price estimation"""

    def __init__(self, rag_engine: RAGEngine):
        """Initialize price estimation agent"""
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.2,
            openai_api_key=self.settings.openai_api_key
        )
        self.rag_engine = rag_engine
        self.domain_service = DomainAPIService()

    def _parse_address(self, address: str) -> Dict[str, str]:
        """
        Parse address into components

        Args:
            address: Full address string

        Returns:
            Dictionary with address components
        """
        # Simple address parsing - in production, use a proper address parsing library
        parts = address.split(',')

        suburb = ""
        state = ""
        postcode = ""

        if len(parts) >= 2:
            suburb = parts[-2].strip()

        if len(parts) >= 3:
            state_postcode = parts[-1].strip()
            # Extract state and postcode
            match = re.search(r'([A-Z]{2,3})\s*(\d{4})', state_postcode)
            if match:
                state = match.group(1)
                postcode = match.group(2)

        return {
            "full_address": address,
            "suburb": suburb,
            "state": state,
            "postcode": postcode
        }

    async def estimate_price(
        self,
        address: str,
        property_type: Optional[str] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[int] = None,
        parking: Optional[int] = None,
        land_size: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Estimate property price using multiple data sources

        Args:
            address: Property address
            property_type: Type of property
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            parking: Number of parking spaces
            land_size: Land size in sqm

        Returns:
            Price estimation with confidence score and explanation
        """
        # Parse address
        parsed_address = self._parse_address(address)
        suburb = parsed_address["suburb"]
        state = parsed_address["state"]

        # 1. Get comparable properties from RAG
        search_query = f"{property_type or 'property'} {bedrooms or ''} bedroom in {suburb} {state}"
        comparable_properties = await self.rag_engine.search_similar_properties(
            query=search_query,
            k=5
        )

        # 2. Get recent sales from Domain API
        domain_data = await self.domain_service.get_property_price_estimate(address)

        # 3. Get suburb statistics
        suburb_stats = await self.domain_service.get_suburb_statistics(suburb, state)

        # 4. Calculate estimated price
        estimation = self._calculate_price_estimate(
            parsed_address=parsed_address,
            property_features={
                "type": property_type,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "parking": parking,
                "land_size": land_size
            },
            comparable_properties=comparable_properties,
            domain_data=domain_data,
            suburb_stats=suburb_stats
        )

        # 5. Generate natural language explanation
        explanation = await self._generate_explanation(
            address=address,
            estimation=estimation,
            suburb_stats=suburb_stats
        )

        return {
            "address": address,
            "estimated_price": estimation["price"],
            "price_range_min": estimation["price_min"],
            "price_range_max": estimation["price_max"],
            "confidence_score": estimation["confidence"],
            "comparable_properties": self._format_comparables(comparable_properties),
            "market_trends": suburb_stats,
            "sources": ["Domain.com.au", "Historical Data", "Suburb Statistics"],
            "explanation": explanation
        }

    def _calculate_price_estimate(
        self,
        parsed_address: Dict[str, str],
        property_features: Dict[str, Any],
        comparable_properties: List[Dict[str, Any]],
        domain_data: Dict[str, Any],
        suburb_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate price estimate using multiple data points

        Returns:
            Dictionary with price, range, and confidence
        """
        estimates = []
        weights = []

        # Use Domain estimate if available
        if domain_data.get("estimatedPrice"):
            estimates.append(domain_data["estimatedPrice"])
            weights.append(0.4)  # 40% weight

        # Use suburb median as baseline
        if suburb_stats.get("medianPrice"):
            # Adjust based on property features
            adjusted_price = suburb_stats["medianPrice"]

            # Adjust for bedrooms (if different from typical 3 bedroom)
            if property_features.get("bedrooms"):
                bedroom_diff = property_features["bedrooms"] - 3
                adjusted_price *= (1 + bedroom_diff * 0.15)

            estimates.append(adjusted_price)
            weights.append(0.3)  # 30% weight

        # Use comparables average
        if comparable_properties:
            # This would need actual price data from comparables
            # For now, using suburb median as proxy
            if suburb_stats.get("medianPrice"):
                estimates.append(suburb_stats["medianPrice"])
                weights.append(0.3)  # 30% weight

        # Calculate weighted average
        if estimates:
            total_weight = sum(weights)
            estimated_price = sum(e * w for e, w in zip(estimates, weights)) / total_weight

            # Calculate price range (±10% for moderate confidence)
            price_variance = 0.10
            price_min = estimated_price * (1 - price_variance)
            price_max = estimated_price * (1 + price_variance)

            # Confidence based on data availability
            confidence = min(0.95, total_weight)
        else:
            # Fallback to Australian median
            estimated_price = 800000
            price_min = 700000
            price_max = 900000
            confidence = 0.5

        return {
            "price": round(estimated_price, -3),  # Round to nearest $1000
            "price_min": round(price_min, -3),
            "price_max": round(price_max, -3),
            "confidence": round(confidence, 2)
        }

    async def _generate_explanation(
        self,
        address: str,
        estimation: Dict[str, Any],
        suburb_stats: Dict[str, Any]
    ) -> str:
        """Generate natural language explanation of the price estimate"""

        prompt = f"""
        You are a professional property valuer. Provide a clear, concise explanation of the
        following property price estimate.

        Address: {address}
        Estimated Price: ${estimation['price']:,}
        Price Range: ${estimation['price_min']:,} - ${estimation['price_max']:,}
        Confidence: {estimation['confidence'] * 100:.0f}%

        Suburb Statistics:
        - Median Price: ${suburb_stats.get('medianPrice', 'N/A'):,}
        - Annual Growth: {suburb_stats.get('annualGrowth', 'N/A')}%
        - Days on Market: {suburb_stats.get('daysOnMarket', 'N/A')}

        Provide a 3-4 sentence explanation that:
        1. States the estimated value and range
        2. Explains how it compares to the suburb median
        3. Mentions the market trend
        4. Notes the confidence level

        Be professional but conversational.
        """

        response = await self.llm.ainvoke(prompt)
        return response.content

    def _format_comparables(self, comparables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format comparable properties for response"""
        formatted = []

        for comp in comparables[:3]:  # Return top 3
            metadata = comp.get("metadata", {})
            formatted.append({
                "address": metadata.get("address", "Unknown"),
                "price": metadata.get("last_sale_price") or metadata.get("estimated_value"),
                "bedrooms": metadata.get("bedrooms"),
                "bathrooms": metadata.get("bathrooms"),
                "similarity_score": comp.get("score")
            })

        return formatted
