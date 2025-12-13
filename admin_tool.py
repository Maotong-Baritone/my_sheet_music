import os
import json
import datetime
import shutil
import re
from flask import Flask, render_template_string, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# === 配置 ===
SCORES_DIR = 'scores'      # 乐谱文件夹
DATA_FILE = 'js/data.js'   # 数据文件
ALLOWED_EXTENSIONS = {'pdf', 'midi', 'mp3', 'sib', 'musx'}

app = Flask(__name__)
app.secret_key = "admin_tool_key"

# 确保文件夹存在
if not os.path.exists(SCORES_DIR):
    os.makedirs(SCORES_DIR)

# --- 辅助函数：读取和写入 data.js ---
def load_data():
    """读取 js/data.js 并提取其中的 JSON 部分"""
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 用正则表达式提取 const musicData = [...] 中的 [...]
    match = re.search(r'const musicData = (\[.*?\]);', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            print("❌ 解析 JSON 失败，请检查 data.js 格式")
            return []
    return []

def save_data(new_list):
    """把列表写回 js/data.js"""
    # 按照 id 倒序排列（新的在前面）
    new_list.sort(key=lambda x: x['id'], reverse=True)
    
    json_str = json.dumps(new_list, indent=4, ensure_ascii=False)
    
    # 包装成 JS 格式
    js_content = f"// 最后更新于 {datetime.date.today()}\n"
    js_content += f"const musicData = {json_str};\n"
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 网页模板 (内嵌在代码里，方便单文件运行) ---
HTML_TEMPLATE = """
<!doctype html>
<html lang="zh">
<head>
    <meta charset="utf-8">
    <title>乐谱库管理工具</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body { background-color: #e9ecef; padding-top: 50px; }</style>
</head>
<body>
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">🎹 向静态库添加新乐谱</h4>
                </div>
                <div class="card-body">
                    {% with messages = get_flashed_messages() %}
                        {% if messages %}
                            <div class="alert alert-success">{{ messages[0] }}</div>
                        {% endif %}
                    {% endwith %}
                    
                    <form method="post" enctype="multipart/form-data">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">曲目名称 <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" name="title" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">作曲家 <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" name="composer" required>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">所属作品/歌剧 (选填)</label>
                                <input type="text" class="form-control" name="work">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">语言 (选填)</label>
                                <input type="text" class="form-control" name="language">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">作品分类</label>
                            <select class="form-select" name="category">
                                <option value="歌剧咏叹调">歌剧咏叹调</option>
                                <option value="艺术歌曲">艺术歌曲</option>
                                <option value="合唱作品">合唱作品</option>
                                <option value="器乐独奏">器乐独奏</option>
                                <option value="室内乐">室内乐</option>
                                <option value="其他">其他</option>
                            </select>
                        </div>
                        <div class="mb-4">
                            <label class="form-label">选择文件 (PDF/MIDI)</label>
                            <input type="file" class="form-control" name="file" required>
                            <div class="form-text">文件将自动归档到 scores/分类/ 文件夹下</div>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-success btn-lg">💾 保存并更新网站数据</button>
                        </div>
                    </form>
                </div>
                <div class="card-footer text-center text-muted">
                    添加完成后，关闭此窗口和黑框框，刷新 index.html 即可看到更新。
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        composer = request.form['composer']
        category = request.form['category']
        work = request.form.get('work', '')
        language = request.form.get('language', '')

        if file and allowed_file(file.filename):
            # 1. 处理文件保存路径
            # 自动创建分类子文件夹，例如 scores/歌剧咏叹调/
            category_dir = os.path.join(SCORES_DIR, category)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir)
            
            filename = secure_filename(file.filename)
            # 防止中文文件名被 secure_filename 删成空
            if not filename: 
                filename = f"file_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
            
            file.save(os.path.join(category_dir, filename))

            # 2. 读取旧数据
            data_list = load_data()
            
            # 3. 生成新 ID (取当前最大ID + 1)
            new_id = 1
            if data_list:
                new_id = max(item['id'] for item in data_list) + 1
            
            # 4. 构建新数据对象
            # 注意路径要用正斜杠 / 方便网页读取
            file_path = f"{category}/{filename}"
            
            new_item = {
                "id": new_id,
                "title": title,
                "composer": composer,
                "work": work,
                "language": language,
                "category": category,
                "filename": file_path,
                "date": datetime.date.today().strftime("%Y-%m-%d")
            }
            
            # 5. 追加并写入文件
            data_list.append(new_item)
            save_data(data_list)
            
            flash(f'成功添加: 《{title}》！文件已归档，data.js 已更新。可以继续添加。')
            return redirect(url_for('upload'))
            
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("启动管理工具... 请在浏览器访问 http://127.0.0.1:5000")
    app.run(debug=True)