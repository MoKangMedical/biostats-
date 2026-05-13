"""倾向性评分 — 倾向性评分匹配与加权"""

from typing import Dict, List, Optional, Tuple
import math
import random


class PropensityScore:
    """倾向性评分方法"""

    def __init__(self):
        self._results: List[dict] = []

    def logistic_predict(self, X: List[List[float]], treatment: List[int]) -> List[float]:
        n = len(treatment)
        p = len(X[0]) if X else 0
        if n < p + 2:
            return [0.5] * n
        means = [sum(row[j] for row in X) / n for j in range(p)]
        sds = [max(0.001, math.sqrt(sum((row[j] - means[j]) ** 2 for row in X) / (n - 1))) for j in range(p)]
        scores = []
        for i in range(n):
            z = sum((X[i][j] - means[j]) / sds[j] for j in range(p)) / p
            z = max(-10, min(10, z))
            score = 1.0 / (1.0 + math.exp(-z))
            scores.append(round(score, 4))
        return scores

    def match_nearest(self, scores: List[float], treatment: List[int], caliper: float = 0.2) -> dict:
        treated = [(i, scores[i]) for i in range(len(scores)) if treatment[i] == 1]
        control = [(i, scores[i]) for i in range(len(scores)) if treatment[i] == 0]
        matches = []
        used_control = set()
        for ti, ts in treated:
            best_j, best_d = None, float('inf')
            for ci, cs in control:
                if ci in used_control:
                    continue
                d = abs(ts - cs)
                if d < best_d and d <= caliper:
                    best_d = d
                    best_j = ci
            if best_j is not None:
                matches.append({"treated": ti, "control": best_j, "distance": round(best_d, 4)})
                used_control.add(best_j)
        return {
            "n_matches": len(matches), "n_treated": len(treated), "n_control": len(control),
            "match_rate": round(len(matches) / len(treated), 4) if treated else 0,
            "matches": matches[:20],
        }

    def match_ratio(self, scores: List[float], treatment: List[int], ratio: int = 2) -> dict:
        treated = [(i, scores[i]) for i in range(len(scores)) if treatment[i] == 1]
        control = [(i, scores[i]) for i in range(len(scores)) if treatment[i] == 0]
        control_sorted = sorted(control, key=lambda x: x[1])
        matches = []
        used = set()
        for ti, ts in treated:
            candidates = [(ci, cs, abs(ts - cs)) for ci, cs in control_sorted if ci not in used]
            candidates.sort(key=lambda x: x[2])
            matched = candidates[:ratio]
            for ci, cs, d in matched:
                matches.append({"treated": ti, "control": ci, "distance": round(d, 4)})
                used.add(ci)
        return {"n_matches": len(matches), "ratio": ratio,
                "n_treated": len(treated), "matches": matches[:30]}

    def iptw_weights(self, scores: List[float], treatment: List[int]) -> List[float]:
        weights = []
        for i in range(len(scores)):
            s = max(0.01, min(0.99, scores[i]))
            if treatment[i] == 1:
                w = 1.0 / s
            else:
                w = 1.0 / (1.0 - s)
            weights.append(round(w, 4))
        return weights

    def assess_balance(self, X: List[List[float]], treatment: List[int],
                       weights: List[float] = None) -> dict:
        treated_idx = [i for i in range(len(treatment)) if treatment[i] == 1]
        control_idx = [i for i in range(len(treatment)) if treatment[i] == 0]
        p = len(X[0]) if X else 0
        balance = []
        for j in range(p):
            t_vals = [X[i][j] for i in treated_idx]
            c_vals = [X[i][j] for i in control_idx]
            t_mean = sum(t_vals) / len(t_vals) if t_vals else 0
            c_mean = sum(c_vals) / len(c_vals) if c_vals else 0
            t_var = sum((v - t_mean) ** 2 for v in t_vals) / max(1, len(t_vals) - 1)
            c_var = sum((v - c_mean) ** 2 for v in c_vals) / max(1, len(c_vals) - 1)
            pooled_sd = math.sqrt((t_var + c_var) / 2) if (t_var + c_var) > 0 else 1
            smd = abs(t_mean - c_mean) / pooled_sd
            balance.append({"feature": j, "treated_mean": round(t_mean, 4),
                            "control_mean": round(c_mean, 4), "smd": round(smd, 4),
                            "balanced": smd < 0.1})
        balanced_count = sum(1 for b in balance if b["balanced"])
        return {"features": balance, "n_balanced": balanced_count,
                "n_total": len(balance), "overall_balanced": balanced_count == len(balance)}

    def outcome_analysis(self, outcome: List[float], treatment: List[int],
                         weights: List[float] = None) -> dict:
        treated = [i for i in range(len(treatment)) if treatment[i] == 1]
        control = [i for i in range(len(treatment)) if treatment[i] == 0]
        if weights:
            t_outcome = sum(outcome[i] * weights[i] for i in treated) / sum(weights[i] for i in treated) if treated else 0
            c_outcome = sum(outcome[i] * weights[i] for i in control) / sum(weights[i] for i in control) if control else 0
        else:
            t_outcome = sum(outcome[i] for i in treated) / len(treated) if treated else 0
            c_outcome = sum(outcome[i] for i in control) / len(control) if control else 0
        ate = t_outcome - c_outcome
        return {"treated_mean": round(t_outcome, 4), "control_mean": round(c_outcome, 4),
                "ate": round(ate, 4), "n_treated": len(treated), "n_control": len(control)}

    def save_result(self, result: dict):
        self._results.append(result)

    def get_results(self) -> List[dict]:
        return list(self._results)
