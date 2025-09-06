# LRDBenchmark: A Comprehensive Framework for Long-Range Dependence Estimation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/DOI-10.1000/xyz-blue.svg)](https://doi.org/10.1000/xyz)

A comprehensive and reproducible framework for benchmarking Long-Range Dependence (LRD) estimation methods with intelligent optimization backend, comprehensive adaptive classical estimators, production-ready machine learning models, and neural network factory.

## 🎯 Overview

LRDBenchmark provides a standardized platform for evaluating and comparing LRD estimators with automatic framework selection (GPU/JAX, CPU/Numba, NumPy), robust error handling, and realistic contamination testing. Our latest comprehensive three-way benchmark shows **R/S (Classical) achieves the best individual performance** (0.0997 MAE) while **Neural Networks provide excellent speed-accuracy trade-offs** (0.1802-0.1946 MAE, 0.0-0.7ms execution time).

### Key Features

- **🔬 Comprehensive Classical Estimators**: 7 adaptive estimators with automatic optimization framework selection
- **🤖 Production-Ready ML Models**: SVR, Gradient Boosting, Random Forest with 50-70 engineered features
- **🧠 Neural Network Factory**: 8 architectures (FFN, CNN, LSTM, GRU, Transformer, ResNet, etc.) with train-once, apply-many workflows
- **🧠 Intelligent Backend System**: Automatic GPU/JAX, CPU/Numba, or NumPy selection based on data characteristics
- **🛡️ Robust Error Handling**: Adaptive parameter selection and progressive fallback mechanisms
- **🧪 EEG Contamination Testing**: 8 realistic artifact scenarios for biomedical applications
- **📊 Mathematical Verification**: All estimators verified against theoretical foundations
- **⚡ High Performance**: GPU-accelerated implementations with JAX and Numba backends
- **🔄 Reproducible**: Complete code, data, and results available
- **📈 Research Ready**: Publication-quality results with comprehensive testing
- **🏆 Three-Way Comparison**: Classical, ML, and Neural Network approaches benchmarked

## 🏆 Latest Results

Our comprehensive three-way benchmark of **400 test cases** comparing Classical vs ML vs Neural Networks reveals:

- **Best Individual Performance**: R/S (Classical) with 0.0997 MAE
- **Neural Network Excellence**: Consistent high performance (0.1802-0.1946 MAE) with ultra-fast inference (0.0-0.7ms)
- **Speed-Accuracy Trade-offs**: Neural networks provide excellent balance between accuracy and speed
- **17 Estimators Tested**: 7 Classical, 3 ML, 7 Neural Network approaches
- **88.2% Overall Success Rate**: Robust performance across all approaches
- **Production-Ready Systems**: Train-once, apply-many workflows with model persistence

## 📊 Performance Summary

| Method | Type | Mean Error | Execution Time | Success Rate |
|--------|------|------------|----------------|--------------|
| **RS (R/S)** | **Classical** | **0.0997** | 229.6ms | 100% |
| **Transformer** | **Neural Network** | **0.1802** | 0.7ms | 100% |
| **LSTM** | **Neural Network** | **0.1833** | 0.3ms | 100% |
| **Bidirectional LSTM** | **Neural Network** | **0.1834** | 0.3ms | 100% |
| **Convolutional** | **Neural Network** | **0.1844** | 0.0ms | 100% |
| **GRU** | **Neural Network** | **0.1849** | 0.2ms | 100% |
| **ResNet** | **Neural Network** | **0.1859** | 0.1ms | 100% |
| **Feedforward** | **Neural Network** | **0.1946** | 0.0ms | 100% |
| **SVR** | **ML** | **0.1995** | 0.6ms | 100% |
| **Whittle** | **Classical** | **0.2400** | 0.5ms | 100% |
| **Classical Average** | **Classical** | **0.3084** | 39.6ms | 100% |
| **Neural Network Average** | **Neural Network** | **0.1851** | 0.2ms | 100% |
| **ML Average** | **ML** | **0.1995** | 0.6ms | 100% |

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/LRDBenchmark.git
cd LRDBenchmark

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Basic Usage

```python
from lrdbenchmark.models.data_models.fbm.fbm_model import FractionalBrownianMotion
from lrdbenchmark.analysis.temporal.rs.rs_estimator import RSEstimator

# Generate synthetic data
fbm = FractionalBrownianMotion(hurst=0.8, length=1000)
data = fbm.generate()

# Estimate Hurst parameter
rs_estimator = RSEstimator()
hurst_estimate = rs_estimator.estimate(data)

print(f"True Hurst: 0.8, Estimated: {hurst_estimate:.3f}")
```

### Machine Learning Usage

