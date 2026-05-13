"""时间序列 — 时间序列分析与预测"""

from typing import Dict, List, Optional
import math


class TimeSeriesAnalysis:
    """时间序列分析方法"""

    def __init__(self):
        self._forecasts: List[dict] = []

    def descriptive(self, series: List[float]) -> dict:
        n = len(series)
        if n == 0:
            return {"error": "空序列"}
        mean = sum(series) / n
        var = sum((x - mean) ** 2 for x in series) / (n - 1) if n > 1 else 0
        sd = math.sqrt(var)
        return {"n": n, "mean": round(mean, 4), "sd": round(sd, 4),
                "min": min(series), "max": max(series), "range": max(series) - min(series)}

    def moving_average(self, series: List[float], window: int = 3) -> List[float]:
        if len(series) < window:
            return []
        result = []
        for i in range(window - 1, len(series)):
            avg = sum(series[i - window + 1:i + 1]) / window
            result.append(round(avg, 4))
        return result

    def exponential_smoothing(self, series: List[float], alpha: float = 0.3) -> List[float]:
        if not series:
            return []
        result = [series[0]]
        for i in range(1, len(series)):
            result.append(round(alpha * series[i] + (1 - alpha) * result[-1], 4))
        return result

    def double_exponential_smoothing(self, series: List[float], alpha: float = 0.3,
                                      beta: float = 0.1) -> dict:
        n = len(series)
        if n < 2:
            return {"error": "需要至少2个数据点"}
        level = [series[0]]
        trend = [series[1] - series[0]]
        fitted = [series[0]]
        for i in range(1, n):
            l = alpha * series[i] + (1 - alpha) * (level[-1] + trend[-1])
            t = beta * (l - level[-1]) + (1 - beta) * trend[-1]
            level.append(l)
            trend.append(t)
            fitted.append(round(l + t, 4))
        forecast_1 = round(level[-1] + trend[-1], 4)
        forecast_2 = round(level[-1] + 2 * trend[-1], 4)
        return {"fitted": fitted, "level": [round(l, 4) for l in level],
                "trend": [round(t, 4) for t in trend],
                "forecast": [forecast_1, forecast_2]}

    def autocorrelation(self, series: List[float], max_lag: int = 10) -> List[float]:
        n = len(series)
        if n < 3:
            return []
        mean = sum(series) / n
        var = sum((x - mean) ** 2 for x in series)
        if var == 0:
            return [1.0] * min(max_lag, n - 1)
        acf = []
        for lag in range(1, min(max_lag + 1, n)):
            cov = sum((series[i] - mean) * (series[i - lag] - mean) for i in range(lag, n))
            acf.append(round(cov / var, 4))
        return acf

    def detect_trend(self, series: List[float]) -> dict:
        n = len(series)
        if n < 3:
            return {"error": "需要至少3个数据点"}
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(series) / n
        ss_xx = sum((xi - x_mean) ** 2 for xi in x)
        ss_xy = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, series))
        slope = ss_xy / ss_xx if ss_xx > 0 else 0
        ss_res = sum((series[i] - (y_mean + slope * (x[i] - x_mean))) ** 2 for i in range(n))
        ss_tot = sum((yi - y_mean) ** 2 for yi in series)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        return {"slope": round(slope, 4), "r_squared": round(r_squared, 4),
                "direction": "increasing" if slope > 0.01 else "decreasing" if slope < -0.01 else "stable"}

    def seasonal_decompose(self, series: List[float], period: int = 12) -> dict:
        n = len(series)
        if n < 2 * period:
            return {"error": f"需要至少{2 * period}个数据点"}
        ma = self.moving_average(series, period)
        trend = [None] * (period // 2) + ma + [None] * (period // 2)
        detrended = []
        for i in range(n):
            if trend[i] is not None:
                detrended.append(series[i] - trend[i])
            else:
                detrended.append(None)
        seasonal = [0.0] * period
        count = [0] * period
        for i in range(n):
            if detrended[i] is not None:
                seasonal[i % period] += detrended[i]
                count[i % period] += 1
        seasonal = [round(seasonal[i] / count[i], 4) if count[i] > 0 else 0 for i in range(period)]
        return {"trend": [round(t, 4) if t is not None else None for t in trend],
                "seasonal": seasonal, "period": period}

    def forecast_linear(self, series: List[float], steps: int = 3) -> List[float]:
        n = len(series)
        if n < 2:
            return [series[-1]] * steps if series else []
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(series) / n
        ss_xx = sum((xi - x_mean) ** 2 for xi in x)
        ss_xy = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, series))
        slope = ss_xy / ss_xx if ss_xx > 0 else 0
        intercept = y_mean - slope * x_mean
        forecasts = []
        for s in range(1, steps + 1):
            forecasts.append(round(intercept + slope * (n + s - 1), 4))
        return forecasts

    def save_forecast(self, forecast: dict):
        self._forecasts.append(forecast)

    def get_forecasts(self) -> List[dict]:
        return list(self._forecasts)
