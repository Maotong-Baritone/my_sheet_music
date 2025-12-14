import os
import json
import datetime
import re
import shutil
import time
from functools import wraps
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

# === ⚙️ 配置区域 (可在此修改) ===
SCORES_DIR = 'scores'          # 乐谱存放目录
DATA_FILE = 'js/data.js'       # 数据文件路径
BACKUP_DIR = 'backup'          # 备份目录
ALLOWED_EXTENSIONS = {'pdf', 'midi', 'mp3', 'sib', 'musx'}

# 🔐 后台登录账号密码
ADMIN_USER = 'admin'
ADMIN_PASS = 'maotong2025'     # 建议修改此密码

app = Flask(__name__)
app.secret_key = "maotong_secret_key_2025" # 用于加密 Session

# 确保目录存在
for folder in [SCORES_DIR, BACKUP_DIR, 'js']:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- 🔐 登录验证装饰器 ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- 💾 数据处理与备份 ---
def load_data_and_log():
    music_data = []
    change_log = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        match_data = re.search(r'const musicData = (\[.*?\]);', content, re.DOTALL)
        if match_data:
            try: music_data = json.loads(match_data.group(1))
            except: pass
        match_log = re.search(r'const changeLog = (\[.*?\]);', content, re.DOTALL)
        if match_log:
            try: change_log = json.loads(match_log.group(1))
            except: pass
    return music_data, change_log

def save_all(music_data, change_log):
    # 1. 先进行备份
    if os.path.exists(DATA_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"data_backup_{timestamp}.js")
        shutil.copy(DATA_FILE, backup_path)
        print(f"备份已创建: {backup_path}")

    # 2. 写入新数据
    music_data.sort(key=lambda x: x['id'], reverse=True)
    json_music = json.dumps(music_data, indent=4, ensure_ascii=False)
    json_log = json.dumps(change_log, indent=4, ensure_ascii=False)
    
    js_content = f"// 最后更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js_content += f"const musicData = {json_music};\n"
    js_content += f"const changeLog = {json_log};\n"
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)

def add_log(change_log, action_type, message):
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = {"date": today, "type": action_type, "msg": message}
    change_log.insert(0, new_entry)
    if len(change_log) > 50: change_log.pop()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 🖥️ HTML 模板 ---
