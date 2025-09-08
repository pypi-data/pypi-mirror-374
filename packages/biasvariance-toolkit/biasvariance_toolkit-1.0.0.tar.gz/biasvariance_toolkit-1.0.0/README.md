# Bias–Variance Decomposition Toolkit

A lightweight Python toolkit for estimating **bias** and **variance** components of machine learning models.  
Supports both **regression** (via Mean Squared Error) and **classification** (via 0–1 loss).  
Works seamlessly with **PyTorch models** and scikit-learn style data workflows.

---

## ✨ Features

- 📊 **Bias–variance decomposition** for:
  - **Regression** using Mean Squared Error (MSE)
  - **Classification** using 0–1 loss
- 🔄 **Bootstrap resampling** for reliable estimates
- 🧠 Works with **PyTorch models** (custom architectures supported)
- ⏱️ **Early stopping** with patience-based validation
- ⚡ Device support: CPU and CUDA (GPU)

---

## 📦 Installation

```bash
pip install biasvariance-toolkit
```

---

## 🚀 Quick Start

### 1. Define your PyTorch model
```python
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))
```

---

### 2. Bias–Variance Decomposition for Regression
```python
from biasvariance_toolkit import estimate_bias_variance_mse
import torch.nn as nn

bias_sq, variance, total_error, bias_plus_var, avg_train_loss, test_loss = estimate_bias_variance_mse(
    model_class=SimpleNet,
    model_kwargs={"input_dim": 10, "hidden_dim": 32, "output_dim": 1},
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    loss_fn=nn.MSELoss(),
    num_models=10,
    max_epochs=100,
    lr=0.001,
    device="cpu"
)
```

---

### 3. Bias–Variance Decomposition for Classification
```python
from biasvariance_toolkit import estimate_bias_variance_0_1
import torch.nn as nn

avg_bias, avg_var, expected_loss, empirical_loss, avg_train_loss, test_loss = estimate_bias_variance_0_1(
    model_class=SimpleNet,
    model_kwargs={"input_dim": 20, "hidden_dim": 64, "output_dim": 3},
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    loss_fn=nn.CrossEntropyLoss(),
    num_models=10,
    max_epochs=100,
    lr=0.001,
    device="cpu"
)
```

---

## 📘 API Overview

### `estimate_bias_variance_mse`
- **Task**: Regression (MSE)
- **Returns**:  
  - `bias_sq` – Squared bias  
  - `variance` – Variance  
  - `total_error` – Average test error (MSE)  
  - `bias_plus_variance` – Bias² + Variance  
  - `avg_train_loss` – Average training loss across models  
  - `test_loss` – Loss of the ensemble’s mean prediction  

---

### `estimate_bias_variance_0_1`
- **Task**: Classification (0–1 Loss)
- **Returns**:  
  - `avg_bias` – Average bias  
  - `avg_var` – Average variance  
  - `expected_loss` – Expected 0–1 loss  
  - `empirical_loss` – Empirical 0–1 loss  
  - `avg_train_loss` – Average training loss across models  
  - `test_loss` – Loss of the ensemble’s mean prediction  

---

## 🛠 Requirements
- Python ≥ 3.8
- PyTorch ≥ 1.9
- NumPy
- SciPy
- scikit-learn

---

## 📊 Example Use Cases
- Analyzing model stability under resampling
- Comparing architectures (e.g., shallow vs deep networks)
- Studying underfitting vs overfitting tradeoffs
- Teaching / demonstrating bias–variance decomposition concepts

---

## 📜 License
MIT License © 2025  
