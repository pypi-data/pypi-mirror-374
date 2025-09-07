"""
Financial calculations module for the Scientific Calculator MCP Server.

This module provides comprehensive financial calculation capabilities including
compound interest, present value, net present value, internal rate of return,
loan payments, and annuity calculations.
"""

from typing import Union, Dict, Any, List, Optional
import math
import numpy as np
from decimal import Decimal, getcontext

from calculator.models.errors import CalculatorError, ValidationError


class FinancialError(CalculatorError):
    """Error for financial calculations."""
    pass


def _validate_positive_number(value: Union[float, int], name: str) -> float:
    """Validate that a number is positive."""
    try:
        num_value = float(value)
        if num_value <= 0:
            raise ValidationError(f"{name} must be positive, got {num_value}")
        return num_value
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid {name}: {e}") from e


def _validate_non_negative_number(value: Union[float, int], name: str) -> float:
    """Validate that a number is non-negative."""
    try:
        num_value = float(value)
        if num_value < 0:
            raise ValidationError(f"{name} must be non-negative, got {num_value}")
        return num_value
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid {name}: {e}") from e


def _validate_rate(rate: Union[float, int], name: str = "interest rate") -> float:
    """Validate interest rate (can be negative but typically positive)."""
    try:
        rate_value = float(rate)
        if rate_value < -1:
            raise ValidationError(f"{name} cannot be less than -100% (-1.0), got {rate_value}")
        return rate_value
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid {name}: {e}") from e


def _validate_periods(periods: Union[int, float], name: str = "periods") -> int:
    """Validate number of periods."""
    try:
        periods_value = int(periods)
        if periods_value <= 0:
            raise ValidationError(f"{name} must be positive, got {periods_value}")
        if periods_value > 1000:
            raise ValidationError(f"{name} too large (maximum 1000), got {periods_value}")
        return periods_value
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid {name}: {e}") from e


