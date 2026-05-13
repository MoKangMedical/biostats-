"""诊断试验评价 — 诊断准确性评估"""

from typing import Dict, List, Optional, Tuple
import math


class DiagnosticTest:
    """诊断试验评价方法"""

    def __init__(self):
        self._studies: List[dict] = []

    def create_2x2(self, tp: int, fp: int, fn: int, tn: int) -> dict:
        n = tp + fp + fn + tn
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0
        accuracy = (tp + tn) / n if n > 0 else 0
        prevalence = (tp + fn) / n if n > 0 else 0
        lr_plus = sensitivity / (1 - specificity) if (1 - specificity) > 0 else float('inf')
        lr_minus = (1 - sensitivity) / specificity if specificity > 0 else float('inf')
        youden = sensitivity + specificity - 1
        f1 = 2 * ppv * sensitivity / (ppv + sensitivity) if (ppv + sensitivity) > 0 else 0
        result = {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn, "n": n,
            "sensitivity": round(sensitivity, 4), "specificity": round(specificity, 4),
            "ppv": round(ppv, 4), "npv": round(npv, 4),
            "accuracy": round(accuracy, 4), "prevalence": round(prevalence, 4),
            "lr_positive": round(lr_plus, 4), "lr_negative": round(lr_minus, 4),
            "youden_index": round(youden, 4), "f1_score": round(f1, 4),
        }
        self._studies.append(result)
        return result

    def sensitivity_ci(self, tp: int, fn: int, alpha: float = 0.05) -> dict:
        n = tp + fn
        if n == 0:
            return {"error": "无阳性病例"}
        se = tp / n
        z = 1.96 if alpha == 0.05 else 2.576
        margin = z * math.sqrt(se * (1 - se) / n) if n > 0 else 0
        return {
            "sensitivity": round(se, 4),
            "ci_lower": round(max(0, se - margin), 4),
            "ci_upper": round(min(1, se + margin), 4),
            "n_positive": n, "alpha": alpha,
        }

    def specificity_ci(self, tn: int, fp: int, alpha: float = 0.05) -> dict:
        n = tn + fp
        if n == 0:
            return {"error": "无阴性病例"}
        sp = tn / n
        z = 1.96 if alpha == 0.05 else 2.576
        margin = z * math.sqrt(sp * (1 - sp) / n) if n > 0 else 0
        return {
            "specificity": round(sp, 4),
            "ci_lower": round(max(0, sp - margin), 4),
            "ci_upper": round(min(1, sp + margin), 4),
            "n_negative": n, "alpha": alpha,
        }

    def roc_auc(self, sensitivities: List[float], specificities: List[float]) -> dict:
        if len(sensitivities) != len(specificities) or len(sensitivities) < 2:
            return {"error": "需要至少2个阈值点"}
        fpr = [1 - sp for sp in specificities]
        auc = 0.0
        for i in range(1, len(fpr)):
            auc += (fpr[i] - fpr[i - 1]) * (sensitivities[i] + sensitivities[i - 1]) / 2
        auc = abs(auc)
        if auc >= 0.9:
            interpretation = "优秀"
        elif auc >= 0.8:
            interpretation = "良好"
        elif auc >= 0.7:
            interpretation = "一般"
        else:
            interpretation = "较差"
        return {"auc": round(auc, 4), "interpretation": interpretation,
                "n_thresholds": len(sensitivities)}

    def likelihood_ratio_posterior(self, pre_test_prob: float, lr: float) -> dict:
        pre_odds = pre_test_prob / (1 - pre_test_prob) if pre_test_prob < 1 else float('inf')
        post_odds = pre_odds * lr
        post_prob = post_odds / (1 + post_odds) if post_odds != float('inf') else 1.0
        return {
            "pre_test_probability": round(pre_test_prob, 4),
            "likelihood_ratio": round(lr, 4),
            "post_test_probability": round(post_prob, 4),
            "change": round(post_prob - pre_test_prob, 4),
        }

    def number_needed_to_diagnose(self, sensitivity: float, specificity: float, prevalence: float) -> dict:
        ppv = (sensitivity * prevalence) / (sensitivity * prevalence + (1 - specificity) * (1 - prevalence))
        npv = (specificity * (1 - prevalence)) / (specificity * (1 - prevalence) + (1 - sensitivity) * prevalence)
        nnd_pos = 1 / (ppv) if ppv > 0 else float('inf')
        nnd_neg = 1 / (npv) if npv > 0 else float('inf')
        return {"nnd_positive": round(nnd_pos, 2), "nnd_negative": round(nnd_neg, 2),
                "ppv": round(ppv, 4), "npv": round(npv, 4)}

    def compare_tests(self, test1: dict, test2: dict) -> dict:
        se_diff = test1.get("sensitivity", 0) - test2.get("sensitivity", 0)
        sp_diff = test1.get("specificity", 0) - test2.get("specificity", 0)
        return {
            "sensitivity_diff": round(se_diff, 4), "specificity_diff": round(sp_diff, 4),
            "test1_better_se": se_diff > 0, "test1_better_sp": sp_diff > 0,
        }

    def get_studies(self) -> List[dict]:
        return list(self._studies)
