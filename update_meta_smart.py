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
                print(f"Error decoding musicData: {e}")
        
        log_match = re.search(r'const\s+changeLog\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if log_match:
            try:
                change_log = json.loads(log_match.group(1), strict=False)
            except json.JSONDecodeError as e:
                print(f"Error decoding changeLog: {e}")
                
    return music_data, change_log

def save_all(music_data, change_log):
    """ 安全地保存 musicData 和 changeLog 到 data.js，并创建备份 """
    if os.path.exists(DATA_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"data_backup_{timestamp}_meta_update.js")
        shutil.copy(DATA_FILE, backup_file)
        print(f"Data backed up to {backup_file}")

    music_data.sort(key=lambda x: x.get('id', 0), reverse=True)
    json_music = json.dumps(music_data, indent=4, ensure_ascii=False)
    json_log = json.dumps(change_log, indent=4, ensure_ascii=False)
    
    js_content = f"// Last updated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js_content += f"const musicData = {json_music};\n"
    js_content += f"const changeLog = {json_log};\n"
    
    # 使用 'utf-8' 编码而非 'utf-8-sig' 来写入，以避免每次都写入BOM
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Successfully saved processed data to {DATA_FILE}")

# ==============================================================================
# 元数据知识库 (METADATA KNOWLEDGE BASE)
# ==============================================================================

WORK_TO_LANGUAGE_MAP = {
    # 莫扎特 (Mozart)
    "Le nozze di Figaro": "意大利语", "Don Giovanni": "意大利语", "Così fan tutte": "意大利语",
    "Idomeneo": "意大利语", "La clemenza di Tito": "意大利语",
    "Die Zauberflöte": "德语", "Die Entführung aus dem Serail": "德语", "Zaide": "德语",
    "Der Schauspieldirektor": "德语", "Bastien und Bastienne": "德语",
    "Exsultate, jubilate": "拉丁语", "Requiem": "拉丁语", "Mass": "拉丁语", "Missa": "拉丁语",

    # 亨德尔 (Handel) - 歌剧
    "Giulio Cesare": "意大利语", "Rinaldo": "意大利语", "Serse": "意大利语", "Alcina": "意大利语",
    "Agrippina": "意大利语", "Rodelinda": "意大利语", "Tamerlano": "意大利语", "Orlando": "意大利语",
    "Ariodante": "意大利语", "Partenope": "意大利语", "Admeto": "意大利语", "Tolomeo": "意大利语",

    # 亨德尔 (Handel) - 清唱剧
    "Messiah": "英语", "Samson": "英语", "Semele": "英语", "Theodora": "英语",
    "Judas Maccabaeus": "英语", "Saul": "英语", "Israel in Egypt": "英语", "Jephtha": "英语",
    "Alexander's Feast": "英语", "Acis and Galatea": "英语",

    # 其他作曲家
    "Carmen": "法语", "Faust": "法语", "Hérodiade": "法语", "Les Contes d'Hoffmann": "法语",
    "Manon": "法语", "Roméo et Juliette": "法语", "Hamlet": "法语", "Don Quichotte": "法语",
    "La traviata": "意大利语", "Rigoletto": "意大利语", "Aida": "意大利语", "Don Carlo": "意大利语",
    "Il barbiere di Siviglia": "意大利语", "La Cenerentola": "意大利语",
    "La bohème": "意大利语", "Tosca": "意大利语", "Madama Butterfly": "意大利语",
    "Andrea Chénier": "意大利语", "Pagliacci": "意大利语", "Il Tabarro": "意大利语",
    "Eugene Onegin": "俄语", "Queen of Spades": "俄语",
    "Der Ring des Nibelungen": "德语", "Tristan und Isolde": "德语", "Tannhäuser": "德语",
    "Der Freischütz": "德语", "Fidelio": "德语",
}

# Key: 咏叹调标题的干净、小写版本
HANDEL_ARIA_TO_VOICE_MAP = {
    # Countertenor / Mezzo
    "ombra mai fu": "Countertenor/假声男高音", "verdi prati": "Countertenor/假声男高音",
    "cara sposa, amante cara": "Countertenor/假声男高音", "venti, turbini": "Countertenor/假声男高音",
    "va tacito e nascosto": "Countertenor/假声男高音", "svegliatevi nel core": "Countertenor/假声男高音",
    "sta nell'ircana": "Countertenor/假声男高音",
    "he was despised": "Alto/女低音",

    # Soprano
    "lascia ch'io pianga": "Soprano/女高音", "piangerò la sorte mia": "Soprano/女高音",
    "tornami a vagheggiar": "Soprano/女高音", "ah, mio cor": "Soprano/女高音",
    "v'adoro, pupille": "Soprano/女高音", "se pietà di me non senti": "Soprano/女高音",
    "da tempeste il legno infranto": "Soprano/女高音", "rejoice greatly, o daughter of zion": "Soprano/女高音",
    "i know that my redeemer liveth": "Soprano/女高音", "let the bright seraphim": "Soprano/女高音",
    "o sleep, why dost thou leave me?": "Soprano/女高音",
    "endless pleasure, endless love": "Soprano/女高音",

    # Tenor
    "where'er you walk": "Tenor/男高音", "total eclipse!": "Tenor/男高音",
    "love sounds the alarm": "Tenor/男高音", "love in her eyes sits playing": "Tenor/男高音",
    "ev'ry valley shall be exalted": "Tenor/男高音",

    # Bass / Bass-Baritone
    "the trumpet shall sound": "Bass/男低音", "o ruddier than the cherry": "Bass/男低音",
    "sorge infausta una procella": "Bass/男低音", "why do the nations so furiously rage": "Bass/男低音",
    "revenge, timotheus cries": "Bass/男低音", "honor and arms": "Bass/男低音",
    "sibilar gli angui d'aletto": "Bass/男低音"
}


# ==============================================================================
# 主逻辑 (MAIN LOGIC)
# ==============================================================================

def main():
    music_data, change_log = load_data_and_log()
    if not music_data:
        print("Could not load music data. Exiting.")
        return

    language_updated_count = 0
    voice_updated_count = 0

    for item in music_data:
        # --- 任务一: 补全语言 ---
        current_lang = item.get("language", "").strip()
        if not current_lang:
            work_title = item.get("work", "")
            if work_title:
                for work_key, lang in WORK_TO_LANGUAGE_MAP.items():
                    if work_key.lower() in work_title.lower():
                        item["language"] = lang
                        language_updated_count += 1
                        print(f"Updated language for ID {item['id']} ({item['title']}) to '{lang}' based on work '{work_title}'")
                        break # 找到第一个匹配就停止

        # --- 任务二: 补全亨德尔声部 ---
        if "handel" in item.get("composer", "").lower() or "亨德尔" in item.get("composer", ""):
            current_voice = item.get("voice_types", "").strip()
            if not current_voice:
                title = item.get("title", "")
                if title:
                    # 清理标题以进行匹配 (取/之前的部分, 转小写, 去除标点)
                    clean_title = title.split('/')[0].strip().lower()
                    clean_title = re.sub(r'[^\w\s]', '', clean_title)
                    
                    if clean_title in HANDEL_ARIA_TO_VOICE_MAP:
                        new_voice = HANDEL_ARIA_TO_VOICE_MAP[clean_title]
                        item["voice_types"] = new_voice
                        voice_updated_count += 1
                        print(f"Updated voice for ID {item['id']} ({title}) to '{new_voice}'")

    # --- 保存和报告 ---
    if language_updated_count > 0 or voice_updated_count > 0:
        total_updates = language_updated_count + voice_updated_count
        print(f"\n--- Metadata Update Summary ---")
        print(f"Languages updated: {language_updated_count}")
        print(f"Handel voices updated: {voice_updated_count}")
        print(f"Total entries modified: {total_updates}")
        
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        change_log.insert(0, {
            "date": today, 
            "type": "update", 
            "msg": f"智能更新元数据：{language_updated_count}条语言，{voice_updated_count}条声部。"
        })
        if len(change_log) > 50: 
            change_log.pop()
        
        save_all(music_data, change_log)
    else:
        print("\nNo metadata entries required updating based on the current rules.")

if __name__ == '__main__':
    main()
