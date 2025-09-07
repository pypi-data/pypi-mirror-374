"""
Equivalence testing methods for FDA 510(k) submissions.
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional, Union, Dict, Any
import pandas as pd


def equivalence_test(
    test_data: np.ndarray,
    reference_data: np.ndarray,
    margin: float,
    alpha: float = 0.05,
    test_type: str = "two_one_sided"
) -> Dict[str, Any]:
    """
    Perform equivalence testing between test and reference devices.
    
    Parameters
    ----------
    test_data : np.ndarray
        Measurements from the test device
    reference_data : np.ndarray
        Measurements from the reference (predicate) device
    margin : float
        Equivalence margin (delta) for the test
    alpha : float, default=0.05
        Significance level
    test_type : str, default="two_one_sided"
        Type of equivalence test ("two_one_sided" or "confidence_interval")
    
    Returns
    -------
    dict
        Test results including p-values, confidence intervals, and conclusion
    """
    if len(test_data) != len(reference_data):
        raise ValueError("Test and reference data must have the same length")
    
    diff = test_data - reference_data
    n = len(diff)
    mean_diff = np.mean(diff)
    std_diff = np.std(diff, ddof=1)
    se_diff = std_diff / np.sqrt(n)
    
    results = {
        "mean_difference": mean_diff,
        "std_difference": std_diff,
        "se_difference": se_diff,
        "n": n,
        "margin": margin,
        "alpha": alpha
    }
    
    if test_type == "two_one_sided":
        # TOST procedure
        t_lower = (mean_diff + margin) / se_diff
        t_upper = (mean_diff - margin) / se_diff
        
        p_lower = stats.t.cdf(t_lower, df=n-1)
        p_upper = 1 - stats.t.cdf(t_upper, df=n-1)
        
        p_value = max(p_lower, p_upper)
        
        results.update({
            "t_lower": t_lower,
            "t_upper": t_upper,
            "p_lower": p_lower,
            "p_upper": p_upper,
            "p_value": p_value,
            "equivalent": p_value < alpha
        })
        
    elif test_type == "confidence_interval":
        # CI approach
        t_critical = stats.t.ppf(1 - alpha, df=n-1)
        ci_lower = mean_diff - t_critical * se_diff
        ci_upper = mean_diff + t_critical * se_diff
        
        equivalent = (ci_lower > -margin) and (ci_upper < margin)
        
        results.update({
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "ci_level": 1 - 2*alpha,
            "equivalent": equivalent
        })
    
    return results


def equivalence_margin_calculation(
    reference_data: np.ndarray,
    clinical_difference: float,
    method: str = "percentage",
    percentage: float = 0.20
) -> float:
    """
    Calculate appropriate equivalence margin based on clinical data.
    
    Parameters
    ----------
    reference_data : np.ndarray
        Historical reference device data
    clinical_difference : float
        Clinically meaningful difference
    method : str, default="percentage"
        Method for margin calculation ("percentage", "sd_based", "clinical")
    percentage : float, default=0.20
        Percentage for margin calculation (if method="percentage")
    
    Returns
    -------
    float
        Calculated equivalence margin
    """
    if method == "percentage":
        margin = np.abs(np.mean(reference_data) * percentage)
    elif method == "sd_based":
        margin = np.std(reference_data, ddof=1) * 0.5
    elif method == "clinical":
        margin = clinical_difference
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return margin


def confidence_interval(
    data: np.ndarray,
    confidence_level: float = 0.95,
    method: str = "t"
) -> Tuple[float, float]:
    """
    Calculate confidence interval for mean.
    
    Parameters
    ----------
    data : np.ndarray
        Sample data
    confidence_level : float, default=0.95
        Confidence level (e.g., 0.95 for 95% CI)
    method : str, default="t"
        Method for CI calculation ("t", "z", "bootstrap")
    
    Returns
    -------
    tuple
        (lower_bound, upper_bound) of confidence interval
    """
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    
    if method == "t":
        t_critical = stats.t.ppf((1 + confidence_level) / 2, df=n-1)
        margin_error = t_critical * se
    elif method == "z":
        z_critical = stats.norm.ppf((1 + confidence_level) / 2)
        margin_error = z_critical * se
    elif method == "bootstrap":
        # Bootstrap CI
        n_bootstrap = 10000
        bootstrap_means = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=n, replace=True)
            bootstrap_means.append(np.mean(sample))
        
        alpha = 1 - confidence_level
        lower = np.percentile(bootstrap_means, 100 * alpha/2)
        upper = np.percentile(bootstrap_means, 100 * (1 - alpha/2))
        return lower, upper
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return mean - margin_error, mean + margin_error