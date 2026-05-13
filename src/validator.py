"""数据验证 — Biostats数据验证"""

from typing import Any, Dict, List, Tuple
import re


class Validator:
    """Biostats数据验证器"""

    VALID_TESTS = ["t_test", "chi_square", "anova", "mann_whitney", "wilcoxon",
                   "fisher", "kruskal_wallis", "friedman"]
    VALID_DESIGNS = ["parallel", "crossover", "factorial", "cluster"]
    VALID_ENDPOINTS = ["primary", "secondary", "safety"]

    def validate_numeric_vector(self, data: Any) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(data, (list, tuple)):
            errors.append("数据必须是列表或元组")
            return False, errors
        if len(data) == 0:
            errors.append("数据不能为空")
            return False, errors
        for i, v in enumerate(data):
            if not isinstance(v, (int, float)):
                errors.append(f"索引{i}处的值不是数字: {v}")
        return len(errors) == 0, errors

    def validate_sample_size(self, n: int) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(n, int) or n < 1:
            errors.append("样本量必须是正整数")
        if n > 1000000:
            errors.append("样本量过大")
        return len(errors) == 0, errors

    def validate_probability(self, p: float, name: str = "概率") -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(p, (int, float)):
            errors.append(f"{name}必须是数字")
        elif p < 0 or p > 1:
            errors.append(f"{name}必须在0-1之间")
        return len(errors) == 0, errors

    def validate_effect_size(self, es: float) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(es, (int, float)):
            errors.append("效应量必须是数字")
        elif abs(es) > 10:
            errors.append("效应量异常大")
        return len(errors) == 0, errors

    def validate_survival_data(self, times: List[float], events: List[int]) -> Tuple[bool, List[str]]:
        errors = []
        if len(times) != len(events):
            errors.append("时间与事件数组长度不一致")
        if any(t < 0 for t in times):
            errors.append("生存时间不能为负")
        if any(e not in (0, 1) for e in events):
            errors.append("事件指标只能为0或1")
        return len(errors) == 0, errors

    def validate_contingency_table(self, table: List[List[int]]) -> Tuple[bool, List[str]]:
        errors = []
        if not table or not table[0]:
            errors.append("列联表不能为空")
            return False, errors
        cols = len(table[0])
        for i, row in enumerate(table):
            if len(row) != cols:
                errors.append(f"第{i}行列数不一致")
            if any(v < 0 for v in row):
                errors.append(f"第{i}行包含负值")
        return len(errors) == 0, errors

    def validate_design(self, design: str) -> Tuple[bool, List[str]]:
        errors = []
        if design not in self.VALID_DESIGNS:
            errors.append(f"无效的试验设计: {design}，有效值: {self.VALID_DESIGNS}")
        return len(errors) == 0, errors

    def validate_alpha(self, alpha: float) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(alpha, (int, float)):
            errors.append("alpha必须是数字")
        elif alpha <= 0 or alpha >= 1:
            errors.append("alpha必须在0和1之间")
        return len(errors) == 0, errors

    def validate_time_series(self, series: List[float], min_length: int = 2) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(series, (list, tuple)):
            errors.append("时间序列必须是列表")
            return False, errors
        if len(series) < min_length:
            errors.append(f"时间序列至少需要{min_length}个数据点")
        return len(errors) == 0, errors

    def validate_groups(self, groups: List[List[float]], min_groups: int = 2) -> Tuple[bool, List[str]]:
        errors = []
        if len(groups) < min_groups:
            errors.append(f"至少需要{min_groups}个组")
        for i, g in enumerate(groups):
            if len(g) == 0:
                errors.append(f"第{i}组为空")
        return len(errors) == 0, errors

    def batch_validate(self, items: List[dict], validator_name: str) -> List[dict]:
        fn = getattr(self, validator_name, None)
        if not fn:
            return [{"valid": False, "error": f"未知验证器: {validator_name}"}]
        results = []
        for item in items:
            valid, errors = fn(**item) if isinstance(item, dict) else fn(item)
            results.append({"valid": valid, "errors": errors})
        return results
