import os
import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse

# === 配置区域 ===
OUTPUT_DIR = "mozart_arias_fixed"      # 下载目录
LOG_FILE = "download_report_v2.txt"     # 失败记录
TARGET_URL = "https://theoperadatabase.com/arias.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def sanitize_filename(name):
    """清洗文件名，去掉非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def download_mozart_v2():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("正在连接数据库获取列表...")
    
    try:
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="ariadatatable")
        
        if not table:
            print("❌ 错误：未找到 id='ariadatatable' 的表格。可能网站改版了。")
            return

        rows = table.find_all("tr")[1:] # 跳过表头
        total_mozart = 0
        success_count = 0
        skip_count = 0
        fail_count = 0

        print(f"网页共加载 {len(rows)} 行数据，开始筛选...")

        with open(LOG_FILE, "w", encoding="utf-8") as log:
            log.write(f"下载报告 - {time.strftime('%Y-%m-%d %H:%M')}\n{'='*50}\n")

            for row in rows:
                cols = row.find_all("td")
                # 确保列数足够（旧脚本是用 >6，即至少7列）
                if len(cols) < 7: 
                    continue

                # 提取信息
                aria_name = cols[0].text.strip()
                composer = cols[1].text.strip()
                
                # 只处理莫扎特 (Mozart)
                if "Mozart" not in composer:
                    continue
                
                total_mozart += 1
                
                # === 关键修复：定位 PDF 链接 ===
                # 优先看第7列 (Index 6)
                pdf_link_tag = cols[6].find("a")
                
                # 如果第7列没找到，尝试在整行里找 class="pdfbutton" 的链接
                if not pdf_link_tag:
                    pdf_link_tag = row.find("a", class_="pdfbutton")

                # 如果还是没有，跳过
                if not pdf_link_tag or not pdf_link_tag.has_attr('href'):
                    print(f"⚪ [无链接] {aria_name}")
                    continue

                raw_url = pdf_link_tag['href']
                # 补全相对路径
                pdf_url = urllib.parse.urljoin(TARGET_URL, raw_url)

                # 构造文件名
                safe_name = sanitize_filename(aria_name)
                file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")

                # === 检查 1: 文件是否已存在且正常 ===
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    if file_size > 5120:  # > 5KB
                        print(f"⏭️ [跳过] {safe_name} (已存在)")
                        skip_count += 1
                        continue
                    else:
                        print(f"⚠️ [重下] {safe_name} (旧文件损坏)")

                # === 开始下载 ===
                try:
                    # timeout 设置为 20秒，stream=True
                    with requests.get(pdf_url, headers=HEADERS, stream=True, timeout=20) as r:
                        # === 检查 2: 智能识别假 PDF ===
                        content_type = r.headers.get("Content-Type", "").lower()
                        
                        # 如果是 html 页面，说明是跳转链接，不是真文件
                        if "html" in content_type:
                            print(f"❌ [非PDF] {safe_name} (是网页跳转)")
                            log.write(f"[External Link] {aria_name} -> {pdf_url}\n")
                            fail_count += 1
                            continue
                        
                        r.raise_for_status()
                        with open(file_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        print(f"✅ [成功] {safe_name}")
                        success_count += 1
                        time.sleep(0.5) # 稍微休息一下

                except Exception as e:
                    print(f"❌ [失败] {safe_name}: {e}")
                    log.write(f"[Error] {aria_name}: {e}\n")
                    fail_count += 1

        print(f"\n{'='*30}")
        print(f"筛选出莫扎特作品: {total_mozart} 首")
        print(f"✅ 成功下载: {success_count}")
        print(f"⏭️ 跳过已有: {skip_count}")
        print(f"❌ 失败/外链: {fail_count} (详见 {LOG_FILE})")

    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    download_mozart_v2()