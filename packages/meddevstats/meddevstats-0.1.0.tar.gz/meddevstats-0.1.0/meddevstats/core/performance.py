"""
Performance metrics for diagnostic device evaluation.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn import metrics
from typing import Dict, Tuple, Optional, Any, Union
import warnings


def sensitivity_specificity(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    confidence_level: float = 0.95,
    method: str = "wilson"
) -> Dict[str, Any]:
    """
    Calculate sensitivity, specificity with confidence intervals.
    
    Parameters
    ----------
    y_true : np.ndarray
        True binary labels (0 or 1)
    y_pred : np.ndarray
        Predicted binary labels (0 or 1)
    confidence_level : float, default=0.95
        Confidence level for intervals
    method : str, default="wilson"
        CI method ("wilson", "exact", "normal")
    
    Returns
    -------
    dict
        Performance metrics with confidence intervals
    """
    # Confusion matrix
    tn, fp, fn, tp = metrics.confusion_matrix(y_true, y_pred).ravel()
    
    # Calculate metrics
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    
    results = {
        "sensitivity": sensitivity,
        "specificity": specificity,
        "ppv": ppv,
        "npv": npv,
        "accuracy": accuracy,
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "prevalence": (tp + fn) / (tp + tn + fp + fn)
    }
    
    # Calculate confidence intervals
    def proportion_ci(successes, trials, method, confidence_level):
        if trials == 0:
            return (0, 0)
        
        p = successes / trials
        alpha = 1 - confidence_level
        
        if method == "wilson":
            # Wilson score interval
            z = stats.norm.ppf(1 - alpha/2)
            denominator = 1 + z**2 / trials
            center = (p + z**2 / (2*trials)) / denominator
            margin = z * np.sqrt(p*(1-p)/trials + z**2/(4*trials**2)) / denominator
            return (max(0, center - margin), min(1, center + margin))
        
        elif method == "exact":
            # Clopper-Pearson exact interval
            if successes == 0:
                lower = 0
            else:
                lower = stats.beta.ppf(alpha/2, successes, trials - successes + 1)
            
            if successes == trials:
                upper = 1
            else:
                upper = stats.beta.ppf(1 - alpha/2, successes + 1, trials - successes)
            
            return (lower, upper)
        
        elif method == "normal":
            # Normal approximation
            se = np.sqrt(p * (1 - p) / trials)
            z = stats.norm.ppf(1 - alpha/2)
            return (max(0, p - z*se), min(1, p + z*se))
    
    # Add confidence intervals
    results["sensitivity_ci"] = proportion_ci(tp, tp + fn, method, confidence_level)
    results["specificity_ci"] = proportion_ci(tn, tn + fp, method, confidence_level)
    results["ppv_ci"] = proportion_ci(tp, tp + fp, method, confidence_level)
    results["npv_ci"] = proportion_ci(tn, tn + fn, method, confidence_level)
    results["accuracy_ci"] = proportion_ci(tp + tn, tp + tn + fp + fn, method, confidence_level)
    
    # Calculate likelihood ratios
    if specificity < 1:
        lr_positive = sensitivity / (1 - specificity)
    else:
        lr_positive = np.inf
    
    if sensitivity < 1:
        lr_negative = (1 - sensitivity) / specificity
    else:
        lr_negative = 0
    
    results["lr_positive"] = lr_positive
    results["lr_negative"] = lr_negative
    
    # Calculate diagnostic odds ratio
    if fp * fn > 0:
        dor = (tp * tn) / (fp * fn)
    else:
        dor = np.inf
    
    results["diagnostic_odds_ratio"] = dor
    
    # Matthews correlation coefficient
    mcc_denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    if mcc_denominator > 0:
        mcc = (tp * tn - fp * fn) / mcc_denominator
    else:
        mcc = 0
    
    results["matthews_correlation"] = mcc
    
    return results


def roc_analysis(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    pos_label: Optional[Union[str, int]] = None,
    confidence_level: float = 0.95,
    n_bootstrap: int = 1000
) -> Dict[str, Any]:
    """
    Perform ROC analysis with AUC and confidence intervals.
    
    Parameters
    ----------
    y_true : np.ndarray
        True binary labels
    y_scores : np.ndarray
        Predicted scores or probabilities
    pos_label : optional
        Label of positive class
    confidence_level : float, default=0.95
        Confidence level for AUC
    n_bootstrap : int, default=1000
        Number of bootstrap samples for CI
    
    Returns
    -------
    dict
        ROC analysis results
    """
    # Calculate ROC curve
    fpr, tpr, thresholds = metrics.roc_curve(y_true, y_scores, pos_label=pos_label)
    auc = metrics.auc(fpr, tpr)
    
    # Find optimal threshold using Youden's J statistic
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[optimal_idx]
    optimal_sensitivity = tpr[optimal_idx]
    optimal_specificity = 1 - fpr[optimal_idx]
    
    results = {
        "auc": auc,
        "fpr": fpr,
        "tpr": tpr,
        "thresholds": thresholds,
        "optimal_threshold": optimal_threshold,
        "optimal_sensitivity": optimal_sensitivity,
        "optimal_specificity": optimal_specificity,
        "youden_j": j_scores[optimal_idx]
    }
    
    # Bootstrap confidence interval for AUC
    n = len(y_true)
    auc_scores = []
    
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, size=n, replace=True)
        y_true_boot = y_true[idx]
        y_scores_boot = y_scores[idx]
        
        try:
            auc_boot = metrics.roc_auc_score(y_true_boot, y_scores_boot)
            auc_scores.append(auc_boot)
        except:
            continue
    
    if auc_scores:
        alpha = 1 - confidence_level
        auc_ci_lower = np.percentile(auc_scores, 100 * alpha/2)
        auc_ci_upper = np.percentile(auc_scores, 100 * (1 - alpha/2))
        results["auc_ci"] = (auc_ci_lower, auc_ci_upper)
        results["auc_se"] = np.std(auc_scores)
    
    # DeLong test statistics (simplified)
    results["n_positive"] = np.sum(y_true == 1)
    results["n_negative"] = np.sum(y_true == 0)
    
    return results


def confusion_matrix_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[np.ndarray] = None,
    normalize: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive metrics from confusion matrix.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels
    y_pred : np.ndarray
        Predicted labels
    labels : np.ndarray, optional
        List of labels to index the matrix
    normalize : str, optional
        Normalization mode ('true', 'pred', 'all')
    
    Returns
    -------
    dict
        Confusion matrix and derived metrics
    """
    cm = metrics.confusion_matrix(y_true, y_pred, labels=labels, normalize=normalize)
    
    # For binary classification
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        
        # Calculate all metrics
        metrics_dict = {
            "confusion_matrix": cm,
            "accuracy": metrics.accuracy_score(y_true, y_pred),
            "balanced_accuracy": metrics.balanced_accuracy_score(y_true, y_pred),
            "precision": metrics.precision_score(y_true, y_pred, zero_division=0),
            "recall": metrics.recall_score(y_true, y_pred, zero_division=0),
            "f1_score": metrics.f1_score(y_true, y_pred, zero_division=0),
            "cohen_kappa": metrics.cohen_kappa_score(y_true, y_pred)
        }
        
        # Additional metrics
        total = np.sum(cm)
        observed_agreement = (tp + tn) / total
        
        # Expected agreement for Cohen's kappa
        marginal_pred_pos = (tp + fp) / total
        marginal_true_pos = (tp + fn) / total
        marginal_pred_neg = (tn + fn) / total
        marginal_true_neg = (tn + fp) / total
        
        expected_agreement = (marginal_pred_pos * marginal_true_pos + 
                            marginal_pred_neg * marginal_true_neg)
        
        metrics_dict["observed_agreement"] = observed_agreement
        metrics_dict["expected_agreement"] = expected_agreement
        
    else:
        # Multi-class metrics
        metrics_dict = {
            "confusion_matrix": cm,
            "accuracy": metrics.accuracy_score(y_true, y_pred),
            "balanced_accuracy": metrics.balanced_accuracy_score(y_true, y_pred),
            "cohen_kappa": metrics.cohen_kappa_score(y_true, y_pred)
        }
        
        # Per-class metrics
        precision = metrics.precision_score(y_true, y_pred, average=None, zero_division=0)
        recall = metrics.recall_score(y_true, y_pred, average=None, zero_division=0)
        f1 = metrics.f1_score(y_true, y_pred, average=None, zero_division=0)
        
        metrics_dict["precision_per_class"] = precision
        metrics_dict["recall_per_class"] = recall
        metrics_dict["f1_per_class"] = f1
        
        # Weighted averages
        metrics_dict["precision_weighted"] = metrics.precision_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics_dict["recall_weighted"] = metrics.recall_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics_dict["f1_weighted"] = metrics.f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    return metrics_dict


