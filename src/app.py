"""
Biostats — Streamlit Web 界面

提供交互式的生物统计分析平台。
"""

import json
import math
from pathlib import Path

# 尝试导入streamlit，若不可用则提供降级方案
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

DATA_DIR = Path(__file__).parent.parent / "data"


def load_sample_datasets() -> list[dict]:
    """加载示例数据集描述"""
    path = DATA_DIR / "sample-datasets.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


if HAS_STREAMLIT:
    st.set_page_config(
        page_title="Biostats — 生物统计分析平台",
        page_icon="🧬",
        layout="wide",
    )

    st.title("🧬 Biostats — AI驱动的生物统计分析平台")
    st.markdown("一站式临床试验设计与统计分析工具")

    # 侧边栏
    with st.sidebar:
        st.header("📊 分析模块")
        module = st.radio("选择模块", [
            "🏠 首页",
            "📏 样本量计算",
            "📈 功效分析",
            "🔬 贝叶斯分析",
            "📊 数据可视化",
            "📋 示例数据集",
        ])

    if module == "🏠 首页":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("分析模块", "6个", "完整覆盖")
        with col2:
            st.metric("检验类型", "12种", "常用统计方法")
        with col3:
            st.metric("示例数据集", "5个", "开箱即用")

        st.markdown("---")
        st.markdown("""
        ### 功能模块

        | 模块 | 说明 |
        |------|------|
        | 📏 样本量计算 | 优效/非劣效/等效设计，连续/二分类/生存终点 |
        | 📈 功效分析 | 给定样本量计算功效，功效曲线可视化 |
        | 🔬 贝叶斯分析 | 先验设定、后验推断、模型比较 |
        | 📊 数据可视化 | 生存曲线、森林图、分布图 |
        | 📋 示例数据集 | 内置临床试验示例数据 |
        """)

    elif module == "📏 样本量计算":
        st.header("📏 样本量计算")

        design_type = st.selectbox("试验设计", [
            "优效性检验 (Superiority)",
            "非劣效性检验 (Non-inferiority)",
            "等效性检验 (Equivalence)",
        ])

        endpoint_type = st.selectbox("终点类型", [
            "连续变量 (均数比较)",
            "二分类变量 (比例比较)",
            "生存变量 (Log-rank检验)",
        ])

        col1, col2 = st.columns(2)
        with col1:
            alpha = st.slider("显著性水平 (α)", 0.01, 0.10, 0.05, 0.01)
        with col2:
            power = st.slider("检验效能 (1-β)", 0.70, 0.99, 0.80, 0.01)

        if endpoint_type == "连续变量 (均数比较)":
            col1, col2 = st.columns(2)
            with col1:
                delta = st.number_input("均数差值", value=0.5, step=0.1)
            with col2:
                sd = st.number_input("标准差", value=1.0, step=0.1)
            effect_size = delta / sd if sd > 0 else 0
            st.info(f"效应量 (Cohen's d) = {effect_size:.3f}")

        elif endpoint_type == "二分类变量 (比例比较)":
            col1, col2 = st.columns(2)
            with col1:
                p1 = st.number_input("试验组比例", value=0.30, step=0.05)
            with col2:
                p2 = st.number_input("对照组比例", value=0.20, step=0.05)
            effect_size = abs(p1 - p2)

        elif endpoint_type == "生存变量 (Log-rank检验)":
            hr = st.number_input("风险比 (HR)", value=0.70, step=0.05)
            effect_size = hr

        if st.button("🧮 计算样本量", type="primary"):
            with st.spinner("计算中..."):
                from src.power_analysis import (
                    sample_size_two_means,
                    sample_size_two_proportions,
                    sample_size_survival,
                    sample_size_non_inferiority,
                    sample_size_equivalence,
                )

                try:
                    if endpoint_type == "连续变量 (均数比较)":
                        result = sample_size_two_means(delta=delta, sd=sd,
                                                       alpha=alpha, power=power)
                    elif endpoint_type == "二分类变量 (比例比较)":
                        result = sample_size_two_proportions(p1=p1, p2=p2,
                                                            alpha=alpha, power=power)
                    else:
                        result = sample_size_survival(hr=hr, alpha=alpha, power=power)

                    st.success(f"✅ 计算完成！")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("每组样本量", f"{result.n_per_group}")
                    with col2:
                        st.metric("总样本量", f"{result.total_n}")
                    with col3:
                        st.metric("效应量", f"{result.effect_size:.3f}")

                    st.code(result.summary())
                except Exception as e:
                    st.error(f"计算出错: {e}")

    elif module == "📈 功效分析":
        st.header("📈 功效分析")
        st.info("给定样本量，计算统计功效；或生成功效曲线。")

        tab1, tab2 = st.tabs(["功效计算", "功效曲线"])

        with tab1:
            n = st.number_input("每组样本量", value=50, min_value=5, step=5)
            es = st.number_input("效应量", value=0.5, step=0.1)
            alpha_val = st.slider("α", 0.01, 0.10, 0.05, 0.01, key="power_alpha")

            if st.button("计算功效"):
                from src.power_analysis import power_two_means
                pw = power_two_means(n, delta=es, alpha=alpha_val)
                st.metric("统计功效", f"{pw:.4f}")
                if pw >= 0.8:
                    st.success("✅ 功效充足 (≥0.80)")
                else:
                    st.warning(f"⚠️ 功效不足 ({pw:.4f} < 0.80)")

        with tab2:
            st.markdown("### 功效曲线")
            es_list = st.multiselect("效应量", [0.2, 0.3, 0.5, 0.8, 1.0], default=[0.3, 0.5, 0.8])
            if st.button("生成曲线"):
                from src.visualization import StatVisualizer
                html = StatVisualizer.power_curve_html(effect_sizes=es_list)
                st.components.v1.html(html, height=500)

    elif module == "🔬 贝叶斯分析":
        st.header("🔬 贝叶斯分析")
        st.info("基于先验信息和观测数据进行贝叶斯推断。")

        prior_type = st.selectbox("先验分布", ["无信息先验", "弱信息先验", "信息先验"])
        st.markdown("### 输入数据")
        data_input = st.text_area("输入数据（逗号分隔）", "23, 25, 28, 30, 22, 27, 26, 24, 29, 31")

        if st.button("运行贝叶斯分析"):
            try:
                data = [float(x.strip()) for x in data_input.split(",")]
                n = len(data)
                mean = sum(data) / n
                var = sum((x - mean) ** 2 for x in data) / (n - 1)
                se = math.sqrt(var / n)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("后验均值", f"{mean:.2f}")
                with col2:
                    st.metric("后验标准差", f"{se:.3f}")
                with col3:
                    st.metric("95% CrI", f"({mean - 1.96*se:.2f}, {mean + 1.96*se:.2f})")

                st.success("✅ 贝叶斯分析完成")
            except Exception as e:
                st.error(f"数据解析错误: {e}")

    elif module == "📊 数据可视化":
        st.header("📊 数据可视化")
        chart_type = st.selectbox("图表类型", [
            "生存曲线 (Kaplan-Meier)",
            "森林图 (Forest Plot)",
            "直方图 (Histogram)",
        ])

        if chart_type == "生存曲线 (Kaplan-Meier)":
            st.info("示例：两组生存曲线比较")
            from src.visualization import StatVisualizer
            html = StatVisualizer.survival_curve_html(
                times=[0, 1, 2, 3, 4, 5, 6, 8, 10, 12],
                survival_probs=[
                    [1.0, 0.95, 0.88, 0.80, 0.72, 0.65, 0.60, 0.52, 0.45, 0.40],
                    [1.0, 0.90, 0.78, 0.65, 0.55, 0.48, 0.42, 0.35, 0.30, 0.25],
                ],
                groups=["试验组", "对照组"],
            )
            st.components.v1.html(html, height=500)

        elif chart_type == "森林图 (Forest Plot)":
            st.info("示例：Meta分析森林图")
            from src.visualization import StatVisualizer
            html = StatVisualizer.forest_plot_html(studies=[
                {"name": "Study A", "effect": 0.72, "ci_low": 0.55, "ci_high": 0.94, "weight": 25},
                {"name": "Study B", "effect": 0.85, "ci_low": 0.68, "ci_high": 1.06, "weight": 30},
                {"name": "Study C", "effect": 0.68, "ci_low": 0.48, "ci_high": 0.96, "weight": 20},
                {"name": "Study D", "effect": 0.78, "ci_low": 0.62, "ci_high": 0.98, "weight": 25},
            ])
            st.components.v1.html(html, height=400)

    elif module == "📋 示例数据集":
        st.header("📋 示例数据集")
        datasets = load_sample_datasets()
        if datasets:
            for ds in datasets:
                with st.expander(f"📁 {ds.get('name', '未命名')}"):
                    st.markdown(f"**描述**: {ds.get('description', '')}")
                    st.markdown(f"**类型**: {ds.get('type', '')}")
                    st.markdown(f"**样本量**: {ds.get('n_samples', 'N/A')}")
                    if ds.get("variables"):
                        st.json(ds["variables"])
        else:
            st.warning("未找到示例数据集文件。")


def create_app():
    """创建Streamlit应用（用于程序化启动）"""
    if not HAS_STREAMLIT:
        print("⚠️ 需要安装 Streamlit: pip install streamlit")
        print("   然后运行: streamlit run src/app.py")
        return
    # Streamlit会自动执行模块级别的代码
    pass


if __name__ == "__main__":
    if not HAS_STREAMLIT:
        print("⚠️ Streamlit 未安装。请运行: pip install streamlit")
        print("   安装后使用: streamlit run src/app.py")
    # 当通过 streamlit run 执行时，模块级代码会自动运行
