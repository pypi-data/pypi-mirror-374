from linear_model import LinearRegression  # import your class

import numpy as np

# Seed for reproducibility
np.random.seed(42)

# Number of samples and features
n_samples = 500
n_features = 10

# Generate independent features (standard normal distribution)
X = np.random.randn(n_samples, n_features)

# Create non-linear relationships and coefficients
true_coefs = np.array([1.5, -2.0, 0.0, 3.3, 0.0, 0.0, -1.2, 0.0, 0.5, 2.1])

# Target with linear and some non-linear terms + noise
y = (X @ true_coefs) + 3.2 * np.sin(X[:, 0]) + 2.1 * np.log(np.abs(X[:, 1]) + 1) + np.random.randn(n_samples) * 0.5

# y is 1D target array; X is n_samples x n_features matrix
# Test without regularization
model_no_reg = LinearRegression(method="ridge", fit_intercept=True, lambd=0)
model_no_reg.fit(X, y, None)

print("\n--- No Ridge Regularization ---")
print("Intercept:", model_no_reg.intercept_())
print("Coefficients:", model_no_reg.coef_())
print("Predictions:", model_no_reg.predict(X))

# Test with regularization
model_reg = LinearRegression(method="ridge", fit_intercept=True, lambd=1.0)
model_reg.fit(X, y, None)

print("\n--- With Ridge Regularization (lambda=1.0) ---")
print("Intercept:", model_reg.intercept_())
print("Coefficients:", model_reg.coef_())
print("Predictions:", model_reg.predict(X))

# You can repeat the same for Lasso
model_lasso = LinearRegression(method="lasso", fit_intercept=True, lambd=1.0)
model_lasso.fit(X, y, None)

print("\n--- With Lasso Regularization (lambda=1.0) ---")
print("Intercept:", model_lasso.intercept_())
print("Coefficients:", model_lasso.coef_())
print("Predictions:", model_lasso.predict(X))
