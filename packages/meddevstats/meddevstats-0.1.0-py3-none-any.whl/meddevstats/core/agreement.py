"""
Agreement analysis methods for method comparison studies.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns


def bland_altman_analysis(
    method1: np.ndarray,
    method2: np.ndarray,
    confidence_level: float = 0.95,
    plot: bool = False
) -> Dict[str, Any]:
    """
    Perform Bland-Altman analysis for method comparison.
    
    Parameters
    ----------
    method1 : np.ndarray
        Measurements from method 1
    method2 : np.ndarray
        Measurements from method 2
    confidence_level : float, default=0.95
        Confidence level for limits of agreement
    plot : bool, default=False
        Whether to generate Bland-Altman plot
    
    Returns
    -------
    dict
        Analysis results including bias, limits of agreement, etc.
    """
    if len(method1) != len(method2):
        raise ValueError("Both methods must have the same number of measurements")
    
    mean_values = (method1 + method2) / 2
    differences = method1 - method2
    
    bias = np.mean(differences)
    std_diff = np.std(differences, ddof=1)
    n = len(differences)
    
    # Calculate limits of agreement
    z_critical = stats.norm.ppf((1 + confidence_level) / 2)
    loa_lower = bias - z_critical * std_diff
    loa_upper = bias + z_critical * std_diff
    
    # Standard errors
    se_bias = std_diff / np.sqrt(n)
    se_loa = np.sqrt(3 * std_diff**2 / n)
    
    # Confidence intervals for bias and LoA
    t_critical = stats.t.ppf((1 + confidence_level) / 2, df=n-1)
    bias_ci = (bias - t_critical * se_bias, bias + t_critical * se_bias)
    loa_lower_ci = (loa_lower - t_critical * se_loa, loa_lower + t_critical * se_loa)
    loa_upper_ci = (loa_upper - t_critical * se_loa, loa_upper + t_critical * se_loa)
    
    # Test for proportional bias
    slope, intercept, r_value, p_value, std_err = stats.linregress(mean_values, differences)
    
    results = {
        "bias": bias,
        "bias_ci": bias_ci,
        "std_differences": std_diff,
        "loa_lower": loa_lower,
        "loa_upper": loa_upper,
        "loa_lower_ci": loa_lower_ci,
        "loa_upper_ci": loa_upper_ci,
        "proportional_bias_slope": slope,
        "proportional_bias_pvalue": p_value,
        "n": n
    }
    
    if plot:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(mean_values, differences, alpha=0.5)
        ax.axhline(y=bias, color='red', linestyle='-', label=f'Bias: {bias:.3f}')
        ax.axhline(y=loa_lower, color='red', linestyle='--', label=f'LoA: {loa_lower:.3f}')
        ax.axhline(y=loa_upper, color='red', linestyle='--', label=f'LoA: {loa_upper:.3f}')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        ax.set_xlabel('Mean of Two Methods')
        ax.set_ylabel('Difference (Method 1 - Method 2)')
        ax.set_title('Bland-Altman Plot')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        results['plot'] = fig
    
    return results


def passing_bablok_regression(
    x: np.ndarray,
    y: np.ndarray,
    confidence_level: float = 0.95,
    n_bootstrap: int = 1000
) -> Dict[str, Any]:
    """
    Perform Passing-Bablok regression for method comparison.
    
    Parameters
    ----------
    x : np.ndarray
        Reference method measurements
    y : np.ndarray
        Test method measurements
    confidence_level : float, default=0.95
        Confidence level for parameters
    n_bootstrap : int, default=1000
        Number of bootstrap samples for CI
    
    Returns
    -------
    dict
        Regression results including slope, intercept, and CIs
    """
    n = len(x)
    if n != len(y):
        raise ValueError("x and y must have the same length")
    
    # Calculate all pairwise slopes
    slopes = []
    for i in range(n):
        for j in range(i+1, n):
            if x[j] != x[i]:
                slope = (y[j] - y[i]) / (x[j] - x[i])
                slopes.append(slope)
    
    slopes = np.array(slopes)
    slopes = slopes[~np.isnan(slopes)]
    
    # Median slope (beta)
    beta = np.median(slopes)
    
    # Calculate intercept (alpha)
    alpha = np.median(y - beta * x)
    
    # Bootstrap confidence intervals
    beta_bootstrap = []
    alpha_bootstrap = []
    
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, size=n, replace=True)
        x_boot = x[idx]
        y_boot = y[idx]
        
        slopes_boot = []
        for i in range(n):
            for j in range(i+1, n):
                if x_boot[j] != x_boot[i]:
                    slope = (y_boot[j] - y_boot[i]) / (x_boot[j] - x_boot[i])
                    slopes_boot.append(slope)
        
        if slopes_boot:
            beta_boot = np.median(slopes_boot)
            alpha_boot = np.median(y_boot - beta_boot * x_boot)
            beta_bootstrap.append(beta_boot)
            alpha_bootstrap.append(alpha_boot)
    
    # Calculate confidence intervals
    alpha_level = 1 - confidence_level
    beta_ci = np.percentile(beta_bootstrap, [100*alpha_level/2, 100*(1-alpha_level/2)])
    alpha_ci = np.percentile(alpha_bootstrap, [100*alpha_level/2, 100*(1-alpha_level/2)])
    
    # Test for systematic bias
    systematic_bias = not (alpha_ci[0] <= 0 <= alpha_ci[1])
    proportional_bias = not (beta_ci[0] <= 1 <= beta_ci[1])
    
    return {
        "slope": beta,
        "intercept": alpha,
        "slope_ci": tuple(beta_ci),
        "intercept_ci": tuple(alpha_ci),
        "systematic_bias": systematic_bias,
        "proportional_bias": proportional_bias,
        "n": n
    }


def deming_regression(
    x: np.ndarray,
    y: np.ndarray,
    error_ratio: float = 1.0,
    confidence_level: float = 0.95
) -> Dict[str, Any]:
    """
    Perform Deming regression accounting for errors in both variables.
    
    Parameters
    ----------
    x : np.ndarray
        Reference method measurements
    y : np.ndarray
        Test method measurements
    error_ratio : float, default=1.0
        Ratio of error variances (var_y / var_x)
    confidence_level : float, default=0.95
        Confidence level for parameters
    
    Returns
    -------
    dict
        Regression results
    """
    n = len(x)
    if n != len(y):
        raise ValueError("x and y must have the same length")
    
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    # Center the data
    x_c = x - x_mean
    y_c = y - y_mean
    
    # Calculate variances and covariance
    s_xx = np.sum(x_c**2) / (n - 1)
    s_yy = np.sum(y_c**2) / (n - 1)
    s_xy = np.sum(x_c * y_c) / (n - 1)
    
    # Deming regression slope
    lambda_ratio = error_ratio
    u = (s_yy - lambda_ratio * s_xx) / (2 * s_xy)
    slope = u + np.sign(s_xy) * np.sqrt(u**2 + lambda_ratio)
    
    # Intercept
    intercept = y_mean - slope * x_mean
    
    # Standard errors (simplified)
    residuals = y - (intercept + slope * x)
    residual_variance = np.var(residuals, ddof=2)
    
    se_slope = np.sqrt(residual_variance / np.sum((x - x_mean)**2))
    se_intercept = np.sqrt(residual_variance * (1/n + x_mean**2 / np.sum((x - x_mean)**2)))
    
    # Confidence intervals
    t_critical = stats.t.ppf((1 + confidence_level) / 2, df=n-2)
    slope_ci = (slope - t_critical * se_slope, slope + t_critical * se_slope)
    intercept_ci = (intercept - t_critical * se_intercept, intercept + t_critical * se_intercept)
    
    return {
        "slope": slope,
        "intercept": intercept,
        "slope_ci": slope_ci,
        "intercept_ci": intercept_ci,
        "se_slope": se_slope,
        "se_intercept": se_intercept,
        "error_ratio": error_ratio,
        "n": n
    }


def lin_concordance_correlation(
    x: np.ndarray,
    y: np.ndarray,
    ci_method: str = "bootstrap",
    n_bootstrap: int = 1000,
    confidence_level: float = 0.95
) -> Dict[str, Any]:
    """
    Calculate Lin's concordance correlation coefficient.
    
    Parameters
    ----------
    x : np.ndarray
        First set of measurements
    y : np.ndarray
        Second set of measurements
    ci_method : str, default="bootstrap"
        Method for CI calculation ("bootstrap" or "asymptotic")
    n_bootstrap : int, default=1000
        Number of bootstrap samples
    confidence_level : float, default=0.95
        Confidence level
    
    Returns
    -------
    dict
        CCC value and confidence interval
    """
    n = len(x)
    if n != len(y):
        raise ValueError("x and y must have the same length")
    
    # Calculate means and variances
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    x_var = np.var(x, ddof=1)
    y_var = np.var(y, ddof=1)
    
    # Covariance and correlation
    covariance = np.cov(x, y)[0, 1]
    pearson_r = covariance / (np.sqrt(x_var) * np.sqrt(y_var))
    
    # CCC components
    precision = pearson_r
    accuracy = 2 * covariance / (x_var + y_var + (x_mean - y_mean)**2)
    
    # Lin's CCC
    ccc = precision * accuracy
    
    results = {
        "ccc": ccc,
        "pearson_r": pearson_r,
        "precision": precision,
        "accuracy": accuracy,
        "bias_correction_factor": accuracy,
        "n": n
    }
    
    if ci_method == "bootstrap":
        # Bootstrap CI
        ccc_bootstrap = []
        for _ in range(n_bootstrap):
            idx = np.random.choice(n, size=n, replace=True)
            x_boot = x[idx]
            y_boot = y[idx]
            
            x_mean_b = np.mean(x_boot)
            y_mean_b = np.mean(y_boot)
            x_var_b = np.var(x_boot, ddof=1)
            y_var_b = np.var(y_boot, ddof=1)
            cov_b = np.cov(x_boot, y_boot)[0, 1]
            
            ccc_b = 2 * cov_b / (x_var_b + y_var_b + (x_mean_b - y_mean_b)**2)
            ccc_bootstrap.append(ccc_b)
        
        alpha = 1 - confidence_level
        ci_lower = np.percentile(ccc_bootstrap, 100 * alpha/2)
        ci_upper = np.percentile(ccc_bootstrap, 100 * (1 - alpha/2))
        
    elif ci_method == "asymptotic":
        # Fisher z-transformation
        z = 0.5 * np.log((1 + ccc) / (1 - ccc))
        se_z = 1 / np.sqrt(n - 3)
        z_critical = stats.norm.ppf((1 + confidence_level) / 2)
        
        z_lower = z - z_critical * se_z
        z_upper = z + z_critical * se_z
        
        # Back-transform
        ci_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
        ci_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)
    
    results["ci"] = (ci_lower, ci_upper)
    results["ci_method"] = ci_method
    
    return results