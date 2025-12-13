import os
import json
import datetime
import re
from flask import Flask, render_template_string, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# === 配置 ===
SCORES_DIR = 'scores'
DATA_FILE = 'js/data.js'
ALLOWED_EXTENSIONS = {'pdf', 'midi', 'mp3', 'sib', 'musx'}

app = Flask(__name__)
app.secret_key = "admin_tool_key"

if not os.path.exists(SCORES_DIR):
    os.makedirs(SCORES_DIR)

# --- 数据处理 ---
def load_data():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'const musicData = (\[.*?\]);', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return []
    return []

def save_data(new_list):
    new_list.sort(key=lambda x: x['id'], reverse=True)
    json_str = json.dumps(new_list, indent=4, ensure_ascii=False)
    js_content = f"// 最后更新于 {datetime.date.today()}\nconst musicData = {json_str};\n"
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- HTML 模板 ---
HTML_TEMPLATE = """
<!doctype html>
<html lang="zh">
<head>
    <meta charset="utf-8">
    <title>乐谱库后台管理</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 20px; }
        .nav-tabs .nav-link.active { font-weight: bold; border-top: 3px solid #0d6efd; }
    </style>
</head>
<body>
<div class="container">
    <h2 class="mb-4 text-center">🎹 乐谱库后台管理</h2>
    
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
                    <div class="col-md-6">
                        <label class="form-label">所属作品/歌剧</label>
                        <input type="text" class="form-control" name="work">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">语言</label>
                        <input type="text" class="form-control" name="language">
                    </div>
                </div>
                
                <div class="row mb-3 p-3 bg-light rounded border mx-0">
                    <div class="col-12 mb-2"><small class="text-primary fw-bold">👥 重唱/合唱信息 (选填)</small></div>
                    <div class="col-md-6">
                        <label class="form-label small">声部数量/类型</label>
                        <input type="text" class="form-control" name="voice_count" placeholder="如：二重唱, 三重唱, 混声合唱">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small">声部编制 (SATB简写)</label>
                        <input type="text" class="form-control" name="voice_types" placeholder="如：TB, ST, SATB, SSAA">
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
                        <th class="ps-3">曲名</th>
                        <th>作曲家</th>
                        <th>分类</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td class="ps-3 fw-bold">
                            {{ item.title }}
                            {% if item.voice_types %}
                                <br><span class="badge bg-secondary" style="font-size:0.6rem">{{ item.voice_types }}</span>
                            {% endif %}
                        </td>
                        <td>{{ item.composer }}</td>
                        <td><span class="badge bg-light text-dark border">{{ item.category }}</span></td>
                        <td>
                            <a href="/edit/{{ item.id }}" class="btn btn-sm btn-outline-primary">✏️ 编辑</a>
                            <a href="/delete/{{ item.id }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('确定要删除吗？')">🗑️ 删除</a>
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
                    <div class="col-md-6">
                        <label class="form-label">所属作品/歌剧</label>
                        <input type="text" class="form-control" name="work" value="{{ item.work }}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">语言</label>
                        <input type="text" class="form-control" name="language" value="{{ item.language }}">
                    </div>
                </div>

                <div class="row mb-3 p-3 bg-light rounded border mx-0">
                    <div class="col-12 mb-2"><small class="text-primary fw-bold">👥 重唱/合唱信息 (选填)</small></div>
                    <div class="col-md-6">
                        <label class="form-label small">声部数量/类型</label>
                        <input type="text" class="form-control" name="voice_count" value="{{ item.voice_count if item.voice_count else '' }}" placeholder="如：二重唱">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small">声部编制 (SATB简写)</label>
                        <input type="text" class="form-control" name="voice_types" value="{{ item.voice_types if item.voice_types else '' }}" placeholder="如：TB, SATB">
                    </div>
                </div>

                {% include 'category_select.html' %}
                
                <div class="d-flex justify-content-between mt-4">
                    <a href="/manage" class="btn btn-secondary">取消</a>
                    <button type="submit" class="btn btn-primary">💾 保存修改</button>
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
            <option value="独唱片段/选段" {{ 'selected' if current == '独唱片段/选段' else '' }}>独唱片段/选段 (Solo Excerpts)</option>
            <option value="----------" disabled>----------</option>
            <option value="歌剧重唱" {{ 'selected' if current == '歌剧重唱' else '' }}>歌剧重唱 (Ensembles)</option>
            <option value="清唱剧重唱" {{ 'selected' if current == '清唱剧重唱' else '' }}>清唱剧重唱</option>
            <option value="艺术歌曲重唱" {{ 'selected' if current == '艺术歌曲重唱' else '' }}>艺术歌曲重唱 (Duets/Trios)</option>
            <option value="----------" disabled>----------</option>
            <option value="合唱作品" {{ 'selected' if current == '合唱作品' else '' }}>合唱作品</option>
        </optgroup>
        <optgroup label="🎻 器乐作品 (Instrumental)">
            <option value="器乐独奏" {{ 'selected' if current == '器乐独奏' else '' }}>器乐独奏</option>
            <option value="室内乐" {{ 'selected' if current == '室内乐' else '' }}>室内乐</option>
        </optgroup>
        <optgroup label="🎼 总谱 (Full Scores)">
            <option value="歌剧总谱" {{ 'selected' if current == '歌剧总谱' else '' }}>歌剧总谱</option>
            <option value="管弦乐/交响曲" {{ 'selected' if current == '管弦乐/交响曲' else '' }}>管弦乐/交响曲</option>
            <option value="协奏曲总谱" {{ 'selected' if current == '协奏曲总谱' else '' }}>协奏曲总谱</option>
            <option value="宗教/声乐总谱" {{ 'selected' if current == '宗教/声乐总谱' else '' }}>宗教/声乐总谱 (弥撒/清唱剧等)</option>
        </optgroup>
        <option value="其他" {{ 'selected' if current == '其他' else '' }}>其他</option>
    </select>
</div>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        composer = request.form['composer']
        category = request.form['category']
        work = request.form.get('work', '')
        language = request.form.get('language', '')
        # 获取新字段
        voice_count = request.form.get('voice_count', '')
        voice_types = request.form.get('voice_types', '')

        if file and allowed_file(file.filename):
            category_dir = os.path.join(SCORES_DIR, category)
            if not os.path.exists(category_dir): os.makedirs(category_dir)
            
            filename = secure_filename(file.filename)
            if not filename: filename = f"file_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
            file.save(os.path.join(category_dir, filename))

            data = load_data()
            new_id = 1 if not data else max(i['id'] for i in data) + 1
            file_path = f"{category}/{filename}"
            
            data.append({
                "id": new_id, "title": title, "composer": composer,
                "work": work, "language": language, "category": category,
                "voice_count": voice_count, "voice_types": voice_types, # 保存新字段
                "filename": file_path, "date": datetime.date.today().strftime("%Y-%m-%d")
            })
            save_data(data)
            flash(f'成功添加: {title}')
            return redirect(url_for('index'))

    return render_template_string(HTML_TEMPLATE.replace("{% include 'category_select.html' %}", CATEGORY_SELECT_HTML), active_tab='upload', item=None)

@app.route('/manage')
def manage():
    query = request.args.get('q', '').lower()
    data = load_data()
    if query:
        data = [i for i in data if query in i['title'].lower() or query in i['composer'].lower()]
    return render_template_string(HTML_TEMPLATE, active_tab='manage', items=data, query=query)

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    data = load_data()
    item = next((i for i in data if i['id'] == item_id), None)
    if not item: return "找不到条目", 404

    if request.method == 'POST':
        item['title'] = request.form['title']
        item['composer'] = request.form['composer']
        item['work'] = request.form['work']
        item['language'] = request.form['language']
        item['category'] = request.form['category']
        # 更新新字段
        item['voice_count'] = request.form['voice_count']
        item['voice_types'] = request.form['voice_types']
        
        save_data(data)
        flash(f'更新成功: {item["title"]}')
        return redirect(url_for('manage'))

    return render_template_string(HTML_TEMPLATE.replace("{% include 'category_select.html' %}", CATEGORY_SELECT_HTML), active_tab='edit', item=item)

@app.route('/delete/<int:item_id>')
def delete(item_id):
    data = load_data()
    data = [i for i in data if i['id'] != item_id]
    save_data(data)
    flash('删除成功')
    return redirect(url_for('manage'))

if __name__ == '__main__':
    print("后台管理启动: http://127.0.0.1:5000")
    app.run(debug=True)