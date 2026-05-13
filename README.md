# 🦾 Biostats终结者 — 生物统计不再愁！

> **AI 驱动的生物统计分析平台** — 让医生和科研人员从繁琐的统计分析中解放出来

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com)

---

## 📌 一句话

**上传数据 → 自然语言描述分析目标 → 自动生成论文级统计图表与报告**

---

## 🔬 学术支撑：为什么生物统计 AI Agent 是刚需

本项目的方法论得到 **Nature Biomedical Engineering (2026)** 最新研究的强力支撑：

> Bu, D., Sun, J., Li, K. et al. *Empowering AI data scientists using a multi-agent LLM framework with self-evolving capabilities for autonomous, tool-aware biomedical data analyses.* Nat. Biomed. Eng. (2026). [DOI: 10.1038/s41551-026-01634-6](https://doi.org/10.1038/s41551-026-01634-6)

**关键发现：**

| 发现 | 数据 | 对本项目的意义 |
|------|------|--------------|
| 统计分析是 AI Agent 最大短板 | 五大类任务中 S 类仅 **59%** 成功率（vs 组学 94%） | ✅ 我们聚焦于此，差异化切入 |
| 多 Agent 协作有效 | 4 Agent 协作，端到端自主分析 | ✅ 验证了我们的 Planner-Executor-Reviewer 架构 |
| 自进化可泛化 | 三轮学习 52%→**77%**，未见问题 **69%** | ✅ 支撑范文学习 + 案例库积累策略 |
| IE 纠错挽救 60.8% 失败 | 交互探索使成功率从 28%→52% | ✅ 证明多层质控 + 人工审核的必要性 |
| LLM 无关性 | DeepSeek/Qwen/GPT-4omini 性能接近 | ✅ 国产模型部署无障碍 |

**BioMedAgent 代码开源**: [github.com/BOBQWERA/BioMedAgent](https://github.com/BOBQWERA/BioMedAgent) ⭐ 32 · 🍴 6

---

## 🎯 核心能力

- 🗣️ **自然语言 → 统计分析**：一句话描述分析目标，自动选择方法
- 📊 **论文级图表**：森林图、生存曲线、ROC、箱线图 — 符合 NEJM/Lancet 规范
- 📝 **自动报告**：Methods + Results + Tables & Figures 结构化输出
- 🧠 **智能适配**：自动识别研究类型（RCT/队列/病例对照），匹配最优统计方法
- 🔄 **范文学习**：上传已发表论文，AI 学习其分析流程并套用

---

## 🏗️ 项目架构

```
biostats-terminator/
├── backend/                  # FastAPI 后端
│   └── app/
│       ├── api/endpoints/    # REST API（统计分析、用户认证、可视化等）
│       ├── core/             # 配置、数据库、安全
│       ├── models/           # SQLAlchemy 数据模型
│       ├── schemas/          # Pydantic 请求/响应模型
│       └── services/         # 业务逻辑（统计引擎、图表生成、报告导出）
├── biostats/                 # 统计计算库
│   ├── bayesian.py           # 贝叶斯分析
│   ├── survival.py           # 生存分析（KM、Cox）
│   └── trial.py              # 临床试验设计
├── src/                      # 核心分析引擎
│   ├── analyzer.py           # 主分析器（自然语言→统计代码）
│   ├── server.py             # 独立分析服务器
│   ├── meta_analysis.py      # Meta 分析
│   ├── propensity_score.py   # 倾向性评分匹配
│   ├── diagnostic_test.py    # 诊断试验评价
│   └── ...                   # 更多统计模块
├── frontend/                 # Web 前端
│   └── app.html              # Landing page + 分析界面
├── data/                     # 统计表、示例数据集
├── docs/                     # 项目方案、部署指南
└── tests/                    # 测试套件
```

**多 Agent 协作流程：**

```
用户输入（自然语言）
    ↓
Planner Agent → 解析研究设计，推荐统计方法
    ↓
Executor Agent → 调用统计引擎，执行分析
    ↓
Reviewer Agent → 检查统计假设、结果一致性
    ↓
输出：论文级图表 + 结构化报告
```

---

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/MoKangMedical/biostats-terminator.git
cd biostats-terminator

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn backend.app.main:app --reload --port 8000

# 访问
open http://localhost:8000
```

### Docker 部署

```bash
docker-compose up -d
```

### 使用示例

```python
from biostats import survival
from src.analyzer import BioStatAnalyzer

# 方式 1：直接调用统计库
km_result = survival.kaplan_meier(
    data="clinical_trial.csv",
    time_col="survival_months",
    event_col="death"
)

# 方式 2：自然语言驱动（AI Agent）
analyzer = BioStatAnalyzer()
report = analyzer.analyze(
    data="experiment.csv",
    instruction="比较两组患者的生存率差异，生成 Kaplan-Meier 曲线和 Cox 回归结果"
)
```

---

## 📦 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 统计引擎 | NumPy · SciPy · Statsmodels · lifelines |
| 机器学习 | scikit-learn |
| 可视化 | Matplotlib · Seaborn · Plotly |
| 数据库 | SQLAlchemy + SQLite/PostgreSQL |
| AI Agent | LLM 驱动（GPT-4 / DeepSeek / Qwen） |
| 部署 | Docker · Render · 腾讯云 |

---

## 🤝 贡献

欢迎提交 Issue 和 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可

MIT License © 2024-2026 MoKangMedical

---

*Made with ❤️ for medical researchers who deserve better tools.*
