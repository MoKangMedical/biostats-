"""Clinical Trial Design Module — Sample size, power analysis, adaptive designs."""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrialDesignResult:
    """Result of a trial design calculation."""
    sample_size_per_arm: int
    total_sample_size: int
    power: float
    alpha: float
    effect_size: float
    design_type: str
    
    def summary(self) -> str:
        return (
            f"Trial Design Summary ({self.design_type}):\n"
            f"• Sample size: {self.sample_size_per_arm} per arm ({self.total_sample_size} total)\n"
            f"• Power: {self.power:.0%} | Alpha: {self.alpha:.3f}\n"
            f"• Effect size: {self.effect_size:.3f}"
        )


class TrialDesign:
    """Clinical trial design calculations."""

    @staticmethod
    def two_arm(
        effect_size: float = 0.3,
        alpha: float = 0.05,
        power: float = 0.80,
        allocation_ratio: float = 1.0,
        test_type: str = "two-sided",
    ) -> TrialDesignResult:
        """Two-arm parallel group sample size calculation.
        
        Args:
            effect_size: Standardized effect size (Cohen's d).
            alpha: Significance level (default 0.05).
            power: Statistical power (default 0.80).
            allocation_ratio: Ratio of arm sizes (n2/n1).
            test_type: "two-sided" or "one-sided".
        
        Returns:
            TrialDesignResult with sample size and design parameters.
        """
        from scipy import stats
        
        z_alpha = stats.norm.ppf(1 - alpha / (2 if test_type == "two-sided" else 1))
        z_beta = stats.norm.ppf(power)
        
        n1 = ((z_alpha + z_beta) ** 2 * (1 + 1/allocation_ratio)) / (effect_size ** 2)
        n1 = int(np.ceil(n1))
        n2 = int(np.ceil(n1 * allocation_ratio))
        
        return TrialDesignResult(
            sample_size_per_arm=n1,
            total_sample_size=n1 + n2,
            power=power,
            alpha=alpha,
            effect_size=effect_size,
            design_type="Two-arm parallel",
        )

    @staticmethod
    def survival(
        hazard_ratio: float = 0.7,
        alpha: float = 0.05,
        power: float = 0.80,
        event_prob_control: float = 0.5,
        test_type: str = "two-sided",
    ) -> TrialDesignResult:
        """Sample size for survival endpoint (log-rank test).
        
        Args:
            hazard_ratio: Expected hazard ratio (treatment vs control).
            alpha: Significance level.
            power: Statistical power.
            event_prob_control: Probability of event in control arm.
            test_type: "two-sided" or "one-sided".
        
        Returns:
            TrialDesignResult with required number of events.
        """
        from scipy import stats
        
        z_alpha = stats.norm.ppf(1 - alpha / (2 if test_type == "two-sided" else 1))
        z_beta = stats.norm.ppf(power)
        
        # Schoenfeld formula for number of events
        d = (z_alpha + z_beta) ** 2 / (np.log(hazard_ratio)) ** 2
        d = int(np.ceil(d))
        
        # Total sample size (assuming equal allocation)
        n_total = int(np.ceil(d / event_prob_control))
        
        return TrialDesignResult(
            sample_size_per_arm=n_total // 2,
            total_sample_size=n_total,
            power=power,
            alpha=alpha,
            effect_size=hazard_ratio,
            design_type=f"Log-rank (HR={hazard_ratio})",
        )

    @staticmethod
    def non_inferiority(
        margin: float = 0.1,
        expected_diff: float = 0.0,
        sd: float = 1.0,
        alpha: float = 0.025,
        power: float = 0.80,
    ) -> TrialDesignResult:
        """Non-inferiority trial sample size.
        
        Args:
            margin: Non-inferiority margin.
            expected_diff: Expected treatment difference.
            sd: Standard deviation.
            alpha: One-sided significance level.
            power: Statistical power.
        """
        from scipy import stats
        
        z_alpha = stats.norm.ppf(1 - alpha)
        z_beta = stats.norm.ppf(power)
        
        n = ((z_alpha + z_beta) ** 2 * 2 * sd**2) / ((margin - expected_diff) ** 2)
        n = int(np.ceil(n))
        
        return TrialDesignResult(
            sample_size_per_arm=n,
            total_sample_size=n * 2,
            power=power,
            alpha=alpha,
            effect_size=margin,
            design_type="Non-inferiority",
        )

    @staticmethod
    def power(
        sample_size: int,
        effect_size: float,
        alpha: float = 0.05,
        test_type: str = "two-sided",
    ) -> float:
        """Calculate power for given sample size and effect size."""
        from scipy import stats
        
        z_alpha = stats.norm.ppf(1 - alpha / (2 if test_type == "two-sided" else 1))
        ncp = effect_size * np.sqrt(sample_size / 2)
        power = 1 - stats.norm.cdf(z_alpha - ncp)
        return power
