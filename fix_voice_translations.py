import json
import re
import os
import datetime

# === 配置 ===
DATA_FILE = 'js/data.js'
BACKUP_DIR = 'backup'

# === 声部中英对照表 ===
# 键为纯英文 (小写)，值为标准双语格式
VOICE_MAP = {
    "soprano": "Soprano/女高音",
    "mezzo-soprano": "Mezzo-soprano/次女高音",
    "mezzo": "Mezzo-soprano/次女高音", # 兼容简写
    "contralto": "Contralto/女低音",
    "tenor": "Tenor/男高音",
    "baritone": "Baritone/男中音",
    "bass": "Bass/男低音",
    "bass-baritone": "Bass-Baritone/低男中音"
}

def fix_voice_translations():
    print(f"📂 正在读取 {DATA_FILE} ...")
    if not os.path.exists(DATA_FILE):
        print("❌ 错误：找不到数据文件！")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f: content = f.read()

    match_data = re.search(r'const musicData = (\[.*?\]);', content, re.DOTALL)
    match_log = re.search(r'const changeLog = (\[.*?\]);', content, re.DOTALL)
    if not match_data: return

    music_data = json.loads(match_data.group(1))
    change_log = json.loads(match_log.group(1)) if match_log else []

    # 备份
    if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(BACKUP_DIR, f"data_backup_trans_fix_{timestamp}.js"), 'w', encoding='utf-8') as f:
        f.write(content)

    count = 0
    print("\n🚀 开始全局汉化声部标签...")

    for item in music_data:
        original_voice = item.get('voice_types', '').strip()
        voice_lower = original_voice.lower()

        # 如果已经是双语格式（包含斜杠或中文），则跳过
        if '/' in original_voice or re.search(r'[\u4e00-\u9fa5]', original_voice):
            continue

        # 检查是否在映射表中
        if voice_lower in VOICE_MAP:
            target_voice = VOICE_MAP[voice_lower]
            
            # 执行替换
            if original_voice != target_voice:
                # print(f"  [汉化] {item['title']}: '{original_voice}' -> '{target_voice}'") # 调试用
                item['voice_types'] = target_voice
                count += 1
        
        # 处理可能的 "Role (Voice)" 格式残留，提取 Voice 并汉化
        # 例如: "Adina (Soprano)" -> "Soprano/女高音"
        elif "(" in voice_lower and ")" in voice_lower:
             for key, val in VOICE_MAP.items():
                 if key in voice_lower:
                     item['voice_types'] = val
                     count += 1
                     print(f"  [清洗并汉化] {original_voice} -> {val}")
                     break

    if count > 0:
        print(f"\n✅ 成功汉化了 {count} 条声部数据！")
        
        # 记录日志
        change_log.insert(0, {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 
            "type": "update", 
            "msg": f"批量补全声部中文翻译 ({count} 条)。"
        })
        
        # 写入文件
        music_data.sort(key=lambda x: x['id'], reverse=True)
        new_content = f"// 最后更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Voice Trans)\n"
        new_content += f"const musicData = {json.dumps(music_data, indent=4, ensure_ascii=False)};\n"
        new_content += f"const changeLog = {json.dumps(change_log, indent=4, ensure_ascii=False)};\n"

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("🎉 data.js 已更新，现在所有声部都带有中文了！")
    else:
        print("\n⚠️ 未发现纯英文声部，数据库可能已经很完美了。")

if __name__ == "__main__":
    fix_voice_translations()