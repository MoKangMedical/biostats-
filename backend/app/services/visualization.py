"""
Visualization service for generating charts and plots
"""

import base64
import io
from typing import Dict, List, Any, Optional
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


class VisualizationService:
    """Service for generating statistical visualizations"""
    
    @staticmethod
    def survival_curve(
        times: List[float],
        survival_prob: List[float],
        confidence_lower: Optional[List[float]] = None,
        confidence_upper: Optional[List[float]] = None,
        title: str = "Kaplan-Meier Survival Curve",
        xlabel: str = "Time",
        ylabel: str = "Survival Probability"
    ) -> str:
        """
        Generate survival curve plot
        
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot survival curve
        ax.step(times, survival_prob, where='post', linewidth=2, color='#2196F3', label='Survival')
        
        # Plot confidence intervals if provided
        if confidence_lower and confidence_upper:
            ax.fill_between(
                times, confidence_lower, confidence_upper,
                alpha=0.3, color='#2196F3', step='post', label='95% CI'
            )
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def forest_plot(
        effects: List[float],
        ci_lower: List[float],
        ci_upper: List[float],
        labels: List[str],
        weights: Optional[List[float]] = None,
        pooled_effect: Optional[float] = None,
        pooled_ci_lower: Optional[float] = None,
        pooled_ci_upper: Optional[float] = None,
        title: str = "Forest Plot",
        xlabel: str = "Effect Size"
    ) -> str:
        """
        Generate forest plot for meta-analysis
        
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, max(6, len(effects) * 0.5 + 2)))
        
        y_positions = np.arange(len(effects))
        
        # Plot individual studies
        for i, (effect, lower, upper) in enumerate(zip(effects, ci_lower, ci_upper)):
            # Point estimate
            marker_size = 8 if weights is None else max(4, weights[i] * 20)
            ax.plot(effect, i, 'o', color='#2196F3', markersize=marker_size)
            # Confidence interval
            ax.plot([lower, upper], [i, i], '-', color='#2196F3', linewidth=2)
        
        # Plot pooled effect if provided
        if pooled_effect is not None:
            ax.plot(pooled_effect, len(effects), 'D', color='#F44336', markersize=10)
            if pooled_ci_lower and pooled_ci_upper:
                ax.plot(
                    [pooled_ci_lower, pooled_ci_upper],
                    [len(effects), len(effects)],
                    '-', color='#F44336', linewidth=3
                )
        
        # Add vertical line at null effect
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        
        # Labels
        all_labels = labels + ['Pooled'] if pooled_effect is not None else labels
        ax.set_yticks(range(len(all_labels)))
        ax.set_yticklabels(all_labels)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def funnel_plot(
        effects: List[float],
        se: List[float],
        title: str = "Funnel Plot"
    ) -> str:
        """
        Generate funnel plot for publication bias assessment
        
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot studies
        ax.scatter(effects, se, s=50, color='#2196F3', alpha=0.6)
        
        # Add vertical line at pooled effect
        pooled_effect = np.mean(effects)
        ax.axvline(x=pooled_effect, color='red', linestyle='--', label=f'Pooled: {pooled_effect:.3f}')
        
        # Add pseudo 95% CI lines
        se_range = np.linspace(0.01, max(se) * 1.2, 100)
        ci_lower = pooled_effect - 1.96 * se_range
        ci_upper = pooled_effect + 1.96 * se_range
        ax.plot(ci_lower, se_range, 'k--', alpha=0.3)
        ax.plot(ci_upper, se_range, 'k--', alpha=0.3)
        
        ax.set_xlabel('Effect Size', fontsize=12)
        ax.set_ylabel('Standard Error', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Invert y-axis (larger SE at bottom)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def histogram(
        data: List[float],
        title: str = "Histogram",
        xlabel: str = "Value",
        ylabel: str = "Frequency",
        bins: int = 20
    ) -> str:
        """
        Generate histogram
        
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(data, bins=bins, color='#2196F3', alpha=0.7, edgecolor='white')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def boxplot(
        groups: List[List[float]],
        labels: List[str],
        title: str = "Box Plot",
        ylabel: str = "Value"
    ) -> str:
        """
        Generate box plot
        
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bp = ax.boxplot(groups, labels=labels, patch_artist=True)
        
        # Customize colors
        colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0']
        for patch, color in zip(bp['boxes'], colors * len(groups)):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def scatter_plot(
        x: List[float],
        y: List[float],
        title: str = "Scatter Plot",
        xlabel: str = "X",
        ylabel: str = "Y",
        show_regression: bool = True
    ) -> str:
        """
        Generate scatter plot with optional regression line
        
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.scatter(x, y, s=50, color='#2196F3', alpha=0.6)
        
        if show_regression and len(x) > 2:
            # Fit regression line
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            x_line = np.linspace(min(x), max(x), 100)
            ax.plot(x_line, p(x_line), '--', color='#F44336', linewidth=2, label=f'y = {z[0]:.3f}x + {z[1]:.3f}')
            ax.legend(loc='best')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
