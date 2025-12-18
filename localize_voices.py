# -*- coding: utf-8 -*-
import os
import json
import re
import datetime
import shutil

DATA_FILE = 'js/data.js'
BACKUP_DIR = 'backup'

def load_data_and_log():
    """ 从 data.js 加载 musicData 和 changeLog """
    music_data = []
    change_log = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 使用更稳健的、非贪婪的正则表达式
        music_match = re.search(r'const\s+musicData\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if music_match:
            try:
                music_data = json.loads(music_match.group(1), strict=False)
            except json.JSONDecodeError as e:
                print(f"Error decoding musicData: {e}")
        
        log_match = re.search(r'const\s+changeLog\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if log_match:
            try:
                change_log = json.loads(log_match.group(1), strict=False)
            except json.JSONDecodeError as e:
                print(f"Error decoding changeLog: {e}")
                
    return music_data, change_log

def save_all(music_data, change_log):
    """ 保存 musicData 和 changeLog 到 data.js，并创建备份 """
    if os.path.exists(DATA_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"data_backup_{timestamp}.js")
        shutil.copy(DATA_FILE, backup_file)
        print(f"Data backed up to {backup_file}")

    music_data.sort(key=lambda x: x['id'], reverse=True)
    json_music = json.dumps(music_data, indent=4, ensure_ascii=False)
    json_log = json.dumps(change_log, indent=4, ensure_ascii=False)
    
    js_content = f"// Last updated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js_content += f"const musicData = {json_music};\n"
    js_content += f"const changeLog = {json_log};\n"
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Successfully saved data to {DATA_FILE}")

def contains_chinese(text):
    """检查字符串是否包含中文字符"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def main():
    """
    主函数，用于汉化 voice_types 字段
    """
    music_data, change_log = load_data_and_log()
    if not music_data:
        print("Could not load music data. Exiting.")
        return

    # 用于汉化的映射表
    # key 使用小写以实现不区分大小写的匹配
    # value 是标准化的双语格式
    voice_translation_map = {
        "soprano": "Soprano/女高音",
        "mezzo-soprano": "Mezzo-soprano/次女高音",
        "alto": "Alto/女低音",
        "tenor": "Tenor/男高音",
        "baritone": "Baritone/男中音",
        "bass-baritone": "Bass-baritone/低男中音",
        "bass": "Bass/男低音",
    }

    updated_count = 0
    for item in music_data:
        original_voice_type = item.get("voice_types")

        # 如果字段为空或已包含中文，则跳过
        if not original_voice_type or contains_chinese(original_voice_type):
            continue

        # 将字段转为小写以进行不区分大小写的匹配
        normalized_voice = original_voice_type.lower().strip()

        if normalized_voice in voice_translation_map:
            new_voice_type = voice_translation_map[normalized_voice]
            # 仅在需要更新时才打印和计数
            if original_voice_type != new_voice_type:
                print(f"Updating ID {item['id']} ({item['title']}): '{original_voice_type}' -> '{new_voice_type}'")
                item["voice_types"] = new_voice_type
                updated_count += 1
    
    if updated_count > 0:
        print(f"\nFound and localized {updated_count} voice type entries.")
        # 添加一条更新日志
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        change_log.insert(0, {"date": today, "type": "update", "msg": f"汉化了 {updated_count} 个声部类型信息。"})
        if len(change_log) > 50: change_log.pop()
        
        save_all(music_data, change_log)
    else:
        print("No voice types found that require localization.")

if __name__ == '__main__':
    main()
