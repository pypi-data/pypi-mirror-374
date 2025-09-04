# 1. Abstract

In Data Science, the goal is often to explain the target variable `Y` in terms of the input `X` as :

- Y = f_alpha(X) + epsilon

  where:

  - `epsilon ~ N(0,1)` is Gaussian noise,
  - `X` is an `n x p` data matrix,
  - `Y` is an `n x 1` vector,
  - and `alpha` represents the model parameters.

The function `f` can be linear or nonlinear, for instance implemented as a neural network. In this case, `alpha` corresponds to the set of weights and biases of the network.

Sylvain Sardy proposed a [relaxation technique to estimate the parameters `alpha`](https://link.springer.com/article/10.1007/s11222-022-10169-0) :

- alpha_hat = argmin_alpha (||Y-f_alpha(X)||\_2 + lambda \* ||alpha||\_1 )

One of the main challenges is choosing the regularization parameter `lambda` :

- If `lambda` is too large, the resulting model will be overly sparse and inaccurate.
- If `lambda` is too small, the model will be accurate but not sparse enough.

The goal is to find the best trade-off :

- The package implements Sardy’s algorithm to compute the optimal `lambda`.
- The implementation automatically runs on one or multiple GPUs if available, or on the CPU otherwise.
- An auto-detection feature ensures the best use of the available hardware.

The optimal value, referred to as the **“lambda happy”**, is computed as :

- lambda_happy = quantile_0.95( || X^T \* Z_centered ||\_∞ / || Z_centered ||\_2 )

- where the numerator uses the Chebyshev (L∞) norm and the denominator the Euclidean (L2) norm.

- Here, `Z_centered` is an `n x m` random matrix (with `m` typically large enough for accurate quantile estimation).

- Each column of `Z` is drawn independently from `N(0,1)` and then centered (its mean is subtracted so that every column has zero mean).

# 2. Warning

A more optimized version is available at the following URL: https://pypi.org/project/lambda-happy/. However, it is less portable, less sustainable over time, and only works under specific conditions on Linux.

The version provided here is more portable and designed to be sustainable in the long run.

# 3. Installation

Here is how to install the package with its dependencies. The torch library must be installed separately depending on the operating system.

## 3.1 Install the `torch-lambda-happy` library :

Only the torch-lambda-happy package below is required.
The others are optional and can be used for benchmarking or validation.
In all cases, however, you must install the PyTorch dependency described below.

```bash
# Core functionality
pip install torch-lambda-happy

# Benchmark GUI (PyQt5)
pip install torch-lambda-happy[benchmark]

# Validation tools (PyQt5 + pandas)
pip install torch-lambda-happy[validation]

# All extras (Benchmark + Validation tools)
pip install torch-lambda-happy[all]
```

## 3.2 Dependencies

The backend relies on PyTorch and CUDA, depending on your hardware.
You must therefore install the corresponding PyTorch version.

- Linux or Windows (successfully tested with Python 3.10)

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

- macOS (currently under testing)

```bash
pip3 install torch torchvision
```

> ℹ️ GPU acceleration is not available on macOS because CUDA is not supported.

> ℹ️ This project was developed on Ubuntu 22.04 with CUDA 11.8 (2025).
> Users are free to install a more recent version of CUDA if needed, depending on availability and their system configuration at the time of use.
> (see: https://pytorch.org/get-started/locally/).

# 4. Examples and recommendations

## 4.1 Recommended use case

Here is an example using best practices. It is always preferable to create the matrix on the correct device to avoid unnecessary conversion.

```py
import torch
from torch_lambda_happy import LambdaHappy

# Prepare data
X = torch.randn(1000, 5000, device="cuda")

# Initialize solver (auto‐select the fastest backend)
solver = LambdaHappy(X, force_fastest=True)

# Single estimate
lambda_value = solver.compute(m=10000)
print(f"lambda_value: {lambda_value:.4f}")

# Multiple runs
lambda_values = solver.compute_many(m=10000, nb_run=50)
print(f"lambda_values: {lambda_values}")

# Aggregated (median)
lambda_median = solver.compute_agg(m=10000, nb_run=500, func=torch.median)
print(f"lambda_median: {lambda_median:.4f}")
```

## 4.2 Example with all parameters (single estimation)

```py
import torch
from torch_lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=False, use_multigpu=False)
lambda_value = model.compute(m=10_000, dtype=torch.float16, device_type="cuda")
print(f"Estimated lambda: {lambda_value:.4f}")

```

## 4.3 Example with all parameters (many estimations)

```py
import torch
from torch_lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=False)
lambda_values = model.compute_many(m=10_000, dtype=torch.float32, device_type="cuda", nb_run=100)
print(f"Estimated lambdas: {lambda_values}")
```

## 4.4 Example with all parameters (aggregated estimation)

```py

import torch
from torch_lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=True)
lambda_mean = model.compute_agg(
    m=10_000, dtype=torch.float32, device_type="cpu", nb_run=10, func=torch.mean
)
print(f"Estimated lambda: {lambda_mean:.4f}")

```

> ⚠️ The examples above illustrate different ways of using the library, but they are not necessarily the fastest methods.  
> For the most efficient versions, please refer to the `4.1 Recommended use case` section.

> ℹ️ Use `float16` (or `force_fastest=True`) on **GPU** only if the input matrix **X** is normalized.
> Setting `use_multigpu=True` will utilize all available GPUs if more than one is present.

## 4.5 Recommended Settings

| Context    | Data Type | Notes                                                           |
| ---------- | --------- | --------------------------------------------------------------- |
| CPU        | `float32` | Stable, widely supported, and generally the fastest on CPU.     |
| GPU (CUDA) | `float16` | High performance if `X` is normalized; otherwise use `float32`. |

# 5. Performance Trade-Offs

## 5.1 Projection Dimension (m)

- ↑ **m** → improves lambda_happy precision.
- ↑ **m** → linearly increases compute time (all kernels scale with m).
- Recommended: **m = 10_000** provides good accuracy in most cases.

> ℹ️ Use `float16` on **GPU** only if the input matrix **X** is normalized.
> Otherwise, lambda_happy estimation may be unstable or inconsistent.

## 5.2 Sample Dimension (n)

- ↑ **n** → increases cost in all kernels (since Z ∈ R^(n × m)), except for the quantile post-processing step.

## 5.3 Feature Dimension (p)

- ↑ **p** → only affects the **X^T·Z** matrix multiplication.

# 6. Benchmark

The `torch-lambda-happy-benchmark` script measures and compares the performance of LambdaHappy on CPU and GPU.
It offers various benchmarking options and displays live throughput plots.
Example usage :

```sh
torch-lambda-happy-benchmark --benchmark_2D --benchmark_3D --benchmark_float --device cuda --dtype float32 -n 1000 -p 1000 -m 10000
```

This runs a 2D benchmark using CUDA with specified matrix dimensions and then run a 3D benchmark.

> ℹ️ Note: Not all hyperparameters are used for every plot, but if provided, they will be applied when relevant.

# 7. Validation

The `torch-lambda-happy-validation` script runs tests to validate lambda_happy estimation accuracy.
It generates detailed reports and distribution plots using pandas and PyQt5.

Example usage :

```sh
torch-lambda-happy-validation --distribution_small --distribution_large --device cuda --dtype float32 -n 1000 -p 1000
```

This plots small and large scale lambda_happy distributions on CUDA for the given parameters.

# 8. Performance comparison

Here are the results for a CUDA calculation :
| Rank | Mode | Precision | FPS | Speed-up |
|-|-|-|-|-|
| 1 | Mono-GPU | Float32 | 449 | 1.00x |
| 2 | Multi-GPU| Float32 | 511 | 1.14x |
| 3 | Multi-GPU| Float16 | 664 | 1.48x |
| 4 | Mono-GPU | Float16 | 1215 | 2.71x |

> ℹ️ FPS : number of times the lambda_happy value is estimated per second.

The test server is equipped with an Intel Xeon E5-2699 v3 processor (2014) and three NVIDIA GeForce RTX 2080 Ti graphics cards (2018).

The evaluation uses the default parameters, with X of size 1000x1000 and m=10000.

> ℹ️ Note: Use device="cuda" when you create X.

# 9. About This Project

This package, including performance optimizations, was developed as part of a Bachelor’s thesis at HE-Arc by Sevan Yerly (sevan.yerly@he-arc.ch), under the supervision of Cédric Bilat (cedric.bilat@he-arc.ch). The mathematical foundations were developed by Sylvain Sardy (sylvain.sardy@unige.ch).

For questions or contact : sevan.yerly@he-arc.ch or cedric.bilat@he-arc.ch
