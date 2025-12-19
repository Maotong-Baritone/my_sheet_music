import json
import re
import os
import datetime

# === 配置 ===
DATA_FILE = 'js/data.js'
BACKUP_DIR = 'backup'

# === 1. 特殊覆盖表 (优先匹配：歌剧名 + 角色名) ===
# 用于解决同名角色冲突 (如 Isabella, Giacomo) 和特殊反串
SPECIFIC_OVERRIDES = {
    # --- Rossini 罗西尼 ---
    ("l'inganno felice", "isabella"): "Soprano/女高音",
    ("l'italiana in algeri", "isabella"): "Mezzo-soprano/次女高音",
    ("eduardo e cristina", "giacomo"): "Bass/男低音",
    ("la donna del lago", "giacomo"): "Tenor/男高音",
    ("la donna del lago", "uberto"): "Tenor/男高音",
    ("matilde di shabran", "edoardo"): "Contralto/女低音", # 反串
    ("eduardo e cristina", "eduardo"): "Mezzo-soprano/次女高音", # 反串
    
    # --- Donizetti 多尼采蒂 ---
    ("l'assedio di calais", "edoardo"): "Baritone/男中音",
    ("l'assedio di calais", "aurelio"): "Mezzo-soprano/次女高音", # 反串
    ("ugo, conte di parigi", "luigi"): "Mezzo-soprano/次女高音", # 反串
    ("le convenienze", "donna agata"): "Baritone/男中音", # 男扮女装
    ("le convenienze", "agata"): "Baritone/男中音",
    ("adelia", "arnoldo"): "Bass/男低音",
    ("guillaume tell", "arnold"): "Tenor/男高音",
    ("il giovedì grasso", "nina"): "Soprano/女高音",
    ("il paria", "neala"): "Soprano/女高音",
    ("il duca d'alba", "marcello"): "Tenor/男高音",
}

