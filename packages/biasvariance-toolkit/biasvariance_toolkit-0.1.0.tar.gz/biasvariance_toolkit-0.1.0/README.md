# BiasVariance Toolkit

A Python toolkit for bias–variance decomposition of machine learning models.

## Features
- Mean Squared Error (MSE) decomposition for regression tasks.
- 0–1 Loss decomposition for classification tasks.
- Works with both PyTorch models and scikit-learn models.

## Installation
Clone the repository and install locally:

```bash
pip install -e .
```

## Usage

```python
from biasvariance_toolkit import estimate_bias_variance_mse, estimate_bias_variance_0_1

# Example for regression (MSE)
bias, variance, total, bias_plus_var, avg_train_loss, test_loss = estimate_bias_variance_mse(...)

# Example for classification (0-1 Loss)
bias, variance, expected_loss, empirical_loss, avg_train_loss, test_loss = estimate_bias_variance_0_1(...)
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
