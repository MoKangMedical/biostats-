"""纵向分析 — 重复测量与纵向数据分析"""

from typing import Dict, List, Optional, Tuple
import math


class LongitudinalAnalysis:
    """纵向数据分析方法"""

    def __init__(self):
        self._results: List[dict] = []

    def descriptive_by_time(self, data: List[List[float]], time_labels: List[str] = None) -> List[dict]:
        if not time_labels:
            time_labels = [f"T{i}" for i in range(len(data))]
        results = []
        for i, values in enumerate(data):
            if not values:
                continue
            n = len(values)
            mean = sum(values) / n
            var = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0
            results.append({
                "time": time_labels[i] if i < len(time_labels) else f"T{i}",
                "n": n, "mean": round(mean, 4), "sd": round(math.sqrt(var), 4),
                "min": min(values), "max": max(values),
            })
        return results

    def change_from_baseline(self, data: List[List[float]], baseline_idx: int = 0) -> List[dict]:
        if not data or baseline_idx >= len(data):
            return []
        baseline = data[baseline_idx]
        baseline_mean = sum(baseline) / len(baseline) if baseline else 0
        results = []
        for i, values in enumerate(data):
            if not values:
                continue
            mean = sum(values) / len(values)
            change = mean - baseline_mean
            pct = (change / baseline_mean * 100) if baseline_mean != 0 else 0
            results.append({
                "time": f"T{i}", "mean": round(mean, 4),
                "change": round(change, 4), "pct_change": round(pct, 2),
            })
        return results

    def paired_ttest(self, group1: List[float], group2: List[float]) -> dict:
        if len(group1) != len(group2) or len(group1) < 2:
            return {"error": "需要等长且至少2对数据"}
        diffs = [a - b for a, b in zip(group1, group2)]
        n = len(diffs)
        d_bar = sum(diffs) / n
        var = sum((d - d_bar) ** 2 for d in diffs) / (n - 1)
        se = math.sqrt(var / n)
        t_stat = d_bar / se if se > 0 else 0
        df = n - 1
        return {
            "n_pairs": n, "mean_diff": round(d_bar, 4), "sd_diff": round(math.sqrt(var), 4),
            "se": round(se, 4), "t_statistic": round(t_stat, 4), "df": df,
            "significant": abs(t_stat) > 2.0,
        }

    def repeated_measures_anova(self, groups: List[List[float]]) -> dict:
        k = len(groups)
        if k < 2:
            return {"error": "至少需要2个时间点"}
        n = min(len(g) for g in groups)
        if n < 2:
            return {"error": "每组至少需要2个观测"}
        grand_mean = sum(sum(g[:n]) for g in groups) / (k * n)
        ss_between = sum(n * (sum(g[:n]) / n - grand_mean) ** 2 for g in groups)
        ss_within = sum(sum((x - sum(g[:n]) / n) ** 2 for x in g[:n]) for g in groups)
        df_between = k - 1
        df_within = k * (n - 1)
        ms_between = ss_between / df_between if df_between > 0 else 0
        ms_within = ss_within / df_within if df_within > 0 else 0
        f_stat = ms_between / ms_within if ms_within > 0 else 0
        return {
            "k_groups": k, "n_per_group": n, "grand_mean": round(grand_mean, 4),
            "ss_between": round(ss_between, 4), "ss_within": round(ss_within, 4),
            "df_between": df_between, "df_within": df_within,
            "ms_between": round(ms_between, 4), "ms_within": round(ms_within, 4),
            "f_statistic": round(f_stat, 4), "significant": f_stat > 3.0,
        }

    def trend_test(self, values: List[float]) -> dict:
        n = len(values)
        if n < 3:
            return {"error": "至少需要3个数据点"}
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        ss_xx = sum((xi - x_mean) ** 2 for xi in x)
        ss_xy = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
        slope = ss_xy / ss_xx if ss_xx > 0 else 0
        intercept = y_mean - slope * x_mean
        y_pred = [slope * xi + intercept for xi in x]
        ss_res = sum((yi - yp) ** 2 for yi, yp in zip(values, y_pred))
        se_slope = math.sqrt(ss_res / (n - 2) / ss_xx) if n > 2 and ss_xx > 0 else 0
        t_stat = slope / se_slope if se_slope > 0 else 0
        return {
            "slope": round(slope, 4), "intercept": round(intercept, 4),
            "t_statistic": round(t_stat, 4), "significant_trend": abs(t_stat) > 2.0,
            "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat",
        }

    def correlation_matrix(self, variables: List[List[float]]) -> List[List[float]]:
        k = len(variables)
        matrix = [[0.0] * k for _ in range(k)]
        for i in range(k):
            for j in range(k):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    matrix[i][j] = self._pearson(variables[i], variables[j])
        return matrix

    def _pearson(self, x: List[float], y: List[float]) -> float:
        n = min(len(x), len(y))
        if n < 2:
            return 0.0
        x, y = x[:n], y[:n]
        mx, my = sum(x) / n, sum(y) / n
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        dx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
        dy = math.sqrt(sum((yi - my) ** 2 for yi in y))
        return round(num / (dx * dy), 4) if dx > 0 and dy > 0 else 0.0

    def save_result(self, result: dict):
        self._results.append(result)

    def get_results(self) -> List[dict]:
        return list(self._results)