# Compound Interest Calculations
def compound_interest(principal: Union[float, int], 
                     rate: Union[float, int], 
                     time: Union[float, int],
                     compounding_frequency: int = 1) -> Dict[str, Any]:
    """Calculate compound interest and future value.
    
    Args:
        principal: Initial principal amount
        rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
        time: Time period in years
        compounding_frequency: Number of times interest is compounded per year
    """
    try:
        P = _validate_positive_number(principal, "principal")
        r = _validate_rate(rate, "annual interest rate")
        t = _validate_non_negative_number(time, "time period")
        n = _validate_periods(compounding_frequency, "compounding frequency")
        
        # Calculate compound interest: A = P(1 + r/n)^(nt)
        if r == 0:
            # No interest case
            future_value = P
            compound_interest_earned = 0.0
        else:
            future_value = P * ((1 + r/n) ** (n * t))
            compound_interest_earned = future_value - P
        
        # Calculate effective annual rate
        if r == 0:
            effective_rate = 0.0
        else:
            effective_rate = ((1 + r/n) ** n) - 1
        
        return {
            "future_value": future_value,
            "compound_interest": compound_interest_earned,
            "effective_annual_rate": effective_rate,
            "principal": P,
            "annual_rate": r,
            "time_years": t,
            "compounding_frequency": n,
            "total_return_percentage": (compound_interest_earned / P) * 100 if P > 0 else 0,
            "operation": "compound_interest"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating compound interest: {e}") from e


def simple_interest(principal: Union[float, int], 
                   rate: Union[float, int], 
                   time: Union[float, int]) -> Dict[str, Any]:
    """Calculate simple interest.
    
    Args:
        principal: Initial principal amount
        rate: Annual interest rate (as decimal)
        time: Time period in years
    """
    try:
        P = _validate_positive_number(principal, "principal")
        r = _validate_rate(rate, "annual interest rate")
        t = _validate_non_negative_number(time, "time period")
        
        # Calculate simple interest: I = P * r * t
        simple_interest_earned = P * r * t
        future_value = P + simple_interest_earned
        
        return {
            "future_value": future_value,
            "simple_interest": simple_interest_earned,
            "principal": P,
            "annual_rate": r,
            "time_years": t,
            "total_return_percentage": (simple_interest_earned / P) * 100 if P > 0 else 0,
            "operation": "simple_interest"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating simple interest: {e}") from e


# Present Value Calculations
def present_value(future_value: Union[float, int], 
                 rate: Union[float, int], 
                 periods: Union[int, float]) -> Dict[str, Any]:
    """Calculate present value of a future amount.
    
    Args:
        future_value: Future value amount
        rate: Discount rate per period (as decimal)
        periods: Number of periods
    """
    try:
        FV = _validate_positive_number(future_value, "future value")
        r = _validate_rate(rate, "discount rate")
        n = _validate_periods(periods, "periods")
        
        # Calculate present value: PV = FV / (1 + r)^n
        if r == -1:
            raise FinancialError("Discount rate cannot be -100% (-1.0)")
        
        present_val = FV / ((1 + r) ** n)
        discount_amount = FV - present_val
        
        return {
            "present_value": present_val,
            "future_value": FV,
            "discount_amount": discount_amount,
            "discount_rate": r,
            "periods": n,
            "discount_percentage": (discount_amount / FV) * 100 if FV > 0 else 0,
            "operation": "present_value"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating present value: {e}") from e


def net_present_value(cash_flows: List[Union[float, int]], 
                     discount_rate: Union[float, int],
                     initial_investment: Union[float, int] = 0) -> Dict[str, Any]:
    """Calculate Net Present Value (NPV) of cash flows.
    
    Args:
        cash_flows: List of cash flows for each period
        discount_rate: Discount rate per period (as decimal)
        initial_investment: Initial investment (negative cash flow at t=0)
    """
    try:
        if not cash_flows:
            raise ValidationError("Cash flows list cannot be empty")
        
        if len(cash_flows) > 100:
            raise ValidationError("Too many cash flows (maximum 100)")
        
        flows = [float(cf) for cf in cash_flows]
        r = _validate_rate(discount_rate, "discount rate")
        initial_inv = float(initial_investment)
        
        if r == -1:
            raise FinancialError("Discount rate cannot be -100% (-1.0)")
        
        # Calculate NPV
        npv = -initial_inv  # Initial investment is typically negative
        present_values = []
        
        for i, cash_flow in enumerate(flows):
            period = i + 1
            pv = cash_flow / ((1 + r) ** period)
            present_values.append(pv)
            npv += pv
        
        # Calculate profitability index
        total_pv_inflows = sum(pv for pv in present_values if pv > 0)
        profitability_index = total_pv_inflows / initial_inv if initial_inv > 0 else float('inf')
        
        return {
            "npv": npv,
            "present_values": present_values,
            "total_cash_flows": sum(flows),
            "initial_investment": initial_inv,
            "discount_rate": r,
            "periods": len(flows),
            "profitability_index": profitability_index,
            "is_profitable": npv > 0,
            "operation": "net_present_value"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating NPV: {e}") from e


# Internal Rate of Return
def internal_rate_of_return(cash_flows: List[Union[float, int]], 
                           initial_investment: Union[float, int],
                           max_iterations: int = 100,
                           tolerance: float = 1e-6) -> Dict[str, Any]:
    """Calculate Internal Rate of Return (IRR) using Newton-Raphson method.
    
    Args:
        cash_flows: List of cash flows for each period
        initial_investment: Initial investment (positive value)
        max_iterations: Maximum iterations for IRR calculation
        tolerance: Convergence tolerance
    """
    try:
        if not cash_flows:
            raise ValidationError("Cash flows list cannot be empty")
        
        if len(cash_flows) > 100:
            raise ValidationError("Too many cash flows (maximum 100)")
        
        flows = [float(cf) for cf in cash_flows]
        initial_inv = _validate_positive_number(initial_investment, "initial investment")
        
        # Prepend negative initial investment
        all_flows = [-initial_inv] + flows
        
        # Check if there are both positive and negative cash flows
        has_positive = any(cf > 0 for cf in all_flows)
        has_negative = any(cf < 0 for cf in all_flows)
        
        if not (has_positive and has_negative):
            raise FinancialError("IRR requires both positive and negative cash flows")
        
        # Newton-Raphson method to find IRR
        def npv_function(rate):
            return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(all_flows))
        
        def npv_derivative(rate):
            return sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(all_flows))
        
        # Initial guess
        rate = 0.1  # 10%
        
        for iteration in range(max_iterations):
            try:
                npv = npv_function(rate)
                npv_prime = npv_derivative(rate)
                
                if abs(npv_prime) < 1e-12:
                    break
                
                new_rate = rate - npv / npv_prime
                
                if abs(new_rate - rate) < tolerance:
                    rate = new_rate
                    break
                
                rate = new_rate
                
                # Prevent extreme values
                if rate < -0.99 or rate > 10:
                    raise FinancialError("IRR calculation diverged")
                    
            except (ZeroDivisionError, OverflowError):
                raise FinancialError("IRR calculation failed due to numerical issues")
        
        else:
            raise FinancialError(f"IRR did not converge after {max_iterations} iterations")
        
        # Verify the result
        final_npv = npv_function(rate)
        
        return {
            "irr": rate,
            "irr_percentage": rate * 100,
            "final_npv": final_npv,
            "iterations": iteration + 1,
            "cash_flows": flows,
            "initial_investment": initial_inv,
            "converged": abs(final_npv) < tolerance * 10,
            "operation": "internal_rate_of_return"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating IRR: {e}") from e


# Loan and Mortgage Calculations
def loan_payment(principal: Union[float, int], 
                rate: Union[float, int], 
                periods: Union[int, float],
                payment_type: str = "end") -> Dict[str, Any]:
    """Calculate loan payment amount (PMT).
    
    Args:
        principal: Loan principal amount
        rate: Interest rate per period (as decimal)
        periods: Number of payment periods
        payment_type: "end" for ordinary annuity, "begin" for annuity due
    """
    try:
        P = _validate_positive_number(principal, "principal")
        r = _validate_rate(rate, "interest rate per period")
        n = _validate_periods(periods, "periods")
        
        if payment_type not in ["end", "begin"]:
            raise ValidationError("Payment type must be 'end' or 'begin'")
        
        if r == 0:
            # No interest case
            payment = P / n
            total_payments = P
            total_interest = 0.0
        else:
            # Calculate payment using PMT formula
            if payment_type == "end":
                # Ordinary annuity: PMT = P * [r(1+r)^n] / [(1+r)^n - 1]
                payment = P * (r * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
            else:
                # Annuity due: PMT = PMT_ordinary / (1 + r)
                payment_ordinary = P * (r * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
                payment = payment_ordinary / (1 + r)
            
            total_payments = payment * n
            total_interest = total_payments - P
        
        return {
            "payment": payment,
            "total_payments": total_payments,
            "total_interest": total_interest,
            "principal": P,
            "interest_rate": r,
            "periods": n,
            "payment_type": payment_type,
            "interest_percentage": (total_interest / P) * 100 if P > 0 else 0,
            "operation": "loan_payment"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating loan payment: {e}") from e


def amortization_schedule(principal: Union[float, int], 
                         rate: Union[float, int], 
                         periods: Union[int, float],
                         max_periods_display: int = 12) -> Dict[str, Any]:
    """Generate loan amortization schedule.
    
    Args:
        principal: Loan principal amount
        rate: Interest rate per period (as decimal)
        periods: Number of payment periods
        max_periods_display: Maximum periods to show in detailed schedule
    """
    try:
        P = _validate_positive_number(principal, "principal")
        r = _validate_rate(rate, "interest rate per period")
        n = _validate_periods(periods, "periods")
        
        if max_periods_display > 100:
            max_periods_display = 100
        
        # Calculate payment amount
        payment_info = loan_payment(P, r, n)
        payment = payment_info["payment"]
        
        # Generate amortization schedule
        schedule = []
        remaining_balance = P
        total_interest_paid = 0.0
        total_principal_paid = 0.0
        
        periods_to_show = min(n, max_periods_display)
        
        for period in range(1, periods_to_show + 1):
            if r == 0:
                interest_payment = 0.0
                principal_payment = payment
            else:
                interest_payment = remaining_balance * r
                principal_payment = payment - interest_payment
            
            remaining_balance -= principal_payment
            total_interest_paid += interest_payment
            total_principal_paid += principal_payment
            
            schedule.append({
                "period": period,
                "payment": payment,
                "principal": principal_payment,
                "interest": interest_payment,
                "remaining_balance": max(0, remaining_balance)
            })
        
        # Calculate summary for all periods if not all shown
        if n > max_periods_display:
            # Calculate totals for all periods
            total_payments = payment * n
            total_interest_all = total_payments - P
        else:
            total_payments = payment * periods_to_show
            total_interest_all = total_interest_paid
        
        return {
            "schedule": schedule,
            "payment_amount": payment,
            "total_payments": total_payments,
            "total_interest": total_interest_all,
            "principal": P,
            "interest_rate": r,
            "periods": n,
            "periods_shown": periods_to_show,
            "operation": "amortization_schedule"
        }
        
    except Exception as e:
        raise FinancialError(f"Error generating amortization schedule: {e}") from e


# Annuity Calculations
def future_value_annuity(payment: Union[float, int], 
                        rate: Union[float, int], 
                        periods: Union[int, float],
                        payment_type: str = "end") -> Dict[str, Any]:
    """Calculate future value of an annuity.
    
    Args:
        payment: Payment amount per period
        rate: Interest rate per period (as decimal)
        periods: Number of payment periods
        payment_type: "end" for ordinary annuity, "begin" for annuity due
    """
    try:
        PMT = _validate_positive_number(payment, "payment")
        r = _validate_rate(rate, "interest rate per period")
        n = _validate_periods(periods, "periods")
        
        if payment_type not in ["end", "begin"]:
            raise ValidationError("Payment type must be 'end' or 'begin'")
        
        if r == 0:
            # No interest case
            future_val = PMT * n
        else:
            # Calculate future value using FV annuity formula
            if payment_type == "end":
                # Ordinary annuity: FV = PMT * [((1+r)^n - 1) / r]
                future_val = PMT * (((1 + r) ** n - 1) / r)
            else:
                # Annuity due: FV = FV_ordinary * (1 + r)
                fv_ordinary = PMT * (((1 + r) ** n - 1) / r)
                future_val = fv_ordinary * (1 + r)
        
        total_payments = PMT * n
        interest_earned = future_val - total_payments
        
        return {
            "future_value": future_val,
            "total_payments": total_payments,
            "interest_earned": interest_earned,
            "payment": PMT,
            "interest_rate": r,
            "periods": n,
            "payment_type": payment_type,
            "return_percentage": (interest_earned / total_payments) * 100 if total_payments > 0 else 0,
            "operation": "future_value_annuity"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating future value of annuity: {e}") from e


def present_value_annuity(payment: Union[float, int], 
                         rate: Union[float, int], 
                         periods: Union[int, float],
                         payment_type: str = "end") -> Dict[str, Any]:
    """Calculate present value of an annuity.
    
    Args:
        payment: Payment amount per period
        rate: Interest rate per period (as decimal)
        periods: Number of payment periods
        payment_type: "end" for ordinary annuity, "begin" for annuity due
    """
    try:
        PMT = _validate_positive_number(payment, "payment")
        r = _validate_rate(rate, "interest rate per period")
        n = _validate_periods(periods, "periods")
        
        if payment_type not in ["end", "begin"]:
            raise ValidationError("Payment type must be 'end' or 'begin'")
        
        if r == 0:
            # No interest case
            present_val = PMT * n
        else:
            # Calculate present value using PV annuity formula
            if payment_type == "end":
                # Ordinary annuity: PV = PMT * [(1 - (1+r)^-n) / r]
                present_val = PMT * ((1 - (1 + r) ** (-n)) / r)
            else:
                # Annuity due: PV = PV_ordinary * (1 + r)
                pv_ordinary = PMT * ((1 - (1 + r) ** (-n)) / r)
                present_val = pv_ordinary * (1 + r)
        
        total_payments = PMT * n
        discount_amount = total_payments - present_val
        
        return {
            "present_value": present_val,
            "total_payments": total_payments,
            "discount_amount": discount_amount,
            "payment": PMT,
            "interest_rate": r,
            "periods": n,
            "payment_type": payment_type,
            "discount_percentage": (discount_amount / total_payments) * 100 if total_payments > 0 else 0,
            "operation": "present_value_annuity"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating present value of annuity: {e}") from e


# Investment Analysis
def return_on_investment(initial_investment: Union[float, int], 
                        final_value: Union[float, int]) -> Dict[str, Any]:
    """Calculate Return on Investment (ROI).
    
    Args:
        initial_investment: Initial investment amount
        final_value: Final value of investment
    """
    try:
        initial = _validate_positive_number(initial_investment, "initial investment")
        final = _validate_non_negative_number(final_value, "final value")
        
        gain_loss = final - initial
        roi_decimal = gain_loss / initial
        roi_percentage = roi_decimal * 100
        
        return {
            "roi_decimal": roi_decimal,
            "roi_percentage": roi_percentage,
            "gain_loss": gain_loss,
            "initial_investment": initial,
            "final_value": final,
            "is_profitable": gain_loss > 0,
            "operation": "return_on_investment"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating ROI: {e}") from e


def break_even_analysis(fixed_costs: Union[float, int], 
                       variable_cost_per_unit: Union[float, int],
                       price_per_unit: Union[float, int]) -> Dict[str, Any]:
    """Calculate break-even point analysis.
    
    Args:
        fixed_costs: Total fixed costs
        variable_cost_per_unit: Variable cost per unit
        price_per_unit: Selling price per unit
    """
    try:
        FC = _validate_non_negative_number(fixed_costs, "fixed costs")
        VC = _validate_non_negative_number(variable_cost_per_unit, "variable cost per unit")
        P = _validate_positive_number(price_per_unit, "price per unit")
        
        if P <= VC:
            raise FinancialError("Price per unit must be greater than variable cost per unit")
        
        # Break-even point in units
        contribution_margin = P - VC
        break_even_units = FC / contribution_margin
        
        # Break-even point in revenue
        break_even_revenue = break_even_units * P
        
        # Contribution margin ratio
        contribution_margin_ratio = contribution_margin / P
        
        return {
            "break_even_units": break_even_units,
            "break_even_revenue": break_even_revenue,
            "contribution_margin": contribution_margin,
            "contribution_margin_ratio": contribution_margin_ratio,
            "fixed_costs": FC,
            "variable_cost_per_unit": VC,
            "price_per_unit": P,
            "operation": "break_even_analysis"
        }
        
    except Exception as e:
        raise FinancialError(f"Error calculating break-even analysis: {e}") from e