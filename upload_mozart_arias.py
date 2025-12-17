import os
import requests
import re

# Website configuration
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
UPLOAD_URL = BASE_URL  # The upload is handled at the root URL in the target app
ADMIN_USER = "admin"
ADMIN_PASS = "maotong2025"

# Directory containing the downloaded Mozart arias
ARIAS_DIR = "mozart_arias"
ARIA_LIST_FILE = os.path.join(ARIAS_DIR, "mozart_arias_list.txt")

def upload_mozart_arias():
    """
    Logs into the website and uploads the Mozart arias.
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
            if "错误" in login_response.text or "Invalid" in login_response.text:
                print(f"Login failed. Please check credentials or ensure the web server at {BASE_URL} is running correctly.")
                return
            print("Login successful.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during login: {e}")
            print(f"Please ensure your Flask server is running at {BASE_URL}.")
            return

        # 2. Read the list of arias
        if not os.path.exists(ARIA_LIST_FILE):
            print(f"Aria list file not found at: {ARIA_LIST_FILE}")
            return

        with open(ARIA_LIST_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Skip header lines
            data_lines = lines[2:]
            
            for line in data_lines:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 5:
                    continue

                # Extract data based on the new translated format
                translated_aria, composer, translated_opera, voice_fach, pdf_url = parts
                
                # The original name is needed to find the downloaded PDF file
                original_aria_name = translated_aria.split('/')[0].strip()

                # Set the category
                category = "歌剧咏叹调" # Opera Arias

                # Sanitize the original filename to match the one saved by the download script
                safe_aria = "".join([c for c in original_aria_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                pdf_filename = f"{safe_aria}.pdf"
                pdf_filepath = os.path.join(ARIAS_DIR, pdf_filename)
                
                if not os.path.exists(pdf_filepath):
                    print(f"PDF file not found for '{original_aria_name}' at '{pdf_filepath}'. Skipping.")
                    continue

                # 3. Construct the multipart/form-data payload
                form_data = {
                    'title': translated_aria,
                    'composer': "Wolfgang Amadeus Mozart/莫扎特", # Standardize composer name
                    'work': translated_opera,
                    'category': category,
                    'language': '',

                    'tonality': '',
                    'voice_types': voice_fach, # Use the extracted voice/fach
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
                    print(f"Uploading '{original_aria_name}'...")
                    upload_response = session.post(UPLOAD_URL, data=form_data, files=files)
                    upload_response.raise_for_status()

                    # Simple check for success keywords
                    if "成功" in upload_response.text or "Success" in upload_response.text:
                        print(f"  Successfully uploaded '{original_aria_name}'.")
                    else:
                        # Try to find a specific error message if available
                        error_match = re.search(r'<div class="alert alert-danger">(.*?)</div>', upload_response.text, re.DOTALL)
                        if error_match:
                            error_text = error_match.group(1).strip()
                            print(f"  Failed to upload '{original_aria_name}'. Reason: {error_text}")
                        else:
                            print(f"  Failed to upload '{original_aria_name}'. The server response did not indicate success.")
                
                except requests.exceptions.RequestException as e:
                    print(f"  An error occurred while uploading '{original_aria_name}': {e}")
                
                finally:
                    # Close the file handle
                    files['file'][1].close()

if __name__ == "__main__":
    upload_mozart_arias()
