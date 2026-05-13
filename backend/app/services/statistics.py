"""
Statistical analysis services
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SurvivalResult:
    """Survival analysis result"""
    times: List[float]
    survival_prob: List[float]
    confidence_lower: List[float]
    confidence_upper: List[float]
    median_survival: Optional[float]
    events: int
    censored: int


@dataclass
class SampleSizeResult:
    """Sample size calculation result"""
    n_per_group: int
    total_n: int
    power: float
    alpha: float
    effect_size: float


class SurvivalService:
    """Survival analysis service"""
    
    @staticmethod
    def kaplan_meier(
        time: List[float],
        event: List[int],
        confidence_level: float = 0.95
    ) -> SurvivalResult:
        """
        Kaplan-Meier survival analysis
        
        Args:
            time: Time to event
            event: Event indicator (1=event, 0=censored)
            confidence_level: Confidence level for CI
        
        Returns:
            SurvivalResult with survival curve and statistics
        """
        import numpy as np
        
        # Convert to numpy arrays
        time = np.array(time)
        event = np.array(event)
        
        # Sort by time
        order = np.argsort(time)
        time = time[order]
        event = event[order]
        
        # Calculate survival curve
        n = len(time)
        survival = np.ones(n + 1)
        variance = np.zeros(n + 1)
        
        at_risk = n
        events_total = 0
        censored_total = 0
        
        times = [0]
        survival_probs = [1.0]
        
        for i in range(n):
            if event[i] == 1:
                # Event occurred
                survival[i + 1] = survival[i] * (at_risk - 1) / at_risk
                variance[i + 1] = variance[i] + 1 / (at_risk * (at_risk - 1))
                events_total += 1
            else:
                # Censored
                survival[i + 1] = survival[i]
                variance[i + 1] = variance[i]
                censored_total += 1
            
            at_risk -= 1
            times.append(time[i])
            survival_probs.append(survival[i + 1])
        
        # Calculate confidence intervals (log-log transformation)
        z = 1.96  # 95% CI
        confidence_lower = []
        confidence_upper = []
        
        for i, s in enumerate(survival_probs):
            if s > 0 and s < 1:
                se = np.sqrt(variance[i])
                log_log_se = se / (s * np.log(s))
                lower = s ** np.exp(z * log_log_se)
                upper = s ** np.exp(-z * log_log_se)
                confidence_lower.append(max(0, lower))
                confidence_upper.append(min(1, upper))
            else:
                confidence_lower.append(s)
                confidence_upper.append(s)
        
        # Calculate median survival
        median_survival = None
        for i, s in enumerate(survival_probs):
            if s <= 0.5:
                median_survival = times[i]
                break
        
        return SurvivalResult(
            times=times,
            survival_prob=survival_probs,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            median_survival=median_survival,
            events=events_total,
            censored=censored_total
        )
    
    @staticmethod
    def log_rank_test(
        time1: List[float], event1: List[int],
        time2: List[float], event2: List[int]
    ) -> Dict[str, Any]:
        """
        Log-rank test for comparing two survival curves
        
        Returns:
            Dictionary with test statistic and p-value
        """
        import numpy as np
        from scipy import stats
        
        # Combine and sort
        all_time = np.concatenate([time1, time2])
        all_event = np.concatenate([event1, event2])
        all_group = np.concatenate([np.zeros(len(time1)), np.ones(len(time2))])
        
        order = np.argsort(all_time)
        all_time = all_time[order]
        all_event = all_event[order]
        all_group = all_group[order]
        
        # Calculate test statistic
        n = len(all_time)
        O1 = 0  # Observed events in group 1
        E1 = 0  # Expected events in group 1
        V = 0   # Variance
        
        n1 = len(time1)
        n2 = len(time2)
        d1 = np.sum(event1)
        d2 = np.sum(event2)
        
        for i in range(n):
            if all_event[i] == 1:
                # Event occurred
                if all_group[i] == 0:
                    O1 += 1
                
                # Expected
                e1 = n1 / (n1 + n2)
                E1 += e1
                
                # Variance
                if n1 + n2 > 1:
                    V += (n1 * n2 * (n1 + n2 - 1)) / ((n1 + n2) ** 2 * (n1 + n2 - 1))
            
            # Update at risk
            if all_group[i] == 0:
                n1 -= 1
            else:
                n2 -= 1
        
        # Test statistic
        chi2 = (O1 - E1) ** 2 / V if V > 0 else 0
        p_value = 1 - stats.chi2.cdf(chi2, df=1)
        
        return {
            "chi2": float(chi2),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
            "observed_group1": O1,
            "expected_group1": float(E1),
            "observed_group2": d2 - (d1 - O1) if d1 > O1 else d2
        }


class SampleSizeService:
    """Sample size calculation service"""
    
    @staticmethod
    def two_means(
        mean1: float, mean2: float, sd: float,
        alpha: float = 0.05, power: float = 0.80,
        ratio: float = 1.0
    ) -> SampleSizeResult:
        """
        Sample size for comparing two means
        
        Args:
            mean1: Mean of group 1
            mean2: Mean of group 2
            sd: Standard deviation
            alpha: Significance level
            power: Statistical power
            ratio: Allocation ratio (n2/n1)
        
        Returns:
            SampleSizeResult
        """
        from scipy import stats
        
        # Effect size
        effect_size = abs(mean1 - mean2) / sd
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        # Sample size per group
        n = ((z_alpha + z_beta) / effect_size) ** 2 * (1 + 1/ratio)
        n_per_group = int(np.ceil(n))
        
        return SampleSizeResult(
            n_per_group=n_per_group,
            total_n=n_per_group * 2,
            power=power,
            alpha=alpha,
            effect_size=effect_size
        )
    
    @staticmethod
    def two_proportions(
        p1: float, p2: float,
        alpha: float = 0.05, power: float = 0.80,
        ratio: float = 1.0
    ) -> SampleSizeResult:
        """
        Sample size for comparing two proportions
        
        Args:
            p1: Proportion in group 1
            p2: Proportion in group 2
            alpha: Significance level
            power: Statistical power
            ratio: Allocation ratio (n2/n1)
        
        Returns:
            SampleSizeResult
        """
        from scipy import stats
        
        # Effect size
        effect_size = abs(p1 - p2)
        
        # Pooled proportion
        p_pool = (p1 + ratio * p2) / (1 + ratio)
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        # Sample size per group
        n = (
            (z_alpha * np.sqrt(p_pool * (1 - p_pool) * (1 + 1/ratio)) +
             z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / ratio)) ** 2 /
            effect_size ** 2
        )
        n_per_group = int(np.ceil(n))
        
        return SampleSizeResult(
            n_per_group=n_per_group,
            total_n=n_per_group * 2,
            power=power,
            alpha=alpha,
            effect_size=effect_size
        )
    
    @staticmethod
    def survival(
        hazard_ratio: float,
        alpha: float = 0.05, power: float = 0.80,
        prob_event: float = 0.5,
        ratio: float = 1.0
    ) -> SampleSizeResult:
        """
        Sample size for survival endpoint (Schoenfeld formula)
        
        Args:
            hazard_ratio: Hazard ratio (treatment/control)
            alpha: Significance level
            power: Statistical power
            prob_event: Probability of event
            ratio: Allocation ratio (n2/n1)
        
        Returns:
            SampleSizeResult
        """
        from scipy import stats
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        # Effect size (log hazard ratio)
        effect_size = np.log(hazard_ratio)
        
        # Number of events required
        d = ((z_alpha + z_beta) / effect_size) ** 2 * (1 + ratio) ** 2 / ratio
        
        # Total sample size
        total_n = int(np.ceil(d / prob_event))
        n_per_group = int(np.ceil(total_n / 2))
        
        return SampleSizeResult(
            n_per_group=n_per_group,
            total_n=total_n,
            power=power,
            alpha=alpha,
            effect_size=abs(effect_size)
        )
