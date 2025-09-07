"""
Statistical operations module for the Scientific Calculator MCP Server.

This module provides comprehensive statistical analysis capabilities including
descriptive statistics, probability distributions, correlation analysis, and
hypothesis testing.
"""

import math
import statistics
from typing import List, Dict, Any, Union, Optional, Tuple
import numpy as np
from scipy import stats
from decimal import Decimal, getcontext

from calculator.models.errors import CalculatorError, ValidationError


class StatisticsError(CalculatorError):
    """Error for statistical operations."""
    pass


def _validate_data_list(data: List[Union[float, int]]) -> List[float]:
    """Validate and convert data list to floats."""
    if not data:
        raise ValidationError("Data list cannot be empty")
    
    if len(data) > 10000:
        raise ValidationError("Data list too large (maximum 10,000 items)")
    
    try:
        return [float(x) for x in data]
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid data in list: {e}") from e


def _validate_positive_number(value: Union[float, int], name: str) -> float:
    """Validate that a number is positive."""
    try:
        num_value = float(value)
        if num_value <= 0:
            raise ValidationError(f"{name} must be positive, got {num_value}")
        return num_value
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid {name}: {e}") from e


def _validate_probability(p: Union[float, int], name: str = "probability") -> float:
    """Validate that a value is a valid probability (0 <= p <= 1)."""
    try:
        prob_value = float(p)
        if not (0 <= prob_value <= 1):
            raise ValidationError(f"{name} must be between 0 and 1, got {prob_value}")
        return prob_value
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid {name}: {e}") from e


# Descriptive Statistics
def mean(data: List[Union[float, int]]) -> float:
    """Calculate the arithmetic mean of a dataset."""
    try:
        validated_data = _validate_data_list(data)
        return statistics.mean(validated_data)
    except statistics.StatisticsError as e:
        raise StatisticsError(f"Error calculating mean: {e}") from e


def median(data: List[Union[float, int]]) -> float:
    """Calculate the median of a dataset."""
    try:
        validated_data = _validate_data_list(data)
        return statistics.median(validated_data)
    except statistics.StatisticsError as e:
        raise StatisticsError(f"Error calculating median: {e}") from e


def mode(data: List[Union[float, int]]) -> Union[float, List[float]]:
    """Calculate the mode(s) of a dataset."""
    try:
        validated_data = _validate_data_list(data)
        
        # Use statistics.multimode to get all modes
        modes = statistics.multimode(validated_data)
        
        if len(modes) == 1:
            return modes[0]
        else:
            return modes
            
    except statistics.StatisticsError as e:
        raise StatisticsError(f"Error calculating mode: {e}") from e


def standard_deviation(data: List[Union[float, int]], sample: bool = True) -> float:
    """Calculate the standard deviation of a dataset.
    
    Args:
        data: List of numerical values
        sample: If True, calculate sample standard deviation (n-1). If False, population (n).
    """
    try:
        validated_data = _validate_data_list(data)
        
        if len(validated_data) < 2 and sample:
            raise StatisticsError("Sample standard deviation requires at least 2 data points")
        
        if sample:
            return statistics.stdev(validated_data)
        else:
            return statistics.pstdev(validated_data)
            
    except statistics.StatisticsError as e:
        raise StatisticsError(f"Error calculating standard deviation: {e}") from e


def variance(data: List[Union[float, int]], sample: bool = True) -> float:
    """Calculate the variance of a dataset.
    
    Args:
        data: List of numerical values
        sample: If True, calculate sample variance (n-1). If False, population (n).
    """
    try:
        validated_data = _validate_data_list(data)
        
        if len(validated_data) < 2 and sample:
            raise StatisticsError("Sample variance requires at least 2 data points")
        
        if sample:
            return statistics.variance(validated_data)
        else:
            return statistics.pvariance(validated_data)
            
    except statistics.StatisticsError as e:
        raise StatisticsError(f"Error calculating variance: {e}") from e


