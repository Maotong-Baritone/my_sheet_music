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

def sanitize_filename(name):
    """清洗文件名"""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def is_pdf_content(content):
    """检查文件头是否为PDF"""
    return content.startswith(b'%PDF')

def clean_voice_text(text):
    """
    清洗声部文本，去掉可能混入的角色名
    例如: 'Violetta (Soprano)' -> 'Soprano'
    """
    # 常见的声部关键词
    valid_voices = ["Soprano", "Mezzo", "Alto", "Tenor", "Baritone", "Bass", "Contralto"]
    
    # 如果文本里包含这些词，优先提取这些词
    for v in valid_voices:
        if v.lower() in text.lower():
            # 简单的归一化，比如把 'Mezzo-soprano' 统一格式
            if "mezzo" in text.lower(): return "Mezzo-soprano"
            return v 
            
    # 如果没找到标准声部词，才返回原文（防止漏掉特殊声部）
    return text

def download_pure():
    print("正在连接数据库...")
    
    try:
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="ariadatatable")
        
        if not table:
            print("❌ 未找到数据表格")
            return

        rows = table.find_all("tr")[1:] 
        
        # === 交互式询问 ===
        print(f"\n✅ 连接成功！")
        print("=" * 40)
        target_composer = input("请输入你想下载的作曲家 (例如 Puccini, Rossini, Wagner): ").strip()
        
        if not target_composer:
            print("输入为空，退出。")
            return

        # 创建目录
        clean_name = sanitize_filename(target_composer.replace(" ", "_"))
        output_dir = f"{clean_name}_Arias"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        list_file = os.path.join(output_dir, f"{clean_name}_upload_list.txt")
        
        print(f"\n📂 存储目录: {output_dir}")
        print("-" * 50)

        success_count = 0
        fail_count = 0

        with open(list_file, "w", encoding="utf-8") as f:
            # 写入标准表头 (不包含 Role)
            f.write("Aria | Composer | Opera | Voice | Filename\n")
            f.write("-" * 100 + "\n")

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 7: continue

                aria_name = cols[0].text.strip()
                composer = cols[1].text.strip()
                opera = cols[2].text.strip()
                
                # === 核心修改：只取声部，并清洗 ===
                raw_voice = cols[3].text.strip()
                voice = clean_voice_text(raw_voice) # 调用清洗函数，去掉多余的角色名

                # 筛选作曲家
                if target_composer.lower() not in composer.lower():
                    continue

                # 寻找链接
                pdf_link_tag = cols[6].find("a")
                if not pdf_link_tag: pdf_link_tag = row.find("a", class_="pdfbutton")
                
                if not pdf_link_tag or not pdf_link_tag.has_attr('href'):
                    continue

                raw_url = pdf_link_tag['href']
                pdf_url = urllib.parse.urljoin(TARGET_URL, raw_url)
                
                safe_name = sanitize_filename(aria_name)
                filename = f"{safe_name}.pdf"
                file_path = os.path.join(output_dir, filename)

                download_success = False

                # 检查是否存在
                if os.path.exists(file_path) and os.path.getsize(file_path) > 5120:
                    print(f"✅ [已存在] {aria_name}")
                    download_success = True
                else:
                    try:
                        print(f"⬇️ [下载中] {aria_name} ...", end="\r")
                        with requests.get(pdf_url, headers=HEADERS, timeout=20) as r:
                            r.raise_for_status()
                            if is_pdf_content(r.content):
                                with open(file_path, 'wb') as pdf_file:
                                    pdf_file.write(r.content)
                                print(f"🎉 [成功] {aria_name}        ")
                                success_count += 1
                                download_success = True
                                time.sleep(0.5) 
                            else:
                                print(f"⏭️ [跳过] {aria_name} (非PDF)")
                                fail_count += 1
                    except Exception as e:
                        print(f"❌ [失败] {aria_name}")
                        fail_count += 1

                # 写入纯净清单
                if download_success:
                    line = f"{aria_name} | {composer} | {opera} | {voice} | {filename}\n"
                    f.write(line)

        print("\n" + "="*40)
        print(f"处理完成！成功获取: {success_count} 首")
        print(f"清单已生成: {list_file}")

    except Exception as e:
        print(f"程序出错: {e}")

if __name__ == "__main__":
    download_pure()