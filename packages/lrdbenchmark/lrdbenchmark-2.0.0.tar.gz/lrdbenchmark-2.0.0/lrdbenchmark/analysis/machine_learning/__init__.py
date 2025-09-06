"""
Machine Learning Estimators for Long-Range Dependence Analysis

This package provides machine learning-based approaches for estimating
Hurst parameters and long-range dependence characteristics from time series data.

The estimators include:
- Neural Network Regression
- Random Forest Regression
- Support Vector Regression
- Gradient Boosting Regression
- Convolutional Neural Networks
- Recurrent Neural Networks (LSTM/GRU)
- Transformer-based approaches
"""

# Import unified estimators
from .random_forest_estimator_unified import RandomForestEstimator
from .svr_estimator_unified import SVREstimator
from .gradient_boosting_estimator_unified import GradientBoostingEstimator
from .cnn_estimator_unified import CNNEstimator
from .lstm_estimator_unified import LSTMEstimator
from .gru_estimator_unified import GRUEstimator
from .transformer_estimator_unified import TransformerEstimator

__all__ = [
    "RandomForestEstimator",
    "SVREstimator",
    "GradientBoostingEstimator",
    "CNNEstimator",
    "LSTMEstimator",
    "GRUEstimator",
    "TransformerEstimator",
]
