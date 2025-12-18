import json
import re
import os
import datetime

# === 配置 ===
DATA_FILE = 'js/data.js'
BACKUP_DIR = 'backup'

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# === 亨德尔清唱剧关键词列表 ===
# 只要作品名包含这些词，就归类为清唱剧
ORATORIO_KEYWORDS = [
    "Messiah", "弥赛亚",
    "Samson", "参孙",
    "Judas Maccabaeus", "犹大",
    "Joshua", "约书亚",
    "Belshazzar", "伯沙撒",
    "Athalia", "亚塔利亚",
    "Solomon", "所罗门",
    "Theodora", "狄奥多拉",
    "Susanna", "苏珊娜",
    "Saul", "扫罗",
    "Jephtha", "耶弗他",
    "Israel in Egypt", "以色列人在埃及",
    "Esther", "以斯帖",
    "Deborah", "底波拉",
    "Joseph and his Brethren", "约瑟",
    "La resurrezione", "复活",
    "Il trionfo del Tempo", "时间的胜利"
]

def fix_handel_categories():
    print(f"正在读取 {DATA_FILE} ...")
    if not os.path.exists(DATA_FILE):
        print("❌ 未找到数据文件")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f: content = f.read()

    match_data = re.search(r'const musicData = (\[.*?\]);', content, re.DOTALL)
    match_log = re.search(r'const changeLog = (\[.*?\]);', content, re.DOTALL)
    
    if not match_data: return
    music_data = json.loads(match_data.group(1))
    change_log = json.loads(match_log.group(1)) if match_log else []

    # 备份
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(BACKUP_DIR, f"data_backup_oratorio_{timestamp}.js"), 'w', encoding='utf-8') as f:
        f.write(content)

    count = 0
    print("\n--- 开始筛选亨德尔清唱剧 ---")

    for item in music_data:
        composer = item.get('composer', '')
        # 1. 锁定亨德尔的作品
        if any(x in composer for x in ['Handel', 'Händel', '亨德尔']):
            work = item.get('work', '')
            
            # 2. 检查是否在清唱剧列表中
            if any(keyword in work for keyword in ORATORIO_KEYWORDS):
                # 检查是否需要修改（防止重复操作）
                if item.get('category') != '宗教声乐作品' or item.get('sub_category') != '清唱剧':
                    print(f"  [修正] 《{item['title']}》 ({work})")
                    print(f"       -> 从 '{item.get('category')}' 改为 '宗教声乐作品' / '清唱剧'")
                    
                    item['category'] = '宗教声乐作品'
                    item['sub_category'] = '清唱剧'
                    count += 1

    if count > 0:
        print(f"\n✅ 成功将 {count} 首作品重新归类为【宗教声乐作品/清唱剧】！")
        
        # 记录日志
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        change_log.insert(0, {
            "date": today,
            "type": "update",
            "msg": f"批量修正了 {count} 首亨德尔清唱剧的分类标签。"
        })
        if len(change_log) > 50: change_log.pop()

        # 保存
        music_data.sort(key=lambda x: x['id'], reverse=True)
        json_music = json.dumps(music_data, indent=4, ensure_ascii=False)
        json_log = json.dumps(change_log, indent=4, ensure_ascii=False)
        
        new_content = f"// 最后更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Oratorio Fix)\n"
        new_content += f"const musicData = {json_music};\n"
        new_content += f"const changeLog = {json_log};\n"

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print("\n⚠️ 未发现需要修改的条目。")

if __name__ == "__main__":
    fix_handel_categories()