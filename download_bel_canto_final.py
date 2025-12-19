import os
import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse

# === 配置 ===
TARGET_URL = "https://theoperadatabase.com/arias.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://theoperadatabase.com/"
}

COMPOSERS = ["Rossini", "Donizetti"]

# === 1. 特殊覆盖表 (优先匹配) ===
# 格式: (小写歌剧名关键词, 小写角色名): 标准声部
# 用于解决同名角色不同声部，或特定歌剧的特殊反串
SPECIFIC_OVERRIDES = {
    # --- Rossini 罗西尼冲突处理 ---
    ("l'inganno felice", "isabella"): "Soprano",   # 幸福的错觉: 女高
    ("l'italiana in algeri", "isabella"): "Mezzo-soprano", # 阿尔及尔: 女中
    ("eduardo e cristina", "giacomo"): "Bass",     # 爱德华多: 男低
    ("la donna del lago", "giacomo"): "Tenor",     # 湖上女郎: 男高 (Uberto)
    ("la donna del lago", "uberto"): "Tenor",
    ("matilde di shabran", "edoardo"): "Contralto", # 反串
    ("eduardo e cristina", "eduardo"): "Mezzo-soprano", # 反串
    
    # --- Donizetti 多尼采蒂冲突处理 ---
    ("l'assedio di calais", "edoardo"): "Baritone", # 加莱之围: 男中 (Edoardo III)
    ("l'assedio di calais", "aurelio"): "Mezzo-soprano", # 反串
    ("ugo, conte di parigi", "luigi"): "Mezzo-soprano", # 反串
    ("le convenienze", "donna agata"): "Baritone", # 男扮女装丑角
    ("le convenienze", "agata"): "Baritone",
    ("adelia", "arnoldo"): "Bass",
    ("guillaume tell", "arnold"): "Tenor", # 罗西尼威廉退尔
    ("il giovedì grasso", "nina"): "Soprano",
    ("il paria", "neala"): "Soprano",
    ("il duca d'alba", "marcello"): "Tenor",
}

