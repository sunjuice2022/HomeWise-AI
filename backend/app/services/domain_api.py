"""
Domain.com.au API integration
"""
import httpx
from typing import Dict, Any, List, Optional
from app.config import get_settings


class DomainAPIService:
    """Service for interacting with Domain.com.au API"""

    BASE_URL = "https://api.domain.com.au/v1"

    def __init__(self):
        """Initialize Domain API service"""
        self.settings = get_settings()
        self.api_key = self.settings.domain_api_key
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def search_properties(
        self,
        suburb: str,
        state: str,
        property_type: Optional[str] = None,
        bedrooms: Optional[int] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for properties in Domain

        Args:
            suburb: Suburb name
            state: State abbreviation
            property_type: Type of property
            bedrooms: Number of bedrooms
            max_results: Maximum number of results

        Returns:
            List of property listings
        """
        if not self.api_key:
            return self._mock_property_search(suburb, state, property_type, bedrooms)

        try:
            async with httpx.AsyncClient() as client:
                # Build search criteria
                criteria = {
                    "listingType": "Sale",
                    "locations": [
                        {
                            "state": state,
                            "suburb": suburb
                        }
                    ],
                    "pageSize": max_results
                }

                if property_type:
                    criteria["propertyTypes"] = [property_type]

                if bedrooms:
                    criteria["bedrooms"] = {"min": bedrooms, "max": bedrooms}

                response = await client.post(
                    f"{self.BASE_URL}/listings/residential/_search",
                    headers=self.headers,
                    json=criteria,
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return self._mock_property_search(suburb, state, property_type, bedrooms)

        except Exception as e:
            print(f"Error fetching from Domain API: {e}")
            return self._mock_property_search(suburb, state, property_type, bedrooms)

    async def get_property_price_estimate(self, address: str) -> Dict[str, Any]:
        """
        Get price estimate for a property

        Args:
            address: Full property address

        Returns:
            Price estimate data
        """
        if not self.api_key:
            return self._mock_price_estimate(address)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/properties/_suggest",
                    headers=self.headers,
                    params={"terms": address},
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        # Get property details for the first match
                        property_id = data[0].get("id")
                        return await self._get_property_details(property_id)

                return self._mock_price_estimate(address)

        except Exception as e:
            print(f"Error fetching price estimate from Domain: {e}")
            return self._mock_price_estimate(address)

    async def _get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get detailed property information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/properties/{property_id}",
                    headers=self.headers,
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            print(f"Error fetching property details: {e}")

        return {}

    async def get_suburb_statistics(self, suburb: str, state: str) -> Dict[str, Any]:
        """
        Get suburb-level statistics

        Args:
            suburb: Suburb name
            state: State abbreviation

        Returns:
            Suburb statistics including median prices, trends
        """
        if not self.api_key:
            return self._mock_suburb_stats(suburb, state)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/suburbPerformanceStatistics",
                    headers=self.headers,
                    params={
                        "state": state,
                        "suburb": suburb,
                        "propertyCategory": "house"
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()

                return self._mock_suburb_stats(suburb, state)

        except Exception as e:
            print(f"Error fetching suburb stats from Domain: {e}")
            return self._mock_suburb_stats(suburb, state)

    def _mock_property_search(
        self,
        suburb: str,
        state: str,
        property_type: Optional[str],
        bedrooms: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Mock property search results for development/testing"""
        return [
            {
                "id": "mock-1",
                "address": f"123 Main Street, {suburb}, {state}",
                "propertyType": property_type or "House",
                "bedrooms": bedrooms or 3,
                "bathrooms": 2,
                "parking": 2,
                "price": "850,000 - 900,000",
                "landArea": 650,
                "description": "Beautiful family home in great location"
            },
            {
                "id": "mock-2",
                "address": f"45 Park Avenue, {suburb}, {state}",
                "propertyType": property_type or "House",
                "bedrooms": bedrooms or 4,
                "bathrooms": 2,
                "parking": 2,
                "price": "920,000",
                "landArea": 720,
                "description": "Modern home with stunning features"
            }
        ]

    def _mock_price_estimate(self, address: str) -> Dict[str, Any]:
        """Mock price estimate for development/testing"""
        return {
            "address": address,
            "estimatedPrice": 875000,
            "priceRange": {
                "min": 820000,
                "max": 930000
            },
            "confidence": 0.75,
            "lastSalePrice": 650000,
            "lastSaleDate": "2020-06-15",
            "source": "mock_data"
        }

    def _mock_suburb_stats(self, suburb: str, state: str) -> Dict[str, Any]:
        """Mock suburb statistics for development/testing"""
        return {
            "suburb": suburb,
            "state": state,
            "medianPrice": 885000,
            "medianRent": 550,
            "numberOfSales": 45,
            "annualGrowth": 8.5,
            "quarterlyGrowth": 2.3,
            "daysOnMarket": 32,
            "source": "mock_data"
        }
