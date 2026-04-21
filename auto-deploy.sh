#!/bin/bash

################################################################################
# Biostats终结者 - 全自动一键部署脚本
# 服务器IP: 43.134.3.158
# 云服务商: 腾讯云
# 
# 使用方法：复制整个脚本到服务器终端，粘贴后按回车
################################################################################

set -e  # 遇到错误立即停止

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_step() {
    echo -e "${BLUE}[步骤 $1/8]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      Biostats终结者 - 全自动部署脚本                        ║"
echo "║      服务器IP: 43.134.3.158                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
sleep 2

# ============================================================================
# 步骤1: 更新系统
# ============================================================================
print_step 1 "更新系统软件包..."
apt update -qq > /dev/null 2>&1
print_success "系统软件包更新完成"
sleep 1

# ============================================================================
# 步骤2: 安装Docker
# ============================================================================
print_step 2 "安装Docker..."

if command -v docker &> /dev/null; then
    print_info "Docker已安装，跳过..."
else
    print_info "正在下载并安装Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh 2>&1 | grep -v "^$" || true
    sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    print_success "Docker安装完成"
fi
sleep 1

# ============================================================================
# 步骤3: 安装Docker Compose
# ============================================================================
print_step 3 "安装Docker Compose..."

if command -v docker-compose &> /dev/null; then
    print_info "Docker Compose已安装，跳过..."
else
    apt install -y docker-compose > /dev/null 2>&1
    print_success "Docker Compose安装完成"
fi
sleep 1

# ============================================================================
# 步骤4: 创建项目目录
# ============================================================================
print_step 4 "创建项目目录..."
mkdir -p /opt/biostats
cd /opt/biostats
print_success "项目目录创建完成: /opt/biostats"
sleep 1

# ============================================================================
# 步骤5: 创建应用文件
# ============================================================================
print_step 5 "创建应用文件..."

# 创建Flask应用
cat > app.py << 'PYTHON_EOF'
from flask import Flask, jsonify, request
import socket
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    hostname = socket.gethostname()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Biostats终结者 - 专业生物统计分析平台</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 800px;
                width: 100%;
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
            }}
            .content {{
                padding: 40px;
            }}
            .status {{
                background: #d4edda;
                border: 2px solid #28a745;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .status-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .status-text {{
                font-size: 24px;
                color: #28a745;
                font-weight: bold;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .info-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }}
            .info-label {{
                font-size: 12px;
                color: #6c757d;
                text-transform: uppercase;
                margin-bottom: 8px;
                font-weight: 600;
            }}
            .info-value {{
                font-size: 18px;
                color: #333;
                font-weight: 500;
            }}
            .features {{
                background: #f8f9fa;
                padding: 30px;
                border-radius: 10px;
            }}
            .features h3 {{
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.5em;
            }}
            .feature-list {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }}
            .feature-item {{
                display: flex;
                align-items: center;
                padding: 10px;
                background: white;
                border-radius: 8px;
            }}
            .feature-icon {{
                font-size: 24px;
                margin-right: 10px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                font-size: 14px;
            }}
            @media (max-width: 768px) {{
                .header h1 {{
                    font-size: 1.8em;
                }}
                .info-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔬 Biostats终结者</h1>
                <p>Professional Biostatistics Analysis Platform</p>
            </div>
            
            <div class="content">
                <div class="status">
                    <div class="status-icon">✅</div>
                    <div class="status-text">部署成功！服务器运行正常</div>
                </div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-label">云服务商</div>
                        <div class="info-value">腾讯云</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">服务器IP</div>
                        <div class="info-value">43.134.3.158</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">服务器主机</div>
                        <div class="info-value">{hostname}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">部署时间</div>
                        <div class="info-value">{now}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">配置</div>
                        <div class="info-value">2核 4GB</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">系统</div>
                        <div class="info-value">Ubuntu 22.04</div>
                    </div>
                </div>
                
                <div class="features">
                    <h3>📊 核心功能（即将上线）</h3>
                    <div class="feature-list">
                        <div class="feature-item">
                            <span class="feature-icon">📈</span>
                            <span>8种统计分析方法</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">👥</span>
                            <span>用户认证系统</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">📁</span>
                            <span>文件上传管理</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">🐍</span>
                            <span>Python分析引擎</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">📊</span>
                            <span>R统计引擎</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">📝</span>
                            <span>报告自动生成</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>🎉 恭喜！Biostats终结者已成功部署到腾讯云</p>
                <p>完整功能即将上线 | Powered by Docker & Flask</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'server': 'Tencent Cloud',
        'ip': '43.134.3.158',
        'hostname': socket.gethostname(),
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/info')
def info():
    return jsonify({
        'name': 'Biostats终结者',
        'description': 'Professional Biostatistics Analysis Platform',
        'cloud': 'Tencent Cloud',
        'cpu': '2 vCPUs',
        'memory': '4GB',
        'storage': '80GB SSD'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
PYTHON_EOF

print_success "应用文件创建完成"
sleep 1

# ============================================================================
# 步骤6: 创建Dockerfile
# ============================================================================
print_step 6 "创建Docker配置..."

cat > Dockerfile << 'DOCKER_EOF'
FROM python:3.11-slim

LABEL maintainer="Biostats Terminator Team"
LABEL description="Professional Biostatistics Analysis Platform"

WORKDIR /app

# 使用清华镜像加速
RUN pip install --no-cache-dir flask gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY app.py .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "app:app"]
DOCKER_EOF

print_success "Docker配置创建完成"
sleep 1

# ============================================================================
# 步骤7: 构建并启动容器
# ============================================================================
print_step 7 "构建并启动Docker容器..."

# 停止旧容器（如果存在）
if docker ps -a | grep -q biostats; then
    print_info "停止旧容器..."
    docker stop biostats > /dev/null 2>&1 || true
    docker rm biostats > /dev/null 2>&1 || true
fi

# 构建镜像
print_info "构建Docker镜像..."
docker build -t biostats-app:latest . > /dev/null 2>&1

# 运行容器
print_info "启动容器..."
docker run -d \
    --name biostats \
    --restart unless-stopped \
    -p 8000:8000 \
    biostats-app:latest > /dev/null 2>&1

# 等待容器启动
sleep 3

print_success "Docker容器启动完成"
sleep 1

# ============================================================================
# 步骤8: 安装并配置Nginx
# ============================================================================
print_step 8 "安装并配置Nginx..."

# 安装Nginx
if ! command -v nginx &> /dev/null; then
    print_info "安装Nginx..."
    apt install -y nginx > /dev/null 2>&1
    print_success "Nginx安装完成"
else
    print_info "Nginx已安装，配置中..."
fi

# 创建Nginx配置
cat > /etc/nginx/sites-available/biostats << 'NGINX_EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    access_log /var/log/nginx/biostats_access.log;
    error_log /var/log/nginx/biostats_error.log;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
}
NGINX_EOF

# 启用配置
ln -sf /etc/nginx/sites-available/biostats /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t > /dev/null 2>&1

# 重启Nginx
systemctl restart nginx > /dev/null 2>&1
systemctl enable nginx > /dev/null 2>&1

print_success "Nginx配置完成"
sleep 1

# ============================================================================
# 验证部署
# ============================================================================
echo ""
echo "════════════════════════════════════════════════════════════"
echo "   正在验证部署..."
echo "════════════════════════════════════════════════════════════"
sleep 2

# 检查Docker容器
if docker ps | grep -q biostats; then
    print_success "Docker容器运行正常"
else
    echo -e "${RED}❌ Docker容器未运行${NC}"
fi

# 检查Nginx
if systemctl is-active --quiet nginx; then
    print_success "Nginx运行正常"
else
    echo -e "${RED}❌ Nginx未运行${NC}"
fi

# 测试本地访问
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "应用响应正常"
else
    echo -e "${RED}❌ 应用无响应${NC}"
fi

# ============================================================================
# 显示部署结果
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 🎉 部署完成！                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 部署信息："
echo "   服务器IP: 43.134.3.158"
echo "   云服务商: 腾讯云"
echo "   配置: 2核 4GB"
echo ""
echo "🌐 访问地址："
echo "   主页: http://43.134.3.158"
echo "   主页(带端口): http://43.134.3.158:8000"
echo "   健康检查: http://43.134.3.158/health"
echo ""
echo "🐳 Docker状态："
docker ps | grep biostats || echo "   容器未运行"
echo ""
echo "💡 常用命令："
echo "   查看日志: docker logs -f biostats"
echo "   重启应用: docker restart biostats"
echo "   停止应用: docker stop biostats"
echo "   启动应用: docker start biostats"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "现在请在浏览器中访问: http://43.134.3.158"
echo "════════════════════════════════════════════════════════════"
echo ""
