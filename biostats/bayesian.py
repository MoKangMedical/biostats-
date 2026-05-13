"""Bayesian Analysis Module — Conjugate priors, MCMC, model comparison."""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class PosteriorResult:
    """Result of Bayesian analysis."""
    posterior_mean: float
    posterior_std: float
    credible_interval: Tuple[float, float]
    prior_params: dict
    data_summary: dict
    method: str

    def credible_interval(self, level: float = 0.95) -> Tuple[float, float]:
        """Get credible interval at specified level."""
        return self.credible_interval

    def summary(self) -> str:
        lo, hi = self.credible_interval
        return (
            f"Bayesian Analysis Summary ({self.method}):\n"
            f"• Posterior mean: {self.posterior_mean:.4f}\n"
            f"• Posterior SD: {self.posterior_std:.4f}\n"
            f"• 95% Credible interval: ({lo:.4f}, {hi:.4f})\n"
            f"• Prior: {self.prior_params}\n"
            f"• Data: {self.data_summary}"
        )

    def plot(self, ax=None):
        """Plot posterior distribution."""
        import matplotlib.pyplot as plt
        from scipy import stats
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.linspace(
            self.posterior_mean - 4 * self.posterior_std,
            self.posterior_mean + 4 * self.posterior_std,
            200
        )
        
        # Approximate with normal
        y = stats.norm.pdf(x, self.posterior_mean, self.posterior_std)
        ax.fill_between(x, y, alpha=0.3, color='#8b5cf6')
        ax.plot(x, y, color='#8b5cf6', linewidth=2)
        
        lo, hi = self.credible_interval
        ax.axvline(x=lo, color='#f59e0b', linestyle='--', alpha=0.7)
        ax.axvline(x=hi, color='#f59e0b', linestyle='--', alpha=0.7)
        ax.axvline(x=self.posterior_mean, color='#06b6d4', linewidth=2)
        
        ax.set_xlabel('Parameter Value', fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
        ax.set_title('Posterior Distribution', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return ax


class Bayesian:
    """Bayesian analysis methods."""

    @staticmethod
    def bernoulli(
        successes: int,
        trials: int,
        prior_beta: Tuple[float, float] = (1, 1),
        ci_level: float = 0.95,
    ) -> PosteriorResult:
        """Bayesian analysis of binomial proportion (Beta-Binomial conjugate).
        
        Args:
            successes: Number of successes.
            trials: Total number of trials.
            prior_beta: Beta prior parameters (alpha, beta).
            ci_level: Credible interval level.
        
        Returns:
            PosteriorResult with posterior distribution properties.
        """
        from scipy import stats
        
        alpha_prior, beta_prior = prior_beta
        alpha_post = alpha_prior + successes
        beta_post = beta_prior + (trials - successes)
        
        posterior = stats.beta(alpha_post, beta_post)
        mean = posterior.mean()
        std = posterior.std()
        ci = posterior.interval(ci_level)
        
        return PosteriorResult(
            posterior_mean=mean,
            posterior_std=std,
            credible_interval=ci,
            prior_params={"distribution": "Beta", "alpha": alpha_prior, "beta": beta_prior},
            data_summary={"successes": successes, "trials": trials, "observed_rate": successes/trials},
            method="Beta-Binomial conjugate",
        )

    @staticmethod
    def normal_mean(
        data: np.ndarray,
        prior_mean: float = 0,
        prior_std: float = 10,
        known_std: float = None,
        ci_level: float = 0.95,
    ) -> PosteriorResult:
        """Bayesian analysis of normal mean (Normal-Normal conjugate).
        
        Args:
            data: Observed data.
            prior_mean: Prior mean for the parameter.
            prior_std: Prior standard deviation.
            known_std: Known standard deviation of data (if None, uses sample std).
            ci_level: Credible interval level.
        
        Returns:
            PosteriorResult with posterior distribution properties.
        """
        from scipy import stats
        
        n = len(data)
        x_bar = np.mean(data)
        
        if known_std is None:
            known_std = np.std(data, ddof=1)
        
        # Posterior parameters
        precision_prior = 1 / (prior_std ** 2)
        precision_data = n / (known_std ** 2)
        precision_post = precision_prior + precision_data
        
        post_mean = (precision_prior * prior_mean + precision_data * x_bar) / precision_post
        post_std = np.sqrt(1 / precision_post)
        
        ci = stats.norm.interval(ci_level, loc=post_mean, scale=post_std)
        
        return PosteriorResult(
            posterior_mean=post_mean,
            posterior_std=post_std,
            credible_interval=ci,
            prior_params={"distribution": "Normal", "mean": prior_mean, "std": prior_std},
            data_summary={"n": n, "mean": x_bar, "std": known_std},
            method="Normal-Normal conjugate",
        )

    @staticmethod
    def compare_rates(
        successes_a: int, trials_a: int,
        successes_b: int, trials_b: int,
        n_samples: int = 10000,
    ) -> dict:
        """Bayesian comparison of two proportions.
        
        Returns:
            Dict with P(A > B), P(B > A), and posterior of difference.
        """
        from scipy import stats
        
        samples_a = stats.beta.rvs(successes_a + 1, trials_a - successes_a + 1, size=n_samples)
        samples_b = stats.beta.rvs(successes_b + 1, trials_b - successes_b + 1, size=n_samples)
        diff = samples_a - samples_b
        
        return {
            "prob_a_greater": np.mean(diff > 0),
            "prob_b_greater": np.mean(diff < 0),
            "mean_difference": np.mean(diff),
            "ci_95": (np.percentile(diff, 2.5), np.percentile(diff, 97.5)),
            "method": "Monte Carlo Beta-Binomial",
        }
