import os
import requests
from bs4 import BeautifulSoup
import time
import re

# === 配置区域 ===
OUTPUT_DIR = "mozart_arias_new"      # 下载目录
LOG_FILE = "download_report.txt"     # 失败记录
TARGET_URL = "https://theoperadatabase.com/arias.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def sanitize_filename(name):
    """清洗文件名，去掉非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def download_mozart_direct():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("正在连接数据库获取莫扎特乐谱列表...")
    
    try:
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="ariadatatable")
        
        if not table:
            print("❌ 错误：未找到数据表格。")
            return

        rows = table.find_all("tr")[1:] # 跳过表头
        total_found = 0
        success_count = 0
        skip_count = 0
        fail_count = 0

        print(f"找到 {len(rows)} 行数据，开始筛选莫扎特作品...")

        with open(LOG_FILE, "w", encoding="utf-8") as log:
            log.write(f"下载报告 - {time.strftime('%Y-%m-%d %H:%M')}\n{'='*50}\n")

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 5: continue

                # 提取信息（根据网页结构：Aria, Composer, Opera, Voice, Link）
                aria_name = cols[0].text.strip()
                composer = cols[1].text.strip()
                opera = cols[2].text.strip()
                pdf_link_tag = cols[4].find("a")

                # 只处理莫扎特
                if "Mozart" not in composer:
                    continue
                
                total_found += 1
                
                # 如果没有 PDF 链接
                if not pdf_link_tag:
                    print(f"⚪ [无链接] {aria_name}")
                    continue

                pdf_url = pdf_link_tag['href']
                # 处理相对链接
                if not pdf_url.startswith("http"):
                    pdf_url = "https://theoperadatabase.com/" + pdf_url.lstrip("/")

                # 构造文件名
                safe_name = sanitize_filename(aria_name)
                file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")

                # === 检查 1: 文件是否已存在且正常 ===
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    if file_size > 5120:  # 大于 5KB 视为正常
                        print(f"⏭️ [跳过] {safe_name} (已存在)")
                        skip_count += 1
                        continue
                    else:
                        print(f"⚠️ [重下] {safe_name} (发现旧文件损坏/过小)")

                # === 开始下载 ===
                try:
                    # stream=True 只下载头信息，不立即下载内容
                    with requests.get(pdf_url, headers=HEADERS, stream=True, timeout=15) as r:
                        # === 检查 2: 内容类型是不是 PDF ===
                        content_type = r.headers.get("Content-Type", "").lower()
                        if "pdf" not in content_type:
                            print(f"❌ [非PDF] {safe_name} (是网页跳转: {content_type})")
                            log.write(f"[Skipped/Not PDF] {aria_name} -> {pdf_url}\n")
                            fail_count += 1
                            continue
                        
                        # 确认下载
                        r.raise_for_status()
                        with open(file_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        print(f"✅ [成功] {safe_name}")
                        success_count += 1
                        # 礼貌性延时
                        time.sleep(0.5)

                except Exception as e:
                    print(f"❌ [失败] {safe_name}: {e}")
                    log.write(f"[Error] {aria_name}: {e}\n")
                    fail_count += 1

        print(f"\n{'='*30}")
        print(f"完成！共扫描: {total_found}")
        print(f"成功下载: {success_count}")
        print(f"跳过已有: {skip_count}")
        print(f"失败/外链: {fail_count} (详见 {LOG_FILE})")

    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    download_mozart_direct()