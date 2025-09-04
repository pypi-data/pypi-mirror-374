# Adaptive Dynamics Toolkit (ADT)

<p align="center">
  <a href="https://github.com/RDM3DC/adaptive-dynamics-toolkit/actions">
    <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/RDM3DC/adaptive-dynamics-toolkit/ci.yml?label=CI">
  </a>
  <a href="https://pypi.org/project/adaptive-dynamics/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/adaptive-dynamics.svg">
  </a>
  <a href="https://pypi.org/project/adaptive-dynamics/">
    <img alt="Python" src="https://img.shields.io/pypi/pyversions/adaptive-dynamics.svg">
  </a>
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg">
  </a>
  <a href="https://github.com/RDM3DC/adaptive-dynamics-toolkit/issues">
    <img alt="Issues" src="https://img.shields.io/github/issues/RDM3DC/adaptive-dynamics-toolkit.svg">
  </a>
  <a href="https://github.com/sponsors/RDM3DC">
    <img alt="Sponsors" src="https://img.shields.io/badge/sponsor-%E2%9D%A4-ff69b4.svg">
  </a>
</p>

<p align="center">
  <img src="docs/assets/hero.gif" alt="Adaptive π visualization" width="640"><br>
  <img src="docs/assets/loss.gif" alt="ARP vs Adam loss (synthetic)" width="640">
</p>

A unified framework for adaptive computing paradigms, including adaptive π geometry, ARP optimization, physics simulations, and compression algorithms.

## Installation

```bash
pip install adaptive-dynamics
```

For development or to include optional dependencies:

```bash
pip install "adaptive-dynamics[torch,sympy,dev]"
# or with uv
uv venv && uv pip install -e ".[dev,docs,torch,sympy]"
```

## Quick Examples

### Curved Geometry with Adaptive π (πₐ)

```python
from adaptive_dynamics.pi.geometry import AdaptivePi

# Create an instance with gentle positive curvature
pi = AdaptivePi(curvature_fn=lambda x, y: 1e-3)

# Calculate circumference in curved space
circumference = pi.circle_circumference(1.0)
print(f"Circumference of unit circle: {circumference:.6f}")
# Output: Circumference of unit circle: 3.144159
```

### Neural Network Training with ARP Optimizer

```python
import torch
import torch.nn as nn
from adaptive_dynamics.arp.optimizers import ARP

# Define a simple model
model = nn.Sequential(nn.Flatten(), nn.Linear(28*28, 10))

# Use ARP optimizer
opt = ARP(model.parameters(), lr=3e-3, alpha=0.01, mu=0.001)

# Training loop (example)
# X, y = ... load a batch ...
loss_fn = nn.CrossEntropyLoss()
loss = loss_fn(model(X), y)
loss.backward()
opt.step()
opt.zero_grad()
```

## Examples

- [πₐ Curved Circles](examples/pi_a_curved_circles.ipynb)
- [ARP Optimizer on MNIST](examples/arp_mnist.ipynb)

## Documentation

Full documentation is available at [https://RDM3DC.github.io/adaptive-dynamics-toolkit](https://RDM3DC.github.io/adaptive-dynamics-toolkit)

- [Getting Started Guide](https://RDM3DC.github.io/adaptive-dynamics-toolkit/getting-started)
- [API Reference](https://RDM3DC.github.io/adaptive-dynamics-toolkit/api)
- [Tutorials](https://RDM3DC.github.io/adaptive-dynamics-toolkit/tutorials)

## Features

- **Adaptive π Geometry**: Curved space mathematics and Gauss-Bonnet inspired algorithms
- **ARP Optimization**: Resistance-conductance model for neural network optimization
- **Physics Simulations**: Gravity, beams, and ringdown simulations with adaptive precision
- **Compression Tools**: Adaptive compression for text, curves, and tensors
- **TSP Solvers**: Tools for 3D printing toolpath optimization

## Pro Features

ADT Pro extends the toolkit with advanced features for enterprise and research:
- Advanced CUDA acceleration
- Premium simulation capabilities
- Enterprise-grade dashboards
- Specialized slicer algorithms

Contact us at [contact@example.com](mailto:contact@example.com) for licensing information.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

- Adaptive Dynamics Toolkit (Community Edition): [MIT License](LICENSE)
- ADT Pro: Commercial license (see [pro/README_PRO.md](src/adaptive_dynamics/pro/README_PRO.md))

## Support & Services

- [Integration & Research Consulting](https://yourusername.github.io/adaptive-dynamics-toolkit/services)
- [Training & Workshops](https://yourusername.github.io/adaptive-dynamics-toolkit/training)
- [GitHub Sponsors](https://github.com/sponsors/yourusername)