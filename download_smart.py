# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import unicodedata

# ==============================================================================
# 配置区域
# ==============================================================================

# 目标网址
TARGET_URL = 'https://theoperadatabase.com/arias.php'

# 文件保存目录
SAVE_DIR = 'mozart_arias_fixed'

# 无法下载的列表将记录在此
FAILED_LOG_FILE = 'failed_list.txt'

# 模拟真实浏览器的请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 跳过已下载文件的阈值（字节），5KB
SKIP_THRESHOLD_BYTES = 5 * 1024

# ==============================================================================
# 核心下载函数
# ==============================================================================

def download_file(aria_title, pdf_url):
    """
    智能下载单个文件。
    - 检查 Content-Type
    - 跳过已存在的有效文件
    - 记录失败的链接
    """
    # 清理文件名，移除不合法字符
    safe_title = re.sub(r'[\\/*?:":<>|]', "", aria_title)
    filename = f"{safe_title}.pdf"
    filepath = os.path.join(SAVE_DIR, filename)

    print(f"\nProcessing: '{aria_title}'")
    print(f"URL: {pdf_url}")

    # 1. 断点续传逻辑：如果文件已存在且大于阈值，则跳过
    if os.path.exists(filepath) and os.path.getsize(filepath) > SKIP_THRESHOLD_BYTES:
        print(f"--- File '{filename}' already exists and is larger than {SKIP_THRESHOLD_BYTES / 1024}KB. Skipping.")
        return

    try:
        # 2. 发起流式请求，并设置超时
        response = requests.get(pdf_url, stream=True, headers=HEADERS, timeout=20)
        response.raise_for_status() # 如果状态码不是 200, 则抛出异常

        # 3. 智能检测内容类型
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/pdf' in content_type:
            print(f"--- Content-Type is PDF. Downloading to '{filename}'...")
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"--- Successfully saved '{filename}'.")
        
        else:
            # 4. 如果不是PDF，则记录到失败列表
            print(f"--- Skipping non-PDF link. Content-Type: '{content_type}'.")
            with open(FAILED_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{aria_title}: {pdf_url}\n")
            print(f"--- Logged to '{FAILED_LOG_FILE}'.")

    except requests.exceptions.RequestException as e:
        print(f"--- ERROR: Could not download file. Reason: {e}")
        with open(FAILED_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{aria_title} (Download Error): {pdf_url}\n")
        print(f"--- Logged error to '{FAILED_LOG_FILE}'.")


# ==============================================================================
# 主逻辑
# ==============================================================================

def main():
    """
    主函数，抓取网页、筛选并启动下载。
    """
    # 确保保存目录存在
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    print(f"Fetching aria list from {TARGET_URL}...")
    try:
        page = requests.get(TARGET_URL, headers=HEADERS)
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not fetch the main page. Error: {e}")
        return

    soup = BeautifulSoup(page.text, 'lxml')
    
    # 假设页面中只有一个表格，如果不是，需要更精确的选择器
    table = soup.find('table')
    if not table:
        print("FATAL: Could not find the data table on the page.")
        return

    rows = table.find_all('tr')
    print(f"Found {len(rows)} total entries. Filtering for Mozart...")

    for row in rows[1:]: # 跳过标题行
        cells = row.find_all('td')
        if len(cells) > 2:
            composer_raw = cells[1].text.strip()
            
            # 使用 unicodedata 进行最终的、最强的规范化处理
            composer_normalized = unicodedata.normalize('NFC', composer_raw)
            target_normalized = unicodedata.normalize('NFC', 'Mozart, Wolfgang Amadeus')

            if composer_normalized == target_normalized:
                aria_cell = cells[0]
                aria_title = aria_cell.text.strip()
                link_tag = aria_cell.find('a')
                
                if link_tag and link_tag.has_attr('href'):
                    pdf_relative_url = link_tag['href']
                    pdf_full_url = urljoin(TARGET_URL, pdf_relative_url)
                    
                    download_file(aria_title, pdf_full_url)

    print("\n--- All tasks completed. ---")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload process interrupted by user.")
