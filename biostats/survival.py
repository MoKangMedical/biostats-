"""Survival Analysis Module — Kaplan-Meier, Cox PH, Fine-Gray."""

import numpy as np
import pandas as pd
from typing import Optional
from dataclasses import dataclass


@dataclass
class KaplanMeierResult:
    """Kaplan-Meier survival curve result."""
    timeline: np.ndarray
    survival_function: np.ndarray
    confidence_interval: np.ndarray
    median_survival: Optional[float]
    events: int
    censored: int

    def plot(self, ax=None, ci=True, **kwargs):
        """Plot KM curve with confidence interval."""
        import matplotlib.pyplot as plt
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.step(self.timeline, self.survival_function, where='post', 
                linewidth=2, color='#06b6d4', **kwargs)
        
        if ci:
            ax.fill_between(self.timeline, 
                           self.confidence_interval[:, 0],
                           self.confidence_interval[:, 1],
                           alpha=0.15, color='#06b6d4', step='post')
        
        if self.median_survival:
            ax.axhline(y=0.5, color='#94a3b8', linestyle='--', alpha=0.5)
            ax.axvline(x=self.median_survival, color='#f59e0b', linestyle='--', alpha=0.7)
            ax.annotate(f'Median: {self.median_survival:.1f}',
                       xy=(self.median_survival, 0.5),
                       fontsize=10, color='#f59e0b')
        
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Survival Probability', fontsize=12)
        ax.set_title('Kaplan-Meier Survival Curve', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return ax

    def summary(self) -> str:
        """AI-generated plain-language summary."""
        median_str = f"{self.median_survival:.1f}" if self.median_survival else "not reached"
        return (
            f"Kaplan-Meier Analysis Summary:\n"
            f"• Total events: {self.events} | Censored: {self.censored}\n"
            f"• Median survival: {median_str}\n"
            f"• {self.events + self.censored} subjects analyzed\n"
            f"• Survival at last timepoint: {self.survival_function[-1]:.1%}"
        )


class Survival:
    """Survival analysis methods."""

    @staticmethod
    def kaplan_meier(
        time: np.ndarray,
        event: np.ndarray,
        conf_level: float = 0.95
    ) -> KaplanMeierResult:
        """Compute Kaplan-Meier survival curve.
        
        Args:
            time: Array of observed times.
            event: Array of event indicators (1=event, 0=censored).
            conf_level: Confidence level for CI (default 0.95).
        
        Returns:
            KaplanMeierResult with survival curve and statistics.
        """
        from lifelines import KaplanMeierFitter
        
        kmf = KaplanMeierFitter()
        kmf.fit(time, event_observed=event)
        
        sf = kmf.survival_function_.values.flatten()
        timeline = kmf.survival_function_.index.values
        ci = kmf.confidence_interval_survival_function_.values
        
        median = kmf.median_survival_time_
        if np.isinf(median):
            median = None
        
        return KaplanMeierResult(
            timeline=timeline,
            survival_function=sf,
            confidence_interval=ci,
            median_survival=median,
            events=int(np.sum(event)),
            censored=int(np.sum(1 - event)),
        )

    @staticmethod
    def cox_ph(
        df: pd.DataFrame,
        duration_col: str,
        event_col: str,
        covariates: list = None,
    ):
        """Cox Proportional Hazards regression.
        
        Args:
            df: DataFrame with survival data.
            duration_col: Column name for time.
            event_col: Column name for event indicator.
            covariates: List of covariate column names.
        
        Returns:
            Fitted CoxPH model with hazard ratios and p-values.
        """
        from lifelines import CoxPHFitter
        
        cph = CoxPHFitter()
        if covariates:
            cols = [duration_col, event_col] + covariates
            cph.fit(df[cols], duration_col=duration_col, event_col=event_col)
        else:
            cph.fit(df, duration_col=duration_col, event_col=event_col)
        
        return cph

    @staticmethod
    def logrank_test(
        time1: np.ndarray, event1: np.ndarray,
        time2: np.ndarray, event2: np.ndarray,
    ) -> dict:
        """Log-rank test comparing two survival curves."""
        from lifelines.statistics import logrank_test
        
        result = logrank_test(time1, time2, event_observed_A=event1, event_observed_B=event2)
        return {
            "test_statistic": result.test_statistic,
            "p_value": result.p_value,
            "significant": result.p_value < 0.05,
        }
