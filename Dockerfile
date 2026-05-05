# Biostats终结者 - Production Dockerfile
FROM ubuntu:26.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    r-base \
    r-base-dev \
    postgresql-client \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装R包
RUN R -e "install.packages(c('survival', 'ggplot2', 'dplyr', 'tidyr', 'readr', 'broom', 'car', 'nortest'), repos='https://cloud.r-project.org/')"

# 创建应用用户
RUN useradd -m -s /bin/bash biostats

# 设置工作目录
WORKDIR /app

# 复制requirements
COPY requirements_production.txt .

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements_production.txt

# 复制应用代码
COPY --chown=biostats:biostats . .

# 创建必要目录
RUN mkdir -p /app/logs /app/uploads /var/log/biostats && \
    chown -R biostats:biostats /app /var/log/biostats

# 暴露端口
EXPOSE 8000

# 切换到应用用户
USER biostats

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["gunicorn", "--config", "gunicorn_config.py", "backend.final_server:app"]
