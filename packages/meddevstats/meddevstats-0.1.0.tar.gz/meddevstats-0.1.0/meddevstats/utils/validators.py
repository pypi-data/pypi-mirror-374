"""
Data validation utilities for medical device data.
"""

import numpy as np
import pandas as pd
from typing import Union, Optional, List, Tuple, Any
import warnings


def validate_input_arrays(
    *arrays: np.ndarray,
    equal_length: bool = True,
    min_samples: int = 3,
    allow_nan: bool = False
) -> List[np.ndarray]:
    """
    Validate input arrays for statistical analysis.
    
    Parameters
    ----------
    *arrays : np.ndarray
        Arrays to validate
    equal_length : bool
        Whether arrays must have equal length
    min_samples : int
        Minimum required samples
    allow_nan : bool
        Whether to allow NaN values
    
    Returns
    -------
    list
        Validated arrays
    
    Raises
    ------
    ValueError
        If validation fails
    """
    validated = []
    
    for i, arr in enumerate(arrays):
        # Convert to numpy array if needed
        if not isinstance(arr, np.ndarray):
            arr = np.array(arr)
        
        # Check dimensions
        if arr.ndim != 1:
            arr = arr.flatten()
        
        # Check minimum samples
        if len(arr) < min_samples:
            raise ValueError(f"Array {i} has {len(arr)} samples, minimum required is {min_samples}")
        
        # Check for NaN values
        if not allow_nan and np.any(np.isnan(arr)):
            raise ValueError(f"Array {i} contains NaN values")
        
        validated.append(arr)
    
    # Check equal length if required
    if equal_length and len(validated) > 1:
        lengths = [len(arr) for arr in validated]
        if len(set(lengths)) > 1:
            raise ValueError(f"Arrays have different lengths: {lengths}")
    
    return validated


def check_binary_classification_data(
    y_true: np.ndarray,
    y_pred: Optional[np.ndarray] = None,
    y_scores: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, ...]:
    """
    Validate binary classification data.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels
    y_pred : np.ndarray, optional
        Predicted labels
    y_scores : np.ndarray, optional
        Prediction scores
    
    Returns
    -------
    tuple
        Validated arrays
    
    Raises
    ------
    ValueError
        If data is not valid for binary classification
    """
    y_true = np.asarray(y_true)
    
    # Check if binary
    unique_labels = np.unique(y_true)
    if len(unique_labels) != 2:
        raise ValueError(f"Expected binary labels, found {len(unique_labels)} classes: {unique_labels}")
    
    # Ensure labels are 0 and 1
    if not set(unique_labels).issubset({0, 1}):
        warnings.warn("Converting labels to 0 and 1")
        y_true = (y_true == unique_labels[1]).astype(int)
    
    result = [y_true]
    
    if y_pred is not None:
        y_pred = np.asarray(y_pred)
        if len(y_pred) != len(y_true):
            raise ValueError(f"y_pred length ({len(y_pred)}) != y_true length ({len(y_true)})")
        
        # Convert to 0/1 if needed
        if not set(np.unique(y_pred)).issubset({0, 1}):
            y_pred = (y_pred == unique_labels[1]).astype(int)
        
        result.append(y_pred)
    
    if y_scores is not None:
        y_scores = np.asarray(y_scores)
        if len(y_scores) != len(y_true):
            raise ValueError(f"y_scores length ({len(y_scores)}) != y_true length ({len(y_true)})")
        
        # Check if scores are probabilities
        if np.all((y_scores >= 0) & (y_scores <= 1)):
            pass  # Valid probabilities
        else:
            warnings.warn("Scores appear to not be probabilities (not in [0, 1])")
        
        result.append(y_scores)
    
    return tuple(result)


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: Optional[List[str]] = None,
    numeric_columns: Optional[List[str]] = None,
    categorical_columns: Optional[List[str]] = None,
    date_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Validate DataFrame structure and content.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate
    required_columns : list, optional
        Required column names
    numeric_columns : list, optional
        Columns that must be numeric
    categorical_columns : list, optional
        Columns that should be categorical
    date_columns : list, optional
        Columns that should be datetime
    
    Returns
    -------
    pd.DataFrame
        Validated DataFrame
    
    Raises
    ------
    ValueError
        If validation fails
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Check required columns
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    # Validate numeric columns
    if numeric_columns:
        for col in numeric_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found")
            
            # Try to convert to numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Check for conversion failures
            if df[col].isna().all():
                raise ValueError(f"Column '{col}' cannot be converted to numeric")
    
    # Validate categorical columns
    if categorical_columns:
        for col in categorical_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found")
            
            # Convert to categorical if not already
            if not pd.api.types.is_categorical_dtype(df[col]):
                df[col] = pd.Categorical(df[col])
    
    # Validate date columns
    if date_columns:
        for col in date_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found")
            
            # Try to convert to datetime
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Check for conversion failures
            if df[col].isna().all():
                raise ValueError(f"Column '{col}' cannot be converted to datetime")
    
    return df


