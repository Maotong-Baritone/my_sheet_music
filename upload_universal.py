import os
import requests
import time
import json
import re

# === 配置区域 ===
API_KEY = "sk-8b158d13c0a64d97ac903bc0a8a975e3" 
API_URL = "https://api.deepseek.com/chat/completions"

BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
UPLOAD_URL = BASE_URL
ADMIN_USER = "admin"
ADMIN_PASS = "maotong2025"

# === 任务配置 ===
TASKS = [
    {
        "folder": "Rossini_Arias",
        "list_file": "Rossini_upload_list.txt",
        "composer_std": "Gioachino Rossini/罗西尼",
        "default_lang": "意大利语"
    },
    {
        "folder": "Donizetti_Arias",
        "list_file": "Donizetti_upload_list.txt",
        "composer_std": "Gaetano Donizetti/多尼采蒂",
        "default_lang": "意大利语"
    }
]

def translate_text(text, type="aria"):
    if not text or text == "N/A": return text
    # 简单的缓存
    if hasattr(translate_text, "cache"):
        if text in translate_text.cache: return translate_text.cache[text]
    else:
        translate_text.cache = {}

    print(f"   [AI翻译中] {text} ...", end="\r")
    
    prompt = f"将这个古典音乐{'咏叹调' if type=='aria' else '歌剧'}名称翻译成中文。格式严格为：原文/中文译名。不要解释。名称：{text}"
    
    try:
        resp = requests.post(API_URL, headers={"Authorization": f"Bearer {API_KEY}"}, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }, timeout=10)
        if resp.status_code == 200:
            res = resp.json()['choices'][0]['message']['content'].strip()
            # 清洗一下可能的 markdown
            res = res.replace("**", "").replace("`", "").strip()
            translate_text.cache[text] = res
            return res
    except:
        pass
    return text

def process_folder(task_config, session):
    folder = task_config["folder"]
    list_name = task_config["list_file"]
    composer_std = task_config["composer_std"]
    
    if not os.path.exists(folder):
        print(f"⚠️ 文件夹不存在: {folder} (跳过)")
        return

    list_path = os.path.join(folder, list_name)
    if not os.path.exists(list_path):
        print(f"⚠️ 清单文件不存在: {list_path} (跳过)")
        return

    print(f"\n📂 正在处理: {folder} ({composer_std})")
    
    with open(list_path, "r", encoding="utf-8") as f:
        lines = f.readlines()[2:] # 跳过表头
        total = len(lines)
        
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 5: continue
            
            aria, raw_composer, opera, voice, filename = parts
            
            file_path = os.path.join(folder, filename)
            if not os.path.exists(file_path):
                print(f"⚠️ 文件丢失: {filename}")
                continue

            # 翻译标题和作品名
            title_cn = translate_text(aria, "aria")
            work_cn = translate_text(opera, "opera")
            
            data = {
                'title': title_cn,
                'composer': composer_std,
                'work': work_cn,
                'category': "歌剧咏叹调",
                'voice_types': voice, # 已经在下载时清洗过了
                'language': task_config["default_lang"],
                'description': f"原文: {aria}\n出处: {opera}\nVoice: {voice}"
            }
            
            try:
                with open(file_path, 'rb') as pdf:
                    files = {'file': (filename, pdf, 'application/pdf')}
                    r = session.post(UPLOAD_URL, data=data, files=files)
                    if r.status_code == 200:
                        print(f"[{i+1}/{total}] ✅ {title_cn[:20]}... -> {work_cn}")
                    else:
                        print(f"[{i+1}/{total}] ❌ 上传失败: {r.status_code}")
            except Exception as e:
                print(f"❌ 错误: {e}")
                
            time.sleep(0.5)

def main():
    print("🚀 启动美声歌剧批量上传 (Rossini & Donizetti)...")
    
    # 登录
    session = requests.Session()
    try:
        r = session.post(LOGIN_URL, data={"username": ADMIN_USER, "password": ADMIN_PASS})
        if r.status_code != 200:
            print("❌ 登录失败，请检查服务器！")
            return
    except:
        print("❌ 连接服务器失败！")
        return

    for task in TASKS:
        process_folder(task, session)

    print("\n🎉 所有任务完成！")

if __name__ == "__main__":
    main()
