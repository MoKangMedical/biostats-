"""非参数检验 — 非参数统计方法"""

from typing import Dict, List, Optional
import math


class NonParametricTests:
    """非参数检验方法集合"""

    def __init__(self):
        self._results: List[dict] = []

    def mann_whitney_u(self, group1: List[float], group2: List[float]) -> dict:
        n1, n2 = len(group1), len(group2)
        all_vals = [(v, 1) for v in group1] + [(v, 2) for v in group2]
        all_vals.sort(key=lambda x: x[0])
        ranks = list(range(1, len(all_vals) + 1))
        for i in range(len(all_vals)):
            j = i
            while j < len(all_vals) and all_vals[j][0] == all_vals[i][0]:
                j += 1
            avg_rank = sum(ranks[i:j]) / (j - i)
            for k in range(i, j):
                ranks[k] = avg_rank
            i = j - 1
        r1 = sum(ranks[i] for i in range(len(all_vals)) if all_vals[i][1] == 1)
        u1 = r1 - n1 * (n1 + 1) / 2
        u2 = n1 * n2 - u1
        u_stat = min(u1, u2)
        mu = n1 * n2 / 2
        sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        z = (u_stat - mu) / sigma if sigma > 0 else 0
        return {"U_statistic": round(u_stat, 4), "U1": round(u1, 4), "U2": round(u2, 4),
                "z": round(z, 4), "n1": n1, "n2": n2,
                "significant": abs(z) > 1.96}

    def wilcoxon_signed_rank(self, x: List[float], y: List[float]) -> dict:
        if len(x) != len(y):
            return {"error": "两组数据长度必须相等"}
        diffs = [(x[i] - y[i], i) for i in range(len(x)) if x[i] != y[i]]
        if not diffs:
            return {"error": "所有差值为零"}
        abs_diffs = sorted([(abs(d), i) for d, i in diffs])
        ranks = list(range(1, len(abs_diffs) + 1))
        for i in range(len(abs_diffs)):
            j = i
            while j < len(abs_diffs) and abs_diffs[j][0] == abs_diffs[i][0]:
                j += 1
            avg = sum(ranks[i:j]) / (j - i)
            for k in range(i, j):
                ranks[k] = avg
            i = j - 1
        w_plus = sum(ranks[i] for i in range(len(abs_diffs))
                     if diffs[abs_diffs[i][1]][0] > 0)
        w_minus = sum(ranks[i] for i in range(len(abs_diffs))
                      if diffs[abs_diffs[i][1]][0] < 0)
        w_stat = min(w_plus, w_minus)
        n = len(abs_diffs)
        mu = n * (n + 1) / 4
        sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
        z = (w_stat - mu) / sigma if sigma > 0 else 0
        return {"W_statistic": round(w_stat, 4), "W_plus": round(w_plus, 4),
                "W_minus": round(w_minus, 4), "z": round(z, 4), "n": n,
                "significant": abs(z) > 1.96}

    def kruskal_wallis(self, groups: List[List[float]]) -> dict:
        k = len(groups)
        if k < 2:
            return {"error": "至少需要2个组"}
        all_vals = []
        for g_idx, group in enumerate(groups):
            for v in group:
                all_vals.append((v, g_idx))
        all_vals.sort(key=lambda x: x[0])
        n = len(all_vals)
        ranks = list(range(1, n + 1))
        for i in range(n):
            j = i
            while j < n and all_vals[j][0] == all_vals[i][0]:
                j += 1
            avg = sum(ranks[i:j]) / (j - i)
            for m in range(i, j):
                ranks[m] = avg
            i = j - 1
        rank_sums = [0.0] * k
        group_sizes = [0] * k
        for i in range(n):
            rank_sums[all_vals[i][1]] += ranks[i]
            group_sizes[all_vals[i][1]] += 1
        H = 12 / (n * (n + 1)) * sum(rs ** 2 / gs for rs, gs in zip(rank_sums, group_sizes)) - 3 * (n + 1)
        return {"H_statistic": round(H, 4), "df": k - 1, "k_groups": k,
                "group_sizes": group_sizes, "significant": H > 5.991}

    def friedman_test(self, data: List[List[float]]) -> dict:
        k = len(data)
        if k < 3:
            return {"error": "至少需要3个处理组"}
        n = min(len(g) for g in data)
        rank_sums = [0.0] * k
        for i in range(n):
            row = [(data[j][i], j) for j in range(k)]
            row.sort()
            ranks = list(range(1, k + 1))
            for m in range(k):
                j_idx = row[m][1]
                rank_sums[j_idx] += ranks[m]
        chi2 = 12 / (n * k * (k + 1)) * sum(rs ** 2 for rs in rank_sums) - 3 * n * (k + 1)
        return {"chi2": round(chi2, 4), "df": k - 1, "n": n, "k": k,
                "significant": chi2 > 5.991}

    def chi_square_test(self, observed: List[List[int]]) -> dict:
        rows = len(observed)
        cols = len(observed[0]) if rows > 0 else 0
        row_totals = [sum(row) for row in observed]
        col_totals = [sum(observed[i][j] for i in range(rows)) for j in range(cols)]
        grand_total = sum(row_totals)
        if grand_total == 0:
            return {"error": "列联表总和为零"}
        chi2 = 0.0
        for i in range(rows):
            for j in range(cols):
                expected = row_totals[i] * col_totals[j] / grand_total
                if expected > 0:
                    chi2 += (observed[i][j] - expected) ** 2 / expected
        df = (rows - 1) * (cols - 1)
        return {"chi_square": round(chi2, 4), "df": df, "n": grand_total,
                "significant": chi2 > 3.841 if df == 1 else chi2 > 5.991}

    def fisher_exact(self, table: List[List[int]]) -> dict:
        a, b = table[0][0], table[0][1]
        c, d = table[1][0], table[1][1]
        n = a + b + c + d
        if min(a, b, c, d) == 0:
            odds_ratio = 0
        else:
            odds_ratio = (a * d) / (b * c) if (b * c) > 0 else float('inf')
        return {"odds_ratio": round(odds_ratio, 4), "table": table, "n": n,
                "exact_test": True}

    def save_result(self, result: dict):
        self._results.append(result)

    def get_results(self) -> List[dict]:
        return list(self._results)
