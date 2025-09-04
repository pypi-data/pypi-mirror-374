# AstroLib - Advanced Astrophysics Library

## Overview
AstroLib is a high-performance Python library for astrophysical computations, focusing on void finding, neutrino physics, and N-body simulations. It's designed to work efficiently even on low-performance hardware through innovative algorithms and resource management.

## Features

### Core Components
- **Void Finding**: Advanced algorithms for void detection and analysis
- **Neutrino Physics**: Tools for neutrino mass estimation using void expansion
- **N-Body Simulations**: Optimized particle simulations
- **Machine Learning Integration**: ML-based analysis tools

### Performance Optimizations
- Adaptive resource management
- Smart caching system
- Memory-efficient data structures
- Parallel processing capabilities

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/astrolib.git
cd astrolib

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Requirements
- Python >= 3.8
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- Astropy >= 4.0
- Numba >= 0.55.0
- h5py >= 3.0.0
- matplotlib >= 3.4.0
- pandas >= 1.3.0
- scikit-learn >= 1.0.0
- psutil >= 5.8.0

## Quick Start

```python
from astrolib.optimized_voids import StreamingVoidFinder
from astrolib.optimized_nbody import OptimizedNBody, SimulationConfig
from astrolib.neutrino_ml import NeutrinoMassEstimator

# Initialize void finder with resource-aware settings
finder = StreamingVoidFinder(chunk_size=100000, n_workers=2)

# Find voids in streaming mode
for void in finder.find_voids_streaming(data_iterator, box_size=500.0):
    print(f"Found void: radius = {void['radius']:.2f}")

# Set up N-body simulation
config = SimulationConfig(
    dt=0.01,
    softening=1e-4,
    theta=0.5,
    use_cache=True,
    n_workers=2
)
simulator = OptimizedNBody(config)

# Run simulation
positions, velocities = simulator.simulate_chunk(
    positions,
    velocities,
    masses,
    steps=100
)

# Estimate neutrino mass
estimator = NeutrinoMassEstimator()
mass, uncertainty = estimator.predict(voids)
print(f"Estimated neutrino mass: {mass:.3f} ± {uncertainty:.3f} eV")
```

## Documentation

### Void Finding
The library implements multiple void finding algorithms:
- Watershed Void Finder
- ZOBOV (Zones Bordering On Voidness)
- ML-enhanced void detection

```python
from astrolib.optimized_voids import StreamingVoidFinder

# Initialize finder
finder = StreamingVoidFinder()

# Find voids
voids = finder.find_voids_streaming(
    data_iterator,
    box_size=500.0
)
```

### N-Body Simulations
Efficient N-body simulations with adaptive time stepping:

```python
from astrolib.optimized_nbody import OptimizedNBody

# Configure simulation
simulator = OptimizedNBody()

# Run simulation
positions, velocities = simulator.simulate_chunk(
    initial_positions,
    initial_velocities,
    masses
)
```

### Neutrino Physics
Tools for neutrino mass estimation:

```python
from astrolib.neutrino_ml import NeutrinoMassEstimator

# Initialize estimator
estimator = NeutrinoMassEstimator()

# Estimate mass
mass, uncertainty = estimator.predict(void_catalog)
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Citation
If you use this library in your research, please cite:

```bibtex
@software{astrolib2025,
  author = {Your Name},
  title = {AstroLib: Advanced Astrophysics Library},
  year = {2025},
  url = {https://github.com/yourusername/astrolib}
}
```