def diagnostic_accuracy(
    tp: int,
    tn: int,
    fp: int,
    fn: int,
    prevalence: Optional[float] = None,
    confidence_level: float = 0.95
) -> Dict[str, Any]:
    """
    Calculate diagnostic accuracy metrics from confusion matrix values.
    
    Parameters
    ----------
    tp : int
        True positives
    tn : int
        True negatives
    fp : int
        False positives
    fn : int
        False negatives
    prevalence : float, optional
        Disease prevalence (if different from sample)
    confidence_level : float, default=0.95
        Confidence level for intervals
    
    Returns
    -------
    dict
        Comprehensive diagnostic accuracy metrics
    """
    total = tp + tn + fp + fn
    
    # Basic metrics
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    accuracy = (tp + tn) / total
    
    # Use sample prevalence if not provided
    if prevalence is None:
        prevalence = (tp + fn) / total
    
    # Likelihood ratios
    if specificity < 1:
        lr_positive = sensitivity / (1 - specificity)
    else:
        lr_positive = np.inf
    
    if sensitivity < 1:
        lr_negative = (1 - sensitivity) / specificity
    else:
        lr_negative = 0
    
    # Diagnostic odds ratio
    if fp * fn > 0:
        dor = (tp * tn) / (fp * fn)
        log_dor = np.log(dor)
        se_log_dor = np.sqrt(1/tp + 1/tn + 1/fp + 1/fn)
        
        z = stats.norm.ppf((1 + confidence_level) / 2)
        dor_ci = (np.exp(log_dor - z * se_log_dor), 
                 np.exp(log_dor + z * se_log_dor))
    else:
        dor = np.inf
        dor_ci = (np.nan, np.nan)
    
    # Youden's J statistic
    youden_j = sensitivity + specificity - 1
    
    # Number needed to diagnose
    if youden_j > 0:
        nnd = 1 / youden_j
    else:
        nnd = np.inf
    
    # Adjusted PPV and NPV for different prevalence
    if lr_positive != np.inf:
        adjusted_ppv = (prevalence * lr_positive) / (prevalence * lr_positive + (1 - prevalence))
    else:
        adjusted_ppv = 1.0
    
    if lr_negative > 0:
        adjusted_npv = ((1 - prevalence) * (1 / lr_negative)) / ((1 - prevalence) * (1 / lr_negative) + prevalence)
    else:
        adjusted_npv = 1.0
    
    results = {
        "sensitivity": sensitivity,
        "specificity": specificity,
        "ppv": ppv,
        "npv": npv,
        "accuracy": accuracy,
        "prevalence": prevalence,
        "lr_positive": lr_positive,
        "lr_negative": lr_negative,
        "diagnostic_odds_ratio": dor,
        "dor_ci": dor_ci,
        "youden_j": youden_j,
        "number_needed_diagnose": nnd,
        "adjusted_ppv": adjusted_ppv,
        "adjusted_npv": adjusted_npv,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "total": total
    }
    
    return results