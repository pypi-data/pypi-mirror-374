import numpy as np
from scipy.stats import rv_continuous, t
from scipy.special import gamma as gamma_func

class skewt_gen(rv_continuous):
    """
    A skewed Student's t-distribution based on the formulation by
    Fernandez and Steel (1998), "On Bayesian Modeling of Fat Tails and Skewness".

    The distribution is constructed by introducing skewness into a symmetric
    Student's t-distribution by scaling the positive and negative sides
    differently.

    Shape Parameters
    ----------------
    df : float
        Degrees of freedom (df > 0). Controls the tail thickness.
    gamma : float
        Skewness parameter (gamma > 0).
        - gamma > 1: skewed to the right.
        - gamma < 1: skewed to the left.
        - gamma = 1: symmetric Student's t-distribution.
    """
    def _argcheck(self, df, gamma):
        """Check if the shape parameters are valid."""
        return (df > 0) and (gamma > 0)

    def _get_m1_m2(self, df):
        """
        Helper function to calculate the first and second moments of the
        folded standard Student's t-distribution, based on the provided PDF.
        M1 = E[|X|], M2 = E[X^2] for X ~ t(df).
        """
        # M1 exists only for df > 1
        if df > 1:
            # Corrected formula from the provided PDF and standard sources
            m1 = (2 * np.sqrt(df) * gamma_func((df + 1) / 2)) / \
                 ((df - 1) * np.sqrt(np.pi) * gamma_func(df / 2))
        else:
            m1 = np.nan

        # M2 exists only for df > 2
        if df > 2:
            m2 = df / (df - 2)
        else:
            m2 = np.nan
        return m1, m2

    def _pdf(self, x, df, gamma):
        """
        Probability Density Function (PDF).
        """
        # Use the standard symmetric t-distribution from scipy.stats
        symmetric_t = t(df)
        
        # Indicator for positive and negative x
        is_positive = (x >= 0)
        
        # Scaling factor from Fernandez and Steel (1998), eq. (1)
        c = 2 / (gamma + 1 / gamma)
        
        # PDF calculation based on the skewing mechanism
        pdf_val = c * (symmetric_t.pdf(x / gamma) * is_positive +
                       symmetric_t.pdf(x * gamma) * (1 - is_positive))
        return pdf_val

    def _cdf(self, x, df, gamma):
        """
        Cumulative Distribution Function (CDF).
        """
        symmetric_t = t(df)
        is_positive = (x >= 0)
        c = 2 / (gamma + 1 / gamma)
        
        # CDF calculation, derived from integrating the PDF
        cdf_val = c * (
            (symmetric_t.cdf(x / gamma) - 0.5) * gamma * is_positive +
            symmetric_t.cdf(x * gamma) / gamma * (1 - is_positive) +
            0.5 * gamma * is_positive
        )
        return cdf_val

    def _ppf(self, q, df, gamma):
        """
        Percent Point Function (PPF) or Inverse CDF.
        """
        symmetric_t = t(df)
        c = 2 / (gamma + 1 / gamma)
        
        # Probability mass in the negative part of the distribution
        p_neg = 1 / (gamma**2 + 1)
        
        is_neg_quantile = (q < p_neg)
        
        # Invert the CDF formula analytically
        # No numerical solver needed
        ppf_val = np.where(
            is_neg_quantile,
            (1 / gamma) * symmetric_t.ppf(q * gamma / c),
            gamma * symmetric_t.ppf(0.5 + (q - p_neg) * (gamma + 1/gamma) / (2*gamma))
        )
        return ppf_val

    def _rvs(self, df, gamma, size=None, random_state=None):
        """
        Random Variates Samples (RVS).
        """
        if random_state is None:
            random_state = np.random.RandomState()
            
        # Generate from standard symmetric t-distribution
        symmetric_t_rvs = t.rvs(df, size=size, random_state=random_state)
        
        # Generate signs based on the skewness parameter
        p_pos = gamma**2 / (1 + gamma**2)
        signs = np.where(random_state.uniform(size=size) < p_pos, 1, -1)

        # Apply the skewing transformation
        rvs = signs * np.abs(symmetric_t_rvs) * np.where(signs > 0, gamma, 1/gamma)
        return rvs

    def _stats(self, df, gamma, moments='mv'):
        """
        Mean, variance, skew, and kurtosis.
        """
        m1, m2 = self._get_m1_m2(df)
        
        # Mean calculation (E[X])
        mean = np.nan
        if df > 1:
            mean = m1 * (gamma - 1 / gamma)
        
        # Variance calculation (Var(X) = E[X^2] - (E[X])^2)
        var = np.nan
        if df > 2:
            # Second non-centered moment E[X^2] from the PDF
            e_x2 = m2 * (gamma**3 + 1/gamma**3) / (gamma + 1/gamma)
            var = e_x2 - mean**2
            
        return mean, var, np.nan, np.nan # Skew and kurtosis not implemented

# Create an instance of the class
skewt = skewt_gen(name='skewt', a=-np.inf, b=np.inf)