# Skew-T Distribution (Fernandez & Steel)

[![PyPI version](https://badge.fury.io/py/skewt-fs.svg)](https://badge.fury.io/py/skewt-fs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This package provides a Python implementation of the skewed Student's t-distribution as proposed by Fernandez and Steel (1998). It is created as a `scipy.stats` compatible continuous random variable, making it easy to use for statistical modeling and analysis.

## Key Features

-   **Easy to use:** Implemented as a standard `scipy.stats` object.
-   **Flexible:** Control both skewness (`gamma`) and tail thickness (`df`).
-   **Standard Methods:** Includes `pdf`, `cdf`, `ppf`, `rvs`, and `stats` (mean/variance).

## Installation

```bash
pip install skewt-fs
```

## Mathematical Details

The implementation follows the original paper:

> Fernández, C., & Steel, M. F. J. (1998). *On Bayesian Modeling of Fat Tails and Skewness*. Journal of the American Statistical Association, 93(441), 359-371.

Let $g_\nu(x)$ be the probability density function (PDF) of the standard symmetric Student's t-distribution with $\nu$ degrees of freedom. The PDF of the skewed Student's t-distribution $f(x | \nu, \gamma)$ is defined as:

$$
f(x | \nu, \gamma) = \frac{2}{\gamma + \frac{1}{\gamma}} \left[ g_\nu\left(\frac{x}{\gamma}\right)I(x \ge 0) + g_\nu(\gamma x)I(x < 0) \right]
$$

where:
- $\nu$ is the degrees of freedom (`df`).
- $\gamma$ is the skewness parameter (`gamma`).
- $I(\cdot)$ is the indicator function.

### Moments

The mean and variance of the distribution are:

**Mean** ($E[X]$), for $\nu > 1$:
$$
E[X] = M_1 \left(\gamma - \frac{1}{\gamma}\right)
$$

**Variance** ($Var(X)$), for $\nu > 2$:
$$
Var(X) = (M_2 - M_1^2)\left(\gamma^2 + \frac{1}{\gamma^2}\right) + 2M_1^2 - M_2
$$

where $M_1 = E[|Z|]$ and $M_2 = E[Z^2]$ for a standard Student's t-distributed random variable $Z \sim g_\nu$.

## How to Use the Package

The main object is `skewt`, which behaves like any other `scipy.stats` distribution object.

### Importing
```python
from skewt_fs import skewt
```

### Basic Operations
You can use all the standard methods. The shape parameters `df` and `gamma` are passed as arguments.

```python
# Define parameters: 5 degrees of freedom, right-skew (gamma > 1)
df = 5
gamma = 1.8

# Get theoretical mean and variance
mean, var = skewt.stats(df=df, gamma=gamma, moments='mv')
print(f"Theoretical Mean: {mean:.4f}")
print(f"Theoretical Variance: {var:.4f}")

# Evaluate the PDF at a point
pdf_val = skewt.pdf(x=1.0, df=df, gamma=gamma)
print(f"PDF at x=1: {pdf_val:.4f}")

# Evaluate the CDF at a point
cdf_val = skewt.cdf(x=1.0, df=df, gamma=gamma)
print(f"CDF at x=1: {cdf_val:.4f}")

# Find a percentile with the PPF (inverse CDF)
# For example, the 95th percentile
ppf_val = skewt.ppf(q=0.95, df=df, gamma=gamma)
print(f"95th percentile: {ppf_val:.4f}")
```

### Generating Random Samples
Use the `.rvs()` method to generate random variates.

```python
# Generate 1000 random samples
samples = skewt.rvs(df=df, gamma=gamma, size=1000)

# Verify sample moments
print(f"Sample Mean: {np.mean(samples):.4f}")
print(f"Sample Variance: {np.var(samples):.4f}")
```

### Visualization
You can easily plot the distribution to visualize the effect of the parameters.

```python
# Set up the plot
fig, ax = plt.subplots(figsize=(10, 6))
x = np.linspace(skewt.ppf(0.001, df, gamma), skewt.ppf(0.999, df, gamma), 200)

# Plot the PDF
ax.plot(x, skewt.pdf(x, df=df, gamma=gamma), 'r-', lw=3, alpha=0.8, label=f'skewt pdf (df={df}, γ={gamma})')

# Plot a histogram of the random samples
ax.hist(samples, bins=50, density=True, histtype='stepfilled', alpha=0.3, label='Sample Histogram')

# Add lines for mean and median
ax.axvline(mean, color='k', linestyle='--', label=f'Mean: {mean:.2f}')
ax.axvline(skewt.ppf(0.5, df, gamma), color='g', linestyle='-', label=f'Median: {skewt.ppf(0.5, df, gamma):.2f}')

ax.set_title("Fernandez-Steel Skewed Student's t-Distribution")
ax.set_xlabel("x")
ax.set_ylabel("Density")
ax.legend()
ax.grid(True, linestyle='--', alpha=0.6)
plt.show()
```

## API Reference

### `skewt`
An instance of the `skewt_gen` class. It is a continuous random variable object from `scipy.stats`.

**Shape Parameters:**
* `df` (float): Degrees of freedom, must be greater than 0.
* `gamma` (float): Skewness parameter, must be greater than 0.
    * `gamma > 1`: Right (positive) skew.
    * `gamma < 1`: Left (negative) skew.
    * `gamma = 1`: Symmetric (reverts to the standard Student's t-distribution).

**Location and Scale:**
Like all `scipy.stats` objects, it also accepts `loc` (for mean/location) and `scale` parameters.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue on the project's GitHub repository.

## License
This project is licensed under the MIT License.