def check_sample_size(
    n: int,
    test_type: str,
    power: float = 0.8,
    alpha: float = 0.05,
    effect_size: Optional[float] = None
) -> Dict[str, Any]:
    """
    Check if sample size is adequate for the intended analysis.
    
    Parameters
    ----------
    n : int
        Sample size
    test_type : str
        Type of statistical test
    power : float
        Desired statistical power
    alpha : float
        Significance level
    effect_size : float, optional
        Expected effect size
    
    Returns
    -------
    dict
        Sample size assessment
    """
    recommendations = {
        "equivalence": 50,
        "agreement": 40,
        "roc_analysis": 100,
        "precision": 20,
        "linearity": 30,
        "method_comparison": 40
    }
    
    min_recommended = recommendations.get(test_type, 30)
    
    assessment = {
        "sample_size": n,
        "test_type": test_type,
        "minimum_recommended": min_recommended,
        "adequate": n >= min_recommended
    }
    
    if n < min_recommended:
        assessment["warning"] = (
            f"Sample size ({n}) is below recommended minimum ({min_recommended}) "
            f"for {test_type} analysis. Results may have limited statistical power."
        )
    
    # Additional checks for specific tests
    if test_type == "equivalence" and effect_size:
        from statsmodels.stats.power import tt_solve_power
        required_n = tt_solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            ratio=1,
            alternative='two-sided'
        )
        assessment["required_for_power"] = int(np.ceil(required_n))
        assessment["current_power"] = tt_solve_power(
            effect_size=effect_size,
            nobs=n,
            alpha=alpha,
            ratio=1,
            alternative='two-sided'
        )
    
    return assessment


def remove_outliers(
    data: np.ndarray,
    method: str = "iqr",
    threshold: float = 1.5,
    return_mask: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Remove outliers from data.
    
    Parameters
    ----------
    data : np.ndarray
        Input data
    method : str
        Method for outlier detection ("iqr", "zscore", "modified_zscore")
    threshold : float
        Threshold for outlier detection
    return_mask : bool
        Whether to return outlier mask
    
    Returns
    -------
    np.ndarray or tuple
        Cleaned data (and outlier mask if requested)
    """
    data = np.asarray(data)
    
    if method == "iqr":
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        mask = (data >= lower_bound) & (data <= upper_bound)
        
    elif method == "zscore":
        z_scores = np.abs(stats.zscore(data))
        mask = z_scores < threshold
        
    elif method == "modified_zscore":
        median = np.median(data)
        mad = np.median(np.abs(data - median))
        modified_z_scores = 0.6745 * (data - median) / mad
        mask = np.abs(modified_z_scores) < threshold
        
    else:
        raise ValueError(f"Unknown method: {method}")
    
    if return_mask:
        return data[mask], ~mask
    else:
        return data[mask]