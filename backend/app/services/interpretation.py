"""
AI interpretation service for statistical results
"""

from typing import Dict, Any, Optional


class InterpretationService:
    """Service for generating plain-language interpretations of statistical results"""
    
    @staticmethod
    def interpret_survival_analysis(
        median_survival: Optional[float],
        events: int,
        censored: int,
        log_rank_p: Optional[float] = None
    ) -> str:
        """
        Generate plain-language interpretation of survival analysis results
        """
        total = events + censored
        event_rate = events / total * 100 if total > 0 else 0
        
        interpretation = f"""
## Survival Analysis Interpretation

### Key Findings:
- **Total participants**: {total}
- **Events observed**: {events} ({event_rate:.1f}%)
- **Censored observations**: {censored} ({100 - event_rate:.1f}%)
"""
        
        if median_survival is not None:
            interpretation += f"- **Median survival time**: {median_survival:.2f} time units\n"
            interpretation += f"\nThis means that 50% of participants experienced the event by {median_survival:.2f} time units.\n"
        else:
            interpretation += "- **Median survival time**: Not reached (more than 50% of participants survived beyond the study period)\n"
        
        if log_rank_p is not None:
            if log_rank_p < 0.05:
                interpretation += f"\n### Statistical Comparison (Log-rank test: p = {log_rank_p:.4f})\n"
                interpretation += "There is a **statistically significant difference** between the survival curves (p < 0.05).\n"
                interpretation += "This suggests that the groups have different survival experiences.\n"
            else:
                interpretation += f"\n### Statistical Comparison (Log-rank test: p = {log_rank_p:.4f})\n"
                interpretation += "There is **no statistically significant difference** between the survival curves (p ≥ 0.05).\n"
                interpretation += "The observed differences could be due to chance.\n"
        
        interpretation += """
### Clinical Meaning:
- Survival analysis helps understand **time-to-event** outcomes
- The Kaplan-Meier curve shows the probability of surviving over time
- Censored observations are participants who didn't experience the event during the study
"""
        
        return interpretation
    
    @staticmethod
    def interpret_sample_size(
        n_per_group: int,
        total_n: int,
        power: float,
        alpha: float,
        effect_size: float
    ) -> str:
        """
        Generate plain-language interpretation of sample size calculation
        """
        interpretation = f"""
## Sample Size Calculation Interpretation

### Results:
- **Sample size per group**: {n_per_group}
- **Total sample size**: {total_n}
- **Statistical power**: {power * 100:.0f}%
- **Significance level (α)**: {alpha}
- **Effect size**: {effect_size:.3f}

### What This Means:
- You need **{n_per_group} participants in each group** (total {total_n}) for your study
- With this sample size, you have a **{power * 100:.0f}% chance** of detecting a true effect if one exists
- The significance level of {alpha} means there's a **{alpha * 100:.0f}% risk** of a false positive (Type I error)

### Practical Considerations:
- Consider adding **10-20%** to account for dropout and missing data
- **Recruited sample**: {int(total_n * 1.15)}-{int(total_n * 1.20)} participants recommended
- Ensure balanced allocation between groups for maximum statistical efficiency

### Power Analysis:
- If the true effect is smaller than expected, you may need a larger sample
- If you can only recruit fewer participants, your study may be underpowered
"""
        
        return interpretation
    
    @staticmethod
    def interpret_meta_analysis(
        pooled_effect: float,
        ci_lower: float,
        ci_upper: float,
        heterogeneity: Dict[str, float],
        n_studies: int
    ) -> str:
        """
        Generate plain-language interpretation of meta-analysis results
        """
        interpretation = f"""
## Meta-Analysis Interpretation

### Results:
- **Number of studies**: {n_studies}
- **Pooled effect size**: {pooled_effect:.3f}
- **95% Confidence interval**: [{ci_lower:.3f}, {ci_upper:.3f}]
- **Heterogeneity (I²)**: {heterogeneity.get('I2', 0):.1f}%

### What This Means:
"""
        
        # Interpret effect direction and significance
        if ci_lower > 0:
            interpretation += "- The pooled effect is **positive and statistically significant** (CI doesn't include 0)\n"
            interpretation += "- There is consistent evidence of a beneficial effect across studies\n"
        elif ci_upper < 0:
            interpretation += "- The pooled effect is **negative and statistically significant** (CI doesn't include 0)\n"
            interpretation += "- There is consistent evidence of a harmful effect across studies\n"
        else:
            interpretation += "- The pooled effect is **not statistically significant** (CI includes 0)\n"
            interpretation += "- The evidence is inconclusive; the true effect could be positive, negative, or null\n"
        
        # Interpret heterogeneity
        I2 = heterogeneity.get('I2', 0)
        if I2 < 25:
            interpretation += "- **Low heterogeneity**: Studies are consistent with each other\n"
        elif I2 < 50:
            interpretation += "- **Moderate heterogeneity**: Some variability between studies\n"
        elif I2 < 75:
            interpretation += "- **Substantial heterogeneity**: Considerable variability between studies\n"
        else:
            interpretation += "- **High heterogeneity**: Major variability; results should be interpreted with caution\n"
            interpretation += "- Consider exploring sources of heterogeneity through subgroup analysis\n"
        
        interpretation += """
### Clinical Implications:
- Meta-analysis provides the **strongest level of evidence** by combining multiple studies
- The confidence interval indicates the **precision** of the estimate
- Consider the clinical significance alongside statistical significance
"""
        
        return interpretation
    
    @staticmethod
    def interpret_hypothesis_test(
        test_name: str,
        test_statistic: float,
        p_value: float,
        effect_size: Optional[float] = None,
        significant: bool = False
    ) -> str:
        """
        Generate plain-language interpretation of hypothesis test results
        """
        interpretation = f"""
## {test_name} Interpretation

### Results:
- **Test statistic**: {test_statistic:.3f}
- **P-value**: {p_value:.4f}
- **Statistically significant**: {'Yes' if significant else 'No'} (α = 0.05)
"""
        
        if effect_size is not None:
            interpretation += f"- **Effect size**: {effect_size:.3f}\n"
            
            # Interpret effect size magnitude
            abs_effect = abs(effect_size)
            if abs_effect < 0.2:
                interpretation += "  - **Interpretation**: Negligible effect\n"
            elif abs_effect < 0.5:
                interpretation += "  - **Interpretation**: Small effect\n"
            elif abs_effect < 0.8:
                interpretation += "  - **Interpretation**: Medium effect\n"
            else:
                interpretation += "  - **Interpretation**: Large effect\n"
        
        interpretation += f"""
### What This Means:
"""
        
        if significant:
            interpretation += "- The **null hypothesis is rejected** (p < 0.05)\n"
            interpretation += "- There is **statistically significant evidence** of a difference/relationship\n"
            interpretation += "- The observed result is unlikely to be due to chance alone\n"
        else:
            interpretation += "- The **null hypothesis is not rejected** (p ≥ 0.05)\n"
            interpretation += "- There is **no statistically significant evidence** of a difference/relationship\n"
            interpretation += "- The observed result could reasonably be due to chance\n"
        
        interpretation += """
### Important Notes:
- Statistical significance ≠ clinical significance
- P-value indicates the probability of observing such extreme results **if the null hypothesis were true**
- Effect size helps quantify the **magnitude** of the difference/relationship
- Consider confidence intervals for a more complete picture
"""
        
        return interpretation
    
    @staticmethod
    def interpret_bayesian(
        posterior_mean: float,
        posterior_sd: float,
        credible_lower: float,
        credible_upper: float,
        prior_mean: float,
        prior_sd: float
    ) -> str:
        """
        Generate plain-language interpretation of Bayesian analysis results
        """
        interpretation = f"""
## Bayesian Analysis Interpretation

### Prior Distribution:
- **Prior mean**: {prior_mean:.3f}
- **Prior standard deviation**: {prior_sd:.3f}

### Posterior Distribution:
- **Posterior mean**: {posterior_mean:.3f}
- **Posterior standard deviation**: {posterior_sd:.3f}
- **95% Credible interval**: [{credible_lower:.3f}, {credible_upper:.3f}]

### What This Means:
"""
        
        # Compare prior and posterior
        if abs(posterior_mean - prior_mean) < posterior_sd:
            interpretation += "- The data **confirms** the prior belief (posterior is close to prior)\n"
        elif posterior_mean > prior_mean:
            interpretation += "- The data suggests the true value is **higher** than the prior belief\n"
        else:
            interpretation += "- The data suggests the true value is **lower** than the prior belief\n"
        
        # Precision update
        if posterior_sd < prior_sd:
            interpretation += "- The data has **increased precision** (posterior is narrower than prior)\n"
            interpretation += "- We are now more certain about the true value\n"
        else:
            interpretation += "- The data has **not increased precision** much\n"
        
        interpretation += f"""
### Credible Interval:
- There is a **95% probability** that the true value lies between {credible_lower:.3f} and {credible_upper:.3f}
- This is a **direct probability statement** about the parameter (unlike confidence intervals)

### Bayesian vs. Frequentist:
- Bayesian analysis provides **probability statements** about parameters
- Results are intuitive: "There is a 95% chance the true value is in this interval"
- Prior beliefs are explicitly incorporated and updated with data
"""
        
        return interpretation
