# Biostats终结者 - 专业生物统计分析平台

<div align="center">

![Biostats终结者](https://img.shields.io/badge/Biostats-终结者-0D7EA8?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![R](https://img.shields.io/badge/R-4.0+-276DC3?style=for-the-badge&logo=r&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**让生物统计分析变得简单高效**

基于R语言的智能分析引擎 · 支持12种常用生物统计方法 · 一键生成专业报告

[快速开始](#快速开始) · [功能特性](#功能特性) · [使用文档](#使用文档) · [API文档](#api文档)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [支持的分析方法](#支持的分析方法)
- [安装要求](#安装要求)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
- [API文档](#api文档)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 🎯 项目简介

**Biostats终结者** 是一个专业的生物统计分析平台，专为医学研究、临床试验、生物信息学等领域设计。它将强大的R语言统计功能封装成易用的Python接口，并提供美观的Web界面，让复杂的统计分析变得简单高效。

### 核心优势

- ✨ **智能化**：自动识别数据类型，智能选择分析方法
- 🚀 **高效**：一键执行分析，自动生成代码和报告
- 📊 **专业**：基于R语言，提供医学级统计分析
- 🎨 **美观**：现代化Web界面，专业的可视化图表
- 📝 **完整**：详细的分析报告和可重现的R代码
- 🔧 **灵活**：支持Python调用和Web界面两种使用方式

---

## ✨ 功能特性

### 核心功能

#### 1. 多种分析方法
- 描述性统计分析
- 假设检验（t检验、方差分析、卡方检验）
- 相关与回归分析
- 生存分析
- 诊断试验评价
- 非参数检验

#### 2. 专业可视化
- 自动生成高质量统计图表
- 相关矩阵热图
- 生存曲线（Kaplan-Meier）
- ROC曲线
- 回归诊断图
- Q-Q图

#### 3. 完整报告
- 详细的统计结果输出
- 可重现的R代码
- 会话分析报告
- 历史记录管理

#### 4. 用户友好
- 直观的Web界面
- 拖拽上传文件
- 参数自动配置
- 实时分析状态
- 结果在线预览

---

## 📊 支持的分析方法

| 分析方法 | 功能描述 | 适用场景 |
|---------|---------|---------|
| **描述性统计** | 数据概览、均值、中位数、标准差、缺失值分析 | 数据探索 |
| **t检验** | 单样本、独立样本、配对样本t检验，含正态性检验 | 两组比较 |
| **方差分析** | 单因素ANOVA，多重比较（Tukey HSD），效应量 | 多组比较 |
| **卡方检验** | 列联表分析、Fisher精确检验、Cramer's V | 分类变量关联 |
| **相关分析** | Pearson/Spearman/Kendall相关，相关矩阵热图 | 变量关系 |
| **线性回归** | 多元线性回归、VIF诊断、残差分析 | 连续预测 |
| **逻辑回归** | 二分类预测、OR值、ROC曲线、AUC | 二分类预测 |
| **Cox回归** | 生存分析、风险比HR、比例风险假设检验 | 生存预测 |
| **生存分析** | Kaplan-Meier曲线、Log-Rank检验 | 生存比较 |
| **诊断试验** | 灵敏度、特异度、ROC曲线、似然比 | 诊断评价 |
| **正态性检验** | Shapiro-Wilk、K-S检验、Q-Q图 | 分布检验 |
| **非参数检验** | Mann-Whitney U、Kruskal-Wallis、Wilcoxon | 非正态数据 |

---

## 💻 安装要求

### 系统要求

- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **内存**: 最低4GB，推荐8GB以上
- **磁盘空间**: 至少2GB可用空间

### 软件依赖

#### 1. Python环境
```bash
Python 3.8 或更高版本
```

#### 2. R环境
```bash
R 4.0.0 或更高版本
```

下载地址: [https://www.r-project.org/](https://www.r-project.org/)

#### 3. Python包
```bash
Flask>=2.0.0
Flask-CORS>=3.0.10
```

#### 4. R包（自动安装）
```r
survival, survminer, pROC, epiR, DescTools, car, nortest,
psych, gtsummary, ggplot2, dplyr, readxl, openxlsx
```

---

## 🚀 快速开始

### 方式一：Web界面（推荐）

1. **安装依赖**
```bash
pip install flask flask-cors
```

2. **启动服务器**
```bash
cd Biostats终结者项目/src
python web_server.py
```

3. **打开浏览器**
```
访问: http://127.0.0.1:5000
```

4. **开始使用**
- 选择分析方法
- 上传数据文件
- 配置参数（可选）
- 点击"开始分析"

### 方式二：Python调用

```python
from biostats_agent import BiostatsAgent

# 创建Agent实例
agent = BiostatsAgent()

# 执行描述性统计
result = agent.analyze(
    method='descriptive',
    data_path='data.csv',
    group_var='gender'
)

# 执行t检验
result = agent.analyze(
    method='ttest',
    data_path='data.csv',
    var1='age',
    group='gender'
)

# 执行生存分析
result = agent.analyze(
    method='survival',
    data_path='survival_data.csv',
    time_var='time',
    event_var='status',
    group_var='treatment'
)

# 保存报告
agent.save_session_report('report.txt')
```

---

## 📖 使用方法

### 数据准备

#### 支持的数据格式
- **CSV文件** (.csv) - 推荐
- **Excel文件** (.xlsx, .xls)
- **RDS文件** (.rds) - R数据格式
- **文本文件** (.txt)

#### 数据格式要求
1. 第一行为列名（变量名）
2. 每行代表一个观测
3. 缺失值用NA或空白表示

#### 示例数据格式

```csv
id,name,age,gender,treatment,time,status
1,Patient1,45,M,A,365,1
2,Patient2,52,F,B,420,0
3,Patient3,38,M,A,180,1
...
```

### 分析流程

#### 1. 描述性统计分析

```python
# 基本描述统计
agent.analyze('descriptive', 'data.csv')

# 分组描述统计
agent.analyze('descriptive', 'data.csv', group_var='gender')
```

**输出内容**:
- 数值变量：均值、标准差、中位数、四分位数
- 分类变量：频数、百分比
- 缺失值统计
- 分组统计（如指定）

#### 2. t检验

```python
# 独立样本t检验
agent.analyze('ttest', 'data.csv', 
              var1='age', 
              group='gender')

# 配对样本t检验
agent.analyze('ttest', 'data.csv',
              var1='before',
              var2='after',
              paired=True)
```

**输出内容**:
- 分组描述统计
- 正态性检验
- 方差齐性检验
- t检验结果

#### 3. 生存分析

```python
# Kaplan-Meier生存分析
agent.analyze('survival', 'survival_data.csv',
              time_var='time',
              event_var='status',
              group_var='treatment')
```

**输出内容**:
- 生存表
- 中位生存时间
- Log-Rank检验
- Kaplan-Meier曲线图

#### 4. 逻辑回归

```python
# 二分类逻辑回归
agent.analyze('logistic_regression', 'data.csv',
              dependent='outcome',
              predictors=['age', 'gender', 'treatment'])
```

**输出内容**:
- 回归系数
- OR值及95%CI
- ROC曲线和AUC
- 混淆矩阵
- 分类性能指标

---

## 🔌 API文档

### REST API端点

#### 健康检查
```http
GET /api/health
```

**响应**:
```json
{
  "status": "healthy",
  "r_installed": true,
  "r_version": "R version 4.3.0",
  "timestamp": "2026-02-07T12:00:00"
}
```

#### 上传文件
```http
POST /api/upload
Content-Type: multipart/form-data
```

**请求**:
```
file: [数据文件]
```

**响应**:
```json
{
  "success": true,
  "filename": "20260207_120000_data.csv",
  "filepath": "/tmp/biostats_uploads/20260207_120000_data.csv",
  "size": 12345,
  "message": "文件上传成功"
}
```

#### 执行分析
```http
POST /api/analyze
Content-Type: application/json
```

**请求**:
```json
{
  "method": "ttest",
  "filepath": "/tmp/biostats_uploads/20260207_120000_data.csv",
  "parameters": {
    "var1": "age",
    "group": "gender"
  }
}
```

**响应**:
```json
{
  "success": true,
  "method": "ttest",
  "method_name": "t检验",
  "timestamp": "2026-02-07T12:00:00",
  "stdout": "[分析结果输出]",
  "stderr": "",
  "code_file": "/tmp/biostats_results/ttest_1.R"
}
```

#### 获取历史
```http
GET /api/history
```

**响应**:
```json
{
  "success": true,
  "history": [
    {
      "method": "ttest",
      "method_name": "t检验",
      "data_path": "data.csv",
      "timestamp": "2026-02-07T12:00:00",
      "success": true,
      "code_file": "/tmp/biostats_results/ttest_1.R"
    }
  ],
  "count": 1
}
```

#### 下载报告
```http
GET /api/session-report
```

**响应**: 文本文件下载

---

## 📁 项目结构

```
Biostats终结者项目/
│
├── src/                          # 源代码目录
│   ├── biostats_agent.py        # 核心Agent类
│   ├── web_server.py            # Flask Web服务器
│   └── web_interface.html       # Web前端界面
│
├── docs/                         # 文档目录
│   ├── README.md                # 项目说明
│   ├── USAGE.md                 # 使用指南
│   ├── API.md                   # API文档
│   └── EXAMPLES.md              # 示例代码
│
├── data/                         # 示例数据目录
│   ├── sample_data.csv          # 示例CSV数据
│   └── survival_data.csv        # 生存分析示例数据
│
├── outputs/                      # 输出目录
│   ├── results/                 # 分析结果
│   ├── plots/                   # 图表文件
│   └── reports/                 # 分析报告
│
├── tests/                        # 测试目录
│   ├── test_agent.py            # Agent单元测试
│   └── test_api.py              # API测试
│
├── requirements.txt              # Python依赖
├── R_packages.txt               # R包依赖
└── LICENSE                      # 许可证
```

---

## 🛠️ 开发指南

### 环境配置

1. **克隆项目**
```bash
git clone [项目地址]
cd Biostats终结者项目
```

2. **安装Python依赖**
```bash
pip install -r requirements.txt
```

3. **安装R包**
```bash
Rscript -e "install.packages(c('survival', 'survminer', 'pROC', 'epiR', 'DescTools', 'car', 'nortest', 'psych', 'gtsummary', 'ggplot2', 'dplyr', 'readxl', 'openxlsx'))"
```

### 添加新的分析方法

1. **在`BiostatsAgent`类中添加方法**

```python
def _code_new_method(self, **kwargs) -> List[str]:
    """新分析方法的R代码生成"""
    code = [
        "# ========== 新分析方法 ==========",
        "",
        "# 在这里添加R代码",
        ""
    ]
    return code
```

2. **在`ANALYSIS_METHODS`中注册**

```python
ANALYSIS_METHODS = {
    # ...
    'new_method': '新分析方法',
}
```

3. **在`_generate_analysis_code`中添加映射**

```python
method_map = {
    # ...
    'new_method': self._code_new_method,
}
```

### 测试

```bash
# 运行单元测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_agent.py
```

---

## ❓ 常见问题

### Q1: R未检测到怎么办？

**A**: 确保R已正确安装并在系统PATH中。

```bash
# 检查R是否在PATH中
which Rscript  # Linux/Mac
where Rscript  # Windows

# 如果不在PATH中，手动指定路径
agent = BiostatsAgent(r_path="/path/to/Rscript")
```

### Q2: R包安装失败怎么办？

**A**: 可以手动在R中安装：

```r
# 在R控制台中运行
install.packages("包名")

# 或使用Agent的安装功能
agent.install_packages(['survival', 'ggplot2'])
```

### Q3: 分析执行超时怎么办？

**A**: 检查数据大小和复杂度。可以：
- 减少数据量
- 简化分析参数
- 增加超时时间（修改`_execute_r_code`中的timeout参数）

### Q4: 支持什么数据格式？

**A**: 支持CSV、Excel (.xlsx, .xls)、RDS、TXT格式。推荐使用CSV格式以获得最佳兼容性。

### Q5: 如何获取R代码？

**A**: 
```python
# 方法1：从结果中获取
result = agent.analyze('ttest', 'data.csv')
print(result['code'])

# 方法2：保存到文件
agent.save_r_code('analysis.R')
```

### Q6: Web界面无法访问？

**A**: 检查：
1. 服务器是否正常启动
2. 端口是否被占用
3. 防火墙设置
4. 浏览器地址是否正确

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码规范

- 遵循PEP 8规范
- 添加适当的注释和文档字符串
- 编写单元测试
- 更新相关文档

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **项目主页**: [GitHub链接]
- **问题反馈**: [Issues]
- **邮箱**: [联系邮箱]

---

## 🙏 致谢

感谢以下开源项目:

- [R Project](https://www.r-project.org/)
- [Flask](https://flask.palletsprojects.com/)
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)

---

<div align="center">

**Biostats终结者** - 让生物统计分析变得简单高效

Made with ❤️ by [Your Name]

</div>
