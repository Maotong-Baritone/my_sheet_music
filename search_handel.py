import requests
from bs4 import BeautifulSoup

# The URL of the website to search
url = "https://theoperadatabase.com/arias.php"

# The search query
search_query = "Handel"

# The parameters for the GET request
params = {"q": search_query}

# The headers for the GET request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

import requests
from bs4 import BeautifulSoup

# The URL of the website to search
url = "https://theoperadatabase.com/arias.php"

# The headers for the GET request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

try:
    # Send a GET request to the website
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing the search results
    table = soup.find("table", id="ariadatatable")

    if table:
        # Find all the rows in the table
        rows = table.find_all("tr")

        # Print the header row
        header = [th.text.strip() for th in rows[0].find_all("th")]
        print(f"{header[0]:<30} | {header[1]:<40} | {header[2]:<20}")
        print("-" * 100)

        # Iterate over the rows and print the data
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) > 1:
                composer = cells[1].text.strip()
                if "Handel" in composer:
                    aria = cells[0].text.strip()
                    opera = cells[2].text.strip()
                    print(f"{composer:<30} | {aria:<40} | {opera:<20}")
    else:
        print("No results found.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
