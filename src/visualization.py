"""
Biostats — 统计可视化模块

生成临床试验和生物统计相关的专业图表。
"""

import json
import math
from typing import Optional


class StatVisualizer:
    """
    统计可视化引擎

    生成：
    - Kaplan-Meier 生存曲线
    - 森林图 (Forest Plot)
    - 功效曲线
    - 样本量-功效关系图
    - 混杂因素调整图
    - 亚组分析瀑布图
    """

    @staticmethod
    def survival_curve_html(times: list, survival_probs: list,
                            groups: list = None,
                            title: str = "Kaplan-Meier 生存曲线",
                            xlabel: str = "时间", ylabel: str = "生存概率") -> str:
        """生成Kaplan-Meier生存曲线的HTML（使用Chart.js）"""
        if groups is None:
            groups = ["总体"]

        colors = ["#4A90D9", "#E74C3C", "#27AE60", "#F39C12", "#9B59B6"]

        datasets_js = ""
        for i, group in enumerate(groups):
            color = colors[i % len(colors)]
            probs = survival_probs[i] if isinstance(survival_probs[0], list) else survival_probs
            data_points = ", ".join([f"{{x: {t}, y: {p:.4f}}}" for t, p in zip(times, probs)])
            datasets_js += f"""{{
                label: '{group}',
                data: [{data_points}],
                borderColor: '{color}',
                backgroundColor: '{color}22',
                fill: true,
                stepped: true,
                pointRadius: 0,
            }},"""

        return f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
<style>
body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f8f9fa; }}
.chart-container {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }}
h2 {{ text-align: center; color: #333; }}
</style>
</head><body>
<div class="chart-container">
<h2>{title}</h2>
<canvas id="survivalChart"></canvas>
</div>
<script>
new Chart(document.getElementById('survivalChart'), {{
    type: 'line',
    data: {{ datasets: [{datasets_js}] }},
    options: {{
        responsive: true,
        scales: {{
            x: {{ type: 'linear', title: {{ display: true, text: '{xlabel}' }}, min: 0 }},
            y: {{ title: {{ display: true, text: '{ylabel}' }}, min: 0, max: 1 }}
        }},
        plugins: {{ legend: {{ position: 'bottom' }} }}
    }}
}});
</script></body></html>"""

    @staticmethod
    def forest_plot_html(studies: list,
                         title: str = "森林图 (Forest Plot)") -> str:
        """
        生成森林图

        Args:
            studies: [{"name": str, "effect": float, "ci_low": float, "ci_high": float, "weight": float}, ...]
        """
        rows_js = ""
        for i, s in enumerate(studies):
            rows_js += f"""{{
                name: '{s["name"]}',
                effect: {s["effect"]},
                ci_low: {s["ci_low"]},
                ci_high: {s["ci_high"]},
                weight: {s.get("weight", 1)},
            }},"""

        return f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f8f9fa; }}
.forest {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
h2 {{ text-align: center; color: #333; }}
.row {{ display: flex; align-items: center; margin: 8px 0; }}
.label {{ width: 150px; text-align: right; padding-right: 15px; font-size: 14px; color: #555; }}
.plot {{ flex: 1; position: relative; height: 30px; background: #f0f0f0; border-radius: 4px; }}
.ci-line {{ position: absolute; height: 3px; background: #4A90D9; top: 50%; transform: translateY(-50%); }}
.ci-point {{ position: absolute; width: 10px; height: 10px; border-radius: 50%; background: #4A90D9; top: 50%; transform: translate(-50%, -50%); }}
.ref-line {{ position: absolute; width: 2px; height: 100%; background: #E74C3C; left: 50%; }}
.effect-label {{ width: 100px; text-align: center; font-size: 13px; color: #666; }}
.axis {{ display: flex; justify-content: space-between; padding: 5px 150px 5px 150px; font-size: 12px; color: #888; }}
</style>
</head><body>
<div class="forest">
<h2>{title}</h2>
<div class="axis"><span>Favors Control</span><span>HR = 1.0</span><span>Favors Treatment</span></div>
<div id="rows"></div>
<script>
const studies = [{rows_js}];
const container = document.getElementById('rows');
studies.forEach(s => {{
    const range = Math.max(Math.abs(s.ci_low - 1), Math.abs(s.ci_high - 1)) * 1.2;
    const min = 1 - range, max = 1 + range;
    const scale = (v) => ((v - min) / (max - min)) * 100;
    const row = document.createElement('div');
    row.className = 'row';
    row.innerHTML = `
        <div class="label">${{s.name}}</div>
        <div class="plot">
            <div class="ref-line"></div>
            <div class="ci-line" style="left:${{scale(s.ci_low)}}%;width:${{scale(s.ci_high)-scale(s.ci_low)}}%"></div>
            <div class="ci-point" style="left:${{scale(s.effect)}}%"></div>
        </div>
        <div class="effect-label">${{s.effect.toFixed(2)}} (${{s.ci_low.toFixed(2)}}-${{s.ci_high.toFixed(2)}})</div>
    `;
    container.appendChild(row);
}});
</script></div></body></html>"""

    @staticmethod
    def power_curve_html(effect_sizes: list = None,
                         sample_sizes: list = None,
                         alpha: float = 0.05,
                         title: str = "统计功效曲线") -> str:
        """生成功效-样本量曲线"""
        if effect_sizes is None:
            effect_sizes = [0.2, 0.3, 0.5, 0.8]
        if sample_sizes is None:
            sample_sizes = list(range(10, 301, 10))

        # 计算功效
        def _qnorm(p):
            t = math.sqrt(-2 * math.log(1 - p))
            c0, c1, c2 = 2.515517, 0.802853, 0.010328
            d1, d2, d3 = 1.432788, 0.189269, 0.001308
            return t - (c0 + c1*t + c2*t*t) / (1 + d1*t + d2*t*t + d3*t*t*t)

        def calc_power(n, es):
            z_alpha = _qnorm(1 - alpha / 2)
            se = math.sqrt(2 / n)
            z_power = es / se - z_alpha
            return max(0, min(1, 0.5 * (1 + math.erf(z_power / math.sqrt(2)))))

        colors = ["#4A90D9", "#27AE60", "#E74C3C", "#F39C12", "#9B59B6"]
        datasets = ""
        for i, es in enumerate(effect_sizes):
            data = ", ".join([str(round(calc_power(n, es), 3)) for n in sample_sizes])
            datasets += f"""{{
                label: 'Effect Size = {es}',
                data: [{data}],
                borderColor: '{colors[i % len(colors)]}',
                fill: false,
                tension: 0.3,
            }},"""

        labels = ", ".join([str(n) for n in sample_sizes])

        return f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f8f9fa; }}