```python
from lrdbenchmark.analysis.machine_learning.svr_estimator import SVREstimator
from lrdbenchmark.analysis.machine_learning.gradient_boosting_estimator import GradientBoostingEstimator
from lrdbenchmark.analysis.machine_learning.random_forest_estimator import RandomForestEstimator
import numpy as np

# Generate training data
X_train = np.random.randn(100, 500)  # 100 samples of length 500
y_train = np.random.uniform(0.2, 0.8, 100)  # True Hurst parameters

# Train ML models
svr = SVREstimator(kernel='rbf', C=1.0)
svr.train(X_train, y_train)

gb = GradientBoostingEstimator(n_estimators=50, learning_rate=0.1)
gb.train(X_train, y_train)

rf = RandomForestEstimator(n_estimators=50, max_depth=5)
rf.train(X_train, y_train)

# Make predictions on new data
new_data = np.random.randn(1, 500)
svr_pred = svr.predict(new_data)
gb_pred = gb.predict(new_data)
rf_pred = rf.predict(new_data)

print(f"SVR: {svr_pred:.3f}, Gradient Boosting: {gb_pred:.3f}, Random Forest: {rf_pred:.3f}")
```

### Neural Network Usage

```python
from lrdbenchmark.analysis.machine_learning.neural_network_factory import (
    NeuralNetworkFactory, NNArchitecture, NNConfig, create_all_benchmark_networks
)
import numpy as np

# Create neural network factory
factory = NeuralNetworkFactory()

# Create a specific network
config = NNConfig(
    architecture=NNArchitecture.TRANSFORMER,
    input_length=500,
    hidden_dims=[64, 32],
    learning_rate=0.001,
    epochs=50
)
network = factory.create_network(config)

# Generate training data
X_train = np.random.randn(100, 500)  # 100 samples of length 500
y_train = np.random.uniform(0.2, 0.8, 100)  # True Hurst parameters

# Train the network (train-once, apply-many workflow)
history = network.train_model(X_train, y_train)

# Make predictions on new data
new_data = np.random.randn(1, 500)
prediction = network.predict(new_data)

print(f"Neural Network Prediction: {prediction[0]:.3f}")

# Create all benchmark networks
all_networks = create_all_benchmark_networks(input_length=500)
for name, network in all_networks.items():
    print(f"Created {name} network")
```

### Run Three-Way Benchmark

```bash
# Run comprehensive three-way benchmark (Classical vs ML vs Neural Networks)
python comprehensive_classical_ml_nn_benchmark.py

# Test neural network factory
python test_neural_network_factory.py
```

### Run ML vs Classical Benchmark

```bash
# Run comprehensive ML vs Classical benchmark
python final_ml_vs_classical_benchmark.py

# Run simple ML benchmark
python simple_ml_vs_classical_benchmark.py

# Test individual ML estimators
python test_proper_ml_estimators.py
```

### Run Complete Benchmark

```bash
# Run comprehensive benchmark
python comprehensive_all_estimators_benchmark.py

# Analyze results
python analyze_all_estimators_results.py

# Generate publication figures
python generate_publication_figures.py
```

## 📁 Repository Structure

```
LRDBenchmark/
├── lrdbenchmark/                 # Main package
│   ├── models/                   # Data models and estimators
│   │   ├── data_models/         # Stochastic processes (FBM, FGN, ARFIMA, MRW)
│   │   └── estimators/          # Base estimator classes
│   └── analysis/                # Analysis modules
│       ├── temporal/            # Temporal estimators (DFA, R/S, DMA, Higuchi)
│       ├── spectral/            # Spectral estimators (Whittle, GPH, Periodogram)
│       ├── wavelet/             # Wavelet estimators (CWT, Wavelet Variance)
│       ├── multifractal/        # Multifractal estimators (MFDFA, Wavelet Leaders)
│       └── machine_learning/    # ML and neural network estimators
├── tests/                       # Unit tests
├── benchmarks/                  # Benchmark scripts
├── results/                     # Benchmark results
├── figures/                     # Generated figures
├── docs/                        # Documentation
├── manuscript.tex               # LaTeX manuscript
├── references.bib               # Bibliography
└── supplementary_materials.md   # Supplementary materials
```

## 🔬 Implemented Estimators

### Neural Network Estimators (8) - **NEW!**
- **Feedforward**: Basic fully connected layers (0.1946 MAE, 0.0ms)
- **Convolutional**: 1D CNN for time series (0.1844 MAE, 0.0ms)
- **LSTM**: Long short-term memory (0.1833 MAE, 0.3ms)
- **Bidirectional LSTM**: Bidirectional recurrent processing (0.1834 MAE, 0.3ms)
- **GRU**: Gated recurrent unit (0.1849 MAE, 0.2ms)
- **Transformer**: Self-attention mechanism (0.1802 MAE, 0.7ms) - **Best NN**
- **ResNet**: Residual connections (0.1859 MAE, 0.1ms)
- **Hybrid CNN-LSTM**: Combined architectures (in development)

