import json
import re
import os
import datetime

# === 配置 ===
DATA_FILE = 'js/data.js'
BACKUP_DIR = 'backup'

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# === 核心字典：亨德尔作品映射 ===
# 逻辑：关键词 (小写) -> 标准全名 (Title, HWV/中文)
# 包含了你刚才提供的所有新作品
HANDEL_MAP = {
    # --- 你刚刚补充的列表 ---
    "susanna": "Susanna, HWV 66/苏珊娜",
    "teseo": "Teseo, HWV 9/泰塞奥",
    "sosarme": "Sosarme, re di Media, HWV 30/索萨梅 (米底亚国王)",
    "solomon": "Solomon, HWV 67/所罗门",
    "siroe": "Siroe, re di Persia, HWV 24/西罗埃 (波斯国王)",
    "silla": "Silla, HWV 10/希拉",
    "rodrigo": "Rodrigo, HWV 5/罗德里戈",
    "poro": "Poro, re delle Indie, HWV 28/波罗 (印度国王)",
    "ottone": "Ottone, re di Germania, HWV 15/奥托内 (德国国王)",
    "muzio": "Muzio Scevola, HWV 13/穆齐奥·谢沃拉",
    "scevola": "Muzio Scevola, HWV 13/穆齐奥·谢沃拉",
    "lotario": "Lotario, HWV 26/洛塔里奥",
    "allegro": "L'Allegro, il Penseroso ed il Moderato, HWV 55/欢快、沉思与稳重的人",
    "penseroso": "L'Allegro, il Penseroso ed il Moderato, HWV 55/欢快、沉思与稳重的人",
    "judas": "Judas Maccabaeus, HWV 63/犹大·马加比",
    "joshua": "Joshua, HWV 64/约书亚",
    "imeneo": "Imeneo, HWV 41/伊梅内奥",
    "pastor fido": "Il pastor fido, HWV 8/忠实的牧羊人",
    "giustino": "Giustino, HWV 37/查士丁尼",
    "floridante": "Floridante, HWV 14/弗洛里丹特",
    "flavio": "Flavio, re di Langobardi, HWV 16/弗拉维奥 (伦巴第国王)",
    "faramondo": "Faramondo, HWV 39/法拉蒙多",
    "ezio": "Ezio, HWV 29/埃齐奥",
    "deidamia": "Deidamia, HWV 42/黛达米亚",
    "berenice": "Berenice, HWV 38/贝蕾妮丝",
    "belshazzar": "Belshazzar, HWV 61/伯沙撒",
    "athalia": "Athalia, HWV 52/亚塔利亚",
    "arminio": "Arminio, HWV 36/阿尔米尼奥",
    "arianna": "Arianna in Creta, HWV 32/克里特岛的阿里阿德涅",
    "alessandro": "Alessandro, HWV 21/亚历山大",

    # --- 原有的常见列表 (保留以防遗漏) ---
    "rinaldo": "Rinaldo, HWV 7/里纳尔多",
    "giulio cesare": "Giulio Cesare in Egitto, HWV 17/凯撒大帝",
    "julius caesar": "Giulio Cesare in Egitto, HWV 17/凯撒大帝",
    "serse": "Serse, HWV 40/塞尔斯 (薛西斯)",
    "xerxes": "Serse, HWV 40/塞尔斯 (薛西斯)",
    "orlando": "Orlando, HWV 31/奥兰多",
    "alcina": "Alcina, HWV 34/阿尔奇娜",
    "ariodante": "Ariodante, HWV 33/阿里奥丹特",
    "agrippina": "Agrippina, HWV 6/阿格里皮娜",
    "rodelinda": "Rodelinda, HWV 19/罗德琳达",
    "semele": "Semele, HWV 58/塞墨勒",
    "messiah": "Messiah, HWV 56/弥赛亚",
    "samson": "Samson, HWV 57/参孙",
    "theodora": "Theodora, HWV 68/狄奥多拉",
    "acis": "Acis and Galatea, HWV 49/阿西斯与加拉蕾亚",
    "galatea": "Acis and Galatea, HWV 49/阿西斯与加拉蕾亚",
    "tolomeo": "Tolomeo, HWV 25/托洛梅奥",
    "partenope": "Partenope, HWV 27/帕耳忒诺珀",
    "almira": "Almira, HWV 1/阿尔米拉",
    "amadigi": "Amadigi di Gaula, HWV 11/阿马迪吉",
    "hercules": "Hercules, HWV 60/海格力斯",
    "saul": "Saul, HWV 53/扫罗",
    "jephtha": "Jephtha, HWV 70/耶弗他",
    "israel in egypt": "Israel in Egypt, HWV 54/以色列人在埃及",
    "radamisto": "Radamisto, HWV 12/拉达米斯托",
    "tamerlano": "Tamerlano, HWV 18/帖木儿",
    "scipione": "Scipione, HWV 20/西庇阿",
    "admeto": "Admeto, HWV 22/阿德梅托",
    "riccardo": "Riccardo Primo, HWV 23/理查一世"
}

def standardize_works():
    print(f"正在读取 {DATA_FILE} ...")
    if not os.path.exists(DATA_FILE): 
        print("未找到数据文件")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f: content = f.read()

    match_data = re.search(r'const musicData = (\[.*?\]);', content, re.DOTALL)
    match_log = re.search(r'const changeLog = (\[.*?\]);', content, re.DOTALL)
    
    if not match_data: return
    music_data = json.loads(match_data.group(1))
    change_log = json.loads(match_log.group(1)) if match_log else []

    # 备份
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(BACKUP_DIR, f"data_backup_handel_full_{timestamp}.js"), 'w', encoding='utf-8') as f:
        f.write(content)

    count_handel = 0
    
    print("\n--- 开始扫描亨德尔作品 ---")

    for item in music_data:
        composer = item.get('composer', '')
        # 1. 修复的核心：宽容匹配，同时识别 Handel, Händel 和 亨德尔
        if any(x in composer for x in ['Handel', 'Händel', '亨德尔']):
            
            original_work = item.get('work', '').strip()
            if not original_work: continue
            
            work_lower = original_work.lower()
            
            # 2. 遍历字典查找匹配
            for key, new_name in HANDEL_MAP.items():
                # 只要关键词出现在原名里，且原名还不是标准格式，就更新
                if key in work_lower:
                    if original_work != new_name:
                        print(f"  [更新] ID:{item['id']} | {original_work} -> {new_name}")
                        item['work'] = new_name
                        count_handel += 1
                    break # 找到一个关键词匹配就跳出，防止重复

    if count_handel > 0:
        print(f"\n✅ 成功更新了 {count_handel} 首亨德尔作品的名称！")
        
        # 保存
        music_data.sort(key=lambda x: x['id'], reverse=True)
        json_music = json.dumps(music_data, indent=4, ensure_ascii=False)
        json_log = json.dumps(change_log, indent=4, ensure_ascii=False)
        
        new_content = f"// 最后更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Handel Full Standard)\n"
        new_content += f"const musicData = {json_music};\n"
        new_content += f"const changeLog = {json_log};\n"

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print("\n⚠️ 没有发现需要更新的条目。")
        print("可能原因：1. 数据已经是最新的。 2. 你的数据中没有这些歌剧的关键词。")

if __name__ == "__main__":
    standardize_works()