# === 2. 通用角色字典 (兜底匹配) ===
# 如果上面没匹配到，查这里。这里存储名字唯一对应的声部。
ROLE_DB = {
    # ====== Rossini (罗西尼) ======
    "bianca": "Soprano", "falliero": "Mezzo-soprano", "contareno": "Tenor",
    "carlo": "Tenor", "cristina": "Soprano",
    "mathilde": "Soprano", "matilde": "Soprano",
    "clarice": "Mezzo-soprano", "macrobio": "Baritone", "asdrubale": "Bass", "giocondo": "Tenor",
    "ilo": "Tenor", "zelmira": "Soprano", "polidoro": "Bass", "emma": "Contralto",
    "publia": "Mezzo-soprano", "aureliano": "Tenor", "zenobia": "Soprano", "gran sacerdote": "Bass",
    "gernando": "Tenor", "armida": "Soprano",
    "polibio": "Bass", "siveno": "Contralto", "lisinga": "Soprano", "eumene": "Tenor",
    "basilio": "Bass", "bartolo": "Bass", "berta": "Soprano",
    "gaudenzio": "Baritone", "sofia": "Soprano", "bruschino": "Baritone",
    "jero": "Bass", "pamira": "Soprano", "neocle": "Mezzo-soprano", "neocles": "Tenor",
    "buralicchio": "Bass", "gamberotto": "Bass", "ernestina": "Mezzo-soprano", "rosalia": "Mezzo-soprano", "ermanno": "Tenor", "frontino": "Tenor",
    "batone": "Baritone", "ormondo": "Bass", "bertrando": "Tenor",
    "martino": "Bass", "berenice": "Soprano", "alberto": "Tenor",
    "slook": "Baritone", "mill": "Bass", "clarina": "Mezzo-soprano", "fanny": "Soprano",
    "clorinda": "Soprano", "cenerentola": "Mezzo-soprano", "angelina": "Mezzo-soprano", "ramiro": "Tenor", "dandini": "Baritone", "magnifico": "Bass",
    "douglas": "Bass", "elena": "Soprano", "malcom": "Mezzo-soprano", "rodrigo": "Tenor",
    "giannetto": "Tenor", "ninetta": "Soprano", "fernando": "Tenor", "podesta": "Bass", "gottardo": "Bass", "pippo": "Mezzo-soprano", "isacco": "Tenor",
    "filippo": "Baritone", "pomponio": "Bass", "madame": "Mezzo-soprano", "doralice": "Soprano", "lisetta": "Soprano",
    "contessa": "Soprano", "adele": "Soprano", "comte": "Tenor", "ory": "Tenor", "isolier": "Mezzo-soprano", "raimbaud": "Baritone", "gouverneur": "Bass",
    "mahomet": "Bass", "maometto": "Bass", "ismene": "Mezzo-soprano", 
    "anaide": "Soprano", "siniade": "Soprano", "mose": "Bass", "faraone": "Baritone",
    "zoraide": "Soprano", "agorante": "Tenor", "ricciardo": "Tenor",
    "bruce": "Baritone", "nelly": "Soprano", "edouard": "Tenor", # Robert Bruce
    "zenovito": "Bass", "sigismondo": "Mezzo-soprano", "aldimira": "Soprano", "anagilda": "Mezzo-soprano", "ladislao": "Tenor",
    "isaura": "Mezzo-soprano", "roggiero": "Mezzo-soprano", "tancredi": "Mezzo-soprano", "amenaide": "Soprano", "argirio": "Tenor", "orbazzano": "Baritone",

    # ====== Donizetti (多尼采蒂) ======
    "adelia": "Soprano", "oliviero": "Tenor", # 用户确认为Tenor
    "volmar": "Baritone", "belfiore": "Bass", "alina": "Mezzo-soprano", "seide": "Tenor",
    "giovanna": "Mezzo-soprano", "seymour": "Mezzo-soprano", "percy": "Tenor", "anna": "Soprano", "bolena": "Soprano", "enrico": "Bass", "henry": "Bass", "smeton": "Mezzo-soprano",
    "irene": "Soprano", "belisario": "Baritone", "antonina": "Soprano", "alamiro": "Tenor",
    "max": "Baritone", "betly": "Soprano", "daniele": "Tenor",
    "mocenigo": "Baritone", "caterina": "Soprano", "cornaro": "Soprano", "gerardo": "Tenor", "lusignano": "Baritone",
    "michel": "Bass", "ivan": "Tenor", "elisabeth": "Soprano", "nizza": "Mezzo-soprano",
    "massimiano": "Baritone", "crispo": "Tenor", "fausta": "Soprano", "constantino": "Tenor",
    "vergy": "Baritone", "guido": "Bass", "tamas": "Tenor", "gemma": "Soprano",
    "gianni": "Tenor", # Gianni di Calais
    "czar": "Baritone", "timoteo": "Bass", "marietta": "Soprano",
    "annibale": "Bass", "enrico": "Baritone", "serafina": "Soprano",
    "warney": "Baritone", "amelia": "Soprano", # Robsart
    "noe": "Bass", "ada": "Mezzo-soprano", "sela": "Soprano",
    "duca": "Baritone", "alba": "Baritone", "marcello": "Tenor", # Duca d'Alba
    "colonnello": "Baritone", "piquet": "Bass", "nina": "Soprano", "teodoro": "Tenor",
    "zarete": "Baritone", "neala": "Soprano", "idamore": "Tenor",
    "giulio": "Baritone", "gilda": "Soprano",
    "claudio": "Baritone", "emilia": "Soprano",
    "murena": "Bass", "argelia": "Soprano", "settimio": "Tenor",
    "baldassarre": "Bass", "ines": "Soprano", "fernand": "Tenor", "fernando": "Tenor", "leonora": "Mezzo-soprano", "alfonso": "Baritone",
    "filinto": "Tenor", "flagiolet": "Bass",
    "filidoro": "Tenor",
    "ranuccio": "Baritone", "sebastiano": "Bass", "argilla": "Mezzo-soprano",
    "procolo": "Baritone", "prima donna": "Soprano",
    "linda": "Soprano", "carlo": "Tenor", "antonio": "Baritone", "pierotto": "Mezzo-soprano",
    "corrado": "Baritone", "maria": "Soprano", # Rudenz
    "gondi": "Mezzo-soprano", "chevreuse": "Baritone", "rohan": "Soprano",
    "pedro": "Baritone", "ruiz": "Tenor", "padilla": "Soprano",
    "israele": "Baritone", "faliero": "Bass",
    "isabella": "Soprano", # Olivo e Pasquale
    "le bross": "Tenor", "pasquale": "Bass", "olivo": "Baritone",
    "azzo": "Baritone", "parisina": "Soprano", "ugo": "Tenor",
    "callistene": "Bass", "poliuto": "Tenor", "severo": "Baritone", "paolina": "Soprano",
    "ircano": "Bass", "garzia": "Mezzo-soprano", "sancia": "Soprano",
    "tasso": "Baritone", "gherardo": "Bass", "eleonora": "Soprano",
    "bianca": "Soprano", # Ugo conte
}

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def is_pdf_content(content):
    return content.startswith(b'%PDF')

