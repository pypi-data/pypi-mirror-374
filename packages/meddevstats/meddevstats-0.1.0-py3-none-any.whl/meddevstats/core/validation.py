"""
Validation study methods for medical devices per FDA guidance.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional, Any, Union
import warnings
from sklearn.linear_model import LinearRegression


def method_comparison(
    reference: np.ndarray,
    test: np.ndarray,
    acceptance_criteria: Dict[str, float],
    methods: List[str] = ["bland_altman", "passing_bablok", "deming"]
) -> Dict[str, Any]:
    """
    Comprehensive method comparison study.
    
    Parameters
    ----------
    reference : np.ndarray
        Reference method measurements
    test : np.ndarray
        Test method measurements
    acceptance_criteria : dict
        Acceptance criteria for agreement
    methods : list
        Comparison methods to use
    
    Returns
    -------
    dict
        Comparison results from all methods
    """
    from .agreement import (
        bland_altman_analysis,
        passing_bablok_regression,
        deming_regression,
        lin_concordance_correlation
    )
    
    results = {
        "n_samples": len(reference),
        "reference_mean": np.mean(reference),
        "reference_std": np.std(reference, ddof=1),
        "test_mean": np.mean(test),
        "test_std": np.std(test, ddof=1),
        "correlation": np.corrcoef(reference, test)[0, 1]
    }
    
    # Run specified methods
    if "bland_altman" in methods:
        ba_results = bland_altman_analysis(test, reference)
        results["bland_altman"] = ba_results
        
        # Check acceptance criteria
        if "bias_limit" in acceptance_criteria:
            results["bland_altman"]["bias_acceptable"] = (
                abs(ba_results["bias"]) <= acceptance_criteria["bias_limit"]
            )
        
        if "loa_limit" in acceptance_criteria:
            loa_range = ba_results["loa_upper"] - ba_results["loa_lower"]
            results["bland_altman"]["loa_acceptable"] = (
                loa_range <= acceptance_criteria["loa_limit"]
            )
    
    if "passing_bablok" in methods:
        pb_results = passing_bablok_regression(reference, test)
        results["passing_bablok"] = pb_results
    
    if "deming" in methods:
        dem_results = deming_regression(reference, test)
        results["deming"] = dem_results
    
    # Lin's CCC
    ccc_results = lin_concordance_correlation(reference, test)
    results["concordance_correlation"] = ccc_results
    
    if "ccc_limit" in acceptance_criteria:
        results["concordance_correlation"]["acceptable"] = (
            ccc_results["ccc"] >= acceptance_criteria["ccc_limit"]
        )
    
    # Overall pass/fail
    all_acceptable = []
    for method in results:
        if isinstance(results[method], dict) and "acceptable" in results[method]:
            all_acceptable.append(results[method]["acceptable"])
    
    if all_acceptable:
        results["overall_acceptable"] = all(all_acceptable)
    
    return results


def precision_study(
    measurements: np.ndarray,
    groups: Optional[np.ndarray] = None,
    study_type: str = "repeatability",
    acceptance_cv: float = 0.10
) -> Dict[str, Any]:
    """
    Analyze precision (repeatability/reproducibility) per CLSI EP05-A3.
    
    Parameters
    ----------
    measurements : np.ndarray
        All measurements
    groups : np.ndarray, optional
        Grouping variable (e.g., day, operator, lot)
    study_type : str
        Type of precision study
    acceptance_cv : float
        Acceptable coefficient of variation
    
    Returns
    -------
    dict
        Precision study results
    """
    results = {
        "study_type": study_type,
        "n_measurements": len(measurements),
        "mean": np.mean(measurements),
        "sd": np.std(measurements, ddof=1),
        "cv": np.std(measurements, ddof=1) / np.mean(measurements)
    }
    
    if study_type == "repeatability":
        # Within-run precision
        results["repeatability_sd"] = np.std(measurements, ddof=1)
        results["repeatability_cv"] = results["cv"]
        results["acceptable"] = results["cv"] <= acceptance_cv
        
    elif study_type == "reproducibility" and groups is not None:
        # Between-group precision (e.g., between-day)
        df = pd.DataFrame({"measurement": measurements, "group": groups})
        groups_data = df.groupby("group")["measurement"].agg(["mean", "std", "count"])
        
        # Within-group variance
        within_var = np.mean(groups_data["std"]**2)
        within_sd = np.sqrt(within_var)
        
        # Between-group variance
        grand_mean = np.mean(measurements)
        between_var = np.sum(groups_data["count"] * (groups_data["mean"] - grand_mean)**2) / (len(groups_data) - 1)
        between_sd = np.sqrt(max(0, between_var - within_var/np.mean(groups_data["count"])))
        
        # Total variance
        total_var = within_var + between_var
        total_sd = np.sqrt(total_var)
        
        results.update({
            "n_groups": len(groups_data),
            "within_sd": within_sd,
            "within_cv": within_sd / grand_mean,
            "between_sd": between_sd,
            "between_cv": between_sd / grand_mean,
            "total_sd": total_sd,
            "total_cv": total_sd / grand_mean,
            "acceptable": total_sd / grand_mean <= acceptance_cv
        })
        
        # Variance components as percentages
        results["variance_components"] = {
            "within_group_pct": 100 * within_var / total_var,
            "between_group_pct": 100 * between_var / total_var
        }
    
    # Calculate confidence intervals for CV
    n = len(measurements)
    chi2_lower = stats.chi2.ppf(0.025, df=n-1)
    chi2_upper = stats.chi2.ppf(0.975, df=n-1)
    
    cv_ci_lower = results["cv"] * np.sqrt((n-1) / chi2_upper)
    cv_ci_upper = results["cv"] * np.sqrt((n-1) / chi2_lower)
    
    results["cv_95ci"] = (cv_ci_lower, cv_ci_upper)
    
    return results


def linearity_study(
    concentrations: np.ndarray,
    measurements: np.ndarray,
    replicates: Optional[int] = None,
    acceptance_r2: float = 0.99,
    acceptance_recovery: Tuple[float, float] = (0.90, 1.10)
) -> Dict[str, Any]:
    """
    Analyze linearity per CLSI EP06-A.
    
    Parameters
    ----------
    concentrations : np.ndarray
        Known concentration values
    measurements : np.ndarray
        Measured values
    replicates : int, optional
        Number of replicates per concentration
    acceptance_r2 : float
        Minimum acceptable R-squared
    acceptance_recovery : tuple
        Acceptable recovery range (min, max)
    
    Returns
    -------
    dict
        Linearity study results
    """
    # If replicates provided, calculate means
    if replicates is not None:
        n_levels = len(measurements) // replicates
        conc_unique = concentrations[:n_levels]
        meas_means = []
        meas_stds = []
        
        for i in range(n_levels):
            level_meas = measurements[i*replicates:(i+1)*replicates]
            meas_means.append(np.mean(level_meas))
            meas_stds.append(np.std(level_meas, ddof=1))
        
        x = conc_unique
        y = np.array(meas_means)
        stds = np.array(meas_stds)
    else:
        x = concentrations
        y = measurements
        stds = None
    
    # Linear regression
    X = x.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    
    slope = model.coef_[0]
    intercept = model.intercept_
    
    # R-squared
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    # Standard error of regression
    n = len(x)
    se_regression = np.sqrt(ss_res / (n - 2))
    
    # Confidence intervals for slope and intercept
    x_mean = np.mean(x)
    sx2 = np.sum((x - x_mean)**2)
    
    t_critical = stats.t.ppf(0.975, df=n-2)
    se_slope = se_regression / np.sqrt(sx2)
    se_intercept = se_regression * np.sqrt(1/n + x_mean**2/sx2)
    
    slope_ci = (slope - t_critical * se_slope, slope + t_critical * se_slope)
    intercept_ci = (intercept - t_critical * se_intercept, intercept + t_critical * se_intercept)
    
    # Recovery (slope as percentage)
    recovery = slope * 100
    
    # Residual analysis
    residuals = y - y_pred
    standardized_residuals = residuals / se_regression
    
    # Test for non-linearity (lack of fit test if replicates available)
    results = {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
        "slope_ci": slope_ci,
        "intercept_ci": intercept_ci,
        "se_regression": se_regression,
        "recovery_pct": recovery,
        "n_points": n,
        "residuals": residuals,
        "standardized_residuals": standardized_residuals
    }
    
    if stds is not None:
        results["measurement_cv"] = np.mean(stds / y) if np.all(y > 0) else np.nan
        results["measurement_stds"] = stds
    
    # Acceptance criteria
    results["r2_acceptable"] = r_squared >= acceptance_r2
    results["recovery_acceptable"] = (
        acceptance_recovery[0] <= recovery/100 <= acceptance_recovery[1]
    )
    results["overall_acceptable"] = (
        results["r2_acceptable"] and results["recovery_acceptable"]
    )
    
    # Linearity range
    results["linearity_range"] = (np.min(x), np.max(x))
    
    # Deviation from linearity
    max_deviation = np.max(np.abs(residuals))
    max_deviation_pct = 100 * max_deviation / np.mean(y)
    results["max_deviation"] = max_deviation
    results["max_deviation_pct"] = max_deviation_pct
    
    return results


def stability_analysis(
    measurements: pd.DataFrame,
    time_column: str,
    value_column: str,
    conditions: Optional[str] = None,
    acceptance_change: float = 0.10
) -> Dict[str, Any]:
    """
    Analyze stability over time.
    
    Parameters
    ----------
    measurements : pd.DataFrame
        DataFrame with time and measurement columns
    time_column : str
        Name of time column
    value_column : str
        Name of measurement column
    conditions : str, optional
        Storage conditions description
    acceptance_change : float
        Maximum acceptable change from baseline
    
    Returns
    -------
    dict
        Stability analysis results
    """
    # Sort by time
    df = measurements.sort_values(time_column)
    times = df[time_column].values
    values = df[value_column].values
    
    # Baseline (T0) value
    baseline = values[0]
    
    # Calculate percent change from baseline
    pct_change = 100 * (values - baseline) / baseline
    
    # Linear regression for trend
    X = times.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, values)
    
    slope = model.coef_[0]
    predicted = model.predict(X)
    
    # Test for significant trend
    n = len(times)
    residuals = values - predicted
    se_regression = np.sqrt(np.sum(residuals**2) / (n - 2))
    
    x_mean = np.mean(times)
    sx2 = np.sum((times - x_mean)**2)
    se_slope = se_regression / np.sqrt(sx2)
    
    t_stat = slope / se_slope
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=n-2))
    
    # Determine stability
    max_change = np.max(np.abs(pct_change[1:]))  # Exclude baseline
    stable = max_change <= (acceptance_change * 100)
    
    # Find stability period
    stability_period = None
    for i, pct in enumerate(pct_change[1:], 1):
        if abs(pct) > acceptance_change * 100:
            stability_period = times[i-1]
            break
    
    if stability_period is None:
        stability_period = times[-1]
    
    results = {
        "conditions": conditions,
        "n_timepoints": n,
        "baseline_value": baseline,
        "final_value": values[-1],
        "pct_change_from_baseline": pct_change,
        "max_pct_change": max_change,
        "trend_slope": slope,
        "trend_pvalue": p_value,
        "significant_trend": p_value < 0.05,
        "stable": stable,
        "stability_period": stability_period,
        "acceptance_change_pct": acceptance_change * 100
    }
    
    # Calculate CV at each timepoint if replicates available
    if measurements.groupby(time_column).size().min() > 1:
        cv_by_time = []
        for time in df[time_column].unique():
            time_values = df[df[time_column] == time][value_column].values
            if len(time_values) > 1:
                cv = np.std(time_values, ddof=1) / np.mean(time_values)
                cv_by_time.append(cv)
        
        results["cv_by_timepoint"] = cv_by_time
        results["mean_cv"] = np.mean(cv_by_time)
    
    return results