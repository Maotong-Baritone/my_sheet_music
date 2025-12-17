import os
import requests
import re

# Website configuration
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
UPLOAD_URL = BASE_URL
ADMIN_USER = "admin"
ADMIN_PASS = "maotong2025"

# Directory containing the downloaded arias
ARIAS_DIR = "handel_arias"
ARIA_LIST_FILE = os.path.join(ARIAS_DIR, "handel_arias_list.txt")

def upload_arias():
    """
    Logs into the website and uploads the Handel arias.
    """
    with requests.Session() as session:
        # 1. Login to the website
        print("Logging in...")
        try:
            login_response = session.post(LOGIN_URL, data={
                "username": ADMIN_USER,
                "password": ADMIN_PASS
            })
            login_response.raise_for_status()
            if "错误" in login_response.text:
                print("Login failed. Please check your credentials in admin_tool.py.")
                return
            print("Login successful.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during login: {e}")
            return

        # 2. Read the list of arias
        if not os.path.exists(ARIA_LIST_FILE):
            print(f"Aria list file not found at: {ARIA_LIST_FILE}")
            return

        with open(ARIA_LIST_FILE, "r", encoding="utf-8") as f:
            # Skip header lines
            next(f)
            next(f)
            
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 4:
                    continue

                aria_title, composer, opera, pdf_url = parts
                
                # Set the composer name
                composer = "Georg Friedrich Händel/亨德尔"

                # Set the category
                category = "歌剧咏叹调" # Opera Arias

                # Sanitize the filename to match the one saved by the download script
                safe_aria = "".join([c for c in aria_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                pdf_filename = f"{safe_aria}.pdf"
                pdf_filepath = os.path.join(ARIAS_DIR, pdf_filename)
                
                if not os.path.exists(pdf_filepath):
                    print(f"PDF file not found for '{aria_title}'. Skipping.")
                    continue

                # 3. Construct the multipart/form-data payload
                form_data = {
                    'title': aria_title,
                    'composer': composer,
                    'work': opera,
                    'category': category,
                    'language': '',
                    'tonality': '',
                    'voice_types': '',
                    'voice_count': '',
                    'sub_category': '',
                    'description': '',
                    'lyrics_og': '',
                    'lyrics_cn': '',
                }
                
                files = {
                    'file': (pdf_filename, open(pdf_filepath, 'rb'), 'application/pdf')
                }

                # 4. Upload the file
                try:
                    print(f"Uploading '{aria_title}'...")
                    upload_response = session.post(UPLOAD_URL, data=form_data, files=files)
                    upload_response.raise_for_status()

                    if "成功" in upload_response.text:
                        print(f"Successfully uploaded '{aria_title}'.")
                    else:
                        print(f"Failed to upload '{aria_title}'. Response: {upload_response.text}")
                
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred while uploading '{aria_title}': {e}")
                
                finally:
                    # Close the file handle
                    files['file'][1].close()

if __name__ == "__main__":
    upload_arias()
