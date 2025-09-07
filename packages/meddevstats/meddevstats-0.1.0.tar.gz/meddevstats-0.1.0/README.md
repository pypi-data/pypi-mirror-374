# MedDevStats

Statistical analysis tools for medical device FDA 510(k) submissions.

## Overview

MedDevStats is a Python package providing comprehensive statistical methods for analyzing medical device data in accordance with FDA CDRH requirements for 510(k) submissions. It includes tools for equivalence testing, method comparison, performance evaluation, and validation studies.

## Features

### Statistical Methods

- **Equivalence Testing**
  - Two One-Sided Tests (TOST) procedure
  - Confidence interval approach
  - Equivalence margin calculations

- **Agreement Analysis**
  - Bland-Altman analysis
  - Passing-Bablok regression
  - Deming regression
  - Lin's concordance correlation coefficient

- **Performance Metrics**
  - Sensitivity and specificity with confidence intervals
  - ROC analysis with AUC
  - Confusion matrix metrics
  - Diagnostic accuracy measures

- **Validation Studies**
  - Method comparison studies
  - Precision studies (repeatability/reproducibility)
  - Linearity studies
  - Stability analysis

## Installation

```bash
pip install meddevstats
```

## Quick Start

```python
import numpy as np
from meddevstats import (
    equivalence_test,
    bland_altman_analysis,
    sensitivity_specificity,
    method_comparison
)

# Equivalence testing
test_device = np.random.normal(100, 10, 50)
reference_device = np.random.normal(98, 10, 50)

result = equivalence_test(
    test_data=test_device,
    reference_data=reference_device,
    margin=5.0,
    alpha=0.05
)

print(f"Devices are equivalent: {result['equivalent']}")
print(f"Mean difference: {result['mean_difference']:.2f}")

# Bland-Altman analysis
ba_result = bland_altman_analysis(
    method1=test_device,
    method2=reference_device,
    confidence_level=0.95
)

print(f"Bias: {ba_result['bias']:.2f}")
print(f"Limits of agreement: ({ba_result['loa_lower']:.2f}, {ba_result['loa_upper']:.2f})")

# Diagnostic accuracy
y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 1])

metrics = sensitivity_specificity(y_true, y_pred)
print(f"Sensitivity: {metrics['sensitivity']:.2%}")
print(f"Specificity: {metrics['specificity']:.2%}")
```

## FDA 510(k) Submission Support

This package is designed to support statistical analyses commonly required for FDA 510(k) submissions:

### Substantial Equivalence Testing
- Compare test device to predicate device
- Calculate confidence intervals for differences
- Assess clinical agreement

### Method Comparison Studies
- Validate new methods against reference standards
- Multiple regression methods (Passing-Bablok, Deming)
- Comprehensive agreement analysis

### Performance Evaluation
- Diagnostic accuracy metrics
- ROC curve analysis
- Confusion matrix with confidence intervals

### Validation Studies (CLSI Guidelines)
- Precision studies (EP05-A3)
- Linearity studies (EP06-A)
- Method comparison (EP09-A3)
- Stability studies

## Documentation

For detailed documentation, visit [https://meddevstats.readthedocs.io/](https://meddevstats.readthedocs.io/)

## Examples

### Equivalence Testing for 510(k)

```python
from meddevstats import equivalence_test, equivalence_margin_calculation

# Calculate appropriate margin based on clinical difference
reference_historical = np.random.normal(100, 8, 100)
margin = equivalence_margin_calculation(
    reference_data=reference_historical,
    clinical_difference=5.0,
    method="clinical"
)

# Perform equivalence test
result = equivalence_test(
    test_data=test_measurements,
    reference_data=reference_measurements,
    margin=margin,
    alpha=0.05,
    test_type="two_one_sided"
)

if result['equivalent']:
    print("Test device is substantially equivalent to predicate device")
```

### Method Comparison Study

```python
from meddevstats import method_comparison

# Define acceptance criteria
criteria = {
    "bias_limit": 5.0,
    "loa_limit": 15.0,
    "ccc_limit": 0.95
}

# Perform comprehensive comparison
comparison = method_comparison(
    reference=reference_method,
    test=new_method,
    acceptance_criteria=criteria,
    methods=["bland_altman", "passing_bablok", "deming"]
)

print(f"Overall acceptable: {comparison['overall_acceptable']}")
```

### Precision Study

```python
from meddevstats import precision_study

# Analyze repeatability
repeatability = precision_study(
    measurements=repeated_measurements,
    study_type="repeatability",
    acceptance_cv=0.05
)

print(f"CV: {repeatability['cv']:.2%}")
print(f"Acceptable: {repeatability['acceptable']}")

# Analyze reproducibility
reproducibility = precision_study(
    measurements=all_measurements,
    groups=day_labels,
    study_type="reproducibility",
    acceptance_cv=0.10
)

print(f"Within-day CV: {reproducibility['within_cv']:.2%}")
print(f"Between-day CV: {reproducibility['between_cv']:.2%}")
print(f"Total CV: {reproducibility['total_cv']:.2%}")
```

## Requirements

- Python >= 3.8
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- Pandas >= 1.3.0
- Matplotlib >= 3.3.0
- Seaborn >= 0.11.0
- Statsmodels >= 0.12.0
- Scikit-learn >= 0.24.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is intended for research and development purposes. While designed to support FDA 510(k) submissions, users are responsible for ensuring their analyses meet all regulatory requirements. Always consult with regulatory experts and FDA guidance documents for your specific submission needs.

## Citation

If you use MedDevStats in your research or regulatory submissions, please cite:

```
MedDevStats: Statistical Analysis Tools for Medical Device FDA 510(k) Submissions
https://github.com/yourusername/meddevstats
```

## Support

For questions, issues, or feature requests, please:
- Open an issue on [GitHub Issues](https://github.com/yourusername/meddevstats/issues)
- Check the [documentation](https://meddevstats.readthedocs.io/)
- Contact the maintainers

## Regulatory References

- [FDA 510(k) Premarket Notification](https://www.fda.gov/medical-devices/premarket-submissions/premarket-notification-510k)
- [Statistical Guidance on Reporting Results from Studies Evaluating Diagnostic Tests](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda)
- [CLSI Guidelines](https://clsi.org/) for method validation