# === 2. 通用角色字典 (兜底匹配) ===
ROLE_DB = {
    # ====== Rossini ======
    "bianca": "Soprano/女高音", "falliero": "Mezzo-soprano/次女高音", "contareno": "Tenor/男高音",
    "carlo": "Tenor/男高音", "cristina": "Soprano/女高音",
    "mathilde": "Soprano/女高音", "matilde": "Soprano/女高音",
    "clarice": "Mezzo-soprano/次女高音", "macrobio": "Baritone/男中音", "asdrubale": "Bass/男低音", "giocondo": "Tenor/男高音",
    "ilo": "Tenor/男高音", "zelmira": "Soprano/女高音", "polidoro": "Bass/男低音", "emma": "Contralto/女低音",
    "publia": "Mezzo-soprano/次女高音", "aureliano": "Tenor/男高音", "zenobia": "Soprano/女高音", "gran sacerdote": "Bass/男低音",
    "gernando": "Tenor/男高音", "armida": "Soprano/女高音",
    "polibio": "Bass/男低音", "siveno": "Contralto/女低音", "lisinga": "Soprano/女高音", "eumene": "Tenor/男高音",
    "basilio": "Bass/男低音", "bartolo": "Bass/男低音", "berta": "Soprano/女高音",
    "gaudenzio": "Baritone/男中音", "sofia": "Soprano/女高音", "bruschino": "Baritone/男中音",
    "jero": "Bass/男低音", "pamira": "Soprano/女高音", "neocle": "Mezzo-soprano/次女高音", "neocles": "Tenor/男高音",
    "buralicchio": "Bass/男低音", "gamberotto": "Bass/男低音", "ernestina": "Mezzo-soprano/次女高音", "rosalia": "Mezzo-soprano/次女高音", "ermanno": "Tenor/男高音", "frontino": "Tenor/男高音",
    "batone": "Baritone/男中音", "ormondo": "Bass/男低音", "bertrando": "Tenor/男高音",
    "martino": "Bass/男低音", "berenice": "Soprano/女高音", "alberto": "Tenor/男高音",
    "slook": "Baritone/男中音", "mill": "Bass/男低音", "clarina": "Mezzo-soprano/次女高音", "fanny": "Soprano/女高音",
    "clorinda": "Soprano/女高音", "cenerentola": "Mezzo-soprano/次女高音", "angelina": "Mezzo-soprano/次女高音", "ramiro": "Tenor/男高音", "dandini": "Baritone/男中音", "magnifico": "Bass/男低音",
    "douglas": "Bass/男低音", "elena": "Soprano/女高音", "malcom": "Mezzo-soprano/次女高音", "rodrigo": "Tenor/男高音",
    "giannetto": "Tenor/男高音", "ninetta": "Soprano/女高音", "fernando": "Tenor/男高音", "podesta": "Bass/男低音", "gottardo": "Bass/男低音", "pippo": "Mezzo-soprano/次女高音", "isacco": "Tenor/男高音",
    "filippo": "Baritone/男中音", "pomponio": "Bass/男低音", "madame": "Mezzo-soprano/次女高音", "doralice": "Soprano/女高音", "lisetta": "Soprano/女高音",
    "contessa": "Soprano/女高音", "adele": "Soprano/女高音", "comte": "Tenor/男高音", "ory": "Tenor/男高音", "isolier": "Mezzo-soprano/次女高音", "raimbaud": "Baritone/男中音", "gouverneur": "Bass/男低音",
    "mahomet": "Bass/男低音", "maometto": "Bass/男低音", "ismene": "Mezzo-soprano/次女高音",
    "anaide": "Soprano/女高音", "siniade": "Soprano/女高音", "mose": "Bass/男低音", "faraone": "Baritone/男中音",
    "zoraide": "Soprano/女高音", "agorante": "Tenor/男高音", "ricciardo": "Tenor/男高音",
    "bruce": "Baritone/男中音", "nelly": "Soprano/女高音", "edouard": "Tenor/男高音",
    "zenovito": "Bass/男低音", "sigismondo": "Mezzo-soprano/次女高音", "aldimira": "Soprano/女高音", "anagilda": "Mezzo-soprano/次女高音", "ladislao": "Tenor/男高音",
    "isaura": "Mezzo-soprano/次女高音", "roggiero": "Mezzo-soprano/次女高音", "tancredi": "Mezzo-soprano/次女高音", "amenaide": "Soprano/女高音", "argirio": "Tenor/男高音", "orbazzano": "Baritone/男中音",

    # ====== Donizetti ======
    "adelia": "Soprano/女高音", "oliviero": "Tenor/男高音",
    "volmar": "Baritone/男中音", "belfiore": "Bass/男低音", "alina": "Mezzo-soprano/次女高音", "seide": "Tenor/男高音",
    "giovanna": "Mezzo-soprano/次女高音", "seymour": "Mezzo-soprano/次女高音", "percy": "Tenor/男高音", "anna": "Soprano/女高音", "bolena": "Soprano/女高音", "enrico": "Baritone/男中音", "henry": "Bass/男低音", "smeton": "Mezzo-soprano/次女高音",
    "irene": "Soprano/女高音", "belisario": "Baritone/男中音", "antonina": "Soprano/女高音", "alamiro": "Tenor/男高音",
    "max": "Baritone/男中音", "betly": "Soprano/女高音", "daniele": "Tenor/男高音",
    "mocenigo": "Baritone/男中音", "caterina": "Soprano/女高音", "cornaro": "Soprano/女高音", "gerardo": "Tenor/男高音", "lusignano": "Baritone/男中音",
    "michel": "Bass/男低音", "ivan": "Tenor/男高音", "elisabeth": "Soprano/女高音", "nizza": "Mezzo-soprano/次女高音",
    "massimiano": "Baritone/男中音", "crispo": "Tenor/男高音", "fausta": "Soprano/女高音", "constantino": "Tenor/男高音",
    "vergy": "Baritone/男中音", "guido": "Bass/男低音", "tamas": "Tenor/男高音", "gemma": "Soprano/女高音",
    "gianni": "Tenor/男高音",
    "czar": "Baritone/男中音", "timoteo": "Bass/男低音", "marietta": "Soprano/女高音",
    "annibale": "Bass/男低音", "serafina": "Soprano/女高音",
    "warney": "Baritone/男中音", "amelia": "Soprano/女高音",
    "noe": "Bass/男低音", "ada": "Mezzo-soprano/次女高音", "sela": "Soprano/女高音",
    "duca": "Baritone/男中音", "alba": "Baritone/男中音", "marcello": "Tenor/男高音",
    "colonnello": "Baritone/男中音", "piquet": "Bass/男低音", "nina": "Soprano/女高音", "teodoro": "Tenor/男高音",
    "zarette": "Baritone/男中音", "neala": "Soprano/女高音", "idamore": "Tenor/男高音",
    "giulio": "Baritone/男中音", "gilda": "Soprano/女高音",
    "claudio": "Baritone/男中音", "emilia": "Soprano/女高音",
    "murena": "Bass/男低音", "argelia": "Soprano/女高音", "settimio": "Tenor/男高音",
    "baldassarre": "Bass/男低音", "ines": "Soprano/女高音", "fernand": "Tenor/男高音", "fernando": "Tenor/男高音", "leonora": "Mezzo-soprano/次女高音", "alfonso": "Baritone/男中音",
    "filinto": "Tenor/男高音", "flagiolet": "Bass/男低音",
    "filidoro": "Tenor/男高音",
    "ranuccio": "Baritone/男中音", "sebastiano": "Bass/男低音", "argilla": "Mezzo-soprano/次女高音",
    "procolo": "Baritone/男中音", "prima donna": "Soprano/女高音",
    "linda": "Soprano/女高音", "carlo": "Tenor/男高音", "antonio": "Baritone/男中音", "pierotto": "Mezzo-soprano/次女高音",
    "corrado": "Baritone/男中音", "maria": "Soprano/女高音",
    "gondi": "Mezzo-soprano/次女高音", "chevreuse": "Baritone/男中音", "rohan": "Soprano/女高音",
    "pedro": "Baritone/男中音", "ruiz": "Tenor/男高音", "padilla": "Soprano/女高音",
    "israele": "Baritone/男中音", "faliero": "Bass/男低音",
    "isabella": "Soprano/女高音",
    "le bross": "Tenor/男高音", "pasquale": "Bass/男低音", "olivo": "Baritone/男中音",
    "azzo": "Baritone/男中音", "parisina": "Soprano/女高音", "ugo": "Tenor/男高音",
    "callistene": "Bass/男低音", "poliuto": "Tenor/男高音", "severo": "Baritone/男中音", "paolina": "Soprano/女高音",
    "ircano": "Bass/男低音", "garzia": "Mezzo-soprano/次女高音", "sancia": "Soprano/女高音",
    "tasso": "Baritone/男中音", "gherardo": "Bass/男低音", "eleonora": "Soprano/女高音",
    "luigi": "Mezzo-soprano/次女高音", # Ugo
    "bianca": "Soprano/女高音", # Ugo
    
    # 通用常见
    "figaro": "Baritone/男中音", "almaviva": "Tenor/男高音", "rosina": "Mezzo-soprano/次女高音",
    "norina": "Soprano/女高音", "malatesta": "Baritone/男中音", "dulcamara": "Bass/男低音",
    "nemorino": "Tenor/男高音", "belcore": "Baritone/男中音", "adina": "Soprano/女高音",
    "lucia": "Soprano/女高音", "edgardo": "Tenor/男高音", "raimondo": "Bass/男低音",
    "marie": "Soprano/女高音", "tonio": "Tenor/男高音",
    "lucrezia": "Soprano/女高音", "gennaro": "Tenor/男高音", "orsini": "Mezzo-soprano/次女高音",
}

