#!/usr/bin/env python3
"""
Biostats终结者 - 完整生产服务器
Full Production Server with Integrated Python Analyzer
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session, send_file
import sqlite3
import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import secrets
from werkzeug.utils import secure_filename
import traceback

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# 导入分析引擎
try:
    from python_analyzer import BiostatsAnalyzer
    ANALYZER_AVAILABLE = True
    print("✅ Python分析引擎已加载")
except Exception as e:
    ANALYZER_AVAILABLE = False
    print(f"⚠️  分析引擎加载失败: {e}")

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['DATABASE'] = str(project_root / 'database' / 'biostats.db')
app.config['UPLOAD_FOLDER'] = str(project_root / 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# 确保目录存在
Path(app.config['DATABASE']).parent.mkdir(exist_ok=True, parents=True)
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True, parents=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'txt'}

def get_db():
    """获取数据库连接"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """初始化数据库"""
    db = get_db()
    
    # [数据库创建代码保持不变...]
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            institution TEXT,
            phone TEXT,
            membership_level TEXT DEFAULT 'free',
            membership_expiry TEXT,
            credits INTEGER DEFAULT 10,
            total_analyses INTEGER DEFAULT 0,
            total_uploads INTEGER DEFAULT 0,
            storage_used INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT,
            rows INTEGER,
            columns INTEGER,
            description TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            upload_id INTEGER,
            method TEXT NOT NULL,
            method_name TEXT,
            parameters TEXT,
            status TEXT DEFAULT 'pending',
            result_stdout TEXT,
            result_stderr TEXT,
            result_json TEXT,
            execution_time REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (upload_id) REFERENCES uploads (id)
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            product_type TEXT NOT NULL,
            product_name TEXT,
            amount REAL NOT NULL,
            final_amount REAL NOT NULL,
            payment_status TEXT DEFAULT 'pending',
            payment_time TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS membership_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            price_monthly REAL DEFAULT 0,
            price_yearly REAL DEFAULT 0,
            credits_monthly INTEGER DEFAULT 0,
            max_file_size INTEGER DEFAULT 5242880,
            max_storage INTEGER DEFAULT 52428800,
            is_active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        )
    ''')
    
    # 插入默认套餐
    plans = [
        ('free', '免费版', '体验基础功能', 0, 0, 10, 5*1024*1024, 50*1024*1024, 1, 1),
        ('basic', '基础版', '适合个人研究者', 99, 999, 100, 50*1024*1024, 500*1024*1024, 1, 2),
        ('premium', '专业版', '适合科研团队', 299, 2999, 500, 200*1024*1024, 2*1024*1024*1024, 1, 3),
        ('enterprise', '企业版', '适合医院和研究机构', 999, 9999, 0, 1024*1024*1024, 10*1024*1024*1024, 1, 4)
    ]
    
    for plan in plans:
        db.execute('''
            INSERT OR IGNORE INTO membership_plans 
            (name, display_name, description, price_monthly, price_yearly, 
             credits_monthly, max_file_size, max_storage, is_active, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', plan)
    
    # 创建管理员账户
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    db.execute('''
        INSERT OR IGNORE INTO users 
        (username, email, password_hash, full_name, is_admin, membership_level, credits)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('admin', 'admin@biostats.com', admin_password, '系统管理员', 1, 'enterprise', 99999))
    
    db.commit()
    db.close()
    return True

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== 路由 ====================

@app.route('/')
def index():
    html = f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Biostats终结者 - 专业生物统计分析云平台</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .navbar {{ background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .nav-content {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
            .logo {{ font-size: 1.5rem; font-weight: 700; color: #667eea; text-decoration: none; }}
            .nav-links a {{ margin-left: 2rem; text-decoration: none; color: #333; font-weight: 500; }}
            .btn {{ padding: 0.75rem 1.5rem; border-radius: 8px; background: #667eea; color: white; border: none; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; }}
            .hero {{ color: white; text-align: center; padding: 6rem 2rem; }}
            .hero h1 {{ font-size: 3.5rem; margin-bottom: 1.5rem; }}
            .features {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; max-width: 1000px; margin: 4rem auto; }}
            .feature {{ background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 12px; backdrop-filter: blur(10px); }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="nav-content">
                <a href="/" class="logo">🔬 Biostats终结者</a>
                <div class="nav-links">
                    <a href="/">首页</a>
                    {'<a href="/dashboard">控制台</a><a href="/logout">登出</a>' if session.get('user_id') else '<a href="/login">登录</a><a href="/register" class="btn">注册</a>'}
                </div>
            </div>
        </nav>
        <div class="hero">
            <h1>让生物统计分析<br>变得简单高效</h1>
            <p style="font-size: 1.25rem; margin-bottom: 2rem;">基于Python的专业分析引擎，支持8种统计方法</p>
            <a href="/register" class="btn" style="font-size: 1.125rem; padding: 1rem 2.5rem;">🚀 开始免费试用</a>
            <div class="features">
                <div class="feature"><div style="font-size: 3rem;">📊</div><h3>8种分析方法</h3><p>描述统计、t检验、方差分析等</p></div>
                <div class="feature"><div style="font-size: 3rem;">⚡</div><h3>Python引擎</h3><p>快速准确的统计计算</p></div>
                <div class="feature"><div style="font-size: 3rem;">☁️</div><h3>云端存储</h3><p>安全存储数据和结果</p></div>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
        
        if existing:
            error = '用户名或邮箱已被注册'
        else:
            password_hash = hash_password(password)
            db.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                      (username, email, password_hash))
            db.commit()
            db.close()
            return redirect(url_for('login') + '?registered=1')
        db.close()
    
    return f'''
    <html><head><meta charset="UTF-8"><title>注册</title>
    <style>* {{margin:0;padding:0;box-sizing:border-box;}}
    body {{font-family:sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;}}
    .container {{background:white;padding:3rem;border-radius:16px;width:100%;max-width:400px;}}
    h2 {{text-align:center;margin-bottom:2rem;}}
    .form-group {{margin-bottom:1.5rem;}}
    label {{display:block;margin-bottom:0.5rem;font-weight:500;}}
    input {{width:100%;padding:0.875rem;border:2px solid #e0e0e0;border-radius:8px;}}
    .btn {{width:100%;padding:1rem;background:#667eea;color:white;border:none;border-radius:8px;font-weight:600;cursor:pointer;}}
    .alert {{padding:1rem;border-radius:8px;margin-bottom:1rem;background:#fee;color:#c33;}}
    </style></head><body>
    <div class="container"><h2>🔬 注册</h2>
    {'<div class="alert">' + error + '</div>' if error else ''}
    <form method="POST">
    <div class="form-group"><label>用户名 *</label><input type="text" name="username" required></div>
    <div class="form-group"><label>邮箱 *</label><input type="email" name="email" required></div>
    <div class="form-group"><label>密码 *</label><input type="password" name="password" required minlength="6"></div>
    <button type="submit" class="btn">注册并获得10次免费分析</button>
    </form>
    <div style="text-align:center;margin-top:1.5rem;"><p>已有账户？<a href="/login" style="color:#667eea;">立即登录</a></p></div>
    </div></body></html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    registered = request.args.get('registered')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = hash_password(password)
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE (username = ? OR email = ?) AND password_hash = ?',
                         (username, username, password_hash)).fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            db.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now().isoformat(), user['id']))
            db.commit()
            db.close()
            return redirect(url_for('dashboard'))
        else:
            error = '用户名或密码错误'
        db.close()
    
    return f'''
    <html><head><meta charset="UTF-8"><title>登录</title>
    <style>* {{margin:0;padding:0;}}body {{font-family:sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;}}
    .container {{background:white;padding:3rem;border-radius:16px;max-width:400px;}}
    input {{width:100%;padding:0.875rem;border:2px solid #e0e0e0;border-radius:8px;margin-bottom:1rem;}}
    .btn {{width:100%;padding:1rem;background:#667eea;color:white;border:none;border-radius:8px;font-weight:600;}}
    .alert {{padding:1rem;border-radius:8px;margin-bottom:1rem;}}
    .success {{background:#dfd;color:#060;}}.error {{background:#fee;color:#c33;}}
    </style></head><body>
    <div class="container"><h2 style="text-align:center;margin-bottom:2rem;">🔬 登录</h2>
    {'<div class="alert success">注册成功！请登录</div>' if registered else ''}
    {'<div class="alert error">' + error + '</div>' if error else ''}
    <form method="POST">
    <input type="text" name="username" placeholder="用户名或邮箱" required>
    <input type="password" name="password" placeholder="密码" required>
    <button type="submit" class="btn">登录</button>
    </form>
    <div style="text-align:center;margin-top:1.5rem;">
    <p>演示: admin / admin123</p>
    <p style="margin-top:1rem;"><a href="/register" style="color:#667eea;">立即注册</a></p>
    </div></div></body></html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    uploads_count = db.execute('SELECT COUNT(*) as count FROM uploads WHERE user_id = ?', (session['user_id'],)).fetchone()['count']
    analyses_count = db.execute('SELECT COUNT(*) as count FROM analyses WHERE user_id = ?', (session['user_id'],)).fetchone()['count']
    db.close()
    
    return f'''
    <html><head><meta charset="UTF-8"><title>控制台</title>
    <style>* {{margin:0;padding:0;}}body {{font-family:sans-serif;background:#f5f7fa;}}
    .navbar {{background:white;padding:1rem 2rem;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin-bottom:2rem;}}
    .nav-content {{max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;}}
    .logo {{font-size:1.5rem;font-weight:700;color:#667eea;}}
    .container {{max-width:1200px;margin:0 auto;padding:0 2rem;}}
    .welcome {{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:3rem;border-radius:16px;margin-bottom:2rem;}}
    .stats {{display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem;margin-bottom:2rem;}}
    .stat-card {{background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);}}
    .stat-value {{font-size:2rem;font-weight:700;color:#667eea;margin:0.5rem 0;}}
    .actions {{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;}}
    .action-card {{background:white;padding:2rem;border-radius:12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.1);}}
    .btn {{padding:0.75rem 1.5rem;background:#667eea;color:white;border:none;border-radius:8px;text-decoration:none;display:inline-block;font-weight:600;}}
    </style></head><body>
    <nav class="navbar"><div class="nav-content"><div class="logo">🔬 Biostats终结者</div>
    <div><span>{user['username']}</span> | <a href="/logout" style="margin-left:1rem;color:#667eea;text-decoration:none;">登出</a></div>
    </div></nav>
    <div class="container">
    <div class="welcome"><h1>欢迎回来，{user['full_name'] or user['username']}！</h1>
    <p style="margin-top:1rem;">会员：<strong>{user['membership_level']}</strong> | 剩余次数：<strong>{user['credits']}</strong></p></div>
    <div class="stats">
    <div class="stat-card"><div style="color:#666;font-size:0.875rem;">总分析次数</div><div class="stat-value">{analyses_count}</div></div>
    <div class="stat-card"><div style="color:#666;font-size:0.875rem;">上传文件</div><div class="stat-value">{uploads_count}</div></div>
    <div class="stat-card"><div style="color:#666;font-size:0.875rem;">剩余次数</div><div class="stat-value">{user['credits']}</div></div>
    <div class="stat-card"><div style="color:#666;font-size:0.875rem;">存储使用</div><div class="stat-value">{round(user['storage_used']/1024/1024,1)} MB</div></div>
    </div>
    <h2 style="margin-bottom:1.5rem;">快速操作</h2>
    <div class="actions">
    <div class="action-card"><div style="font-size:3rem;margin-bottom:1rem;">📊</div><h3>开始分析</h3>
    <p style="color:#666;margin:1rem 0;">上传数据并执行统计分析</p><a href="/analysis" class="btn">立即开始</a></div>
    <div class="action-card"><div style="font-size:3rem;margin-bottom:1rem;">📁</div><h3>文件管理</h3>
    <p style="color:#666;margin:1rem 0;">查看和管理您的数据文件</p><a href="/files" class="btn">查看文件</a></div>
    <div class="action-card"><div style="font-size:3rem;margin-bottom:1rem;">📜</div><h3>分析历史</h3>
    <p style="color:#666;margin:1rem 0;">查看所有分析记录</p><a href="/history" class="btn">查看历史</a></div>
    </div>
    <div style="background:#d1f2eb;padding:1.5rem;border-radius:12px;margin-top:2rem;border-left:4px solid:#00d97e;">
    <strong>✅ Python分析引擎已启用</strong> - 所有8种统计方法可用！</div>
    </div></body></html>
    '''

@app.route('/analysis')
def analysis_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user_files = db.execute('SELECT * FROM uploads WHERE user_id = ? ORDER BY uploaded_at DESC',
                           (session['user_id'],)).fetchall()
    db.close()
    
    files_options = ''.join([f'<option value="{f["id"]}">{f["original_filename"]}</option>' for f in user_files])
    
    return f'''
    <html><head><meta charset="UTF-8"><title>数据分析</title>
    <style>* {{margin:0;padding:0;}}body {{font-family:sans-serif;background:#f5f7fa;}}
    .navbar {{background:white;padding:1rem 2rem;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin-bottom:2rem;}}
    .container {{max-width:1200px;margin:0 auto;padding:0 2rem;}}
    .card {{background:white;padding:2rem;border-radius:12px;margin-bottom:2rem;box-shadow:0 2px 8px rgba(0,0,0,0.05);}}
    select,input {{width:100%;padding:0.875rem;border:2px solid #e0e0e0;border-radius:8px;margin-bottom:1rem;}}
    .btn {{padding:1rem 2rem;background:#667eea;color:white;border:none;border-radius:8px;font-weight:600;cursor:pointer;}}
    .result {{background:#f8f9fa;padding:1.5rem;border-radius:8px;white-space:pre-wrap;font-family:monospace;max-height:500px;overflow-y:auto;}}
    </style></head><body>
    <nav class="navbar"><div style="max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;">
    <div style="font-size:1.5rem;font-weight:700;color:#667eea;">🔬 Biostats终结者</div>
    <a href="/dashboard" style="color:#667eea;text-decoration:none;">← 返回控制台</a></div></nav>
    <div class="container">
    <h1 style="margin-bottom:2rem;">📊 数据分析</h1>
    <div class="card"><h3>选择分析方法和数据</h3><br>
    <form id="analysisForm">
    <label>分析方法:</label>
    <select name="method" id="method" required>
    <option value="descriptive">描述性统计</option>
    <option value="ttest">t检验</option>
    <option value="anova">方差分析(ANOVA)</option>
    <option value="chi_square">卡方检验</option>
    <option value="correlation">相关分析</option>
    <option value="regression">线性回归</option>
    <option value="normality">正态性检验</option>
    <option value="nonparametric">非参数检验</option>
    </select>
    <label>选择数据文件:</label>
    <select name="upload_id" required>{files_options or '<option>请先上传文件</option>'}</select>
    <div id="params"></div>
    <button type="submit" class="btn" {'disabled' if not files_options else ''}>开始分析</button>
    </form></div>
    <div class="card" id="resultCard" style="display:none;">
    <h3>分析结果</h3><br>
    <div id="result" class="result"></div>
    </div>
    </div>
    <script>
    document.getElementById('analysisForm').onsubmit = async (e) => {{
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        document.getElementById('resultCard').style.display = 'block';
        document.getElementById('result').textContent = '正在分析...';
        
        const response = await fetch('/api/analyze', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify(data)
        }});
        
        const result = await response.json();
        if(result.success) {{
            document.getElementById('result').textContent = result.report || JSON.stringify(result, null, 2);
        }} else {{
            document.getElementById('result').textContent = '错误: ' + result.error;
        }}
    }};
    </script>
    </body></html>
    '''

@app.route('/files')
def files():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user_files = db.execute('SELECT * FROM uploads WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 20',
                           (session['user_id'],)).fetchall()
    db.close()
    
    files_html = ''.join([f'''
    <div style="background:white;padding:1.5rem;border-radius:8px;margin-bottom:1rem;">
    <h4>📄 {f['original_filename']}</h4>
    <p style="color:#666;font-size:0.875rem;">上传: {f['uploaded_at']} | 大小: {round(f['file_size']/1024,1)} KB</p>
    </div>
    ''' for f in user_files])
    
    return f'''
    <html><head><meta charset="UTF-8"><title>文件管理</title>
    <style>body {{font-family:sans-serif;background:#f5f7fa;margin:0;}}
    .navbar {{background:white;padding:1rem 2rem;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin-bottom:2rem;}}
    .container {{max-width:1200px;margin:0 auto;padding:0 2rem;}}
    .card {{background:white;padding:2rem;border-radius:12px;margin-bottom:2rem;}}
    .btn {{padding:0.75rem 1.5rem;background:#667eea;color:white;border:none;border-radius:8px;cursor:pointer;}}
    </style></head><body>
    <nav class="navbar"><div style="max-width:1200px;margin:0 auto;"><a href="/dashboard" style="color:#667eea;text-decoration:none;">← 返回</a></div></nav>
    <div class="container">
    <h1 style="margin-bottom:2rem;">📁 文件管理</h1>
    <div class="card"><h3>上传新文件</h3><br>
    <form id="uploadForm" enctype="multipart/form-data">
    <input type="file" id="fileInput" name="file" accept=".csv,.xlsx,.xls,.txt" style="margin-bottom:1rem;">
    <button type="submit" class="btn">上传</button>
    </form>
    <div id="uploadResult" style="margin-top:1rem;"></div>
    </div>
    <h3>我的文件 ({len(user_files)})</h3>
    {files_html if user_files else '<p style="color:#666;text-align:center;padding:2rem;">暂无文件</p>'}
    </div>
    <script>
    document.getElementById('uploadForm').onsubmit = async (e) => {{
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', document.getElementById('fileInput').files[0]);
        const response = await fetch('/api/upload', {{method:'POST',body:formData}});
        const result = await response.json();
        document.getElementById('uploadResult').innerHTML = result.success ?
            '<div style="background:#dfd;padding:1rem;border-radius:8px;">上传成功！</div>' :
            '<div style="background:#fee;padding:1rem;border-radius:8px;">失败: ' + result.error + '</div>';
        if(result.success) setTimeout(() => location.reload(), 1500);
    }};
    </script>
    </body></html>
    '''

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    analyses = db.execute('SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 20',
                         (session['user_id'],)).fetchall()
    db.close()
    
    history_html = ''.join([f'''
    <div style="background:white;padding:1.5rem;border-radius:8px;margin-bottom:1rem;">
    <h4>📊 {a['method_name'] or a['method']}</h4>
    <p style="color:#666;font-size:0.875rem;">时间: {a['created_at']} | 状态: <span style="color:{'#28a745' if a['status']=='success' else '#dc3545'};">{a['status']}</span></p>
    </div>
    ''' for a in analyses])
    
    return f'''
    <html><head><meta charset="UTF-8"><title>分析历史</title>
    <style>body {{font-family:sans-serif;background:#f5f7fa;margin:0;}}
    .navbar {{background:white;padding:1rem 2rem;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin-bottom:2rem;}}
    .container {{max-width:1200px;margin:0 auto;padding:0 2rem;}}
    </style></head><body>
    <nav class="navbar"><div style="max-width:1200px;margin:0 auto;"><a href="/dashboard" style="color:#667eea;text-decoration:none;">← 返回</a></div></nav>
    <div class="container">
    <h1 style="margin-bottom:2rem;">📜 分析历史</h1>
    {history_html if analyses else '<p style="color:#666;text-align:center;padding:2rem;background:white;border-radius:12px;">暂无记录</p>'}
    </div></body></html>
    '''

# ==================== API ====================

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件'}), 400
    
    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'success': False, 'error': '文件格式不支持'}), 400
    
    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{session['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        
        db = get_db()
        db.execute('''INSERT INTO uploads (user_id, filename, original_filename, file_path, file_size, file_type)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], unique_filename, filename, filepath, file_size,
                   filename.rsplit('.', 1)[1].lower()))
        db.execute('UPDATE users SET total_uploads = total_uploads + 1, storage_used = storage_used + ? WHERE id = ?',
                  (file_size, session['user_id']))
        db.commit()
        db.close()
        
        return jsonify({'success': True, 'filename': unique_filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'}), 401
    
    if not ANALYZER_AVAILABLE:
        return jsonify({'success': False, 'error': '分析引擎未加载'}), 500
    
    try:
        data = request.json
        method = data.get('method')
        upload_id = data.get('upload_id')
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if user['credits'] <= 0 and user['membership_level'] != 'enterprise':
            return jsonify({'success': False, 'error': '分析次数不足'})
        
        upload = db.execute('SELECT * FROM uploads WHERE id = ? AND user_id = ?',
                           (upload_id, session['user_id'],)).fetchone()
        if not upload:
            return jsonify({'success': False, 'error': '文件不存在'})
        
        # 创建分析记录
        cursor = db.execute('''INSERT INTO analyses (user_id, upload_id, method, method_name, status)
                             VALUES (?, ?, ?, ?, 'running')''',
                           (session['user_id'], upload_id, method, BiostatsAnalyzer.METHODS.get(method, method)))
        analysis_id = cursor.lastrowid
        db.commit()
        
        # 执行分析
        analyzer = BiostatsAnalyzer()
        start_time = datetime.now()
        
        # 根据不同方法准备参数
        kwargs = {}
        if method == 'ttest':
            kwargs = {'test_type': 'independent', 'var1': data.get('var1'), 'group_var': data.get('group_var')}
        elif method == 'anova':
            kwargs = {'dependent_var': data.get('dependent_var'), 'group_var': data.get('group_var')}
        elif method == 'correlation':
            kwargs = {'variables': data.get('variables', []).split(',') if isinstance(data.get('variables'), str) else data.get('variables', [])}
        elif method == 'regression':
            kwargs = {'dependent_var': data.get('dependent_var'), 'independent_vars': data.get('independent_vars', []).split(',') if isinstance(data.get('independent_vars'), str) else data.get('independent_vars', [])}
        
        result = analyzer.analyze(method, upload['file_path'], **kwargs)
        end_time = datetime.now()
        
        # 更新分析记录
        db.execute('''UPDATE analyses SET status = ?, result_json = ?, execution_time = ?, completed_at = ?
                     WHERE id = ?''',
                  ('success' if result['success'] else 'failed',
                   json.dumps(result),
                   (end_time - start_time).total_seconds(),
                   end_time.isoformat(),
                   analysis_id))
        
        if result['success']:
            db.execute('UPDATE users SET credits = credits - 1, total_analyses = total_analyses + 1 WHERE id = ? AND credits > 0',
                      (session['user_id'],))
        
        db.commit()
        db.close()
        
        return jsonify(result)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def main():
    if not os.path.exists(app.config['DATABASE']):
        print("\n初始化数据库...")
        init_db()
        print("✅ 完成\n")
    
    print("=" * 70)
    print("Biostats终结者 - 完整生产服务器")
    print("=" * 70)
    print("\n✅ 服务器已启动")
    print("\n访问: http://127.0.0.1:9000")
    print("\n默认账户: admin / admin123")
    print("\n功能:")
    print("  ✅ 用户注册登录")
    print("  ✅ 文件上传管理")
    print("  ✅ Python统计分析(8种方法)")
    print("  ✅ 分析历史记录")
    print("  ✅ SQLite数据库")
    print("\n按 Ctrl+C 停止")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=9000, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()
