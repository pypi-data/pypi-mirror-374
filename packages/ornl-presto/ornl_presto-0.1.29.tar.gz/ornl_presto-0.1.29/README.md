![# PRESTO](images/PRESTO-logo-tagline-no-bg.png)

[![CI/CD Pipeline](https://github.com/ORNL/PRESTO/actions/workflows/ci.yml/badge.svg)](https://github.com/ORNL/PRESTO/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-81%25-brightgreen)](https://github.com/ORNL/PRESTO)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-pending-yellow)](https://doi.org/pending)
[![JOSS](https://img.shields.io/badge/JOSS-submitted-blue)](https://joss.theoj.org/)

# PRESTO
PRESTO: Privacy REcommendation and SecuriTy Optimization is a Python package that provides automated recommendations for the best privacy preservation algorithm based on user preferences and data characteristics. Traditional privacy preservation libraries provide implementations of various algorithms but require users to experiment and determine which algorithm is best for their dataset. PRESTO provides intelligent recommendations of the top algorithms and compares all available algorithms, making it easier for users to make informed decisions.

## Statement of Need

Privacy-preserving data analysis has become critical across healthcare, finance, IoT, and research domains. However, existing differential privacy libraries present significant barriers to adoption:

**Current Challenges:**
- **Expertise Barrier**: Selecting appropriate privacy mechanisms requires deep theoretical knowledge
- **Parameter Tuning**: Manual trial-and-error to find optimal privacy-utility trade-offs
- **No Guidance**: Limited automated recommendations for algorithm selection
- **Uncertainty**: Lack of confidence intervals and reliability metrics

**PRESTO Solution:**
- **Automated Selection**: Bayesian optimization to find optimal privacy mechanisms and parameters
- **Data-Driven**: Analyzes dataset characteristics to recommend suitable algorithms
- **Quantified Uncertainty**: Provides confidence intervals and reliability metrics
- **Accessible**: Enables both experts and non-experts to deploy privacy-preserving analytics
- **Extensible**: Modular architecture for integrating new algorithms and metrics

**Target Users:**
- Data scientists implementing privacy-preserving analytics
- Researchers requiring compliant data sharing (HIPAA, GDPR)
- Organizations deploying differential privacy in production
- Domain experts needing privacy guidance without deep DP knowledge

## Comparison to Existing Tools

PRESTO complements and enhances existing differential privacy libraries:

| Feature | IBM Diffprivlib | Google PyDP | Facebook Opacus | SmartNoise | **PRESTO** |
|---------|-----------------|-------------|-----------------|------------|------------|
| Privacy Mechanisms | Yes | Yes | Yes | Yes | Yes |
| Algorithm Selection | No | No | No | No | Yes |
| Parameter Optimization | No | No | No | No | Yes |
| Data-driven Recommendations | No | No | No | No | Yes |
| Confidence Intervals | No | No | No | No | Yes |
| Bayesian Optimization | No | No | No | No | Yes |
| Multi-objective Ranking | No | No | No | No | Yes |
| Extensible Architecture | Partial | Partial | Partial | Yes | Yes |

**Key Differentiators:**
- **Automated Decision Making**: PRESTO automatically selects and tunes privacy mechanisms
- **Statistical Rigor**: Provides confidence intervals and reliability metrics for recommendations
- **Domain Adaptability**: Analyzes data characteristics to suggest domain-appropriate algorithms
- **Integration Ready**: Can work alongside existing libraries rather than replacing them

## Summary
This package includes functions for:
- Defining reliability, confidence, and similarity scores for privacy mechanisms
- Providing a modular solution so new privacy preservation algorithms or libraries can be easily integrated
- Determining the best algorithm, privacy loss, confidence interval, and reliability using Bayesian Optimization
- Recommending the best privacy preservation algorithms for a given dataset and user requirements
- Calculating privacy-utility trade-offs, similarity, and reliability scores
- Finding optimal privacy preservation and machine learning settings for a given algorithm, dataset, and user requirements
- Visualizing the top 3 algorithms and their confidence intervals
- Visualizing original and private datasets with similarity analysis
- Integrating with existing privacy preservation libraries (e.g., Opacus) for finding optimal parameters

## Installation

### Requirements
- Python 3.7 or higher
- PyTorch
- NumPy, SciPy, Pandas
- Matplotlib, Seaborn (for visualization)
- Scikit-learn
- Bayesian Optimization
- GPyTorch
- Opacus (for differential privacy)

### Install from Source
You can install the package from source:

```bash
git clone https://github.com/ORNL/PRESTO.git
cd PRESTO
pip install -e .
```

### Install Dependencies
To install all dependencies:

```bash
pip install -r requirements.txt
```

### Verify Installation
Test your installation:

```bash
python -c "import ornl_presto; print('PRESTO installed successfully!')"
```

## Quick Start
Here's a simple example of how to use `presto` for time-series data.
```
import torch
import numpy as np
import matplotlib.pyplot as plt

# Import PRESTO functions from your latest module
from ornl_presto import (
    get_noise_generators,
    recommend_top3,
    visualize_data,
    visualize_similarity
)

# 1) Generate a synthetic energy consumption time series
#    Simulate one week of hourly data (168 points)
np.random.seed(42)
hours = np.arange(0, 168)
# Base consumption: sinusoidal daily pattern + trend + noise
daily_pattern = 2.0 * np.sin(2 * np.pi * hours / 24)
trend = 0.01 * hours
noise = np.random.normal(0, 0.3, size=hours.shape)
consumption = 5.0 + daily_pattern + trend + noise

# Convert to PyTorch tensor
data = torch.tensor(consumption, dtype=torch.float32)

# 2) Visualize original time series distribution
visualize_data(data, title="Original Energy Consumption Distribution")

# 3) Recommend top-3 privacy algorithms
top3 = recommend_top3(data, n_evals=5, init_points=3, n_iter=10)

print("Top-3 recommended privacy algorithms for energy data:")
for rank, rec in enumerate(top3, start=1):
    print(f"{rank}. {rec['algorithm']} | ε={rec['epsilon']:.2f} | score={rec['score']:.4f} "
          f"| mean_rmse={rec['mean_rmse']:.4f} | ci_width={rec['ci_width']:.4f} | rel={rec['reliability']:.2f}")

# 4) For each top algorithm, visualize privatized data and similarity metrics
for rec in top3:
    algo = rec['algorithm']
    eps  = rec['epsilon']
    noise_fn = get_noise_generators()[algo]

    # 1) Generate private data and visualize its distribution
    private = noise_fn(data, eps)
    if not torch.is_tensor(private):
        private = torch.as_tensor(private, dtype=data.dtype)
    visualize_data(private, title=f"Private Data ({algo}, ε={eps:.2f})")

    # 2) Invoke visualize_similarity with (domain, key, epsilon)
    metrics = visualize_similarity(
        domain  = data.numpy(),  # pass the raw series
        key     = algo,
        epsilon = eps
    )
    print(f"{algo} similarity metrics: {metrics}")
```

## Detailed Examples
For more comprehensive examples, see the `tutorial/` folder and `examples/` directory, which contain examples using real-world datasets for electric grid, medical, and financial domains.

## Experimental Results
Top-3 recommended privacy algorithms for energy data:
1. exponential | ε=5.00 | score=-0.2689 | mean_rmse=0.2705 | ci_width=0.0201 | rel=96.48
2. laplace | ε=4.72 | score=-0.2855 | mean_rmse=0.2899 | ci_width=0.0232 | rel=96.20
3. gaussian | ε=3.85 | score=-0.3156 | mean_rmse=0.3201 | ci_width=0.0298 | rel=89.34

Similarity analysis comparing original data, private data distributions, and metrics: ![Similarity Analysis](images/similarity_analysis_combined.png)

## API Reference

### Core Functions
- `get_noise_generators()`: Returns a dictionary of privacy algorithms.
- `recommend_top3(data, n_evals=5, init_points=2, n_iter=5)`: Calculate the Top-3 Recommendation via Bayesian Optimization.
- `recommend_best_algorithms(data, epsilon, ...)`: Calculate the best algorithm(s) for privacy, reliability, and similarity.
- `evaluate_algorithm_confidence(domain, key, epsilon, n_evals=10, **params)`: Calculate the confidence score.
- `calculate_utility_privacy_score(domain, key, epsilon, **params)`: Calculate Utility-Privacy Scoring.
- `performance_explanation_metrics(metrics)`: Calculates the performance explanation metrics: RMSE, Confidence Interval and Reliability.
- `visualize_similarity(domain, key, epsilon, **params)`: Visualize similarity using KS Statistic, Jensen–Shannon Divergence, and Pearson Correlation.
- `visualize_top3(recommendations)`: Visualize Top 3 Privacy Mechanism Recommendations.
- `visualize_confidence(domain, key, epsilon, n_evals=10, **params)`: Visualize confidence for top algorithm.
- `visualize_confidence_top3(domain, recommendations, n_evals=10)`: Visualize the Confidence Intervals for Top-3 Mechanisms.
- `visualize_overlay_original_and_private(domain, top3)`: Visualize overlay Original vs Top-3 Privatized Distributions.

## Community Guidelines

### Contributing
We welcome contributions from the community! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- How to report bugs and request features
- Development setup and workflow
- Code style and testing requirements
- Pull request process

### Getting Help
- **Documentation**: Check our comprehensive examples in the `tutorial/` and `examples/` directories
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/ORNL/PRESTO/issues)
- **Discussions**: Join discussions about PRESTO development and usage

### Support
For support with PRESTO:
1. Check the documentation and examples first
2. Search existing [GitHub Issues](https://github.com/ORNL/PRESTO/issues)
3. Create a new issue with detailed information about your problem
4. For sensitive issues, contact the maintainers directly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
This material is based upon work supported by the U.S. Department of Energy, Office of Science, Office of Advanced Scientific Computing Research under Contract No. DE-AC05-00OR22725. This manuscript has been co-authored by UT-Battelle, LLC under Contract No. DE-AC05-00OR22725 with the U.S. Department of Energy. The United States Government retains and the publisher, by accepting the article for publication, acknowledges that the United States Government retains a non-exclusive, paid-up, irrevocable, world-wide license to publish or reproduce the published form of this manuscript, or allow others to do so, for United States Government purposes. The Department of Energy will provide public access to these results of federally sponsored research in accordance with the DOE Public Access Plan (http://energy.gov/downloads/doe-public-access-plan).

## References
Dwork, C., & Roth, A. (2014). The algorithmic foundations of differential privacy. Foundations and Trends® in Theoretical Computer Science, 9(3–4), 211-407.
