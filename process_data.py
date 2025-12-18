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
        # 使用 'utf-8-sig' 来处理可能存在的BOM (字节顺序标记)
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 使用稳健的、非贪婪的正则表达式
        music_match = re.search(r'const\s+musicData\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if music_match:
            try:
                # 允许非法控制字符，因为源文件存在此问题
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
        backup_file = os.path.join(BACKUP_DIR, f"data_backup_{timestamp}_processed.js")
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
    print(f"Successfully saved processed data to {DATA_FILE}")

def contains_chinese(text):
    """检查字符串是否包含中文字符"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def main():
    music_data, change_log = load_data_and_log()
    if not music_data:
        print("Could not load music data. Exiting.")
        return

    # --- Pass 1: Clean Mozart Voice Types ---
    character_to_voice_type = {
        "Count Almaviva": "Baritone", "The Countess Almaviva": "Soprano", "Susanna": "Soprano",
        "Figaro": "Bass-baritone", "Cherubino": "Mezzo-soprano", "Marcellina": "Mezzo-soprano",
        "Doctor Bartolo": "Bass", "Don Basilio": "Tenor", "Barbarina": "Soprano",
        "Don Giovanni": "Baritone", "Leporello": "Bass", "Donna Anna": "Soprano",
        "Don Ottavio": "Tenor", "Donna Elvira": "Soprano", "Zerlina": "Soprano",
        "Masetto": "Bass", "Commendatore": "Bass", "Tamino": "Tenor", "Pamina": "Soprano",
        "Papageno": "Baritone", "Papagena": "Soprano", "Sarastro": "Bass", 
        "The Queen of the Night": "Soprano", "Monostatos": "Tenor", "Fiordiligi": "Soprano",
        "Dorabella": "Mezzo-soprano", "Guglielmo": "Baritone", "Ferrando": "Tenor",
        "Despina": "Soprano", "Don Alfonso": "Bass-baritone", "Idomeneo": "Tenor",
        "Idamantes": "Mezzo-soprano", "Ilia": "Soprano", "Electra": "Soprano", "Arbaces": "Tenor",
        "Konstanze": "Soprano", "Belmonte": "Tenor", "Blondchen": "Soprano",
        "Pedrillo": "Tenor", "Osmin": "Bass", "Tito": "Tenor", "Vitellia": "Soprano",
        "Sextus": "Mezzo-soprano", "Annius": "Mezzo-soprano", "Servilia": "Soprano",
        "Publius": "Bass-baritone", "Zaide": "Soprano", "Gomatz": "Tenor", "Allazim": "Bass",
        "Sultan Soliman": "Tenor", "Zaram": "Tenor", "Alonso": "Tenor", "Juan": "Tenor",
        "Bastien": "Tenor", "Bastienne": "Soprano", "Colas": "Bass",
        "Madame Herz": "Soprano", "Madame Silberklang": "Soprano"
    }
    
    cleaned_count = 0
    for item in music_data:
        if "mozart" in item.get("composer", "").lower():
            current_voice = item.get("voice_types", "").strip()
            if current_voice in character_to_voice_type:
                new_voice = character_to_voice_type[current_voice]
                if item["voice_types"] != new_voice:
                    item["voice_types"] = new_voice
                    cleaned_count += 1
    
    if cleaned_count > 0:
        print(f"Cleaned {cleaned_count} Mozart voice type entries.")

    # --- Pass 2: Localize All Voice Types ---
    voice_translation_map = {
        "soprano": "Soprano/女高音", "mezzo-soprano": "Mezzo-soprano/次女高音",
        "alto": "Alto/女低音", "tenor": "Tenor/男高音", "baritone": "Baritone/男中音",
        "bass-baritone": "Bass-baritone/低男中音", "bass": "Bass/男低音",
    }

    localized_count = 0
    for item in music_data:
        original_voice_type = item.get("voice_types")
        if not original_voice_type or contains_chinese(original_voice_type) or "/" in original_voice_type:
            continue

        normalized_voice = original_voice_type.lower().strip()
        if normalized_voice in voice_translation_map:
            new_voice_type = voice_translation_map[normalized_voice]
            if original_voice_type != new_voice_type:
                item["voice_types"] = new_voice_type
                localized_count += 1

    if localized_count > 0:
        print(f"Localized {localized_count} voice type entries.")

    # --- Save if any changes were made ---
    if cleaned_count > 0 or localized_count > 0:
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        change_log.insert(0, {"date": today, "type": "update", "msg": f"批量处理数据：清理 {cleaned_count} 条声部，汉化 {localized_count} 条声部。"})
        if len(change_log) > 50: change_log.pop()
        
        save_all(music_data, change_log)
    else:
        print("No data processing was necessary.")

if __name__ == '__main__':
    main()
