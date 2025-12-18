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
        
        # 使用稳健的、非贪婪的正则表达式
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
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
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

def main():
    """
    主函数，用于清理莫扎特咏叹调的 voice_types 字段
    """
    music_data, change_log = load_data_and_log()
    if not music_data:
        print("Could not load music data. Exiting.")
        return

    # 歌剧角色到声部类型的映射
    character_to_voice_type = {
        # Le nozze di Figaro
        "Count Almaviva": "Baritone", "The Countess Almaviva": "Soprano", "Susanna": "Soprano",
        "Figaro": "Bass-baritone", "Cherubino": "Mezzo-soprano", "Marcellina": "Mezzo-soprano",
        "Doctor Bartolo": "Bass", "Don Basilio": "Tenor", "Barbarina": "Soprano",

        # Don Giovanni
        "Don Giovanni": "Baritone", "Leporello": "Bass", "Donna Anna": "Soprano",
        "Don Ottavio": "Tenor", "Donna Elvira": "Soprano", "Zerlina": "Soprano",
        "Masetto": "Bass", "Commendatore": "Bass",

        # Die Zauberflöte
        "Tamino": "Tenor", "Pamina": "Soprano", "Papageno": "Baritone", "Papagena": "Soprano",
        "Sarastro": "Bass", "The Queen of the Night": "Soprano", "Monostatos": "Tenor",

        # Così fan tutte
        "Fiordiligi": "Soprano", "Dorabella": "Mezzo-soprano", "Guglielmo": "Baritone",
        "Ferrando": "Tenor", "Despina": "Soprano", "Don Alfonso": "Bass-baritone",

        # Idomeneo
        "Idomeneo": "Tenor", "Idamantes": "Mezzo-soprano", "Ilia": "Soprano",
        "Electra": "Soprano", "Arbaces": "Tenor",

        # Die Entführung aus dem Serail
        "Konstanze": "Soprano", "Belmonte": "Tenor", "Blondchen": "Soprano",
        "Pedrillo": "Tenor", "Osmin": "Bass",

        # La clemenza di Tito
        "Tito": "Tenor", "Vitellia": "Soprano", "Sextus": "Mezzo-soprano",
        "Annius": "Mezzo-soprano", "Servilia": "Soprano", "Publius": "Bass-baritone",
        
        # Zaide
        "Zaide": "Soprano", "Gomatz": "Tenor", "Allazim": "Bass", "Sultan Soliman": "Tenor",
        "Zaram": "Tenor", "Alonso": "Tenor", "Juan": "Tenor",

        # Bastien und Bastienne
        "Bastien": "Tenor", "Bastienne": "Soprano", "Colas": "Bass",

        # Der Schauspieldirektor
        "Madame Herz": "Soprano",
        "Madame Silberklang": "Soprano",
    }

    updated_count = 0
    for item in music_data:
        # 检查作曲家字段是否包含 "mozart"
        if "mozart" in item.get("composer", "").lower():
            current_voice = item.get("voice_types", "").strip()
            if current_voice in character_to_voice_type:
                new_voice = character_to_voice_type[current_voice]
                if item["voice_types"] != new_voice:
                    print(f"Updating ID {item['id']} ({item['title']}): '{current_voice}' -> '{new_voice}'")
                    item["voice_types"] = new_voice
                    updated_count += 1
    
    if updated_count > 0:
        print(f"\nFound and updated {updated_count} entries.")
        # 记录一条changelog
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        change_log.insert(0, {"date": today, "type": "update", "msg": f"批量更新了 {updated_count} 个莫扎特咏叹调的声部信息。"})
        if len(change_log) > 50: change_log.pop()
        
        save_all(music_data, change_log)
    else:
        print("No Mozart arias with character names in 'voice_types' field found to update.")

if __name__ == '__main__':
    main()
