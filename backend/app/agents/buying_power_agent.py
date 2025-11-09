"""
Buying Power & Affordability Agent
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.utils.calculators import BuyingPowerCalculator
from app.services.rba_api import RBAAPIService


class BuyingPowerAgent:
    """Agent specialized in calculating buying power and affordability"""

    def __init__(self):
        """Initialize buying power agent"""
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.3,
            openai_api_key=self.settings.openai_api_key
        )
        self.rba_service = RBAAPIService()

    async def calculate_buying_power(
        self,
        deposit: float,
        annual_income: float,
        monthly_expenses: float,
        other_income: float = 0,
        dependents: int = 0,
        employment_type: str = "full_time",
        existing_debts: float = 0,
        state: str = "NSW",
        is_first_home: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive buying power analysis

        Args:
            deposit: Available deposit
            annual_income: Annual gross income
            monthly_expenses: Monthly living expenses
            other_income: Additional monthly income
            dependents: Number of dependents
            employment_type: Type of employment
            existing_debts: Existing monthly debt repayments
            state: Australian state
            is_first_home: First home buyer status

        Returns:
            Complete buying power analysis
        """
        # Get current interest rate from RBA
        rba_data = await self.rba_service.get_current_cash_rate()
        current_cash_rate = rba_data.get("current_rate", 4.35) / 100

        # Typical home loan rates are cash rate + 2-3%
        typical_home_loan_rate = current_cash_rate + 0.025  # Add 2.5%

        # Initialize calculator with current rates
        calculator = BuyingPowerCalculator(
            interest_rate=typical_home_loan_rate,
            loan_term_years=30
        )

        # Calculate buying power
        result = calculator.calculate_buying_power(
            deposit=deposit,
            annual_income=annual_income,
            monthly_expenses=monthly_expenses,
            other_income=other_income,
            dependents=dependents,
            employment_type=employment_type,
            existing_debts=existing_debts,
            state=state,
            is_first_home=is_first_home
        )

        # Generate personalized explanation
        explanation = await self._generate_explanation(
            deposit=deposit,
            annual_income=annual_income,
            result=result,
            is_first_home=is_first_home
        )

        result["explanation"] = explanation
        result["current_interest_rates"] = {
            "rba_cash_rate": current_cash_rate * 100,
            "typical_home_loan_rate": typical_home_loan_rate * 100,
            "rate_outlook": rba_data.get("trend", "stable")
        }

        return result

    async def _generate_explanation(
        self,
        deposit: float,
        annual_income: float,
        result: Dict[str, Any],
        is_first_home: bool
    ) -> str:
        """Generate personalized explanation of buying power"""

        prompt = f"""
        You are a friendly mortgage broker explaining buying power to a client.

        Client Details:
        - Deposit: ${deposit:,}
        - Annual Income: ${annual_income:,}
        - First Home Buyer: {is_first_home}

        Calculation Results:
        - Maximum Loan: ${result['max_loan_amount']:,}
        - Maximum Property Price: ${result['max_property_price']:,}
        - Monthly Repayment: ${result['monthly_repayment']:,}
        - Loan-to-Value Ratio: {result['loan_to_value_ratio']}%
        - Affordability Rating: {result['affordability_rating']}
        - Total Upfront Costs: ${result['total_upfront_costs']:,}

        Provide a 4-5 sentence explanation that:
        1. Summarizes their buying power in simple terms
        2. Explains the monthly commitment
        3. Mentions total upfront costs needed
        4. Provides encouragement or practical advice
        5. If first home buyer, mention potential benefits

        Be warm, encouraging, and practical. Avoid jargon.
        """

        response = await self.llm.ainvoke(prompt)
        return response.content

    async def analyze_scenario(
        self,
        current_buying_power: Dict[str, Any],
        target_property_price: float
    ) -> Dict[str, Any]:
        """
        Analyze if a specific property is affordable

        Args:
            current_buying_power: Result from calculate_buying_power
            target_property_price: Price of property they're considering

        Returns:
            Affordability analysis
        """
        max_affordable = current_buying_power["max_property_price"]
        shortfall = target_property_price - max_affordable
        is_affordable = target_property_price <= max_affordable

        analysis = {
            "is_affordable": is_affordable,
            "target_price": target_property_price,
            "max_affordable": max_affordable,
            "shortfall": max(0, shortfall),
            "surplus": max(0, -shortfall)
        }

        if not is_affordable:
            # Calculate what's needed to afford it
            additional_deposit_needed = shortfall * 0.2  # Assuming 80% LVR
            additional_income_needed = shortfall * 0.15  # Rough approximation

            analysis["recommendations"] = [
                f"Increase deposit by ${additional_deposit_needed:,.0f}, or",
                f"Increase annual income by ${additional_income_needed:,.0f}, or",
                "Reduce monthly expenses to improve serviceability",
                f"Consider properties up to ${max_affordable:,.0f}"
            ]
        else:
            analysis["recommendations"] = [
                f"This property is within your budget!",
                f"You have ${-shortfall:,.0f} buffer for negotiation or upgrades"
            ]

        return analysis
