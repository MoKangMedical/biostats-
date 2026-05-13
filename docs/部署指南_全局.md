# 🌍 Biostats终结者 - 全球部署完整指南

## 📋 目录
1. [域名注册](#1-域名注册)
2. [服务器选择与购买](#2-服务器选择与购买)
3. [服务器环境配置](#3-服务器环境配置)
4. [GitHub仓库创建](#4-github仓库创建)
5. [生产环境部署](#5-生产环境部署)
6. [域名解析配置](#6-域名解析配置)
7. [HTTPS证书配置](#7-https证书配置)
8. [持续集成部署](#8-持续集成部署)
9. [监控与维护](#9-监控与维护)

---

## 1. 域名注册

### 推荐域名
- `biostats-killer.com`
- `biostat-terminator.com`
- `stats-analyzer.com`
- `medstat-pro.com`
- `clinicalstat.io`

### 域名注册商推荐

#### Option 1: Namecheap (推荐)
- 网站: https://www.namecheap.com
- 价格: ~$10-15/年
- 优势: 价格便宜，界面友好，免费隐私保护
- 步骤:
  ```
  1. 访问 namecheap.com
  2. 搜索域名: biostat-terminator.com
  3. 加入购物车
  4. 创建账户
  5. 完成支付 (接受信用卡/PayPal)
  6. 设置DNS (后续配置)
  ```

#### Option 2: GoDaddy
- 网站: https://www.godaddy.com
- 价格: ~$12-20/年
- 优势: 知名度高，客服好

#### Option 3: Google Domains
- 网站: https://domains.google
- 价格: ~$12/年
- 优势: Google服务集成

### 域名配置
购买后保存以下信息：
- 域名: `biostat-terminator.com`
- 注册商: Namecheap
- DNS服务器: 使用Cloudflare (免费CDN)

---

## 2. 服务器选择与购买

### 推荐方案对比

| 服务商 | 配置 | 价格/月 | 适用场景 |
|--------|------|---------|----------|
| **DigitalOcean** | 2GB RAM, 1 CPU | $12 | 初期测试 |
| **DigitalOcean** | 4GB RAM, 2 CPU | $24 | 小规模生产 |
| **AWS Lightsail** | 2GB RAM, 1 CPU | $10 | 初期测试 |
| **Linode** | 4GB RAM, 2 CPU | $24 | 中等规模 |
| **Vultr** | 4GB RAM, 2 CPU | $24 | 全球节点 |

### 推荐配置: DigitalOcean Droplet

**基础配置** (初期):
- CPU: 2 vCPUs
- RAM: 4GB
- SSD: 80GB
- 带宽: 4TB
- 价格: $24/月
- 位置: San Francisco (美国西海岸)

**步骤**:
```
1. 访问 https://www.digitalocean.com
2. 注册账户 (新用户可获$200信用额度)
3. Create → Droplets
4. Choose Region: San Francisco 或 Singapore (亚洲用户)
5. Choose Image: Ubuntu 22.04 LTS
6. Choose Size: Basic - $24/mo (4GB RAM)
7. 选择SSH密钥或密码认证
8. Create Droplet
```

获得服务器IP: `123.45.67.89` (示例)

---

## 3. 服务器环境配置

### 3.1 连接服务器

```bash
# 使用SSH连接
ssh root@your_server_ip

# 首次登录后，更新系统
apt update && apt upgrade -y
```

### 3.2 创建非root用户

```bash
# 创建用户
adduser biostats

# 添加sudo权限
usermod -aG sudo biostats

# 切换到新用户
su - biostats
```

### 3.3 安装必要软件

```bash
# 安装Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# 安装R和必要包
sudo apt install -y r-base r-base-dev

# 安装数据库
sudo apt install -y postgresql postgresql-contrib

# 安装Nginx (Web服务器)
sudo apt install -y nginx

# 安装Git
sudo apt install -y git

# 安装其他工具
sudo apt install -y curl wget htop
```

### 3.4 安装R包

```bash
# 进入R控制台
sudo R

# 在R中执行
install.packages(c(
  "survival",
  "ggplot2",
  "dplyr",
  "tidyr",
  "readr",
  "broom",
  "car",
  "nortest"
), repos = "https://cloud.r-project.org/")

# 退出R
q()
```

### 3.5 配置PostgreSQL

```bash
# 切换到postgres用户
sudo -u postgres psql

# 在PostgreSQL中执行
CREATE DATABASE biostats_db;
CREATE USER biostats_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE biostats_db TO biostats_user;
\q
```

---

## 4. GitHub仓库创建

### 4.1 在GitHub上创建仓库

1. 访问 https://github.com
2. 点击 "New repository"
3. 填写信息:
   - Repository name: `biostats-terminator`
   - Description: "Professional Biostatistics Analysis Platform - Global Cloud Service"
   - Public (开源) 或 Private (私有)
   - 勾选 "Add a README file"
   - 选择 License: MIT License
   - 点击 "Create repository"

### 4.2 准备项目文件

在本地项目根目录创建以下文件：

**`.gitignore`**:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp

# Uploads
uploads/*
!uploads/.gitkeep

# Config
config/local.py
secrets.yaml
```

**`LICENSE`** (MIT License):
```
MIT License

Copyright (c) 2026 Biostats Terminator Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 4.3 推送代码到GitHub

```bash
# 在项目目录中
cd ~/Desktop/Biostats终结者项目

# 初始化Git仓库
git init

# 添加远程仓库
git remote add origin https://github.com/your_username/biostats-terminator.git

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Complete biostatistics analysis platform"

# 推送到GitHub
git push -u origin main
```

---

## 5. 生产环境部署

### 5.1 在服务器上克隆项目

```bash
# SSH连接到服务器
ssh biostats@your_server_ip

# 克隆项目
cd /home/biostats
git clone https://github.com/your_username/biostats-terminator.git
cd biostats-terminator
```

### 5.2 创建生产环境配置

创建 `config/production.py`:
```python
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://biostats_user:your_password@localhost/biostats_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload
    UPLOAD_FOLDER = '/var/www/biostats/uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Email (for notifications)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # R Configuration
    R_EXECUTABLE = '/usr/bin/R'
    R_SCRIPTS_PATH = '/home/biostats/biostats-terminator/r_scripts'
```

### 5.3 设置环境变量

```bash
# 创建 .env 文件
cat > .env << 'EOF'
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://biostats_user:your_password@localhost/biostats_db
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
FLASK_ENV=production
EOF

# 保护 .env 文件
chmod 600 .env
```

### 5.4 安装Python依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements_production.txt

# 或手动安装
pip install flask flask-sqlalchemy flask-login flask-wtf \
    gunicorn psycopg2-binary pandas numpy scipy \
    matplotlib seaborn python-docx python-dotenv \
    celery redis
```

### 5.5 配置Gunicorn (WSGI服务器)

创建 `gunicorn_config.py`:
```python
import multiprocessing

# 服务器socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2

# 日志
accesslog = "/var/log/biostats/access.log"
errorlog = "/var/log/biostats/error.log"
loglevel = "info"

# 进程命名
proc_name = "biostats-terminator"

# 守护进程
daemon = False
pidfile = "/var/run/biostats/gunicorn.pid"
```

创建日志目录:
```bash
sudo mkdir -p /var/log/biostats
sudo chown biostats:biostats /var/log/biostats
sudo mkdir -p /var/run/biostats
sudo chown biostats:biostats /var/run/biostats
```

### 5.6 创建Systemd服务

创建 `/etc/systemd/system/biostats.service`:
```ini
[Unit]
Description=Biostats Terminator Web Application
After=network.target

[Service]
Type=notify
User=biostats
Group=biostats
WorkingDirectory=/home/biostats/biostats-terminator
Environment="PATH=/home/biostats/biostats-terminator/venv/bin"
EnvironmentFile=/home/biostats/biostats-terminator/.env
ExecStart=/home/biostats/biostats-terminator/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --bind 127.0.0.1:8000 \
    backend.final_server:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl start biostats
sudo systemctl enable biostats
sudo systemctl status biostats
```

---

## 6. Nginx配置

### 6.1 创建Nginx配置

创建 `/etc/nginx/sites-available/biostats`:
```nginx
# HTTP - 重定向到HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name biostat-terminator.com www.biostat-terminator.com;
    
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name biostat-terminator.com www.biostat-terminator.com;
    
    # SSL证书 (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/biostat-terminator.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/biostat-terminator.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 日志
    access_log /var/log/nginx/biostats_access.log;
    error_log /var/log/nginx/biostats_error.log;
    
    # 上传限制
    client_max_body_size 100M;
    
    # 静态文件
    location /static {
        alias /home/biostats/biostats-terminator/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /uploads {
        alias /var/www/biostats/uploads;
        internal;  # 只允许通过应用访问
    }
    
    # 代理到Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

启用站点:
```bash
sudo ln -s /etc/nginx/sites-available/biostats /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 7. HTTPS证书配置 (Let's Encrypt)

### 7.1 安装Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2 获取SSL证书

```bash
# 为域名申请证书
sudo certbot --nginx -d biostat-terminator.com -d www.biostat-terminator.com

# 按提示输入:
# 1. 邮箱地址
# 2. 同意服务条款
# 3. 是否接收新闻 (可选)
```

### 7.3 自动续期

```bash
# 测试自动续期
sudo certbot renew --dry-run

# Certbot会自动创建续期任务
sudo systemctl status certbot.timer
```

---

## 8. 域名解析配置

### 8.1 使用Cloudflare (推荐)

1. 注册 Cloudflare: https://dash.cloudflare.com/sign-up
2. 添加站点: `biostat-terminator.com`
3. 在域名注册商(Namecheap)修改DNS服务器为Cloudflare提供的:
   ```
   例如:
   austin.ns.cloudflare.com
   reza.ns.cloudflare.com
   ```

4. 在Cloudflare添加DNS记录:
   ```
   类型: A
   名称: @
   内容: your_server_ip
   代理状态: 已代理 (橙色云朵)
   
   类型: A
   名称: www
   内容: your_server_ip
   代理状态: 已代理
   ```

5. Cloudflare设置:
   - SSL/TLS: Full (strict)
   - 自动HTTPS重写: 开启
   - 始终使用HTTPS: 开启
   - 最小TLS版本: 1.2

---

## 9. 数据库迁移

### 9.1 从SQLite迁移到PostgreSQL

```bash
# 在服务器上
cd /home/biostats/biostats-terminator

# 激活虚拟环境
source venv/bin/activate

# 创建迁移脚本
python << 'EOF'
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# 连接SQLite
sqlite_conn = sqlite3.connect('database/biostats.db')
sqlite_conn.row_factory = sqlite3.Row

# 连接PostgreSQL
pg_conn = psycopg2.connect(
    dbname='biostats_db',
    user='biostats_user',
    password='your_password',
    host='localhost'
)

# 迁移每个表
tables = ['users', 'uploads', 'analyses', 'orders', 'membership_plans']

for table in tables:
    print(f"Migrating {table}...")
    
    # 从SQLite读取
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f"SELECT * FROM {table}")
    rows = sqlite_cursor.fetchall()
    
    if rows:
        # 获取列名
        columns = [description[0] for description in sqlite_cursor.description]
        
        # 写入PostgreSQL
        pg_cursor = pg_conn.cursor()
        
        # 构建INSERT语句
        cols = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        
        # 批量插入
        data = [tuple(row) for row in rows]
        execute_values(pg_cursor, query, data)
        pg_conn.commit()
        
        print(f"  Migrated {len(rows)} rows")

sqlite_conn.close()
pg_conn.close()
print("Migration completed!")
EOF
```

---

## 10. 监控与日志

### 10.1 设置日志轮转

创建 `/etc/logrotate.d/biostats`:
```
/var/log/biostats/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 biostats biostats
    sharedscripts
    postrotate
        systemctl reload biostats > /dev/null 2>&1 || true
    endscript
}
```

### 10.2 监控工具

```bash
# 安装监控工具
sudo apt install -y htop iotop nethogs

# 查看系统资源
htop

# 查看应用日志
sudo journalctl -u biostats -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/biostats_access.log
```

---

## 11. 防火墙配置

```bash
# 启用UFW
sudo ufw enable

# 允许SSH
sudo ufw allow 22/tcp

# 允许HTTP和HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 查看状态
sudo ufw status
```

---

## 12. 备份策略

### 12.1 创建备份脚本

创建 `/home/biostats/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/home/biostats/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -U biostats_user biostats_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/biostats/uploads

# 删除30天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

设置定时任务:
```bash
chmod +x /home/biostats/backup.sh

# 添加到crontab (每天凌晨2点)
crontab -e
# 添加: 0 2 * * * /home/biostats/backup.sh >> /var/log/biostats/backup.log 2>&1
```

---

## 13. 完整部署检查清单

- [ ] 域名已注册并配置DNS
- [ ] 服务器已购买并配置
- [ ] Python, R, PostgreSQL已安装
- [ ] GitHub仓库已创建并推送代码
- [ ] 生产环境配置已完成
- [ ] Gunicorn服务已启动
- [ ] Nginx已配置并运行
- [ ] SSL证书已安装
- [ ] 防火墙已配置
- [ ] 数据库已迁移
- [ ] 备份脚本已设置
- [ ] 日志轮转已配置
- [ ] 监控工具已安装

---

## 14. 访问测试

1. 访问: https://biostat-terminator.com
2. 测试注册功能
3. 测试文件上传
4. 测试统计分析
5. 检查性能和响应时间

---

## 15. 持续维护

### 每周
- 检查系统日志
- 检查磁盘空间
- 检查备份状态

### 每月
- 更新系统包: `sudo apt update && sudo apt upgrade`
- 更新Python包: `pip list --outdated`
- 检查SSL证书有效期
- 审查访问日志

### 按需
- 扩展服务器资源
- 优化数据库性能
- 更新应用代码

---

## 💡 成本估算

| 项目 | 费用 | 周期 |
|------|------|------|
| 域名 | $12 | 年 |
| 服务器 (DigitalOcean 4GB) | $24 | 月 |
| Cloudflare | $0 | 免费 |
| SSL证书 (Let's Encrypt) | $0 | 免费 |
| **总计 (第一年)** | **$300** | - |

---

## 🆘 故障排查

### 服务无法启动
```bash
sudo systemctl status biostats
sudo journalctl -u biostats -n 50
```

### 数据库连接失败
```bash
sudo -u postgres psql
\l  # 列出数据库
\du # 列出用户
```

### Nginx错误
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

---

**部署完成后，你的平台将可以通过 https://biostat-terminator.com 全球访问！** 🎉