.chart-container {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }}
h2 {{ text-align: center; color: #333; }}
</style>
</head><body>
<div class="chart-container">
<h2>{title}</h2>
<canvas id="powerChart"></canvas>
</div>
<script>
new Chart(document.getElementById('powerChart'), {{
    type: 'line',
    data: {{
        labels: [{labels}],
        datasets: [{datasets}]
    }},
    options: {{
        responsive: true,
        scales: {{
            x: {{ title: {{ display: true, text: '每组样本量 (n)' }} }},
            y: {{ title: {{ display: true, text: '统计功效 (1-β)' }}, min: 0, max: 1 }}
        }},
        plugins: {{
            legend: {{ position: 'bottom' }},
            annotation: {{ annotations: {{
                refLine: {{ type: 'line', yMin: 0.8, yMax: 0.8, borderColor: '#E74C3C', borderDash: [5,5], label: {{ content: 'Power=0.8', display: true }} }}
            }} }}
        }}
    }}
}});
</script></body></html>"""

    @staticmethod
    def subgroup_analysis_html(subgroups: list,
                               title: str = "亚组分析结果") -> str:
        """
        亚组分析瀑布图

        Args:
            subgroups: [{"name": str, "n": int, "effect": float, "ci_low": float, "ci_high": float, "p_interaction": float}, ...]
        """
        rows = ""
        for s in subgroups:
            p_str = f'p={s.get("p_interaction", 0):.3f}' if s.get("p_interaction") else ""
            rows += f"""<tr>
                <td>{s["name"]}</td>
                <td>{s.get("n", "-")}</td>
                <td>{s["effect"]:.2f} ({s["ci_low"]:.2f}-{s["ci_high"]:.2f})</td>
                <td>{p_str}</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f8f9fa; }}
.container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
h2 {{ text-align: center; color: #333; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ background: #4A90D9; color: white; padding: 12px; text-align: left; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #f5f8ff; }}
</style>
</head><body>
<div class="container">
<h2>{title}</h2>
<table>
<tr><th>亚组</th><th>样本量</th><th>效应值 (95% CI)</th><th>交互作用P值</th></tr>
{rows}
</table>
</div></body></html>"""

    @staticmethod
    def distribution_plot_html(data: list, bins: int = 20,
                               title: str = "数据分布",
                               xlabel: str = "值", ylabel: str = "频数") -> str:
        """生成直方图"""
        if not data:
            return "<p>无数据</p>"

        min_val, max_val = min(data), max(data)
        bin_width = (max_val - min_val) / bins if max_val > min_val else 1
        counts = [0] * bins
        for v in data:
            idx = min(int((v - min_val) / bin_width), bins - 1)
            counts[idx] += 1

        labels = ", ".join([f'{min_val + i * bin_width:.1f}' for i in range(bins)])
        values = ", ".join([str(c) for c in counts])

        return f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f8f9fa; }}
.chart-container {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }}
h2 {{ text-align: center; color: #333; }}
</style>
</head><body>
<div class="chart-container">
<h2>{title}</h2>
<canvas id="histChart"></canvas>
</div>
<script>
new Chart(document.getElementById('histChart'), {{
    type: 'bar',
    data: {{
        labels: [{labels}],
        datasets: [{{ label: '{ylabel}', data: [{values}], backgroundColor: '#4A90D988', borderColor: '#4A90D9', borderWidth: 1 }}]
    }},
    options: {{
        responsive: true,
        scales: {{
            x: {{ title: {{ display: true, text: '{xlabel}' }} }},
            y: {{ title: {{ display: true, text: '{ylabel}' }}, beginAtZero: true }}
        }},
        plugins: {{ legend: {{ display: false }} }}
    }}
}});
</script></body></html>"""

    @staticmethod
    def export_chart_data(data: dict, fmt: str = "json") -> str:
        """导出图表数据"""
        if fmt == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif fmt == "csv":
            if isinstance(data, list) and data:
                headers = list(data[0].keys())
                lines = [",".join(headers)]
                for row in data:
                    lines.append(",".join([str(row.get(h, "")) for h in headers]))
                return "\n".join(lines)
        return json.dumps(data, ensure_ascii=False)
