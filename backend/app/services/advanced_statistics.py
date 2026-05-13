"""
Advanced statistical analysis services
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class MetaAnalysisResult:
    """Meta-analysis result"""
    pooled_effect: float
    pooled_se: float
    ci_lower: float
    ci_upper: float
    heterogeneity: Dict[str, float]
    studies: List[Dict[str, Any]]


@dataclass
class BayesianResult:
    """Bayesian analysis result"""
    posterior_mean: float
    posterior_sd: float
    credible_lower: float
    credible_upper: float
    prior_mean: float
    prior_sd: float


@dataclass
class HypothesisTestResult:
    """Hypothesis test result"""
    test_statistic: float
    p_value: float
    significant: bool
    effect_size: Optional[float]
    confidence_interval: Optional[Dict[str, float]]


class MetaAnalysisService:
    """Meta-analysis service"""
    
    @staticmethod
    def fixed_effects(
        effects: List[float],
        se: List[float],
        method: str = "inverse_variance"
    ) -> MetaAnalysisResult:
        """
        Fixed-effects meta-analysis
        
        Args:
            effects: Effect sizes from each study
            se: Standard errors from each study
            method: Method for pooling (inverse_variance, mantel_haenszel)
        
        Returns:
            MetaAnalysisResult with pooled effect and heterogeneity
        """
        effects = np.array(effects)
        se = np.array(se)
        
        # Weights (inverse variance)
        weights = 1 / (se ** 2)
        
        # Pooled effect
        pooled_effect = np.sum(weights * effects) / np.sum(weights)
        pooled_se = np.sqrt(1 / np.sum(weights))
        
        # Confidence interval (95%)
        ci_lower = pooled_effect - 1.96 * pooled_se
        ci_upper = pooled_effect + 1.96 * pooled_se
        
        # Heterogeneity statistics
        Q = np.sum(weights * (effects - pooled_effect) ** 2)
        k = len(effects)
        df = k - 1
        
        # I-squared
        I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0
        
        # Tau-squared (DerSimonian-Laird)
        C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
        tau2 = max(0, (Q - df) / C) if C > 0 else 0
        
        # Individual study results
        studies = []
        for i in range(k):
            studies.append({
                "effect": float(effects[i]),
                "se": float(se[i]),
                "weight": float(weights[i] / np.sum(weights) * 100),
                "ci_lower": float(effects[i] - 1.96 * se[i]),
                "ci_upper": float(effects[i] + 1.96 * se[i])
            })
        
        return MetaAnalysisResult(
            pooled_effect=float(pooled_effect),
            pooled_se=float(pooled_se),
            ci_lower=float(ci_lower),
            ci_upper=float(ci_upper),
            heterogeneity={
                "Q": float(Q),
                "df": df,
                "p_value": float(1 - __import__('scipy').stats.chi2.cdf(Q, df)),
                "I2": float(I2),
                "tau2": float(tau2)
            },
            studies=studies
        )
    
    @staticmethod
    def random_effects(
        effects: List[float],
        se: List[float]
    ) -> MetaAnalysisResult:
        """
        Random-effects meta-analysis (DerSimonian-Laird)
        
        Args:
            effects: Effect sizes from each study
            se: Standard errors from each study
        
        Returns:
            MetaAnalysisResult with pooled effect and heterogeneity
        """
        effects = np.array(effects)
        se = np.array(se)
        
        # First pass: fixed-effects to estimate tau2
        weights_fixed = 1 / (se ** 2)
        pooled_fixed = np.sum(weights_fixed * effects) / np.sum(weights_fixed)
        
        Q = np.sum(weights_fixed * (effects - pooled_fixed) ** 2)
        k = len(effects)
        df = k - 1
        C = np.sum(weights_fixed) - np.sum(weights_fixed ** 2) / np.sum(weights_fixed)
        tau2 = max(0, (Q - df) / C) if C > 0 else 0
        
        # Second pass: random-effects weights
        weights_random = 1 / (se ** 2 + tau2)
        
        # Pooled effect
        pooled_effect = np.sum(weights_random * effects) / np.sum(weights_random)
        pooled_se = np.sqrt(1 / np.sum(weights_random))
        
        # Confidence interval (95%)
        ci_lower = pooled_effect - 1.96 * pooled_se
        ci_upper = pooled_effect + 1.96 * pooled_se
        
        # I-squared
        I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0
        
        # Individual study results
        studies = []
        for i in range(k):
            studies.append({
                "effect": float(effects[i]),
                "se": float(se[i]),
                "weight": float(weights_random[i] / np.sum(weights_random) * 100),
                "ci_lower": float(effects[i] - 1.96 * se[i]),
                "ci_upper": float(effects[i] + 1.96 * se[i])
            })
        
        return MetaAnalysisResult(
            pooled_effect=float(pooled_effect),
            pooled_se=float(pooled_se),
            ci_lower=float(ci_lower),
            ci_upper=float(ci_upper),
            heterogeneity={
                "Q": float(Q),
                "df": df,
                "p_value": float(1 - __import__('scipy').stats.chi2.cdf(Q, df)),
                "I2": float(I2),
                "tau2": float(tau2)
            },
            studies=studies
        )


class BayesianService:
    """Bayesian analysis service"""
    
    @staticmethod
    def beta_binomial(
        successes: int,
        trials: int,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0
    ) -> BayesianResult:
        """
        Beta-Binomial conjugate analysis
        
        Args:
            successes: Number of successes
            trials: Number of trials
            prior_alpha: Prior alpha parameter
            prior_beta: Prior beta parameter
        
        Returns:
            BayesianResult with posterior statistics
        """
        from scipy import stats
        
        # Posterior parameters
        post_alpha = prior_alpha + successes
        post_beta = prior_beta + (trials - successes)
        
        # Posterior distribution
        posterior = stats.beta(post_alpha, post_beta)
        
        # Posterior statistics
        posterior_mean = posterior.mean()
        posterior_sd = posterior.std()
        credible_lower = posterior.ppf(0.025)
        credible_upper = posterior.ppf(0.975)
        
        # Prior statistics
        prior = stats.beta(prior_alpha, prior_beta)
        prior_mean = prior.mean()
        prior_sd = prior.std()
        
        return BayesianResult(
            posterior_mean=float(posterior_mean),
            posterior_sd=float(posterior_sd),
            credible_lower=float(credible_lower),
            credible_upper=float(credible_upper),
            prior_mean=float(prior_mean),
            prior_sd=float(prior_sd)
        )
    
    @staticmethod
    def normal_normal(
        data_mean: float,
        data_sd: float,
        n: int,
        prior_mean: float = 0.0,
        prior_sd: float = 1.0
    ) -> BayesianResult:
        """
        Normal-Normal conjugate analysis
        
        Args:
            data_mean: Sample mean
            data_sd: Sample standard deviation
            n: Sample size
            prior_mean: Prior mean
            prior_sd: Prior standard deviation
        
        Returns:
            BayesianResult with posterior statistics
        """
        from scipy import stats
        
        # Likelihood precision
        likelihood_precision = n / (data_sd ** 2)
        
        # Prior precision
        prior_precision = 1 / (prior_sd ** 2)
        
        # Posterior precision
        post_precision = prior_precision + likelihood_precision
        post_sd = np.sqrt(1 / post_precision)
        
        # Posterior mean
        post_mean = (prior_precision * prior_mean + likelihood_precision * data_mean) / post_precision
        
        # Posterior distribution
        posterior = stats.norm(post_mean, post_sd)
        
        # Credible interval
        credible_lower = posterior.ppf(0.025)
        credible_upper = posterior.ppf(0.975)
        
        return BayesianResult(
            posterior_mean=float(post_mean),
            posterior_sd=float(post_sd),
            credible_lower=float(credible_lower),
            credible_upper=float(credible_upper),
            prior_mean=float(prior_mean),
            prior_sd=float(prior_sd)
        )


class HypothesisTestService:
    """Hypothesis testing service"""
    
    @staticmethod
    def t_test_two_samples(
        group1: List[float],
        group2: List[float],
        alternative: str = "two-sided"
    ) -> HypothesisTestResult:
        """
        Two-sample t-test
        
        Args:
            group1: First group data
            group2: Second group data
            alternative: Alternative hypothesis (two-sided, less, greater)
        
        Returns:
            HypothesisTestResult with test statistics
        """
        from scipy import stats
        
        group1 = np.array(group1)
        group2 = np.array(group2)
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(group1, group2, alternative=alternative)
        
        # Effect size (Cohen's d)
        pooled_sd = np.sqrt((np.std(group1, ddof=1) ** 2 + np.std(group2, ddof=1) ** 2) / 2)
        cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_sd if pooled_sd > 0 else 0
        
        # Confidence interval for difference in means
        se = np.sqrt(np.var(group1, ddof=1) / len(group1) + np.var(group2, ddof=1) / len(group2))
        diff = np.mean(group1) - np.mean(group2)
        ci_lower = diff - 1.96 * se
        ci_upper = diff + 1.96 * se
        
        return HypothesisTestResult(
            test_statistic=float(t_stat),
            p_value=float(p_value),
            significant=p_value < 0.05,
            effect_size=float(cohens_d),
            confidence_interval={"lower": float(ci_lower), "upper": float(ci_upper)}
        )
    
    @staticmethod
    def chi_square_test(
        observed: List[List[int]]
    ) -> HypothesisTestResult:
        """
        Chi-square test of independence
        
        Args:
            observed: Observed frequency table (2D list)
        
        Returns:
            HypothesisTestResult with test statistics
        """
        from scipy import stats
        
        observed = np.array(observed)
        
        # Perform chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        
        # Effect size (Cramér's V)
        n = observed.sum()
        min_dim = min(observed.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        
        return HypothesisTestResult(
            test_statistic=float(chi2),
            p_value=float(p_value),
            significant=p_value < 0.05,
            effect_size=float(cramers_v),
            confidence_interval=None
        )
    
    @staticmethod
    def mann_whitney_test(
        group1: List[float],
        group2: List[float],
        alternative: str = "two-sided"
    ) -> HypothesisTestResult:
        """
        Mann-Whitney U test (non-parametric)
        
        Args:
            group1: First group data
            group2: Second group data
            alternative: Alternative hypothesis
        
        Returns:
            HypothesisTestResult with test statistics
        """
        from scipy import stats
        
        group1 = np.array(group1)
        group2 = np.array(group2)
        
        # Perform Mann-Whitney U test
        u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative=alternative)
        
        # Effect size (rank-biserial correlation)
        n1 = len(group1)
        n2 = len(group2)
        r = 1 - (2 * u_stat) / (n1 * n2)
        
        return HypothesisTestResult(
            test_statistic=float(u_stat),
            p_value=float(p_value),
            significant=p_value < 0.05,
            effect_size=float(r),
            confidence_interval=None
        )
