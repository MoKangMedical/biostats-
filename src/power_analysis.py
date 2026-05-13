"""
Biostats — 样本量计算与功效分析模块

支持多种临床试验设计的样本量计算：
- 优效性检验 (Superiority)
- 非劣效性检验 (Non-inferiority)
- 等效性检验 (Equivalence)
- 单组/两组设计
- 连续/二分类/生存终点
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class PowerResult:
    """功效分析结果"""
    n_per_group: int
    total_n: int
    alpha: float
    power: float
    effect_size: float
    method: str
    design: str
    notes: str = ""

    def to_dict(self):
        return {
            "n_per_group": self.n_per_group,
            "total_n": self.total_n,
            "alpha": self.alpha,
            "power": self.power,
            "effect_size": self.effect_size,
            "method": self.method,
            "design": self.design,
            "notes": self.notes,
        }

    def summary(self) -> str:
        return (
            f"📊 样本量计算结果\n"
            f"   设计: {self.design}\n"
            f"   方法: {self.method}\n"
            f"   每组样本量: {self.n_per_group}\n"
            f"   总样本量: {self.total_n}\n"
            f"   α = {self.alpha}, Power = {self.power}\n"
            f"   效应量 = {self.effect_size}\n"
            f"   {self.notes}"
        )


# ── 正态分布分位数近似（避免scipy依赖）──────────────────────────────

def _qnorm(p: float) -> float:
    """标准正态分布分位数近似（Beasley-Springer-Moro算法）"""
    if p <= 0 or p >= 1:
        raise ValueError("p must be in (0, 1)")
    if p < 0.5:
        return -_qnorm(1 - p)

    t = math.sqrt(-2 * math.log(1 - p))
    # Rational approximation
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


def _zt(p: float, df: float) -> float:
    """t分布分位数近似（用于小样本）"""
    # 对于大df，近似正态
    z = _qnorm(p)
    if df > 30:
        return z
    # Cornish-Fisher展开
    g1 = (z ** 3 + z) / (4 * df)
    g2 = (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)
    return z + g1 + g2


# ── 两组连续变量 ──────────────────────────────────────────────────────

def sample_size_two_means(delta: float, sd: float = 1.0,
                          alpha: float = 0.05, power: float = 0.80,
                          ratio: float = 1.0,
                          alternative: str = "two-sided") -> PowerResult:
    """
    两独立样本均数比较的样本量

    Args:
        delta: 均数差值 (H1 - H0)
        sd: 合并标准差
        alpha: 显著性水平
        power: 检验效能 (1-β)
        ratio: n2/n1 分配比
        alternative: "two-sided" | "one-sided"
    """
    z_alpha = _qnorm(1 - alpha / 2) if alternative == "two-sided" else _qnorm(1 - alpha)
    z_beta = _qnorm(power)

    effect = delta / sd
    n1 = ((z_alpha + z_beta) ** 2 * (1 + 1 / ratio)) / (effect ** 2)
    n1 = math.ceil(n1)
    n2 = math.ceil(n1 * ratio)

    return PowerResult(
        n_per_group=n1,
        total_n=n1 + n2,
        alpha=alpha,
        power=power,
        effect_size=effect,
        method="两样本t检验",
        design="两组连续变量",
        notes=f"均数差={delta}, SD={sd}, 分配比={ratio}",
    )


# ── 两组比例 ──────────────────────────────────────────────────────────

def sample_size_two_proportions(p1: float, p2: float,
                                alpha: float = 0.05, power: float = 0.80,
                                ratio: float = 1.0,
                                alternative: str = "two-sided") -> PowerResult:
    """
    两独立样本比例比较的样本量

    Args:
        p1: 试验组比例
        p2: 对照组比例
        alpha: 显著性水平
        power: 检验效能
        ratio: n2/n1 分配比
        alternative: "two-sided" | "one-sided"
    """
    z_alpha = _qnorm(1 - alpha / 2) if alternative == "two-sided" else _qnorm(1 - alpha)
    z_beta = _qnorm(power)

    p_bar = (p1 + ratio * p2) / (1 + ratio)
    delta = abs(p1 - p2)

    n1_num = (z_alpha * math.sqrt(p_bar * (1 - p_bar) * (1 + 1 / ratio)) +
              z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / ratio)) ** 2
    n1 = math.ceil(n1_num / (delta ** 2))
    n2 = math.ceil(n1 * ratio)

    return PowerResult(
        n_per_group=n1,
        total_n=n1 + n2,
        alpha=alpha,
        power=power,
        effect_size=delta,
        method="两样本比例检验",
        design="两组二分类变量",
        notes=f"p1={p1}, p2={p2}, 差值={delta:.4f}",
    )


# ── 非劣效性检验 ──────────────────────────────────────────────────────

def sample_size_non_inferiority(delta: float, margin: float, sd: float = 1.0,
                                alpha: float = 0.05, power: float = 0.80,
                                ratio: float = 1.0) -> PowerResult:
    """
    非劣效性检验样本量

    Args:
        delta: 预期差值（试验组-对照组，通常≤0）
        margin: 非劣效界值（正值）
        sd: 合并标准差
        alpha: 显著性水平（单侧）
        power: 检验效能
        ratio: n2/n1 分配比
    """
    z_alpha = _qnorm(1 - alpha)  # 单侧
    z_beta = _qnorm(power)

    effect = (margin + delta) / sd
    n1 = ((z_alpha + z_beta) ** 2 * (1 + 1 / ratio)) / (effect ** 2)
    n1 = math.ceil(n1)
    n2 = math.ceil(n1 * ratio)

    return PowerResult(
        n_per_group=n1,
        total_n=n1 + n2,
        alpha=alpha,
        power=power,
        effect_size=effect,
        method="非劣效性检验",
        design="非劣效性设计",
        notes=f"非劣效界值={margin}, 预期差值={delta}, SD={sd}",
    )


# ── 等效性检验 ────────────────────────────────────────────────────────

def sample_size_equivalence(delta: float, margin: float, sd: float = 1.0,
                            alpha: float = 0.05, power: float = 0.80,
                            ratio: float = 1.0) -> PowerResult:
    """
    等效性检验样本量（双单侧检验 TOST）

    Args:
        delta: 预期差值（通常=0）
        margin: 等效界值
        sd: 合并标准差
        alpha: 显著性水平
        power: 检验效能
        ratio: n2/n1 分配比
    """
    z_alpha = _qnorm(1 - alpha)
    z_beta = _qnorm((1 + power) / 2)  # TOST功效

    effect = (margin - abs(delta)) / sd
    n1 = ((z_alpha + z_beta) ** 2 * (1 + 1 / ratio)) / (effect ** 2)
    n1 = math.ceil(n1)
    n2 = math.ceil(n1 * ratio)

    return PowerResult(
        n_per_group=n1,
        total_n=n1 + n2,
        alpha=alpha,
        power=power,
        effect_size=effect,
        method="等效性检验 (TOST)",
        design="等效性设计",
        notes=f"等效界值={margin}, 预期差值={delta}, SD={sd}",
    )


# ── 生存分析（Log-rank检验）──────────────────────────────────────────

def sample_size_survival(hr: float, p_event: float = 0.5,
                         alpha: float = 0.05, power: float = 0.80,
                         ratio: float = 1.0) -> PowerResult:
    """
    Log-rank检验样本量（基于事件数）

    Args:
        hr: 风险比 (Hazard Ratio)
        p_event: 预期事件率
        alpha: 显著性水平
        power: 检验效能
        ratio: n2/n1 分配比
    """
    z_alpha = _qnorm(1 - alpha / 2)
    z_beta = _qnorm(power)

    # Schoenfeld公式
    events = ((z_alpha + z_beta) ** 2 * (1 + ratio) ** 2) / (ratio * (math.log(hr)) ** 2)
    events = math.ceil(events)

    # 由事件数推算总样本量
    total_n = math.ceil(events / p_event)
    n1 = math.ceil(total_n / (1 + ratio))
    n2 = math.ceil(n1 * ratio)

    return PowerResult(
        n_per_group=n1,
        total_n=n1 + n2,
        alpha=alpha,
        power=power,
        effect_size=hr,
        method="Log-rank检验 (Schoenfeld)",
        design="生存分析",
        notes=f"HR={hr}, 所需事件数={events}, 预期事件率={p_event}",
    )


# ── 单组设计 ──────────────────────────────────────────────────────────

def sample_size_one_mean(delta: float, sd: float = 1.0,
                         alpha: float = 0.05, power: float = 0.80,
                         alternative: str = "two-sided") -> PowerResult:
    """单样本均数检验样本量"""
    z_alpha = _qnorm(1 - alpha / 2) if alternative == "two-sided" else _qnorm(1 - alpha)
    z_beta = _qnorm(power)

    n = math.ceil(((z_alpha + z_beta) * sd / delta) ** 2)

    return PowerResult(
        n_per_group=n,
        total_n=n,
        alpha=alpha,
        power=power,
        effect_size=delta / sd,
        method="单样本t检验",
        design="单组连续变量",
        notes=f"差值={delta}, SD={sd}",
    )


def sample_size_one_proportion(p0: float, p1: float,
                               alpha: float = 0.05, power: float = 0.80,
                               alternative: str = "two-sided") -> PowerResult:
    """单样本比例检验样本量"""
    z_alpha = _qnorm(1 - alpha / 2) if alternative == "two-sided" else _qnorm(1 - alpha)
    z_beta = _qnorm(power)

    n_num = (z_alpha * math.sqrt(p0 * (1 - p0)) +
             z_beta * math.sqrt(p1 * (1 - p1))) ** 2
    n = math.ceil(n_num / ((p1 - p0) ** 2))

    return PowerResult(
        n_per_group=n,
        total_n=n,
        alpha=alpha,
        power=power,
        effect_size=abs(p1 - p0),
        method="单样本比例检验",
        design="单组二分类变量",
        notes=f"H0: p={p0}, H1: p={p1}",
    )


# ── 功效计算（反向）──────────────────────────────────────────────────

def power_two_means(n: int, delta: float, sd: float = 1.0,
                    alpha: float = 0.05,
                    alternative: str = "two-sided") -> float:
    """给定样本量计算功效（两样本均数）"""
    z_alpha = _qnorm(1 - alpha / 2) if alternative == "two-sided" else _qnorm(1 - alpha)
    se = sd * math.sqrt(2 / n)
    z_power = delta / se - z_alpha
    # 标准正态CDF近似
    return 0.5 * (1 + math.erf(z_power / math.sqrt(2)))


def power_two_proportions(n: int, p1: float, p2: float,
                          alpha: float = 0.05,
                          alternative: str = "two-sided") -> float:
    """给定样本量计算功效（两样本比例）"""
    z_alpha = _qnorm(1 - alpha / 2) if alternative == "two-sided" else _qnorm(1 - alpha)
    se = math.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    z_power = abs(p1 - p2) / se - z_alpha
    return 0.5 * (1 + math.erf(z_power / math.sqrt(2)))


# ── 便捷函数 ──────────────────────────────────────────────────────────

def sample_size(effect_size: float = 0.5, alpha: float = 0.05,
                power: float = 0.80, design: str = "two_means",
                **kwargs) -> PowerResult:
    """
    通用样本量计算入口

    Args:
        effect_size: 效应量（Cohen's d 或比例差值）
        alpha: 显著性水平
        power: 检验效能
        design: 设计类型
        **kwargs: 传递给具体函数的参数
    """
    designs = {
        "two_means": lambda: sample_size_two_means(
            delta=kwargs.get("delta", effect_size),
            sd=kwargs.get("sd", 1.0),
            alpha=alpha, power=power,
            ratio=kwargs.get("ratio", 1.0),
        ),
        "two_proportions": lambda: sample_size_two_proportions(
            p1=kwargs.get("p1", 0.5),
            p2=kwargs.get("p2", 0.5 + effect_size),
            alpha=alpha, power=power,
        ),
        "non_inferiority": lambda: sample_size_non_inferiority(
            delta=kwargs.get("delta", 0),
            margin=kwargs.get("margin", effect_size),
            sd=kwargs.get("sd", 1.0),
            alpha=alpha, power=power,
        ),
        "equivalence": lambda: sample_size_equivalence(
            delta=kwargs.get("delta", 0),
            margin=kwargs.get("margin", effect_size),
            sd=kwargs.get("sd", 1.0),
            alpha=alpha, power=power,
        ),
        "survival": lambda: sample_size_survival(
            hr=kwargs.get("hr", effect_size),
            p_event=kwargs.get("p_event", 0.5),
            alpha=alpha, power=power,
        ),
        "one_mean": lambda: sample_size_one_mean(
            delta=kwargs.get("delta", effect_size),
            sd=kwargs.get("sd", 1.0),
            alpha=alpha, power=power,
        ),
        "one_proportion": lambda: sample_size_one_proportion(
            p0=kwargs.get("p0", 0.5),
            p1=kwargs.get("p1", 0.5 + effect_size),
            alpha=alpha, power=power,
        ),
    }

    if design not in designs:
        raise ValueError(f"未知设计类型: {design}。可选: {list(designs.keys())}")

    return designs[design]()


def power_curves(design: str = "two_means",
                 effect_sizes: list = None,
                 sample_sizes: list = None,
                 alpha: float = 0.05, **kwargs) -> list[dict]:
    """
    生成功效曲线数据（用于可视化）

    Returns:
        [{"effect_size": ..., "n": ..., "power": ...}, ...]
    """
    if effect_sizes is None:
        effect_sizes = [0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
    if sample_sizes is None:
        sample_sizes = [20, 30, 50, 80, 100, 150, 200, 300, 500]

    results = []
    for es in effect_sizes:
        for n in sample_sizes:
            try:
                if design == "two_means":
                    pw = power_two_means(n, delta=es, sd=kwargs.get("sd", 1.0), alpha=alpha)
                elif design == "two_proportions":
                    pw = power_two_proportions(n, p1=kwargs.get("p1", 0.5),
                                               p2=kwargs.get("p1", 0.5) + es, alpha=alpha)
                else:
                    pw = 0
                results.append({
                    "effect_size": es,
                    "n_per_group": n,
                    "power": round(pw, 4),
                })
            except Exception:
                pass

    return results
