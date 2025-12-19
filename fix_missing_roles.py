import json
import re
import os
import datetime

# === 配置 ===
DATA_FILE = 'js/data.js'
BACKUP_DIR = 'backup'

# === 补充角色字典 (基于您提供的清单) ===
# 键为小写英文角色名，值为标准声部
ADDITIONAL_ROLES = {
    # --- Puccini: Edgar (埃德加) ---
    "edgar": "Tenor/男高音",
    "frank": "Baritone/男中音",
    "fidelia": "Soprano/女高音",
    "tigrana": "Mezzo-soprano/次女高音",
    "gualtiero": "Bass/男低音",

    # --- Puccini: Il tabarro (外套) ---
    "michele": "Baritone/男中音",
    "giorgetta": "Soprano/女高音",
    "luigi": "Tenor/男高音",
    "tinca": "Tenor/男高音", "il tinca": "Tenor/男高音",
    "talpa": "Bass/男低音", "il talpa": "Bass/男低音",
    "frugola": "Mezzo-soprano/次女高音", "la frugola": "Mezzo-soprano/次女高音",

    # --- Puccini: Le Villi (维利) ---
    "roberto": "Tenor/男高音",
    "anna": "Soprano/女高音",
    "guglielmo": "Baritone/男中音", "guglielmo wulf": "Baritone/男中音", "wulf": "Baritone/男中音",

    # --- Puccini: Suor Angelica (修女安杰利卡) ---
    "suor angelica": "Soprano/女高音", "angelica": "Soprano/女高音",
    "zia principessa": "Contralto/女低音", "la zia principessa": "Contralto/女低音", "principessa": "Contralto/女低音",
    "abbess": "Mezzo-soprano/次女高音", "the abbess": "Mezzo-soprano/次女高音",
    "monitor": "Mezzo-soprano/次女高音", "suor genovieffa": "Soprano/女高音", "genovieffa": "Soprano/女高音",

    # --- Wagner: Das Liebesverbot (禁爱) ---
    "friedrich": "Baritone/男中音", # 低男中音归类为男中音，方便筛选
    "luzio": "Tenor/男高音",
    "claudio": "Tenor/男高音",
    "isabella": "Soprano/女高音",
    "mariana": "Soprano/女高音",
    "brighella": "Baritone/男中音",

    # --- Wagner: Das Rheingold (莱茵的黄金) ---
    "wotan": "Baritone/男中音", # 低男中音
    "loge": "Tenor/男高音",
    "alberich": "Baritone/男中音",
    "mime": "Tenor/男高音",
    "fricka": "Mezzo-soprano/次女高音",
    "freia": "Soprano/女高音",
    "erda": "Contralto/女低音",
    "fasolt": "Bass/男低音",
    "fafner": "Bass/男低音",

    # --- Wagner: Der fliegende Holländer (漂泊的荷兰人) ---
    "holländer": "Baritone/男中音", "the dutchman": "Baritone/男中音", "dutchman": "Baritone/男中音",
    "senta": "Soprano/女高音",
    "daland": "Bass/男低音",
    "erik": "Tenor/男高音",
    "mary": "Mezzo-soprano/次女高音",
    "steersman": "Tenor/男高音",

    # --- Wagner: Die Feen (仙女) ---
    "fairy king": "Bass/男低音", "the fairy king": "Bass/男低音",
    "ada": "Soprano/女高音",
    "arindal": "Tenor/男高音",
    "morald": "Baritone/男中音",
    "lora": "Soprano/女高音",

    # --- Wagner: Die Meistersinger (名歌手) ---
    "sachs": "Baritone/男中音", "hans sachs": "Baritone/男中音",
    "pogner": "Bass/男低音", "veit pogner": "Bass/男低音",
    "beckmesser": "Baritone/男中音",
    "walther": "Tenor/男高音",
    "david": "Tenor/男高音",
    "eva": "Soprano/女高音",
    "magdalene": "Mezzo-soprano/次女高音",

    # --- Wagner: Lohengrin (罗恩格林) ---
    "lohengrin": "Tenor/男高音",
    "elsa": "Soprano/女高音",
    "ortrud": "Mezzo-soprano/次女高音", 
    "telramund": "Baritone/男中音",
    "heinrich": "Bass/男低音", "king heinrich": "Bass/男低音",
    "herald": "Baritone/男中音",

    # --- Wagner: Rienzi (黎恩济) ---
    "rienzi": "Tenor/男高音",
    "irene": "Soprano/女高音",
    "adriano": "Mezzo-soprano/次女高音",
    "colonna": "Bass/男低音", "stefano colonna": "Bass/男低音",
    "orsini": "Bass/男低音", "paolo orsini": "Bass/男低音"
}