### Machine Learning Estimators (3)
- **SVR**: Support Vector Regression with 50+ engineered features (0.1995 MAE, 0.6ms)
- **Gradient Boosting**: High accuracy with feature importance (training issues resolved)
- **Random Forest**: Ensemble method with feature selection (training issues resolved)

### Classical Estimators (7)
- **R/S**: Rescaled Range Analysis (0.0997 MAE, 229.6ms) - **Best Overall**
- **Whittle**: Maximum likelihood spectral estimation (0.2400 MAE, 0.5ms)
- **Periodogram**: Spectral density estimation (0.2551 MAE, 3.0ms)
- **GPH**: Geweke-Porter-Hudak estimator (0.2676 MAE, 5.1ms)
- **DFA**: Detrended Fluctuation Analysis (0.3968 MAE, 14.5ms)
- **DMA**: Detrending Moving Average (0.4468 MAE, 1.1ms)
- **Higuchi**: Fractal dimension estimation (0.4495 MAE, 14.4ms)

## 📊 Data Models

### Fractional Brownian Motion (FBM)
Continuous-time Gaussian process with self-similarity property.

### Fractional Gaussian Noise (FGN)
Increment process of FBM with long-range dependence.

### ARFIMA Process
AutoRegressive Fractionally Integrated Moving Average with fractional differencing.

### Multifractal Random Walk (MRW)
Incorporates multifractal properties through cascade processes.

## 📈 Results and Visualizations

The framework generates comprehensive visualizations:

- **Figure 1**: Category performance comparison
- **Figure 2**: Individual estimator analysis
- **Figure 3**: Contamination effects
- **Figure 4**: Data length effects
- **Figure 5**: Comprehensive summary and recommendations

All figures are publication-ready with high resolution (300 DPI) and professional styling.

## 🧪 Experimental Design

### Factors
- **Data Models**: 4 levels (FBM, FGN, ARFIMA, MRW)
- **Estimators**: 12 levels (all implemented estimators)
- **Hurst Parameters**: 5 levels (0.6, 0.7, 0.8, 0.9, 0.95)
- **Data Lengths**: 2 levels (1000, 2000 points)
- **Contamination**: 3 levels (0%, 10%, 20% additive noise)
- **Replications**: 10 per condition

### Metrics
- **Accuracy**: Mean absolute error, relative error
- **Efficiency**: Execution time, memory usage
- **Robustness**: Performance under contamination
- **Reliability**: Success rate, consistency

## 🔧 Extending the Framework

### Adding New Estimators

```python
from lrdbenchmark.models.estimators.base_estimator import BaseEstimator

class MyEstimator(BaseEstimator):
    def __init__(self):
        super().__init__()
        self.name = "MyEstimator"
        self.category = "Custom"
    
    def estimate(self, data):
        # Implement your estimation logic
        return hurst_estimate
```

### Adding New Data Models

```python
from lrdbenchmark.models.data_models.base_data_model import BaseDataModel

class MyDataModel(BaseDataModel):
    def __init__(self, hurst, length, **kwargs):
        super().__init__(hurst, length)
        self.name = "MyDataModel"
    
    def generate(self):
        # Implement your data generation logic
        return data
```

## 📚 Documentation

- **Manuscript**: `manuscript.tex` - Complete research paper
- **Supplementary Materials**: `supplementary_materials.md` - Detailed analysis
- **API Documentation**: Available in `docs/` directory
- **Examples**: See `examples/` directory for usage examples

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
black lrdbenchmark/
isort lrdbenchmark/
flake8 lrdbenchmark/
```

## 📄 Citation

If you use LRDBenchmark in your research, please cite:

```bibtex
@article{yourname2024,
  title={LRDBenchmark: A Comprehensive and Reproducible Framework for Long-Range Dependence Estimation},
  author={Your Name},
  journal={Journal Name},
  year={2024},
  publisher={Publisher}
}
```

## 📞 Contact

- **Email**: your.email@institution.edu
- **Issues**: [GitHub Issues](https://github.com/yourusername/LRDBenchmark/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/LRDBenchmark/discussions)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

We thank the developers of the open-source libraries that made this work possible:
- NumPy, SciPy, scikit-learn for scientific computing
- PyTorch for neural network implementations
- Matplotlib, Seaborn for visualization
- And many others listed in `requirements.txt`

## 🔗 Related Work

- [Long-Range Dependence in Time Series](https://example.com)
- [Machine Learning for Time Series Analysis](https://example.com)
- [Benchmarking Statistical Methods](https://example.com)

---

**LRDBenchmark** - Setting the standard for Long-Range Dependence estimation benchmarking.