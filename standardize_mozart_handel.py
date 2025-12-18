# -*- coding: utf-8 -*-
import os
import json
import re
import datetime
import shutil

DATA_FILE = 'js/data.js'
BACKUP_DIR = 'backup'

# ==============================================================================
# 核心数据加载/保存函数 (从之前的调试中保留的最稳健版本)
# ==============================================================================

def load_data_and_log():
    """ 安全地从 data.js 加载 musicData 和 changeLog """
    music_data = []
    change_log = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        music_match = re.search(r'const\s+musicData\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if music_match:
            try:
                music_data = json.loads(music_match.group(1), strict=False)
            except json.JSONDecodeError as e:
                print(f"FATAL: Error decoding musicData JSON: {e}")
                return [], []
        
        log_match = re.search(r'const\s+changeLog\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if log_match:
            try:
                change_log = json.loads(log_match.group(1), strict=False)
            except json.JSONDecodeError as e:
                print(f"Warning: Error decoding changeLog JSON: {e}")
                
    return music_data, change_log

def save_all(music_data, change_log):
    """ 安全地保存 musicData 和 changeLog 到 data.js，并创建备份 """
    if os.path.exists(DATA_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"data_backup_{timestamp}_standardize.js")
        shutil.copy(DATA_FILE, backup_file)
        print(f"Data backed up to {backup_file}")

    music_data.sort(key=lambda x: x.get('id', 0), reverse=True)
    json_music = json.dumps(music_data, indent=4, ensure_ascii=False)
    json_log = json.dumps(change_log, indent=4, ensure_ascii=False)
    
    js_content = f"// Last updated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js_content += f"const musicData = {json_music};\n"
    js_content += f"const changeLog = {json_log};\n"
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Successfully saved standardized data to {DATA_FILE}")

# ==============================================================================
# 标准化规则
# ==============================================================================

MOZART_STANDARDIZATION_RULES = [
    {'keywords': ['figaro', '费加罗'], 'standard': 'Le Nozze di Figaro, K.492/费加罗的婚礼'},
    {'keywords': ['giovanni', '乔凡尼', '唐璜'], 'standard': 'Don Giovanni, K.527/唐璜'},
    {'keywords': ['cosi', 'così', '女人心'], 'standard': 'Così fan tutte, K.588/女人心'},
    {'keywords': ['zauberflöte', 'magic flute', '魔笛'], 'standard': 'Die Zauberflöte, K.620/魔笛'},
]

# ==============================================================================
# 主逻辑 (MAIN LOGIC)
# ==============================================================================

def main():
    music_data, change_log = load_data_and_log()
    if not music_data:
        print("Could not load music data. Exiting.")
        return

    mozart_updated_count = 0
    handel_updated_count = 0

    for item in music_data:
        composer = item.get("composer", "").lower()
        
        # --- 任务一: 莫扎特作品名标准化 ---
        if "mozart" in composer:
            work_title = item.get("work", "")
            if work_title:
                for rule in MOZART_STANDARDIZATION_RULES:
                    # 检查是否有任何一个关键词匹配
                    if any(keyword in work_title.lower() for keyword in rule['keywords']):
                        # 如果当前值不是标准值，则更新
                        if item.get("work") != rule['standard']:
                            print(f"Standardizing Mozart work for ID {item['id']}: '{item.get('work')}' -> '{rule['standard']}'")
                            item["work"] = rule['standard']
                            mozart_updated_count += 1
                        break # 匹配到第一个规则后即停止，防止多重匹配

        # --- 任务二: 亨德尔语言补全 ---
        if "handel" in composer or "händel" in composer or "亨德尔" in composer:
            lang = item.get("language", "").strip()
            if not lang or lang.lower() == 'n/a':
                print(f"Updating Handel language for ID {item['id']} ('{item['title']}') to '意大利语'")
                item["language"] = "意大利语"
                handel_updated_count += 1

    # --- 保存和报告 ---
    if mozart_updated_count > 0 or handel_updated_count > 0:
        print(f"\n--- Standardization Summary ---")
        print(f"Mozart works standardized: {mozart_updated_count}")
        print(f"Handel languages filled: {handel_updated_count}")
        
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        change_log.insert(0, {
            "date": today, 
            "type": "update", 
            "msg": f"数据标准化：更新 {mozart_updated_count} 条莫扎特作品名，填充 {handel_updated_count} 条亨德尔语言。"
        })
        if len(change_log) > 50: 
            change_log.pop()
        
        save_all(music_data, change_log)
    else:
        print("\nNo data entries required standardization based on the current rules.")

if __name__ == '__main__':
    main()