def smart_voice_lookup(text, opera, composer):
    """
    上下文感知声部查找：
    1. 优先检查原文是否包含标准声部词。
    2. 检查 SPECIFIC_OVERRIDES (歌剧+角色)。
    3. 检查 ROLE_DB (仅角色)。
    """
    text_lower = text.lower().strip()
    opera_lower = opera.lower().strip()
    
    # 1. 原文优先 (如果原文已经写了 "Soprano", 就信它，除非是反串名字混淆)
    # 但 TheOperaDatabase 有时会写 "Isabella (Soprano)" 但其实是 Mezzo，所以我们还是优先查字典纠错
    # 不过通常我们只提取纯净词，如果有明确的 Voice type 词，暂且认为是对的，除了特例。
    # 为了保险，我们让字典优先级最高（修正错误），原文次之。

    clean_role_name = re.sub(r'\(.*?\)', '', text_lower).strip() # 去掉括号内容

    # 2. 查特定歌剧覆盖表
    for (op_key, role_key), voice in SPECIFIC_OVERRIDES.items():
        if op_key in opera_lower and role_key in clean_role_name:
            return voice

    # 3. 查通用角色表
    for role, voice in ROLE_DB.items():
        # 匹配单词边界
        if re.search(r'\b' + re.escape(role) + r'\b', clean_role_name):
            return voice

    # 4. 如果字典里没找到，再看原文有没有标准词
    if "mezzo" in text_lower: return "Mezzo-soprano"
    if "contralto" in text_lower: return "Contralto"
    if "soprano" in text_lower: return "Soprano"
    if "baritone" in text_lower: return "Baritone"
    if "bass" in text_lower: return "Bass"
    if "tenor" in text_lower: return "Tenor"
            
    # 5. 兜底
    return f"Check ({text})"

def download_bel_canto_final():
    print("🚀 [Final Context-Aware] 启动最终版美声歌剧下载...")
    print("   (包含特定歌剧同名角色区分与反串修正)")
    
    try:
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="ariadatatable")
        if not table: return

        rows = table.find_all("tr")[1:] 
        
        for composer_name in COMPOSERS:
            clean_name = sanitize_filename(composer_name)
            output_dir = f"{clean_name}_Arias"
            if not os.path.exists(output_dir): os.makedirs(output_dir)
                
            list_file = os.path.join(output_dir, f"{clean_name}_upload_list.txt")
            stats = {"success": 0, "exist": 0, "skip": 0}

            print(f"\n🎵 正在处理: {composer_name} -> {list_file}")

            with open(list_file, "w", encoding="utf-8") as f:
                f.write("Aria | Composer | Opera | Voice | Filename\n")
                f.write("-" * 100 + "\n")

                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 7: continue

                    aria_name = cols[0].text.strip()
                    row_composer = cols[1].text.strip()
                    opera = cols[2].text.strip()
                    raw_voice = cols[3].text.strip()

                    if composer_name.lower() not in row_composer.lower(): continue

                    # === 上下文感知查找 ===
                    clean_voice = smart_voice_lookup(raw_voice, opera, composer_name)

                    # 获取链接
                    pdf_link_tag = cols[6].find("a")
                    if not pdf_link_tag: pdf_link_tag = row.find("a", class_="pdfbutton")
                    if not pdf_link_tag or not pdf_link_tag.has_attr('href'): continue

                    raw_url = pdf_link_tag['href']
                    pdf_url = urllib.parse.urljoin(TARGET_URL, raw_url)
                    
                    safe_name = sanitize_filename(aria_name)
                    filename = f"{safe_name}.pdf"
                    file_path = os.path.join(output_dir, filename)

                    download_success = False

                    if os.path.exists(file_path) and os.path.getsize(file_path) > 5120:
                        stats["exist"] += 1
                        download_success = True
                    else:
                        try:
                            # print(f"⬇️ 下载: {aria_name} ...", end="\r")
                            with requests.get(pdf_url, headers=HEADERS, timeout=20) as r:
                                r.raise_for_status()
                                if is_pdf_content(r.content):
                                    with open(file_path, 'wb') as pdf_file:
                                        pdf_file.write(r.content)
                                    stats["success"] += 1
                                    download_success = True
                                else:
                                    stats["skip"] += 1
                        except:
                            stats["skip"] += 1

                    if download_success:
                        line = f"{aria_name} | {row_composer} | {opera} | {clean_voice} | {filename}\n"
                        f.write(line)
            
            print(f"✅ {composer_name} 统计: 新下载 {stats['success']} / 已有 {stats['exist']}")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    download_bel_canto_final()