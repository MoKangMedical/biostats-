"""Bootstrap方法 — 非参数自助法"""

from typing import Dict, List, Optional, Callable
import math
import random


class Bootstrap:
    """Bootstrap重抽样方法"""

    def __init__(self, seed: int = None):
        self._results: List[dict] = []
        if seed is not None:
            random.seed(seed)

    def resample(self, data: List[float], n_bootstrap: int = 1000) -> List[List[float]]:
        n = len(data)
        return [random.choices(data, k=n) for _ in range(n_bootstrap)]

    def bootstrap_mean(self, data: List[float], n_bootstrap: int = 1000,
                       alpha: float = 0.05) -> dict:
        if len(data) < 2:
            return {"error": "需要至少2个数据点"}
        means = [sum(random.choices(data, k=len(data))) / len(data) for _ in range(n_bootstrap)]
        means.sort()
        original_mean = sum(data) / len(data)
        lower_idx = int(n_bootstrap * alpha / 2)
        upper_idx = int(n_bootstrap * (1 - alpha / 2))
        return {
            "statistic": "mean", "original": round(original_mean, 4),
            "bootstrap_mean": round(sum(means) / len(means), 4),
            "bootstrap_se": round(math.sqrt(sum((m - sum(means)/len(means))**2 for m in means) / (len(means)-1)), 4),
            "ci_lower": round(means[lower_idx], 4), "ci_upper": round(means[min(upper_idx, len(means)-1)], 4),
            "n_bootstrap": n_bootstrap, "alpha": alpha,
        }

    def bootstrap_median(self, data: List[float], n_bootstrap: int = 1000,
                         alpha: float = 0.05) -> dict:
        n = len(data)
        medians = []
        for _ in range(n_bootstrap):
            sample = sorted(random.choices(data, k=n))
            mid = n // 2
            med = (sample[mid] + sample[mid - 1]) / 2 if n % 2 == 0 else sample[mid]
            medians.append(med)
        medians.sort()
        original = sorted(data)
        orig_med = (original[n // 2] + original[n // 2 - 1]) / 2 if n % 2 == 0 else original[n // 2]
        lower_idx = int(n_bootstrap * alpha / 2)
        upper_idx = int(n_bootstrap * (1 - alpha / 2))
        return {"statistic": "median", "original": round(orig_med, 4),
                "ci_lower": round(medians[lower_idx], 4),
                "ci_upper": round(medians[min(upper_idx, len(medians)-1)], 4),
                "n_bootstrap": n_bootstrap}

    def bootstrap_std(self, data: List[float], n_bootstrap: int = 1000,
                      alpha: float = 0.05) -> dict:
        n = len(data)
        stds = []
        for _ in range(n_bootstrap):
            sample = random.choices(data, k=n)
            m = sum(sample) / n
            v = sum((x - m) ** 2 for x in sample) / (n - 1)
            stds.append(math.sqrt(v))
        stds.sort()
        original_mean = sum(data) / n
        original_std = math.sqrt(sum((x - original_mean) ** 2 for x in data) / (n - 1))
        lower_idx = int(n_bootstrap * alpha / 2)
        upper_idx = int(n_bootstrap * (1 - alpha / 2))
        return {"statistic": "std", "original": round(original_std, 4),
                "ci_lower": round(stds[lower_idx], 4),
                "ci_upper": round(stds[min(upper_idx, len(stds)-1)], 4),
                "n_bootstrap": n_bootstrap}

    def bootstrap_difference(self, group1: List[float], group2: List[float],
                             n_bootstrap: int = 1000, alpha: float = 0.05) -> dict:
        n1, n2 = len(group1), len(group2)
        diffs = []
        for _ in range(n_bootstrap):
            s1 = random.choices(group1, k=n1)
            s2 = random.choices(group2, k=n2)
            diffs.append(sum(s1) / n1 - sum(s2) / n2)
        diffs.sort()
        orig_diff = sum(group1) / n1 - sum(group2) / n2
        lower_idx = int(n_bootstrap * alpha / 2)
        upper_idx = int(n_bootstrap * (1 - alpha / 2))
        return {"statistic": "mean_difference", "original": round(orig_diff, 4),
                "ci_lower": round(diffs[lower_idx], 4),
                "ci_upper": round(diffs[min(upper_idx, len(diffs)-1)], 4),
                "significant": diffs[lower_idx] > 0 or diffs[min(upper_idx, len(diffs)-1)] < 0,
                "n_bootstrap": n_bootstrap}

    def bootstrap_correlation(self, x: List[float], y: List[float],
                              n_bootstrap: int = 1000, alpha: float = 0.05) -> dict:
        n = min(len(x), len(y))
        cors = []
        for _ in range(n_bootstrap):
            idx = [random.randint(0, n - 1) for _ in range(n)]
            sx = [x[i] for i in idx]
            sy = [y[i] for i in idx]
            cors.append(self._pearson(sx, sy))
        cors.sort()
        orig = self._pearson(x[:n], y[:n])
        lower_idx = int(n_bootstrap * alpha / 2)
        upper_idx = int(n_bootstrap * (1 - alpha / 2))
        return {"statistic": "correlation", "original": round(orig, 4),
                "ci_lower": round(cors[lower_idx], 4),
                "ci_upper": round(cors[min(upper_idx, len(cors)-1)], 4),
                "n_bootstrap": n_bootstrap}

    def bootstrap_percentile(self, bootstrap_stats: List[float], alpha: float = 0.05) -> dict:
        s = sorted(bootstrap_stats)
        n = len(s)
        lower = s[int(n * alpha / 2)]
        upper = s[int(n * (1 - alpha / 2))]
        return {"ci_lower": round(lower, 4), "ci_upper": round(upper, 4), "alpha": alpha}

    def _pearson(self, x: List[float], y: List[float]) -> float:
        n = len(x)
        mx, my = sum(x) / n, sum(y) / n
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        dx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
        dy = math.sqrt(sum((yi - my) ** 2 for yi in y))
        return num / (dx * dy) if dx > 0 and dy > 0 else 0.0

    def save_result(self, result: dict):
        self._results.append(result)

    def get_results(self) -> List[dict]:
        return list(self._results)
