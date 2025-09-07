# Changelog

All notable changes to forgeNN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-09-06

### Added
- Initial release of forgeNN framework
- Vectorized automatic differentiation with `Tensor` class
- High-performance `VectorizedMLP` implementation
- Legacy educational implementations in `forgeNN.legacy`
- Complete activation function library
- Professional loss functions (cross-entropy, MSE)
- Vectorized optimizer with momentum support
- Comprehensive MNIST example achieving 93%+ accuracy
- Full documentation and performance guides
- PyPI-ready packaging configuration

### Features
- **Vectorized Operations**: NumPy-powered batch processing (100x+ speedup)
- **Dynamic Computation Graphs**: Automatic differentiation with gradient tracking
- **Complete Neural Networks**: From simple neurons to complex architectures
- **Production Loss Functions**: Cross-entropy, MSE with numerical stability
- **Educational Components**: Legacy implementations for learning purposes
- **High Performance**: 38,000+ samples/sec training speed

### Performance
- MNIST classification: 93%+ accuracy in under 2 seconds
- Training speed: 38,000+ samples per second
- Memory efficient vectorized operations
- Optimized backward pass implementations

### Documentation
- Comprehensive README with examples
- Performance optimization guide
- Activation function reference guide
- Complete installation instructions
- Full API documentation in docstrings

### Examples
- Complete MNIST classification demo
- Performance benchmarking examples
- Educational automatic differentiation examples
- Production-ready training loops

## [0.1.0] - 2025-09-01

### Added
- Initial development version
- Basic automatic differentiation engine
- Simple neural network implementations
- Educational examples and tutorials