def fix_uploaded_data():
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
    with open(os.path.join(BACKUP_DIR, f"data_backup_belcanto_fix_{timestamp}.js"), 'w', encoding='utf-8') as f:
        f.write(content)

    count = 0
    print("\n🚀 开始修复已上传的罗西尼/多尼采蒂数据...")

    for item in music_data:
        composer = item.get('composer', '')
        # 只处理这两位作曲家
        if not any(x in composer for x in ['Rossini', 'Donizetti', '罗西尼', '多尼采蒂']):
            continue

        original_voice = item.get('voice_types', '').strip()
        
        # 提取用于判断的信息
        clean_role_raw = re.sub(r'Check\s*\((.*?)\)', r'\1', original_voice) # 去掉 Check()
        clean_role_raw = re.sub(r'\(.*?\)', '', clean_role_raw).strip() # 去掉其他括号
        role_lower = clean_role_raw.lower()
        opera_lower = item.get('work', '').lower()

        matched_voice = None

        # 1. 优先查特殊覆盖表
        for (op_key, role_key), voice in SPECIFIC_OVERRIDES.items():
            if op_key in opera_lower and role_key in role_lower:
                matched_voice = voice
                break
        
        # 2. 查通用角色表
        if not matched_voice:
            for role, voice in ROLE_DB.items():
                if re.search(r'\b' + re.escape(role) + r'\b', role_lower):
                    matched_voice = voice
                    break

        # 3. 如果原本是 Check 但字典里没找到，尝试提取标准声部词
        if not matched_voice and "Check" in original_voice:
             if "soprano" in role_lower and "mezzo" not in role_lower: matched_voice = "Soprano/女高音"
             elif "mezzo" in role_lower: matched_voice = "Mezzo-soprano/次女高音"
             elif "tenor" in role_lower: matched_voice = "Tenor/男高音"
             elif "baritone" in role_lower: matched_voice = "Baritone/男中音"
             elif "bass" in role_lower: matched_voice = "Bass/男低音"
             elif "contralto" in role_lower: matched_voice = "Contralto/女低音"

        # 执行更新
        if matched_voice and item['voice_types'] != matched_voice:
            print(f"  [修复] 《{item['title']}》: '{original_voice}' -> '{matched_voice}'")
            item['voice_types'] = matched_voice
            count += 1

    if count > 0:
        print(f"\n✅ 成功修复了 {count} 条数据！")
        
        # 记录日志
        change_log.insert(0, {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 
            "type": "update", 
            "msg": f"批量修复罗西尼与多尼采蒂的声部数据 ({count} 条)。"
        })
        
        # 写入文件
        music_data.sort(key=lambda x: x['id'], reverse=True)
        new_content = f"// 最后更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Bel Canto Fix)\n"
        new_content += f"const musicData = {json.dumps(music_data, indent=4, ensure_ascii=False)};\n"
        new_content += f"const changeLog = {json.dumps(change_log, indent=4, ensure_ascii=False)};\n"

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("🎉 data.js 已更新，请刷新网页查看效果。")
    else:
        print("\n⚠️ 未发现需要修复的数据。可能已经修复过了？")

if __name__ == "__main__":
    fix_uploaded_data()