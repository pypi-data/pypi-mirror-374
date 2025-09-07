"""
Report generation utilities for FDA submissions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


def generate_summary_statistics(
    data: pd.DataFrame,
    group_by: Optional[str] = None,
    variables: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Generate comprehensive summary statistics.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data
    group_by : str, optional
        Grouping variable
    variables : list, optional
        Variables to summarize
    
    Returns
    -------
    pd.DataFrame
        Summary statistics table
    """
    if variables is None:
        variables = data.select_dtypes(include=[np.number]).columns.tolist()
    
    def calculate_stats(df):
        stats_dict = {}
        for var in variables:
            if var in df.columns:
                stats_dict[f"{var}_n"] = df[var].count()
                stats_dict[f"{var}_mean"] = df[var].mean()
                stats_dict[f"{var}_std"] = df[var].std()
                stats_dict[f"{var}_median"] = df[var].median()
                stats_dict[f"{var}_q25"] = df[var].quantile(0.25)
                stats_dict[f"{var}_q75"] = df[var].quantile(0.75)
                stats_dict[f"{var}_min"] = df[var].min()
                stats_dict[f"{var}_max"] = df[var].max()
                stats_dict[f"{var}_cv"] = df[var].std() / df[var].mean() if df[var].mean() != 0 else np.nan
        return pd.Series(stats_dict)
    
    if group_by:
        summary = data.groupby(group_by).apply(calculate_stats).reset_index()
    else:
        summary = pd.DataFrame([calculate_stats(data)])
    
    return summary


def create_validation_report(
    results: Dict[str, Any],
    study_info: Dict[str, str],
    acceptance_criteria: Dict[str, Any],
    output_format: str = "dict"
) -> Union[Dict, str]:
    """
    Create a comprehensive validation report.
    
    Parameters
    ----------
    results : dict
        Analysis results
    study_info : dict
        Study information (protocol, device, etc.)
    acceptance_criteria : dict
        Pass/fail criteria
    output_format : str
        Output format ("dict", "json", "markdown")
    
    Returns
    -------
    dict or str
        Formatted report
    """
    report = {
        "study_information": study_info,
        "analysis_date": datetime.now().isoformat(),
        "acceptance_criteria": acceptance_criteria,
        "results": results,
        "conclusions": {}
    }
    
    # Determine pass/fail status
    all_passed = True
    for key, value in results.items():
        if isinstance(value, dict) and "acceptable" in value:
            report["conclusions"][key] = {
                "passed": value["acceptable"],
                "value": value.get("value", "N/A")
            }
            if not value["acceptable"]:
                all_passed = False
    
    report["overall_conclusion"] = {
        "passed": all_passed,
        "recommendation": "Accept" if all_passed else "Review required"
    }
    
    if output_format == "json":
        return json.dumps(report, indent=2, default=str)
    
    elif output_format == "markdown":
        md = f"# Validation Report\n\n"
        md += f"## Study Information\n"
        for key, value in study_info.items():
            md += f"- **{key}**: {value}\n"
        md += f"\n- **Analysis Date**: {report['analysis_date']}\n\n"
        
        md += f"## Acceptance Criteria\n"
        for key, value in acceptance_criteria.items():
            md += f"- **{key}**: {value}\n"
        
        md += f"\n## Results Summary\n"
        md += f"| Metric | Value | Passed |\n"
        md += f"|--------|-------|--------|\n"
        for key, value in report["conclusions"].items():
            passed = "✓" if value["passed"] else "✗"
            md += f"| {key} | {value['value']} | {passed} |\n"
        
        md += f"\n## Overall Conclusion\n"
        md += f"**Status**: {'PASSED' if all_passed else 'FAILED'}\n"
        md += f"**Recommendation**: {report['overall_conclusion']['recommendation']}\n"
        
        return md
    
    return report


def format_results_table(
    results: Dict[str, Any],
    precision: int = 3,
    include_ci: bool = True
) -> pd.DataFrame:
    """
    Format results as a clean table.
    
    Parameters
    ----------
    results : dict
        Analysis results
    precision : int
        Decimal precision
    include_ci : bool
        Whether to include confidence intervals
    
    Returns
    -------
    pd.DataFrame
        Formatted results table
    """
    rows = []
    
    for key, value in results.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                if isinstance(subvalue, (int, float)):
                    rows.append({
                        "Category": key,
                        "Metric": subkey,
                        "Value": round(subvalue, precision)
                    })
                elif isinstance(subvalue, tuple) and len(subvalue) == 2 and include_ci:
                    if "ci" in subkey.lower() or "interval" in subkey.lower():
                        rows.append({
                            "Category": key,
                            "Metric": subkey,
                            "Value": f"({round(subvalue[0], precision)}, {round(subvalue[1], precision)})"
                        })
        elif isinstance(value, (int, float)):
            rows.append({
                "Category": "General",
                "Metric": key,
                "Value": round(value, precision)
            })
    
    return pd.DataFrame(rows)


def export_results(
    results: Dict[str, Any],
    filename: str,
    format: str = "excel",
    **kwargs
) -> None:
    """
    Export results to file.
    
    Parameters
    ----------
    results : dict
        Results to export
    filename : str
        Output filename
    format : str
        Export format ("excel", "csv", "json", "html")
    **kwargs
        Additional arguments for export function
    """
    if format == "excel":
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main results
            df_results = format_results_table(results)
            df_results.to_excel(writer, sheet_name='Results', index=False)
            
            # Add additional sheets if results contain DataFrames
            sheet_num = 2
            for key, value in results.items():
                if isinstance(value, pd.DataFrame):
                    sheet_name = f"Sheet{sheet_num}_{key[:20]}"
                    value.to_excel(writer, sheet_name=sheet_name, index=False)
                    sheet_num += 1
    
    elif format == "csv":
        df = format_results_table(results)
        df.to_csv(filename, index=False, **kwargs)
    
    elif format == "json":
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str, **kwargs)
    
    elif format == "html":
        df = format_results_table(results)
        html = df.to_html(index=False, **kwargs)
        with open(filename, 'w') as f:
            f.write(html)
    
    else:
        raise ValueError(f"Unsupported format: {format}")


def generate_fda_tables(
    data: pd.DataFrame,
    analysis_type: str
) -> Dict[str, pd.DataFrame]:
    """
    Generate FDA-compliant summary tables.
    
    Parameters
    ----------
    data : pd.DataFrame
        Analysis data
    analysis_type : str
        Type of analysis performed
    
    Returns
    -------
    dict
        Dictionary of formatted tables
    """
    tables = {}
    
    if analysis_type == "method_comparison":
        # Table 1: Descriptive Statistics
        tables["descriptive"] = generate_summary_statistics(data)
        
        # Table 2: Correlation Analysis
        if "reference" in data.columns and "test" in data.columns:
            correlation = data[["reference", "test"]].corr()
            tables["correlation"] = correlation
        
        # Table 3: Agreement Statistics (would need results dict)
        # This would be populated from analysis results
        
    elif analysis_type == "precision":
        # Precision study tables
        tables["precision_summary"] = generate_summary_statistics(
            data, 
            group_by="run" if "run" in data.columns else None
        )
    
    elif analysis_type == "diagnostic_accuracy":
        # Diagnostic accuracy tables
        if "truth" in data.columns and "predicted" in data.columns:
            crosstab = pd.crosstab(
                data["truth"], 
                data["predicted"],
                rownames=["Reference"],
                colnames=["Test"]
            )
            tables["confusion_matrix"] = crosstab
    
    return tables