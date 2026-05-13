"""Meta分析 — 系统综述与Meta分析方法"""

from typing import Dict, List, Optional, Tuple
import math


class MetaAnalysis:
    """Meta分析方法集合"""

    def __init__(self):
        self._analyses: List[dict] = []

    def fixed_effect_mean_diff(self, effects: List[float], variances: List[float]) -> dict:
        if len(effects) != len(variances) or len(effects) < 2:
            return {"error": "需要至少2个研究"}
        weights = [1.0 / v if v > 0 else 0.0 for v in variances]
        total_w = sum(weights)
        if total_w == 0:
            return {"error": "权重总和为零"}
        pooled = sum(w * e for w, e in zip(weights, effects)) / total_w
        se = math.sqrt(1.0 / total_w)
        z = pooled / se if se > 0 else 0
        ci_lower = pooled - 1.96 * se
        ci_upper = pooled + 1.96 * se
        return {
            "method": "fixed_effect", "pooled_effect": round(pooled, 4),
            "se": round(se, 4), "z_statistic": round(z, 4),
            "ci_lower": round(ci_lower, 4), "ci_upper": round(ci_upper, 4),
            "significant": abs(z) > 1.96, "k_studies": len(effects),
            "weights": [round(w / total_w * 100, 2) for w in weights],
        }

    def random_effect_mean_diff(self, effects: List[float], variances: List[float]) -> dict:
        if len(effects) != len(variances) or len(effects) < 3:
            return {"error": "随机效应模型需要至少3个研究"}
        k = len(effects)
        weights_fe = [1.0 / v if v > 0 else 0.0 for v in variances]
        w_fe_sum = sum(weights_fe)
        if w_fe_sum == 0:
            return {"error": "权重为零"}
        pooled_fe = sum(w * e for w, e in zip(weights_fe, effects)) / w_fe_sum
        Q = sum(w * (e - pooled_fe) ** 2 for w, e in zip(weights_fe, effects))
        df = k - 1
        C = w_fe_sum - sum(w ** 2 for w in weights_fe) / w_fe_sum
        tau2 = max(0, (Q - df) / C) if C > 0 else 0
        weights_re = [1.0 / (v + tau2) if (v + tau2) > 0 else 0.0 for v in variances]
        w_re_sum = sum(weights_re)
        pooled_re = sum(w * e for w, e in zip(weights_re, effects)) / w_re_sum if w_re_sum > 0 else 0
        se_re = math.sqrt(1.0 / w_re_sum) if w_re_sum > 0 else 0
        I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0
        return {
            "method": "random_effect", "pooled_effect": round(pooled_re, 4),
            "se": round(se_re, 4), "ci_lower": round(pooled_re - 1.96 * se_re, 4),
            "ci_upper": round(pooled_re + 1.96 * se_re, 4), "tau_squared": round(tau2, 4),
            "Q_statistic": round(Q, 4), "I_squared": round(I2, 2),
            "k_studies": k, "significant": abs(pooled_re / se_re) > 1.96 if se_re > 0 else False,
        }

    def heterogeneity_test(self, effects: List[float], variances: List[float]) -> dict:
        k = len(effects)
        if k < 2:
            return {"error": "需要至少2个研究"}
        weights = [1.0 / v if v > 0 else 0.0 for v in variances]
        w_sum = sum(weights)
        pooled = sum(w * e for w, e in zip(weights, effects)) / w_sum if w_sum > 0 else 0
        Q = sum(w * (e - pooled) ** 2 for w, e in zip(weights, effects))
        df = k - 1
        I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0
        if I2 < 25:
            level = "低异质性"
        elif I2 < 75:
            level = "中等异质性"
        else:
            level = "高异质性"
        return {"Q": round(Q, 4), "df": df, "I_squared": round(I2, 2), "level": level, "k": k}

    def fixed_effect_or(self, events_t: List[int], total_t: List[int],
                        events_c: List[int], total_c: List[int]) -> dict:
        k = len(events_t)
        effects = []
        variances = []
        for i in range(k):
            a, n1 = events_t[i], total_t[i]
            c, n2 = events_c[i], total_c[i]
            b, d = n1 - a, n2 - c
            if min(a, b, c, d) == 0:
                a += 0.5; b += 0.5; c += 0.5; d += 0.5
            log_or = math.log((a * d) / (b * c))
            var = 1 / a + 1 / b + 1 / c + 1 / d
            effects.append(log_or)
            variances.append(var)
        result = self.fixed_effect_mean_diff(effects, variances)
        result["pooled_or"] = round(math.exp(result["pooled_effect"]), 4)
        result["or_ci_lower"] = round(math.exp(result["ci_lower"]), 4)
        result["or_ci_upper"] = round(math.exp(result["ci_upper"]), 4)
        return result

    def funnel_plot_data(self, effects: List[float], variances: List[float]) -> dict:
        se = [math.sqrt(v) for v in variances]
        return {"effects": effects, "standard_errors": se,
                "mean_effect": round(sum(effects) / len(effects), 4) if effects else 0}

    def leave_one_out(self, effects: List[float], variances: List[float]) -> List[dict]:
        results = []
        for i in range(len(effects)):
            sub_e = effects[:i] + effects[i + 1:]
            sub_v = variances[:i] + variances[i + 1:]
            r = self.fixed_effect_mean_diff(sub_e, sub_v)
            r["excluded_study"] = i + 1
            results.append(r)
        return results

    def save_analysis(self, result: dict):
        self._analyses.append(result)

    def get_analyses(self) -> List[dict]:
        return list(self._analyses)
