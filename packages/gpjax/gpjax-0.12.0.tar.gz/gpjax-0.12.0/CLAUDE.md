# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- **Run all tests**: `hatch run dev:test` or `pytest . -v -n 4 --beartype-packages='gpjax'`
- **Run tests with coverage**: `hatch run dev:coverage`
- **Run a single test file**: `pytest tests/test_file.py -v`
- **Run docstring tests**: `hatch run dev:docstrings`
- **Full test suite**: `hatch run dev:all-tests` (includes format check, docstrings, and tests)

### Code Formatting and Linting
- **Format all code**: `hatch run dev:format` (runs black, isort, and ruff format)
- **Check formatting**: `hatch run dev:check` (black-check, imports-check, lint-check)
- **Format with black**: `hatch run dev:black-format`
- **Format imports**: `hatch run dev:imports-format`
- **Lint and auto-fix**: `hatch run dev:lint-check`
- **Remove unused imports**: `hatch run dev:remove-unused`

### Documentation
- **Build docs**: `hatch run docs:build`
- **Serve docs locally**: `hatch run docs:serve`
- **Run integration tests**: `hatch run docs:integration`

### Build and Installation
- **Install for development**: `hatch env create` then `hatch shell`
- **Install stable version**: `pip install gpjax`

## High-Level Architecture

GPJax is a Gaussian Process library built on JAX and Flax (nnx), designed with a modular architecture that closely mirrors mathematical abstractions:

### Core Components

1. **Gaussian Processes (`gpjax.gps`)**
   - `AbstractPrior`: Base class for GP priors combining kernels and mean functions
   - `Prior`: Standard GP prior implementation  
   - `AbstractPosterior`: Base class for posterior inference
   - `ConjugatePosterior`: Exact inference for Gaussian likelihoods
   - `NonConjugatePosterior`: Approximate inference for non-Gaussian likelihoods
   - Uses Flax nnx.Module for parameter management

2. **Kernels (`gpjax.kernels`)**
   - `AbstractKernel`: Base kernel class with composition support (+, *)
   - Stationary kernels: RBF, Matern12/32/52, RationalQuadratic, Periodic, White
   - Non-stationary kernels: Linear, Polynomial, ArcCosine
   - Non-Euclidean kernels: Graph kernels for structured data
   - Kernel computations: Dense, Diagonal, Eigen decomposition strategies
   - Approximations: Random Fourier Features (RFF)

3. **Likelihoods (`gpjax.likelihoods`)**
   - `AbstractLikelihood`: Base class defining the observation model
   - `Gaussian`: Standard Gaussian likelihood with observation noise
   - Non-Gaussian: Bernoulli, Poisson for classification and count data
   - Links prediction and observation spaces

4. **Variational Inference (`gpjax.variational_families`)**
   - `AbstractVariationalFamily`: Base for variational approximations
   - `VariationalGaussian`: Mean-field Gaussian variational distribution
   - `WhitenedVariationalGaussian`: Whitened parameterization
   - `NaturalVariationalGaussian`: Natural gradient parameterization
   - Supports both collapsed and uncollapsed VI

5. **Objectives (`gpjax.objectives`)**
   - `AbstractObjective`: Base class for optimization objectives
   - `ConjugateMLL`: Marginal likelihood for exact inference
   - `NonConjugateMLL`: Laplace approximation for non-Gaussian likelihoods
   - `ELBO`: Evidence lower bound for variational inference
   - `CollapsedELBO`: Analytically integrated ELBO

6. **Optimization (`gpjax.fit`)**
   - `fit()`: General optimizer using Optax optimizers
   - `fit_lbfgs()`: L-BFGS optimization via Optax
   - `fit_scipy()`: Interface to scipy optimizers via JAXopt
   - Supports custom loss functions and stopping criteria

### Key Design Patterns

- **Functional Design**: Functions are first-class, mirroring mathematical notation
- **Composability**: Kernels support arithmetic operations for easy combination
- **JAX Integration**: Full support for JIT compilation, automatic differentiation, and vectorization
- **Type Safety**: Extensive use of jaxtyping and beartype for runtime type checking
- **CoLA Integration**: Uses CoLA (Compositional Linear Algebra) for efficient linear algebra operations
- **Parameter Management**: Uses Flax nnx for trainable parameters with PyTree support

### Data Structures

- `Dataset`: Simple dataclass for (X, y) pairs with optional y
- `GaussianDistribution`: Represents multivariate Gaussians with efficient sampling
- Parameters use `nnx.Param` with transformation support (e.g., `SoftplusTransformation`)

### Important Implementation Details

- All kernels must implement `__call__(x, y)` for single point evaluation
- Kernel matrices are computed via `compute_engine.gram()` or `compute_engine.cross_covariance()`
- Jitter (small diagonal noise) is added for numerical stability, default 1e-6
- Uses `cola.PSD` annotations for positive semi-definite matrices
- Cholesky decompositions use custom `lower_cholesky` for better gradients