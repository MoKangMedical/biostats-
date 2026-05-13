"""多变量分析 — 多元统计分析方法"""

from typing import Dict, List, Optional, Tuple
import math


class MultivariateAnalysis:
    """多变量统计分析"""

    def __init__(self):
        self._results: List[dict] = []

    def multiple_regression(self, X: List[List[float]], y: List[float]) -> dict:
        n = len(y)
        p = len(X[0]) if X else 0
        if n < p + 2:
            return {"error": f"样本量不足，需要至少{p+2}个观测"}
        X_aug = [[1.0] + row for row in X]
        XtX = self._mat_mul(self._transpose(X_aug), X_aug)
        Xty = self._mat_vec_mul(self._transpose(X_aug), y)
        try:
            beta = self._solve(XtX, Xty)
        except Exception:
            return {"error": "矩阵求解失败，可能存在多重共线性"}
        y_hat = self._mat_vec_mul(X_aug, beta)
        residuals = [yi - yi_hat for yi, yi_hat in zip(y, y_hat)]
        ss_res = sum(r ** 2 for r in residuals)
        y_mean = sum(y) / n
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        adj_r2 = 1 - (1 - r_squared) * (n - 1) / (n - p - 1) if n > p + 1 else 0
        mse = ss_res / (n - p - 1) if n > p + 1 else 0
        return {
            "coefficients": [round(b, 4) for b in beta],
            "r_squared": round(r_squared, 4), "adj_r_squared": round(adj_r2, 4),
            "mse": round(mse, 4), "n": n, "p_predictors": p,
            "residuals": [round(r, 4) for r in residuals[:10]],
        }

    def pca(self, data: List[List[float]], n_components: int = 2) -> dict:
        if not data or not data[0]:
            return {"error": "数据为空"}
        n = len(data)
        p = len(data[0])
        means = [sum(row[j] for row in data) / n for j in range(p)]
        centered = [[row[j] - means[j] for j in range(p)] for row in data]
        cov = [[0.0] * p for _ in range(p)]
        for i in range(p):
            for j in range(p):
                cov[i][j] = sum(centered[k][i] * centered[k][j] for k in range(n)) / (n - 1)
        total_var = sum(cov[i][i] for i in range(p))
        eigenvals = [max(0.0, cov[i][i]) for i in range(p)]
        eigenvals.sort(reverse=True)
        explained = [round(ev / total_var * 100, 2) if total_var > 0 else 0 for ev in eigenvals[:n_components]]
        return {
            "n_components": n_components, "explained_variance_pct": explained,
            "total_variance_explained": round(sum(explained), 2),
            "original_features": p, "observations": n,
        }

    def mahalanobis_distance(self, x: List[float], mean: List[float], cov_inv: List[List[float]]) -> float:
        diff = [xi - mi for xi, mi in zip(x, mean)]
        temp = [sum(cov_inv[i][j] * diff[j] for j in range(len(diff))) for i in range(len(diff))]
        d_sq = sum(diff[i] * temp[i] for i in range(len(diff)))
        return round(math.sqrt(max(0, d_sq)), 4)

    def discriminant_analysis(self, group1: List[List[float]], group2: List[List[float]]) -> dict:
        if not group1 or not group2:
            return {"error": "需要两个非空组"}
        p = len(group1[0])
        n1, n2 = len(group1), len(group2)
        mean1 = [sum(row[j] for row in group1) / n1 for j in range(p)]
        mean2 = [sum(row[j] for row in group2) / n2 for j in range(p)]
        diff = [mean1[j] - mean2[j] for j in range(p)]
        return {
            "group1_mean": [round(m, 4) for m in mean1],
            "group2_mean": [round(m, 4) for m in mean2],
            "discriminant_weights": [round(d, 4) for d in diff],
            "n1": n1, "n2": n2, "features": p,
        }

    def cluster_distances(self, data: List[List[float]], metric: str = "euclidean") -> List[List[float]]:
        n = len(data)
        dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if metric == "euclidean":
                    d = math.sqrt(sum((data[i][k] - data[j][k]) ** 2 for k in range(len(data[i]))))
                elif metric == "manhattan":
                    d = sum(abs(data[i][k] - data[j][k]) for k in range(len(data[i])))
                else:
                    d = 0.0
                dist[i][j] = dist[j][i] = round(d, 4)
        return dist

    def _transpose(self, m: List[List[float]]) -> List[List[float]]:
        return [[m[i][j] for i in range(len(m))] for j in range(len(m[0]))]

    def _mat_mul(self, a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        rows, cols, inner = len(a), len(b[0]), len(b)
        return [[sum(a[i][k] * b[k][j] for k in range(inner)) for j in range(cols)] for i in range(rows)]

    def _mat_vec_mul(self, m: List[List[float]], v: List[float]) -> List[float]:
        return [sum(m[i][j] * v[j] for j in range(len(v))) for i in range(len(m))]

    def _solve(self, A: List[List[float]], b: List[float]) -> List[float]:
        n = len(b)
        aug = [row[:] + [bi] for row, bi in zip(A, b)]
        for col in range(n):
            max_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
            aug[col], aug[max_row] = aug[max_row], aug[col]
            pivot = aug[col][col]
            if abs(pivot) < 1e-12:
                raise ValueError("Singular matrix")
            for j in range(col, n + 1):
                aug[col][j] /= pivot
            for row in range(n):
                if row != col:
                    factor = aug[row][col]
                    for j in range(col, n + 1):
                        aug[row][j] -= factor * aug[col][j]
        return [aug[i][n] for i in range(n)]

    def save_result(self, result: dict):
        self._results.append(result)

    def get_results(self) -> List[dict]:
        return list(self._results)
