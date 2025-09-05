# 📦 linear_model

A lightweight and easy-to-use Python library for **Linear Regression**.  
Supports multiple training methods, regularization options, and sample weighting.

✨ Features:
- 📐 Normal Equation
- 🔁 Gradient Descent
- 🛡️ Ridge Regression (L2 regularization)
- ✂️ Lasso Regression (L1 regularization)
- ⚖️ Sample weights for weighted regression
- 🎯 Optional intercept fitting

---

## 🚀 Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/<your-username>/linear_model.git
cd linear_model
pip install -e .

Or install directly from GitHub (no clone needed):

pip install git+https://github.com/<your-username>/linear_model.git
```
---
## 📌 Quick Start
```python
import numpy as np
from linear_model import LinearRegression

# Training data
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

# Initialize model
model = LinearRegression(method="ridge", alpha=0.01, lambd=0.1)

# Fit model
model.fit(X, y, sample_weight=None)

# Predictions
print("Predictions:", model.predict([[5], [6]]))

# Model details
print("Coef:", model.coef_())
print("Intercept:", model.intercept_())

# R² score
print("R²:", model.score(X, y))
```

## ⚙️ API Overview

- **`fit(X, y, sample_weight=None)`** → Train the model  
- **`predict(X)`** → Predict target values  
- **`score(X, y, sample_weight=None)`** → Compute R² score  
- **`coef_()`** → Get feature coefficients  
- **`intercept_()`** → Get model intercept  

### Parameters
- `method`: `"normal_equation" | "gradient_descent" | "ridge" | "lasso"`  
- `fit_intercept`: `True` (default) | `False`  
- `n_iter`: Number of iterations for gradient methods (default: `1000`)  
- `alpha`: Learning rate for gradient methods (default: `0.01`)  
- `lambd`: Regularization strength (default: `0.1`)  

---

## 🧪 Testing

Run unit tests with:

```bash
pytest tests/
```
## 📂 Project Structure
```arduino
linear_model/
│── __init__.py
tests/
│── test_linear_regression.py
setup.py
README.md
LICENSE
```
## 📜 License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