def quartiles(data: List[Union[float, int]]) -> Dict[str, float]:
    """Calculate quartiles (Q1, Q2, Q3) of a dataset."""
    try:
        validated_data = _validate_data_list(data)
        
        if len(validated_data) < 4:
            raise StatisticsError("Quartile calculation requires at least 4 data points")
        
        np_data = np.array(validated_data)
        
        q1 = float(np.percentile(np_data, 25))
        q2 = float(np.percentile(np_data, 50))  # Same as median
        q3 = float(np.percentile(np_data, 75))
        
        return {
            "Q1": q1,
            "Q2": q2,
            "Q3": q3,
            "IQR": q3 - q1  # Interquartile range
        }
        
    except Exception as e:
        raise StatisticsError(f"Error calculating quartiles: {e}") from e


def percentile(data: List[Union[float, int]], p: Union[float, int]) -> float:
    """Calculate the p-th percentile of a dataset."""
    try:
        validated_data = _validate_data_list(data)
        
        if not (0 <= p <= 100):
            raise ValidationError("Percentile must be between 0 and 100")
        
        np_data = np.array(validated_data)
        return float(np.percentile(np_data, p))
        
    except Exception as e:
        raise StatisticsError(f"Error calculating percentile: {e}") from e


def range_stats(data: List[Union[float, int]]) -> Dict[str, float]:
    """Calculate range statistics (min, max, range) of a dataset."""
    try:
        validated_data = _validate_data_list(data)
        
        min_val = min(validated_data)
        max_val = max(validated_data)
        range_val = max_val - min_val
        
        return {
            "min": min_val,
            "max": max_val,
            "range": range_val
        }
        
    except Exception as e:
        raise StatisticsError(f"Error calculating range statistics: {e}") from e


def descriptive_statistics(data: List[Union[float, int]], sample: bool = True) -> Dict[str, Any]:
    """Calculate comprehensive descriptive statistics for a dataset."""
    try:
        validated_data = _validate_data_list(data)
        
        result = {
            "count": len(validated_data),
            "mean": mean(validated_data),
            "median": median(validated_data),
            "mode": mode(validated_data),
            **range_stats(validated_data)
        }
        
        # Add variance and standard deviation if we have enough data points
        if len(validated_data) >= 2 or not sample:
            result["variance"] = variance(validated_data, sample)
            result["std_dev"] = standard_deviation(validated_data, sample)
        
        # Add quartiles if we have enough data points
        if len(validated_data) >= 4:
            result.update(quartiles(validated_data))
        
        return result
        
    except Exception as e:
        raise StatisticsError(f"Error calculating descriptive statistics: {e}") from e


