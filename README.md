BGG Player Count Data Scraper
Overview
This tool is designed to scrape and process board game data from BoardGameGeek (BGG), focusing on collecting information such as game ownership, ratings, weights, and player count recommendations. It aims to assist board game enthusiasts and researchers in gathering detailed insights into various board games listed on BGG.

Features
Data Scraping: Collects data directly from BoardGameGeek using BeautifulSoup and requests.
Data Processing: Organizes scraped data into structured formats for easy analysis.
Customizable Searches: Allows users to specify search parameters, including username and page number, to tailor the data collection process to their needs.

Dependencies
BeautifulSoup4
requests
fake_useragent
tqdm
csv
json
Make sure to install these dependencies using pip before running the script.

Usage
Clone the repository or download the script.
Install required dependencies: pip install -r requirements.txt.
Run the script with Python 3.x: python BGG_PlayerCountData.py.
Follow on-screen prompts or modify the script to customize your data collection criteria.
Note
This tool is intended for educational and personal use. Please ensure you comply with BoardGameGeek's terms of service when using this script. Avoid making excessive requests to BGG's servers to prevent strain on their resources.

License
This project is open-source and available under the MIT License. Contributions and suggestions are welcome.
