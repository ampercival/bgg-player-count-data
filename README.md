These are two scripts: one for collecting data from BGG, in particular the player count information for games; the second is for visualizing these data in a filterable and sortable table.

# BoardGameGeek Player Count Data Script

This Python script fetches and processes board game data from BoardGameGeek (BGG), focusing on player count data and other relevant game details. It is designed to help users analyze game preferences based on player counts, ratings, and ownership.

## Features

- Fetch game data using BoardGameGeek's API.
- Process and analyze data based on player counts, ratings, and ownership.
- Output the processed data to a CSV file for easy analysis and sharing.

## Requirements

- Python 3.x
- External libraries: requests, beautifulsoup4, lxml, fake_useragent, tqdm`

## Usage

The script can be run with custom parameters via command-line arguments. Below are the available options:

- `-u`, `--username`: Specify the BoardGameGeek username to fetch games for. Default is `Percy0715`.
- `-f`, `--fetch`: Number of games to fetch. Default is `1000`.
- `-o`, `--output`: Filename for the output CSV. Default is `PlayerCountDataList.csv`.
- `-b`, `--batch_size`: Batch size for processing games. Default is `500`.

### Running the Script

To run the script with default parameters, simply execute:

python BGG_PlayerCountData.py

To customize parameters, include them like so:

python BGG_PlayerCountData.py --username YourUsername --fetch 5000 --output custom_output.csv --batch_size 100

# Contributing
Contributions to improve the script or add new features are welcome. Please follow the standard GitHub pull request process to submit your changes.

# License
This script is distributed under the MIT License. See LICENSE file for more information.

# Contact
For any questions or suggestions, please open an issue on GitHub.