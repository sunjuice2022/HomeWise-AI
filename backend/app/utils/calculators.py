"""
Financial calculators for buying power and affordability
"""
import math
from typing import Dict, Any, List


class BuyingPowerCalculator:
    """Calculate buying power and affordability metrics"""

    # Default assumptions
    DEFAULT_INTEREST_RATE = 0.065  # 6.5% p.a.
    DEFAULT_LOAN_TERM_YEARS = 30
    LVR_THRESHOLD_LMI = 0.80  # 80% LVR threshold for Lenders Mortgage Insurance
    MAX_LVR = 0.95  # Maximum 95% LVR
    STAMP_DUTY_RATES = {
        "NSW": [(15000, 0.0125), (32000, 0.015), (85000, 0.0175), (330000, 0.035), (float('inf'), 0.045)],
        "VIC": [(25000, 0.014), (130000, 0.024), (960000, 0.06), (float('inf'), 0.065)],
        "QLD": [(5000, 0.015), (75000, 0.035), (540000, 0.045), (1000000, 0.0575), (float('inf'), 0.0575)],
        "SA": [(12000, 0.01), (30000, 0.02), (50000, 0.03), (100000, 0.035), (200000, 0.04), (250000, 0.045), (300000, 0.05), (500000, 0.055), (float('inf'), 0.07)],
        "WA": [(120000, 0.019), (150000, 0.028), (360000, 0.038), (725000, 0.049), (float('inf'), 0.051)],
        "TAS": [(3000, 0.0175), (25000, 0.02), (75000, 0.025), (200000, 0.035), (375000, 0.04), (725000, 0.045), (float('inf'), 0.045)],
        "ACT": [(200000, 0), (300000, 0.022), (500000, 0.042), (750000, 0.0465), (1000000, 0.049), (1455000, 0.052), (float('inf'), 0.06)],
        "NT": [(525000, 0), (3000000, 0.0495), (5000000, 0.057), (float('inf'), 0.059)],
    }

    def __init__(self, interest_rate: float = None, loan_term_years: int = 30):
        """
        Initialize calculator

        Args:
            interest_rate: Annual interest rate (e.g., 0.065 for 6.5%)
            loan_term_years: Loan term in years
        """
        self.interest_rate = interest_rate or self.DEFAULT_INTEREST_RATE
        self.loan_term_years = loan_term_years

    def calculate_maximum_loan(
        self,
        annual_income: float,
        monthly_expenses: float,
        other_income: float = 0,
        existing_debts: float = 0,
        dependents: int = 0,
        employment_type: str = "full_time"
    ) -> float:
        """
        Calculate maximum loan amount based on income and expenses

        Uses the serviceability ratio approach used by Australian banks
        """
        # Calculate total monthly income
        monthly_income = (annual_income / 12) + other_income

        # Apply employment type multiplier (lenders are more conservative with non-permanent employment)
        employment_multipliers = {
            "full_time": 1.0,
            "part_time": 0.9,
            "casual": 0.8,
            "self_employed": 0.8,
            "contract": 0.85
        }
        income_multiplier = employment_multipliers.get(employment_type, 0.8)
        adjusted_income = monthly_income * income_multiplier

        # Calculate minimum living expenses (HEM - Household Expenditure Measure approximation)
        base_living_expenses = 2000 + (dependents * 500)
        total_monthly_expenses = max(monthly_expenses, base_living_expenses)

        # Add existing debt commitments
        total_monthly_commitments = total_monthly_expenses + existing_debts

        # Calculate surplus income
        surplus = adjusted_income - total_monthly_commitments

        # Apply stress test (calculate repayments at higher rate)
        stress_rate = self.interest_rate + 0.03  # Add 3% buffer as per APRA guidelines

        # Maximum loan based on surplus income
        if surplus <= 0:
            return 0

        # Calculate maximum monthly repayment (typically 30% of gross income)
        max_monthly_repayment = min(surplus * 0.8, adjusted_income * 0.30)

        # Calculate maximum loan amount based on repayment capacity
        max_loan = self._calculate_loan_from_repayment(
            monthly_repayment=max_monthly_repayment,
            interest_rate=stress_rate,
            term_years=self.loan_term_years
        )

        # Apply income multiplier cap (typically 6x annual income)
        income_based_cap = annual_income * 6

        return min(max_loan, income_based_cap)

    def _calculate_loan_from_repayment(
        self,
        monthly_repayment: float,
        interest_rate: float,
        term_years: int
    ) -> float:
        """Calculate loan amount from monthly repayment using present value formula"""
        monthly_rate = interest_rate / 12
        num_payments = term_years * 12

        if monthly_rate == 0:
            return monthly_repayment * num_payments

        # Present value of annuity formula
        loan_amount = monthly_repayment * (
            (1 - math.pow(1 + monthly_rate, -num_payments)) / monthly_rate
        )

        return loan_amount

    def calculate_monthly_repayment(
        self,
        loan_amount: float,
        interest_rate: float = None,
        term_years: int = None
    ) -> float:
        """Calculate monthly loan repayment"""
        rate = interest_rate or self.interest_rate
        term = term_years or self.loan_term_years

        monthly_rate = rate / 12
        num_payments = term * 12

        if monthly_rate == 0:
            return loan_amount / num_payments

        # Monthly payment formula
        monthly_payment = loan_amount * (
            monthly_rate * math.pow(1 + monthly_rate, num_payments)
        ) / (math.pow(1 + monthly_rate, num_payments) - 1)

        return monthly_payment

    def calculate_stamp_duty(self, property_price: float, state: str = "NSW", is_first_home: bool = False) -> float:
        """
        Calculate stamp duty for property purchase

        Args:
            property_price: Purchase price of property
            state: Australian state/territory
            is_first_home: Whether buyer is first home buyer (may get concessions)
        """
        state = state.upper()
        if state not in self.STAMP_DUTY_RATES:
            state = "NSW"  # Default to NSW

        rates = self.STAMP_DUTY_RATES[state]
        stamp_duty = 0
        remaining_value = property_price

        # First home buyer concessions (simplified - varies by state)
        if is_first_home and property_price < 650000:
            return 0  # Many states offer stamp duty exemption for first home buyers under threshold

        # Calculate progressive stamp duty
        prev_threshold = 0
        for threshold, rate in rates:
            if remaining_value <= 0:
                break

            taxable_amount = min(remaining_value, threshold - prev_threshold)
            stamp_duty += taxable_amount * rate
            remaining_value -= taxable_amount
            prev_threshold = threshold

        return stamp_duty

    def calculate_buying_power(
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

        Returns:
            Dictionary containing all buying power metrics
        """
        # Calculate maximum loan
        max_loan = self.calculate_maximum_loan(
            annual_income=annual_income,
            monthly_expenses=monthly_expenses,
            other_income=other_income,
            existing_debts=existing_debts,
            dependents=dependents,
            employment_type=employment_type
        )

        # Calculate maximum property price (loan + deposit)
        max_property_price = max_loan + deposit

        # Calculate LVR
        lvr = (max_loan / max_property_price * 100) if max_property_price > 0 else 0

        # Calculate monthly repayment
        monthly_repayment = self.calculate_monthly_repayment(max_loan)

        # Calculate stamp duty
        stamp_duty = self.calculate_stamp_duty(max_property_price, state, is_first_home)

        # Calculate other costs
        legal_fees = 1500
        building_inspection = 500
        loan_application_fee = 600
        lmi = 0

        if lvr > 80:
            # Estimate LMI (Lenders Mortgage Insurance) - simplified calculation
            lmi = max_loan * 0.02  # Roughly 2% of loan for LVR > 80%

        total_upfront_costs = deposit + stamp_duty + legal_fees + building_inspection + loan_application_fee + lmi

        # Affordability rating
        debt_to_income_ratio = (monthly_repayment * 12) / annual_income if annual_income > 0 else 0

        if debt_to_income_ratio < 0.25:
            affordability_rating = "Excellent"
        elif debt_to_income_ratio < 0.30:
            affordability_rating = "Good"
        elif debt_to_income_ratio < 0.35:
            affordability_rating = "Fair"
        else:
            affordability_rating = "Stretched"

        # Generate recommendations
        recommendations = self._generate_recommendations(
            deposit=deposit,
            max_property_price=max_property_price,
            lvr=lvr,
            debt_to_income_ratio=debt_to_income_ratio,
            is_first_home=is_first_home
        )

        return {
            "max_loan_amount": round(max_loan, 2),
            "max_property_price": round(max_property_price, 2),
            "monthly_repayment": round(monthly_repayment, 2),
            "interest_rate": self.interest_rate,
            "loan_to_value_ratio": round(lvr, 2),
            "stamp_duty": round(stamp_duty, 2),
            "total_upfront_costs": round(total_upfront_costs, 2),
            "affordability_rating": affordability_rating,
            "recommendations": recommendations,
            "assumptions": {
                "interest_rate": f"{self.interest_rate * 100:.2f}%",
                "loan_term": f"{self.loan_term_years} years",
                "stress_test_rate": f"{(self.interest_rate + 0.03) * 100:.2f}%",
                "legal_fees": legal_fees,
                "building_inspection": building_inspection,
                "loan_application_fee": loan_application_fee,
                "lmi": round(lmi, 2)
            }
        }

    def _generate_recommendations(
        self,
        deposit: float,
        max_property_price: float,
        lvr: float,
        debt_to_income_ratio: float,
        is_first_home: bool
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []

        if lvr > 80:
            recommendations.append(
                f"Your LVR is {lvr:.1f}%. Consider saving a larger deposit to avoid "
                "Lenders Mortgage Insurance (LMI) and get better interest rates."
            )

        if lvr > 90:
            recommendations.append(
                "With LVR above 90%, you may face higher interest rates and stricter "
                "lending criteria. Aim for at least 20% deposit if possible."
            )

        if debt_to_income_ratio > 0.30:
            recommendations.append(
                "Your debt-to-income ratio is relatively high. Consider reducing expenses "
                "or increasing income to improve borrowing capacity."
            )

        if is_first_home:
            recommendations.append(
                "As a first home buyer, you may be eligible for government grants and "
                "stamp duty concessions. Check your state's first home buyer schemes."
            )

        if max_property_price < 500000:
            recommendations.append(
                "Consider looking in outer suburbs or regional areas where property "
                "prices may be more affordable for your budget."
            )

        if not recommendations:
            recommendations.append(
                "Your financial position looks strong. You have good borrowing capacity "
                "and flexibility in your property search."
            )

        return recommendations