LOGIN_HTML = """
<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>管理员登录</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body { background: #f0f2f5; display: flex; align-items: center; justify-content: center; height: 100vh; }
    .card { width: 100%; max-width: 400px; border: none; shadow: 0 4px 12px rgba(0,0,0,0.1); }
</style>
</head>
<body>
<div class="card p-4">
    <h3 class="text-center mb-4">🎹 后台登录</h3>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div class="alert alert-danger">{{ messages[0] }}</div>
        {% endif %}
    {% endwith %}
    <form method="post">
        <div class="mb-3">
            <label class="form-label">账号</label>
            <input type="text" name="username" class="form-control" required>
        </div>
        <div class="mb-3">
            <label class="form-label">密码</label>
            <input type="password" name="password" class="form-control" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">进入系统</button>
    </form>
</div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!doctype html>
<html lang="zh">
<head>
    <meta charset="utf-8">
    <title>乐谱库后台管理</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 20px; padding-bottom: 50px; }
        .nav-tabs .nav-link.active { font-weight: bold; border-top: 3px solid #0d6efd; }
    </style>
</head>
<body>
<div class="container">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>🎹 乐谱库后台管理</h2>
        <a href="/logout" class="btn btn-outline-danger btn-sm">退出登录</a>
    </div>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div class="alert alert-success">{{ messages[0] }}</div>
        {% endif %}
    {% endwith %}

    <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
            <a class="nav-link {{ 'active' if active_tab == 'upload' else '' }}" href="/">📤 上传新乐谱</a>
        </li>
        <li class="nav-item">
            <a class="nav-link {{ 'active' if active_tab == 'manage' else '' }}" href="/manage">📋 管理与编辑</a>
        </li>
    </ul>

    {% if active_tab == 'upload' %}
    <div class="card shadow">
        <div class="card-body">
            <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="action" value="upload">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">曲名 *</label>
                        <input type="text" class="form-control" name="title" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">作曲家 *</label>
                        <input type="text" class="form-control" name="composer" required>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-4">
                        <label class="form-label">所属作品/歌剧</label>
                        <input type="text" class="form-control" name="work">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">语言</label>
                        <input type="text" class="form-control" name="language">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label fw-bold text-primary">调性 (Key)</label>
                        <input type="text" class="form-control" name="tonality" placeholder="如: F Major">
                    </div>
                </div>
                
                <div class="row mb-3 p-3 bg-light rounded border mx-0">
                    <div class="col-12 mb-2"><small class="text-primary fw-bold">🎻 编制与声部信息 (选填)</small></div>
                    <div class="col-md-6">
                        <label class="form-label small">声部/乐器编制</label>
                        <input type="text" class="form-control" name="voice_types" placeholder="如: Soprano, SATB">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small">数量/类型补充</label>
                        <input type="text" class="form-control" name="voice_count" placeholder="如: 二重唱">
                    </div>
                </div>

                {% include 'category_select.html' %}

                <div class="mb-4">
                    <label class="form-label">文件 (PDF/MIDI) *</label>
                    <input type="file" class="form-control" name="file" required>
                </div>
                <div class="d-grid">
                    <button type="submit" class="btn btn-success">保存并发布</button>
                </div>
            </form>
        </div>
    </div>
    {% endif %}

    {% if active_tab == 'manage' %}
    <div class="card shadow">
        <div class="card-header bg-white">
            <form class="d-flex" action="/manage" method="get">
                <input class="form-control me-2" type="search" name="q" placeholder="搜素曲名、作曲家..." value="{{ query }}">
                <button class="btn btn-primary" type="submit">搜索</button>
            </form>
        </div>
        <div class="card-body p-0">
            <table class="table table-striped table-hover mb-0 align-middle">
                <thead class="table-light">
                    <tr>
                        <th class="ps-3">曲名 / 调性</th>
                        <th>作曲家</th>
                        <th>分类</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td class="ps-3">
                            <div class="fw-bold">{{ item.title }}</div>
                            {% if item.tonality %}
                                <span class="badge bg-warning text-dark" style="font-size:0.6rem">{{ item.tonality }}</span>
                            {% endif %}
                        </td>
                        <td>{{ item.composer }}</td>
                        <td><small class="text-muted">{{ item.category }}</small></td>
                        <td>
                            <a href="/edit/{{ item.id }}" class="btn btn-sm btn-outline-primary">✏️</a>
                            <a href="/delete/{{ item.id }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('确定要删除吗？')">🗑️</a>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="4" class="text-center p-4">没有找到数据</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    {% if active_tab == 'edit' %}
    <div class="card shadow">
        <div class="card-header bg-warning">
            <h5 class="mb-0">✏️ 编辑乐谱信息</h5>
        </div>
        <div class="card-body">
            <form method="post">
                <input type="hidden" name="action" value="update">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">曲名</label>
                        <input type="text" class="form-control" name="title" value="{{ item.title }}" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">作曲家</label>
                        <input type="text" class="form-control" name="composer" value="{{ item.composer }}" required>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-4">
                        <label class="form-label">所属作品/歌剧</label>
                        <input type="text" class="form-control" name="work" value="{{ item.work }}">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">语言</label>
                        <input type="text" class="form-control" name="language" value="{{ item.language }}">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label fw-bold text-primary">调性 (Key)</label>
                        <input type="text" class="form-control" name="tonality" value="{{ item.tonality if item.tonality else '' }}">
                    </div>
                </div>

                <div class="row mb-3 p-3 bg-light rounded border mx-0">
                    <div class="col-12 mb-2"><small class="text-primary fw-bold">🎻 编制与声部信息</small></div>
                    <div class="col-md-6">
                        <label class="form-label small">声部/乐器编制</label>
                        <input type="text" class="form-control" name="voice_types" value="{{ item.voice_types if item.voice_types else '' }}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small">数量/类型补充</label>
                        <input type="text" class="form-control" name="voice_count" value="{{ item.voice_count if item.voice_count else '' }}">
                    </div>
                </div>

                {% include 'category_select.html' %}
                
                <div class="d-flex justify-content-between mt-4">
                    <a href="/manage" class="btn btn-secondary">取消</a>
                    <button type="submit" class="btn btn-primary">💾 保存修改并记录日志</button>
                </div>
            </form>
        </div>
    </div>
    {% endif %}
</div>
</body>
</html>
"""