# Probability Distributions
def normal_distribution(x: Union[float, int], mean: Union[float, int] = 0, 
                       std_dev: Union[float, int] = 1) -> Dict[str, float]:
    """Calculate normal distribution probability density and cumulative distribution.
    
    Args:
        x: Value to evaluate
        mean: Distribution mean (default: 0)
        std_dev: Distribution standard deviation (default: 1)
    """
    try:
        x_val = float(x)
        mean_val = float(mean)
        std_val = _validate_positive_number(std_dev, "standard deviation")
        
        # Probability density function
        pdf = stats.norm.pdf(x_val, mean_val, std_val)
        
        # Cumulative distribution function
        cdf = stats.norm.cdf(x_val, mean_val, std_val)
        
        return {
            "x": x_val,
            "mean": mean_val,
            "std_dev": std_val,
            "pdf": float(pdf),
            "cdf": float(cdf),
            "distribution": "normal"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error calculating normal distribution: {e}") from e


def binomial_distribution(k: int, n: int, p: Union[float, int]) -> Dict[str, float]:
    """Calculate binomial distribution probability mass and cumulative distribution.
    
    Args:
        k: Number of successes
        n: Number of trials
        p: Probability of success on each trial
    """
    try:
        if not isinstance(k, int) or k < 0:
            raise ValidationError("k must be a non-negative integer")
        
        if not isinstance(n, int) or n < 1:
            raise ValidationError("n must be a positive integer")
        
        if k > n:
            raise ValidationError("k cannot be greater than n")
        
        p_val = _validate_probability(p)
        
        # Probability mass function
        pmf = stats.binom.pmf(k, n, p_val)
        
        # Cumulative distribution function
        cdf = stats.binom.cdf(k, n, p_val)
        
        return {
            "k": k,
            "n": n,
            "p": p_val,
            "pmf": float(pmf),
            "cdf": float(cdf),
            "distribution": "binomial"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error calculating binomial distribution: {e}") from e


def poisson_distribution(k: int, lambda_param: Union[float, int]) -> Dict[str, float]:
    """Calculate Poisson distribution probability mass and cumulative distribution.
    
    Args:
        k: Number of events
        lambda_param: Average rate of events
    """
    try:
        if not isinstance(k, int) or k < 0:
            raise ValidationError("k must be a non-negative integer")
        
        lambda_val = _validate_positive_number(lambda_param, "lambda parameter")
        
        # Probability mass function
        pmf = stats.poisson.pmf(k, lambda_val)
        
        # Cumulative distribution function
        cdf = stats.poisson.cdf(k, lambda_val)
        
        return {
            "k": k,
            "lambda": lambda_val,
            "pmf": float(pmf),
            "cdf": float(cdf),
            "distribution": "poisson"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error calculating Poisson distribution: {e}") from e


def uniform_distribution(x: Union[float, int], a: Union[float, int], 
                        b: Union[float, int]) -> Dict[str, float]:
    """Calculate uniform distribution probability density and cumulative distribution.
    
    Args:
        x: Value to evaluate
        a: Lower bound
        b: Upper bound
    """
    try:
        x_val = float(x)
        a_val = float(a)
        b_val = float(b)
        
        if a_val >= b_val:
            raise ValidationError("Lower bound (a) must be less than upper bound (b)")
        
        # Probability density function
        pdf = stats.uniform.pdf(x_val, a_val, b_val - a_val)
        
        # Cumulative distribution function
        cdf = stats.uniform.cdf(x_val, a_val, b_val - a_val)
        
        return {
            "x": x_val,
            "a": a_val,
            "b": b_val,
            "pdf": float(pdf),
            "cdf": float(cdf),
            "distribution": "uniform"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error calculating uniform distribution: {e}") from e


def exponential_distribution(x: Union[float, int], 
                           lambda_param: Union[float, int]) -> Dict[str, float]:
    """Calculate exponential distribution probability density and cumulative distribution.
    
    Args:
        x: Value to evaluate (must be non-negative)
        lambda_param: Rate parameter
    """
    try:
        x_val = float(x)
        if x_val < 0:
            raise ValidationError("x must be non-negative for exponential distribution")
        
        lambda_val = _validate_positive_number(lambda_param, "lambda parameter")
        
        # Probability density function
        pdf = stats.expon.pdf(x_val, scale=1/lambda_val)
        
        # Cumulative distribution function
        cdf = stats.expon.cdf(x_val, scale=1/lambda_val)
        
        return {
            "x": x_val,
            "lambda": lambda_val,
            "pdf": float(pdf),
            "cdf": float(cdf),
            "distribution": "exponential"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error calculating exponential distribution: {e}") from e


# Correlation and Regression Analysis
def correlation_coefficient(x_data: List[Union[float, int]], 
                          y_data: List[Union[float, int]]) -> Dict[str, float]:
    """Calculate Pearson correlation coefficient between two datasets."""
    try:
        x_validated = _validate_data_list(x_data)
        y_validated = _validate_data_list(y_data)
        
        if len(x_validated) != len(y_validated):
            raise ValidationError("x_data and y_data must have the same length")
        
        if len(x_validated) < 2:
            raise StatisticsError("Correlation requires at least 2 data points")
        
        # Calculate Pearson correlation coefficient
        correlation, p_value = stats.pearsonr(x_validated, y_validated)
        
        return {
            "correlation": float(correlation),
            "p_value": float(p_value),
            "n": len(x_validated),
            "method": "pearson"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error calculating correlation: {e}") from e


def linear_regression(x_data: List[Union[float, int]], 
                     y_data: List[Union[float, int]]) -> Dict[str, float]:
    """Perform linear regression analysis on two datasets."""
    try:
        x_validated = _validate_data_list(x_data)
        y_validated = _validate_data_list(y_data)
        
        if len(x_validated) != len(y_validated):
            raise ValidationError("x_data and y_data must have the same length")
        
        if len(x_validated) < 2:
            raise StatisticsError("Linear regression requires at least 2 data points")
        
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_validated, y_validated)
        
        return {
            "slope": float(slope),
            "intercept": float(intercept),
            "r_value": float(r_value),
            "r_squared": float(r_value ** 2),
            "p_value": float(p_value),
            "std_err": float(std_err),
            "n": len(x_validated),
            "equation": f"y = {slope:.6f}x + {intercept:.6f}"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error performing linear regression: {e}") from e


# Hypothesis Testing
def t_test_one_sample(data: List[Union[float, int]], 
                     population_mean: Union[float, int]) -> Dict[str, float]:
    """Perform one-sample t-test."""
    try:
        validated_data = _validate_data_list(data)
        pop_mean = float(population_mean)
        
        if len(validated_data) < 2:
            raise StatisticsError("t-test requires at least 2 data points")
        
        # Perform one-sample t-test
        t_statistic, p_value = stats.ttest_1samp(validated_data, pop_mean)
        
        # Calculate degrees of freedom
        df = len(validated_data) - 1
        
        return {
            "t_statistic": float(t_statistic),
            "p_value": float(p_value),
            "degrees_of_freedom": df,
            "sample_mean": mean(validated_data),
            "population_mean": pop_mean,
            "n": len(validated_data),
            "test_type": "one_sample_t_test"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error performing t-test: {e}") from e


def t_test_two_sample(data1: List[Union[float, int]], 
                     data2: List[Union[float, int]], 
                     equal_var: bool = True) -> Dict[str, float]:
    """Perform two-sample t-test."""
    try:
        data1_validated = _validate_data_list(data1)
        data2_validated = _validate_data_list(data2)
        
        if len(data1_validated) < 2 or len(data2_validated) < 2:
            raise StatisticsError("Two-sample t-test requires at least 2 data points in each group")
        
        # Perform two-sample t-test
        t_statistic, p_value = stats.ttest_ind(data1_validated, data2_validated, equal_var=equal_var)
        
        return {
            "t_statistic": float(t_statistic),
            "p_value": float(p_value),
            "sample1_mean": mean(data1_validated),
            "sample2_mean": mean(data2_validated),
            "n1": len(data1_validated),
            "n2": len(data2_validated),
            "equal_variance_assumed": equal_var,
            "test_type": "two_sample_t_test"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error performing two-sample t-test: {e}") from e


def chi_square_test(observed: List[Union[float, int]], 
                   expected: Optional[List[Union[float, int]]] = None) -> Dict[str, float]:
    """Perform chi-square goodness of fit test."""
    try:
        observed_validated = _validate_data_list(observed)
        
        # Check for non-negative values
        if any(x < 0 for x in observed_validated):
            raise ValidationError("Observed frequencies must be non-negative")
        
        if expected is not None:
            expected_validated = _validate_data_list(expected)
            
            if len(observed_validated) != len(expected_validated):
                raise ValidationError("Observed and expected arrays must have the same length")
            
            # Check for positive expected values
            if any(x <= 0 for x in expected_validated):
                raise ValidationError("Expected frequencies must be positive")
        else:
            # If no expected values provided, assume uniform distribution
            total = sum(observed_validated)
            expected_validated = [total / len(observed_validated)] * len(observed_validated)
        
        # Perform chi-square test
        chi2_statistic, p_value = stats.chisquare(observed_validated, expected_validated)
        
        # Calculate degrees of freedom
        df = len(observed_validated) - 1
        
        return {
            "chi2_statistic": float(chi2_statistic),
            "p_value": float(p_value),
            "degrees_of_freedom": df,
            "observed": observed_validated,
            "expected": expected_validated,
            "test_type": "chi_square_goodness_of_fit"
        }
        
    except Exception as e:
        raise StatisticsError(f"Error performing chi-square test: {e}") from e


# Distribution registry for dynamic access
DISTRIBUTIONS = {
    'normal': normal_distribution,
    'gaussian': normal_distribution,
    'binomial': binomial_distribution,
    'poisson': poisson_distribution,
    'uniform': uniform_distribution,
    'exponential': exponential_distribution,
}


def get_distribution_function(distribution_name: str):
    """Get a distribution function by name from the registry."""
    if distribution_name.lower() not in DISTRIBUTIONS:
        available_distributions = ', '.join(sorted(DISTRIBUTIONS.keys()))
        raise ValidationError(
            f"Unknown distribution: {distribution_name}. "
            f"Available distributions: {available_distributions}"
        )
    return DISTRIBUTIONS[distribution_name.lower()]