"""混合效应模型 — 线性混合模型与广义混合模型"""

from typing import Dict, List, Optional, Tuple
import math


class MixedModel:
    """混合效应模型分析"""

    def __init__(self):
        self._models: List[dict] = []

    def random_intercept_model(self, y: List[float], groups: List[int],
                                X: List[List[float]] = None) -> dict:
        n = len(y)
        unique_groups = list(set(groups))
        k = len(unique_groups)
        if k < 2:
            return {"error": "至少需要2个组"}
        group_means = {}
        group_counts = {}
        for g in unique_groups:
            vals = [y[i] for i in range(n) if groups[i] == g]
            group_means[g] = sum(vals) / len(vals)
            group_counts[g] = len(vals)
        grand_mean = sum(y) / n
        ss_between = sum(group_counts[g] * (group_means[g] - grand_mean) ** 2 for g in unique_groups)
        ss_within = sum((y[i] - group_means[groups[i]]) ** 2 for i in range(n))
        ms_between = ss_between / (k - 1) if k > 1 else 0
        ms_within = ss_within / (n - k) if n > k else 0
        sigma2_within = ms_within
        sigma2_between = max(0, (ms_between - ms_within) / (sum(group_counts[g] ** 2 for g in unique_groups) / n - 1)) if n > 1 else 0
        icc = sigma2_between / (sigma2_between + sigma2_within) if (sigma2_between + sigma2_within) > 0 else 0
        result = {
            "n": n, "k_groups": k, "grand_mean": round(grand_mean, 4),
            "sigma2_within": round(sigma2_within, 4), "sigma2_between": round(sigma2_between, 4),
            "icc": round(icc, 4), "group_sizes": dict(group_counts),
        }
        self._models.append(result)
        return result

    def random_slope_model(self, y: List[float], time: List[float],
                           groups: List[int]) -> dict:
        n = len(y)
        unique_groups = list(set(groups))
        k = len(unique_groups)
        group_results = []
        for g in unique_groups:
            idx = [i for i in range(n) if groups[i] == g]
            g_y = [y[i] for i in idx]
            g_t = [time[i] for i in idx]
            if len(g_y) < 2:
                continue
            t_mean = sum(g_t) / len(g_t)
            y_mean = sum(g_y) / len(g_y)
            ss_tt = sum((t - t_mean) ** 2 for t in g_t)
            ss_ty = sum((t - t_mean) * (y - y_mean) for t, y in zip(g_t, g_y))
            slope = ss_ty / ss_tt if ss_tt > 0 else 0
            intercept = y_mean - slope * t_mean
            group_results.append({"group": g, "intercept": round(intercept, 4),
                                  "slope": round(slope, 4), "n": len(g_y)})
        slopes = [g["slope"] for g in group_results]
        intercepts = [g["intercept"] for g in group_results]
        return {
            "k_groups": k, "group_results": group_results,
            "mean_slope": round(sum(slopes) / len(slopes), 4) if slopes else 0,
            "sd_slope": round(math.sqrt(sum((s - sum(slopes)/len(slopes))**2 for s in slopes) / max(1, len(slopes)-1)), 4) if slopes else 0,
            "mean_intercept": round(sum(intercepts) / len(intercepts), 4) if intercepts else 0,
        }

    def variance_components(self, y: List[float], groups: List[int]) -> dict:
        n = len(y)
        unique_groups = list(set(groups))
        k = len(unique_groups)
        grand_mean = sum(y) / n
        group_means = {}
        for g in unique_groups:
            vals = [y[i] for i in range(n) if groups[i] == g]
            group_means[g] = sum(vals) / len(vals)
        ss_total = sum((y[i] - grand_mean) ** 2 for i in range(n))
        ss_between = sum(len([i for i in range(n) if groups[i] == g]) * (group_means[g] - grand_mean) ** 2 for g in unique_groups)
        ss_within = ss_total - ss_between
        return {
            "ss_total": round(ss_total, 4), "ss_between": round(ss_between, 4),
            "ss_within": round(ss_within, 4),
            "pct_between": round(ss_between / ss_total * 100, 2) if ss_total > 0 else 0,
            "pct_within": round(ss_within / ss_total * 100, 2) if ss_total > 0 else 0,
        }

    def likelihood_ratio_test(self, model1_loglik: float, model2_loglik: float,
                               df_diff: int) -> dict:
        lr = 2 * (model2_loglik - model1_loglik)
        if lr < 0:
            lr = 0
        return {
            "lr_statistic": round(lr, 4), "df": df_diff,
            "significant": lr > 3.841 if df_diff == 1 else lr > 5.991,
        }

    def predict_random_effects(self, y: List[float], groups: List[int],
                                grand_mean: float = None) -> dict:
        n = len(y)
        unique_groups = list(set(groups))
        if grand_mean is None:
            grand_mean = sum(y) / n
        group_effects = {}
        for g in unique_groups:
            vals = [y[i] for i in range(n) if groups[i] == g]
            group_effects[g] = round(sum(vals) / len(vals) - grand_mean, 4)
        return {"grand_mean": round(grand_mean, 4), "random_effects": group_effects}

    def get_models(self) -> List[dict]:
        return list(self._models)
