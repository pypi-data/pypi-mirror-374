import numpy as np

class LinearRegression:

    def __init__(self, method='normal_equation', fit_intercept=True, n_iter=1000, alpha=0.01, lambd=0.1):
        """
        Initialize the Linear Regression model.

        Parameters:
        - method: training method ('normal_equation', 'gradient_descent', 'ridge', 'lasso')
        - fit_intercept: whether to fit an intercept term
        - n_iter: number of iterations for gradient descent
        - alpha: learning rate for gradient descent
        - lambd: regularization strength (lambda)
        """
        self.method = method
        self.fit_intercept = fit_intercept
        self.n_iter = n_iter
        self.alpha = alpha
        self.lambd = lambd
        self.theta_ = None

    def fit(self, X, y, sample_weight):
        """
        Fit model to data X and target y with optional sample weights.

        Parameters:
        - X: feature matrix (2D array)
        - y: target vector or matrix
        - sample_weight: array of sample weights (1D array) or None
        """
        X = np.array(X)
        y = np.array(y)

        # Input validation
        if X.ndim != 2:
            raise ValueError("X must be 2D array")
        if y.ndim != 1 and y.ndim != 2:
            raise ValueError("y must be 1D or 2D array")
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have same number of samples")
        if sample_weight is not None and (sample_weight.ndim != 1 or sample_weight.shape[0] != X.shape[0]):
            raise ValueError("sample_weight must be 1D with length equal to number of samples")

        # Set default sample weights if None
        if sample_weight is None:
            sample_weight = np.ones(X.shape[0])
        else:
            sample_weight = np.array(sample_weight)

        # Add intercept (column of ones) if requested
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]

        # Choose method to train
        if self.method == "normal_equation":
            self.theta_ = self.Normal_Eqn(X, y, sample_weight)
        elif self.method == "gradient_descent":
            self.theta_ = self.GradientDescent(X, y, sample_weight, self.n_iter, self.alpha)
        elif self.method == "ridge":
            self.theta_ = self.Ridge(X, y, sample_weight, self.n_iter, self.alpha, self.lambd)
        elif self.method == "lasso":
            self.theta_ = self.Lasso(X, y, sample_weight, self.n_iter, self.alpha, self.lambd)
        else:
            raise ValueError(f"Unknown method {self.method}")
        return self

    def predict(self, X):
        """
        Predict target values for input features X.

        Parameters:
        - X: input feature matrix (2D array)
        """
        X = np.array(X)
        if X.ndim != 2:
            raise ValueError("X must be 2D array")

        # Add intercept column if fitted with intercept
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]

        return X.dot(self.theta_)

    def score(self, X, y, sample_weight=None):
        """
        Compute R^2 score of model on data.

        Parameters:
        - X: feature matrix
        - y: true target values
        - sample_weight: optional sample weights
        """
        X = np.array(X)
        y = np.array(y)

        # Input validation
        if X.ndim != 2:
            raise ValueError("X must be 2D array")
        if y.ndim != 1 and y.ndim != 2:
            raise ValueError("y must be 1D or 2D array")
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have same number of samples")
        if sample_weight is not None and (sample_weight.ndim != 1 or sample_weight.shape[0] != X.shape[0]):
            raise ValueError("sample_weight must be 1D with length equal to number of samples")

        if sample_weight is None:
            sample_weight = np.ones(X.shape[0])
        else:
            sample_weight = np.array(sample_weight)

        y_pred = self.predict(X)
        # Calculation of weighted R^2 score
        return 1 - np.sum(sample_weight * (y - y_pred) ** 2) / np.sum(sample_weight * (y - np.mean(y)) ** 2)

    def coef_(self):
        #Return feature coefficients, excluding intercept if fitted.
        if self.fit_intercept:
            if self.theta_.ndim == 1:
                return self.theta_[1:]
            else:
                return self.theta_[1:].T
        else:
            if self.theta_.ndim == 1:
                return self.theta_
            else:
                return self.theta_.T

    def intercept_(self):
        #Return intercept term, or zero if not fitted with intercept.
        if self.fit_intercept:
            if self.theta_.ndim == 1:
                return self.theta_[0]
            else:
                return self.theta_[0, :]
        else:
            if self.theta_.ndim == 1:
                return 0
            else:
                return np.zeros(self.theta_.shape[1])

    def MSE(self, y_true, y_pred, sample_weight):
        #Calculate weighted mean squared error.
        return np.sum(sample_weight * ((y_pred - y_true) ** 2)) / np.sum(sample_weight)

    def Normal_Eqn(self, X, y, sample_weight):
        #Compute parameters using the weighted normal equation.
        W = np.diag(sample_weight)  # Weight matrix for samples
        theta = np.linalg.inv(X.T.dot(W).dot(X)).dot(X.T).dot(W).dot(y)
        return theta

    def GradientDescent(self, X, y, sample_weight, iteration, alpha):
        #Gradient descent for ordinary linear regression.
        theta = np.zeros(X.shape[1])
        mse_old = self.MSE(y, X.dot(theta), sample_weight)

        for _ in range(iteration):
            grad = (2 / np.sum(sample_weight)) * X.T.dot(sample_weight * (X.dot(theta) - y))
            theta -= alpha * grad
            mse_new = self.MSE(y, X.dot(theta), sample_weight)

            if mse_old - mse_new < (alpha * 0.01):
                break
            else:
                mse_old = mse_new
        return theta

    def Ridge(self, X, y, sample_weight, iteration, alpha, lambd):
        #Gradient descent for Ridge Regression (L2 regularization).
        theta = np.zeros(X.shape[1])
        mse_old = self.MSE(y, X.dot(theta), sample_weight)

        for _ in range(iteration):
            ridge = (2 / X.shape[0]) * X.T.dot((X.dot(theta) - y) * sample_weight)
            ridge[1:] += 2 * lambd * theta[1:]  # Excluding intercept from regularization
            theta -= alpha * ridge
            mse_new = self.MSE(y, X.dot(theta), sample_weight)

            if mse_old - mse_new < (alpha * 0.01):
                break
            else:
                mse_old = mse_new
        return theta

    def Lasso(self, X, y, sample_weight, iteration, alpha, lambd):
        #Gradient descent for Lasso Regression (L1 regularization).
        theta = np.zeros(X.shape[1])
        mse_old = self.MSE(y, X.dot(theta), sample_weight)

        for _ in range(iteration):
            ridge = (2 / X.shape[0]) * X.T.dot((X.dot(theta) - y) * sample_weight)
            ridge[1:] += lambd * np.sign(theta[1:])  # Exclude intercept from penalty
            theta -= alpha * ridge
            mse_new = self.MSE(y, X.dot(theta), sample_weight)

            if mse_old - mse_new < (alpha * 0.01):
                break
            else:
                mse_old = mse_new
        return theta
