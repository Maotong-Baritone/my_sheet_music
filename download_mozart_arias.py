import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Create a directory to store the arias if it doesn't exist
output_dir = "mozart_arias"
os.makedirs(output_dir, exist_ok=True)

# The URL of the website to search
url = "https://theoperadatabase.com/arias.php"

# The headers for the GET request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

# File to store the list of arias
list_file_path = os.path.join(output_dir, "mozart_arias_list.txt")

try:
    # Send a GET request to the website
    print("Fetching the list of arias...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing the search results
    table = soup.find("table", id="ariadatatable")

    if table:
        # Find all the rows in the table
        rows = table.find_all("tr")

        # Open the list file in write mode
        with open(list_file_path, "w", encoding="utf-8") as list_file:
            print(f"Saving the list of arias to {list_file_path}")
            # Add Voice/Fach to the header
            list_file.write("Aria | Composer | Opera | Voice/Fach | PDF URL\n")
            list_file.write("-" * 120 + "\n")

            # Iterate over the rows and process the data
            for i, row in enumerate(rows[1:]):  # Skip header row
                cells = row.find_all("td")
                if len(cells) > 6: # Ensure there are enough cells to avoid index errors
                    composer = cells[1].text.strip()
                    if "Mozart" in composer:
                        aria = cells[0].text.strip()
                        opera = cells[2].text.strip()
                        voice_fach = cells[3].text.strip() # Extract Voice/Fach
                        pdf_cell = cells[6]
                        pdf_link_tag = pdf_cell.find("a", class_="pdfbutton")
                        
                        if pdf_link_tag and pdf_link_tag.has_attr("href"):
                            pdf_url = pdf_link_tag["href"]
                            
                            # Make the URL absolute
                            pdf_url = urllib.parse.urljoin(url, pdf_url)
                            
                            # Write the aria info to the list file
                            list_file.write(f"{aria:<30} | {composer:<20} | {opera:<30} | {voice_fach:<15} | {pdf_url}\n")
                            
                            # Download the PDF
                            try:
                                print(f"Downloading PDF for '{aria}'...")
                                pdf_response = requests.get(pdf_url, headers=headers)
                                pdf_response.raise_for_status()
                                
                                # Sanitize the filename
                                safe_aria = "".join([c for c in aria if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                                filename = f"{safe_aria}.pdf"
                                file_path = os.path.join(output_dir, filename)
                                
                                with open(file_path, "wb") as pdf_file:
                                    pdf_file.write(pdf_response.content)
                                print(f"Saved PDF to {file_path}")

                            except requests.exceptions.RequestException as e:
                                print(f"Could not download PDF for '{aria}'. Reason: {e}")
                        else:
                            # Write the aria info to the list file even if there is no PDF
                            list_file.write(f"{aria:<30} | {composer:<20} | {opera:<30} | {voice_fach:<15} | No PDF link found\n")
                            print(f"No PDF link found for '{aria}'.")

        print("\nFinished downloading Mozart arias.")
        
    else:
        print("No results table found on the page.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching the page: {e}")

except IOError as e:
    print(f"An error occurred while writing to a file: {e}")