CATEGORY_SELECT_HTML = """
<div class="mb-3">
    <label class="form-label">作品分类</label>
    <select class="form-select" name="category">
        {% set current = item.category if item else '' %}
        <optgroup label="🎤 声乐作品 (Vocal)">
            <option value="歌剧咏叹调" {{ 'selected' if current == '歌剧咏叹调' else '' }}>歌剧咏叹调</option>
            <option value="清唱剧咏叹调" {{ 'selected' if current == '清唱剧咏叹调' else '' }}>清唱剧咏叹调</option>
            <option value="康塔塔咏叹调" {{ 'selected' if current == '康塔塔咏叹调' else '' }}>康塔塔咏叹调</option>
            <option value="艺术歌曲" {{ 'selected' if current == '艺术歌曲' else '' }}>艺术歌曲</option>
            <option value="音乐剧选段" {{ 'selected' if current == '音乐剧选段' else '' }}>音乐剧选段 (Musical)</option>
            <option value="独唱片段/选段" {{ 'selected' if current == '独唱片段/选段' else '' }}>独唱片段/选段 (Solo Excerpts)</option>
            <option value="----------" disabled>----------</option>
            <option value="歌剧重唱" {{ 'selected' if current == '歌剧重唱' else '' }}>歌剧重唱 (Ensembles)</option>
            <option value="音乐剧重唱" {{ 'selected' if current == '音乐剧重唱' else '' }}>音乐剧重唱 (Musical Ensembles)</option>
            <option value="清唱剧重唱" {{ 'selected' if current == '清唱剧重唱' else '' }}>清唱剧重唱</option>
            <option value="艺术歌曲重唱" {{ 'selected' if current == '艺术歌曲重唱' else '' }}>艺术歌曲重唱 (Duets/Trios)</option>
            <option value="----------" disabled>----------</option>
            <option value="合唱作品" {{ 'selected' if current == '合唱作品' else '' }}>合唱作品</option>
        </optgroup>
        <optgroup label="📚 曲集与套曲 (Collections)">
            <option value="声乐套曲" {{ 'selected' if current == '声乐套曲' else '' }}>声乐套曲 (Song Cycles)</option>
            <option value="乐谱书/曲集" {{ 'selected' if current == '乐谱书/曲集' else '' }}>乐谱书/曲集 (Songbooks/Anthologies)</option>
        </optgroup>
        <optgroup label="🎻 器乐作品 (Instrumental)">
            <option value="器乐独奏" {{ 'selected' if current == '器乐独奏' else '' }}>器乐独奏</option>
            <option value="室内乐" {{ 'selected' if current == '室内乐' else '' }}>室内乐</option>
        </optgroup>
        <optgroup label="🎼 总谱 (Full Scores)">
            <option value="歌剧总谱" {{ 'selected' if current == '歌剧总谱' else '' }}>歌剧总谱</option>
            <option value="管弦乐/交响曲" {{ 'selected' if current == '管弦乐/交响曲' else '' }}>管弦乐/交响曲</option>
            <option value="协奏曲总谱" {{ 'selected' if current == '协奏曲总谱' else '' }}>协奏曲总谱</option>
            <option value="宗教声乐作品总谱" {{ 'selected' if current == '宗教声乐作品总谱' else '' }}>宗教声乐作品总谱 (弥撒/清唱剧等)</option>
        </optgroup>
        <option value="其他" {{ 'selected' if current == '其他' else '' }}>其他</option>
    </select>
</div>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('账号或密码错误')
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        composer = request.form['composer']
        category = request.form['category']
        work = request.form.get('work', '')
        language = request.form.get('language', '')
        voice_count = request.form.get('voice_count', '')
        voice_types = request.form.get('voice_types', '')
        tonality = request.form.get('tonality', '')

        if file and allowed_file(file.filename):
            category_dir = os.path.join(SCORES_DIR, category)
            if not os.path.exists(category_dir): os.makedirs(category_dir)
            
            ext = file.filename.rsplit('.', 1)[1].lower()
            safe_name = secure_filename(file.filename)
            timestamp_name = f"{int(time.time())}_{safe_name}" if safe_name else f"{int(time.time())}.{ext}"
            
            file.save(os.path.join(category_dir, timestamp_name))

            music_data, change_log = load_data_and_log()
            
            new_id = 1 if not music_data else max(i['id'] for i in music_data) + 1
            file_path = f"{category}/{timestamp_name}"
            
            music_data.append({
                "id": new_id, "title": title, "composer": composer,
                "work": work, "language": language, "category": category,
                "voice_count": voice_count, "voice_types": voice_types,
                "tonality": tonality,
                "filename": file_path, "date": datetime.date.today().strftime("%Y-%m-%d")
            })
            
            add_log(change_log, 'add', f"添加了新乐谱：《{title}》 ({composer})")
            save_all(music_data, change_log)
            
            flash(f'成功添加: {title}')
            return redirect(url_for('index'))

    return render_template_string(HTML_TEMPLATE.replace("{% include 'category_select.html' %}", CATEGORY_SELECT_HTML), active_tab='upload', item=None)

@app.route('/manage')
@login_required
def manage():
    query = request.args.get('q', '').lower()
    music_data, _ = load_data_and_log()
    if query:
        music_data = [i for i in music_data if query in i['title'].lower() or query in i['composer'].lower()]
    return render_template_string(HTML_TEMPLATE, active_tab='manage', items=music_data, query=query)

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    music_data, change_log = load_data_and_log()
    item = next((i for i in music_data if i['id'] == item_id), None)
    if not item: return "找不到条目", 404

    if request.method == 'POST':
        item['title'] = request.form['title']
        item['composer'] = request.form['composer']
        item['work'] = request.form['work']
        item['language'] = request.form['language']
        item['category'] = request.form['category']
        item['voice_count'] = request.form['voice_count']
        item['voice_types'] = request.form['voice_types']
        item['tonality'] = request.form['tonality']
        
        add_log(change_log, 'update', f"更新了乐谱信息：《{item['title']}》")
        save_all(music_data, change_log)
        flash(f'更新成功: {item["title"]}')
        return redirect(url_for('manage'))

    return render_template_string(HTML_TEMPLATE.replace("{% include 'category_select.html' %}", CATEGORY_SELECT_HTML), active_tab='edit', item=item)

@app.route('/delete/<int:item_id>')
@login_required
def delete(item_id):
    music_data, change_log = load_data_and_log()
    target = next((i for i in music_data if i['id'] == item_id), None)
    if target:
        music_data = [i for i in music_data if i['id'] != item_id]
        add_log(change_log, 'delete', f"移除了乐谱：《{target['title']}》 ({target['composer']})")
        save_all(music_data, change_log)
        flash('删除成功')
    return redirect(url_for('manage'))

if __name__ == '__main__':
    print("后台管理启动: http://127.0.0.1:5000")
    print("请使用浏览器访问，默认账号: admin，密码: maotong2025")
    app.run(debug=True)