# Changelog

All notable changes to fdprof will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of fdprof
- Real-time file descriptor monitoring
- Event logging support with timestamped messages
- Interactive matplotlib plotting with plateau detection
- Jump detection and analysis between FD plateaus
- Command-line interface with configurable options
- uvx/uv tool compatibility for easy installation

### Features
- **Monitoring**: Real-time FD usage tracking for any command
- **Events**: Capture timestamped events from application output
- **Analysis**: Intelligent plateau detection with configurable parameters
- **Visualization**: Interactive plots showing FD usage, plateaus, and events
- **CLI**: Simple command-line interface with `--plot` and `--interval` options

### Technical
- Comprehensive test suite with 54+ tests
- Modern Python packaging with pyproject.toml
- Pre-commit hooks with ruff formatting
- GitHub Actions ready (CI/CD configuration)
- Cross-platform support (Linux, macOS, limited Windows)

## [0.1.0] - 2024-XX-XX

### Added
- Initial public release
- Core FD monitoring functionality
- Event parsing and timeline generation
- Plateau detection algorithms
- matplotlib integration for visualization
- CLI argument parsing and validation
- JSON logging for FD data
- Comprehensive documentation and examples

### Dependencies
- Python 3.8+ support
- psutil for cross-platform FD monitoring
- matplotlib for plotting and visualization
- numpy for numerical analysis
- scipy for statistical functions

### Installation
- PyPI package distribution
- uvx/uv tool installation support
- pip installation compatibility
- Development environment setup with uv