def fix_missing_roles():
    print(f"📂 正在读取 {DATA_FILE} ...")
    if not os.path.exists(DATA_FILE): return

    with open(DATA_FILE, 'r', encoding='utf-8') as f: content = f.read()

    match_data = re.search(r'const musicData = (\[.*?\]);', content, re.DOTALL)
    match_log = re.search(r'const changeLog = (\[.*?\]);', content, re.DOTALL)
    if not match_data: return
    
    music_data = json.loads(match_data.group(1))
    change_log = json.loads(match_log.group(1)) if match_log else []

    # 备份
    if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(BACKUP_DIR, f"data_backup_missing_roles_{timestamp}.js"), 'w', encoding='utf-8') as f:
        f.write(content)

    count = 0
    print("\n🚀 开始补充缺失的角色声部...")

    for item in music_data:
        # 只检查普契尼和瓦格纳
        composer = item.get('composer', '')
        if not any(x in composer for x in ['Puccini', '普契尼', 'Wagner', '瓦格纳']):
            continue

        original_voice = item.get('voice_types', '').strip()
        voice_lower = original_voice.lower()
        
        # 移除括号内容 (e.g., "Wotan (Bass-Baritone)" -> "wotan")
        clean_voice = re.sub(r'\s*\(.*?\)', '', voice_lower).strip()

        matched_voice = None

        # 1. 尝试完全匹配
        if clean_voice in ADDITIONAL_ROLES:
            matched_voice = ADDITIONAL_ROLES[clean_voice]
        
        # 2. 尝试包含匹配 (防止 "Role: Wotan" 或 "Hans Sachs")
        else:
            for role, v_type in ADDITIONAL_ROLES.items():
                # 匹配单词边界，防止 "Ada" 匹配到 "Madam"
                if re.search(r'\b' + re.escape(role) + r'\b', clean_voice):
                    matched_voice = v_type
                    break
        
        # 如果找到了匹配，且当前填写的声部还不是标准格式
        # (比如原来填的是 'Wotan'，现在要改成 'Baritone/男中音')
        if matched_voice and item['voice_types'] != matched_voice:
            print(f"  [修正] 《{item['title']}》: '{original_voice}' -> '{matched_voice}'")
            item['voice_types'] = matched_voice
            count += 1

    if count > 0:
        print(f"\n✅ 成功修正了 {count} 个遗漏的角色声部！")
        
        # 记录日志
        change_log.insert(0, {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 
            "type": "update", 
            "msg": f"补充修正 {count} 个普契尼与瓦格纳的稀有角色声部。"
        })
        
        music_data.sort(key=lambda x: x['id'], reverse=True)
        new_content = f"// 最后更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Missing Roles)\n"
        new_content += f"const musicData = {json.dumps(music_data, indent=4, ensure_ascii=False)};\n"
        new_content += f"const changeLog = {json.dumps(change_log, indent=4, ensure_ascii=False)};\n"

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print("\n⚠️ 未发现需要修正的角色。看来大部分已经很完美了！")

if __name__ == "__main__":
    fix_missing_roles()