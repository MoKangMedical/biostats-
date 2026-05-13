# CHANGELOG

## [2.0.0] - 2026-05-13 — 🔄 项目合并

### 重大变更
- **合并 MoKangMedical/biostats- 和 MoKangMedical/Biostats 为统一项目「Biostats终结者」**
- 统一目录结构：backend / biostats / src / frontend / data / docs

### 新增（来自 Biostats 仓库）
- FastAPI 后端框架（用户认证、统计分析 API、可视化接口）
- biostats 统计库（贝叶斯分析、生存分析、临床试验设计）
- src 高级统计模块（Meta分析、倾向性评分、诊断试验、混合效应模型 等 14 个模块）
- 前端 landing page（app.html）
- 统计参考数据（9 个 JSON 数据集）
- Render 部署配置、Procfile、pyproject.toml

### 新增（来自 biostats- 仓库）
- 主分析器（python_analyzer.py → src/analyzer.py）
- 独立分析服务器（final_server.py → src/server.py）
- 全平台部署指南（腾讯云 / 全局 / Docker）
- 项目方案文档、Lancet 手稿
- 测试基础设施
- GitHub 社区配置（ISSUE_TEMPLATE、CODEOWNERS、FUNDING）

### 优化
- 统一 .gitignore（覆盖 Python/R/Docker/OS/IDE）
- 统一 requirements.txt（精简去重）
- 统一 Dockerfile + docker-compose.yml
- 全新 README（含 Nature BME 2026 BioMedAgent 论文背书）
- 清理所有 __pycache__ 和 .pyc 文件

---

## [1.0.0] — biostats-

### 2026-04-23 — Hermes 改进
- 📐 理论标准化
- 🔒 安全规则补全
- 📝 README 升级

### 2026-04-22 — 初始版本
- 核心分析模块
- 部署脚本
- API 测试用例

---

## [1.0.0] — Biostats

### 2026-04-30 — v0.2.0
- FastAPI 后端 + 用户认证
- 统计分析 API
- 自动提交本地变更

### 2026-04-27 — v0.1.0
- 初始版本：生存分析、临床试验设计、贝叶斯方法
- Landing page
- 首次 GitHub 同步
