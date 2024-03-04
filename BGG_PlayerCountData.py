import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import csv
from tqdm.auto import tqdm
import time
import argparse 

# Below are the imports required for the script to function properly:
# - `re`: module for using regular expressions.
# - `BeautifulSoup`: library for parsing HTML and XML documents.
# - `UserAgent`: tool for generating random user agent strings.
# - `requests`: library for making HTTP requests.
# - `csv`: module for reading and writing CSV files.
# - `tqdm`: tool for creating progress meters.
# - `time`: module for working with time-related tasks.

def get_args():
    parser = argparse.ArgumentParser(description="Fetch and process game data from BoardGameGeek.")
    
    # Step 3: Adding command-line arguments
    parser.add_argument("-u", "--username", default="Percy0715", help="BoardGameGeek username (default: Percy0715)")
    parser.add_argument("-f", "--fetch", type=int, default=1000, help="Number of games to fetch (default: 1000)")
    parser.add_argument("-o", "--output", default="PlayerCountDataList.csv", help="Output CSV filename (default: PlayerCountDataList.csv)")
    parser.add_argument("-b", "--batch_size", type=int, default=500, help="Batch size for processing games in batches from API call (default: 500)")    
    
    return parser.parse_args()

def create_session():
    
    """
    Creates a session with a random user agent.

    This function initializes a session for making HTTP requests while
    simulating a random browser user agent. This can help in preventing
    the web server from blocking the requests due to scraping activities.

    Returns:
        session (requests.Session): A session object configured with a random user agent.
    """
    
    # Initialize UserAgent with a list of browser types to simulate.
    ua = UserAgent(browsers=['chrome', 'edge', 'firefox', 'safari'])
    # Create a dictionary with the 'User-Agent' header using a random user agent string.
    headers = {'User-Agent': ua.random}

    # Create a session object from the requests library.
    session = requests.Session()
    # Update the session's headers with the created 'headers' dictionary.
    session.headers.update(headers)

    # Return the configured session object.
    return session

def fetch_games(session, username, page_number):
    """
    Fetches game data from BoardGameGeek based on a specified username and page number.

    This function uses a session object to make a GET request to the BoardGameGeek website,
    retrieving a list of games associated with a given username. The function parses the HTML
    response to extract relevant game details such as title, ID, type, average rating, and number
    of voters. It supports pagination through the page_number argument.

    Args:
        session (requests.Session): The session object used for making HTTP requests.
        username (str): The BoardGameGeek username whose game list is to be fetched.
        page_number (int): The page number for pagination purposes.

    Returns:
        dict: A dictionary containing game IDs as keys and dictionaries with game details as values.
    """
    # Construct the URL for fetching games, including the username and page number for pagination.
    url = f"https://boardgamegeek.com/search/boardgame/page/{page_number}?sort=avgrating&advsearch=1&q=&include%5Bdesignerid%5D=&include%5Bpublisherid%5D=&geekitemname=&range%5Byearpublished%5D%5Bmin%5D=&range%5Byearpublished%5D%5Bmax%5D=&range%5Bminage%5D%5Bmax%5D=&range%5Bnumvoters%5D%5Bmin%5D=100&range%5Bnumweights%5D%5Bmin%5D=&range%5Bminplayers%5D%5Bmax%5D=&range%5Bmaxplayers%5D%5Bmin%5D=&range%5Bleastplaytime%5D%5Bmin%5D=&range%5Bplaytime%5D%5Bmax%5D=&floatrange%5Bavgrating%5D%5Bmin%5D=&floatrange%5Bavgrating%5D%5Bmax%5D=&floatrange%5Bavgweight%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmax%5D=&colfiltertype=&searchuser={username}&playerrangetype=normal&B1=Submit&sortdir=desc"
    response = session.get(url)  # Make the GET request using the session object.
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML response.
    table = soup.find('table', {'class': 'collection_table'})  # Locate the table containing game data.

    games = {}  # Initialize an empty dictionary to store game details.

    # Iterate over each row in the table to extract game details.
    for row in table.find_all('tr', {'id': re.compile(r'^row_')}):
        game_title_element = row.find_all('td')[2]
        game_title = game_title_element.a.text.strip()  # Extract the game title.
        game_id = re.search(r'/boardgame(?:expansion)?/(\d+)', game_title_element.a['href']).group(1)  # Extract the game ID.

        # Determine if the game is a base game or an expansion.
        if "boardgameexpansion" in game_title_element.a['href']:
            game_type = "Expansion"
        else:
            game_type = "Base Game"

        avg_rating = float(row.find_all('td')[4].text.strip())  # Extract the average rating.
        num_voters = int(row.find_all('td')[5].text.strip())  # Extract the number of voters.

        # Initialize variables for game weight and ownership status; these could be updated later.
        weight = None
        weight_votes = None
        owned = 'Not Owned'

        # Store the extracted game details in the games dictionary using the game ID as the key.
        games[game_id] = {
            'Game Title': game_title,
            'Type': game_type,
            'Game ID': game_id,
            'Average Rating': avg_rating,
            'Number of Voters': num_voters,
            'Weight': weight,
            'Weight Votes': weight_votes,
            'Owned': owned
        }
            
    return games  # Return the dictionary containing all the fetched game details.

def fetch_games_owned_api(session, username):
    """
    Fetches owned game data for a specified username from the BoardGameGeek API.

    This function makes a request to the BoardGameGeek XML API to retrieve information
    about games owned by a specific user, including base games and expansions. It parses
    the XML response to extract game details such as the title, ID, average rating, and
    number of voters for each game in the user's collection.

    Args:
        session (requests.Session): The session object used for making HTTP requests.
        username (str): The BoardGameGeek username whose owned games are to be fetched.

    Returns:
        dict: A dictionary with game IDs as keys and dictionaries containing game details as values.
    """
    # Initialize an empty dictionary to store details of games owned by the user.
    games_owned = {}        
    # Set the ownership status for all games fetched through this function.
    owned = 'Owned'
    
    # Base URL for the BoardGameGeek XML API request, specifying owned games with stats for the given username.
    base_url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&own=1&stats=1&subtype="
    # Specify the types of games to fetch: base games and expansions.
    types = ["boardgame", "boardgameexpansion"]
    
    # Loop through both game types to fetch.
    for type in types:
        # Construct the final URL with the specific game type.
        url = base_url + type
        retries = 0  # Initialize retries counter for handling request failures.

        # Initialize the game_type variable depending on what the API is fetching.
        if type == "boardgame":
            game_type = "Base Game"
        else:
            game_type = "Expansion"

        # Retry loop in case of unsuccessful API responses.
        while True:
            response = session.get(url)  # Make the API request.
            time.sleep(1.5)  # Sleep to respect rate limiting.

            # Check if the API response is successful (HTTP status code 200).
            if response.status_code != 200:
                retries += 1  # Increment the retries counter.
                print(f"Response from API Status Code {response.status_code}. Retrying... ({retries})")
                if retries >= 50:  # Give up after 50 retries.
                    raise Exception("50 retries reached. Stopping.")
                time.sleep(5)  # Wait a bit longer before retrying.
                continue  # Retry the request.

            break  # Exit the retry loop on success.

        # Parse the XML response.
        soup = BeautifulSoup(response.text, 'lxml-xml')
        items = soup.find_all("item")  # Find all game items in the response.
        
        # Loop through each game item to extract details.
        for item in items:
            game_id = item["objectid"]
            game_title = item.find('name').text
            avg_rating = float(item.stats.find('average')['value'])
            num_voters = int(item.stats.find('usersrated')['value'])            
            
            # Add the game details to the dictionary.
            games_owned[game_id] = {
                'Game Title': game_title,
                'Type': game_type,
                'Game ID': game_id,
                'Average Rating': avg_rating,
                'Number of Voters': num_voters,
                'Weight': None,  # Placeholder for game weight; may be updated later.
                'Weight Votes': None,  # Placeholder for weight votes; may be updated later.
                'Owned': owned  # Mark the game as owned.
            }
        
    return games_owned  # Return the dictionary of owned games.
  
def merge_games_and_update_owned(games, games_owned):
    """
    Merges two dictionaries of games, updating the ownership status based on the games_owned data.

    This function iterates through the games_owned dictionary and updates the ownership status
    of the corresponding games in the games dictionary. If a game from the games_owned dictionary
    does not exist in the games dictionary, it will be added to it. This ensures that the final
    games dictionary contains a comprehensive list of games with accurate ownership information.

    Args:
        games (dict): A dictionary of games with various details, potentially without ownership information.
        games_owned (dict): A dictionary of games owned by the user, used to update the 'Owned' status in the games dictionary.

    Returns:
        dict: The updated games dictionary with ownership information correctly merged from games_owned.
    """
    # Iterate through each game ID and its details in the games_owned dictionary.
    for game_id, game_owned in games_owned.items():
        # Check if the current game ID from games_owned exists in the games dictionary.
        if game_id in games:
            # If it exists, update the 'Owned' status to 'Owned'.
            games[game_id]['Owned'] = 'Owned'
        else:
            # If the game ID does not exist in the games dictionary, add it along with its details from games_owned.
            game_owned['Owned'] = 'Owned'  # Ensure the 'Owned' status is explicitly set to 'Owned'.
            games[game_id] = game_owned  # Add the game to the games dictionary.

    # Return the updated games dictionary with merged ownership information.
    return games


def write_merged_data_to_csv(games, player_count_data_dict, csv_filename):
    """
    Writes the merged game and player count data to a CSV file.

    This function takes the merged data from the games dictionary and the player count data dictionary,
    then writes it into a CSV file with detailed information for each game. This includes game title,
    ID, year, average rating, number of voters, weight, weight votes, ownership status, type, player count,
    and various voting percentages and counts related to player count recommendations.

    Args:
        games (dict): A dictionary containing game details.
        player_count_data_dict (dict): A dictionary containing player count recommendation data for each game.
        csv_filename (str): The filename of the CSV file to write the data to.
    """
    merged_data = []  # Initialize a list to hold the merged data for CSV writing.

    # Iterate through the player count data dictionary to merge it with the games dictionary.
    for game_id, player_count_data in player_count_data_dict.items():
        if game_id in games:
            for player_count, player_data in player_count_data.items():
                row = {
                    'Game Title': games[game_id]['Game Title'],
                    'Game ID': game_id,
                    'Year': games[game_id].get('Year', 'N/A'),  # Use 'N/A' if 'Year' is not available.
                    'Average Rating': games[game_id]['Average Rating'],
                    'Number of Voters': games[game_id]['Number of Voters'],
                    'Weight': games[game_id].get('Weight', 'N/A'),  # Use 'N/A' if 'Weight' is not available.
                    'Weight Votes': games[game_id].get('Weight Votes', 'N/A'),  # Use 'N/A' if 'Weight Votes' is not available.
                    'Owned': games[game_id]['Owned'],
                    'Type': games[game_id]['Type'],
                    'Player Count': player_count,
                    'Best %': player_data['Best %'],
                    'Best Votes': player_data['Best Votes'],
                    'Recommended %': player_data['Recommended %'],
                    'Recommended Votes': player_data['Recommended Votes'],
                    'Not Recommended %': player_data['Not Recommended %'],
                    'Not Recommended Votes': player_data['Not Recommended Votes'],
                    'Vote Count': player_data['Vote Count']
                }
                merged_data.append(row)  # Add the row to the merged_data list.

    # Write the merged data to a CSV file.
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        if merged_data:  # Ensure there is data to write.
            fieldnames = list(merged_data[0].keys())  # Extract the field names from the first row.
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # Write the header row.
            for row in merged_data:
                writer.writerow(row)  # Write each row of data.


def update_boardgame_data(games, batch_size=100, progress_bar=None):
    """
    Updates the games dictionary with additional board game data from the BoardGameGeek API.

    This function fetches detailed game data in batches, including publication year, weight,
    weight votes, and player count recommendations. It updates the games dictionary with this
    new information for each game. The function handles API requests in batches to manage
    request volume and incorporates a progress bar for visual progress tracking.

    Args:
        games (dict): The dictionary of games to be updated with additional data.
        batch_size (int): The number of game IDs to include in each batch API request.
        progress_bar (tqdm.tqdm, optional): Optional tqdm progress bar instance for visual progress tracking.

    Returns:
        tuple: A tuple containing the updated games dictionary and a new dictionary with player count data.
    """
    game_ids = list(games.keys())  # Extract game IDs from the games dictionary.

    # Initialize a dictionary to store player count data for all games.
    player_count_data_dict = {}

    # Iterate over game IDs in batches to manage API request volume.
    for i in range(0, len(game_ids), batch_size):
        batch_ids = game_ids[i:i + batch_size]  # Create a batch of game IDs.
        game_ids_param = ",".join(map(str, batch_ids))  # Convert batch IDs to a comma-separated string.
        url = f"https://boardgamegeek.com/xmlapi2/thing?id={game_ids_param}&stats=1"  # Construct the API request URL.

        retries = 0  # Initialize a retry counter.
        while True:
            response = requests.get(url)  # Send the API request.
            time.sleep(1.5)  # Pause to respect the API's rate limiting.

            if response.status_code != 200:  # Check for a successful response.
                retries += 1
                print(f"Error {response.status_code}. Retrying... ({retries})")
                if retries >= 50:  # Abort after 50 unsuccessful retries.
                    raise Exception("50 retries reached. Stopping.")
                time.sleep(10)
                continue

            break  # Exit the retry loop on a successful response.

        soup = BeautifulSoup(response.text, "xml")  # Parse the XML response.
        
        # Iterate over each game item in the XML to extract and update game details.
        for item in soup.find_all("item"):
            game_id = item["id"]
            year_pub = item.yearpublished["value"]
            games[game_id]['Year'] = year_pub  # Update the game's publication year.

            num_weights = int(item.statistics.ratings.numweights["value"])
            average_weight = round(float(item.statistics.ratings.averageweight["value"]), 2)
            games[game_id]['Weight'] = average_weight  # Update the game's weight.
            games[game_id]['Weight Votes'] = num_weights  # Update the number of weight votes.

            # Extract and process player count recommendation data.
            suggested_numplayers = item.find("poll", {"name": "suggested_numplayers"})
            player_count_data = {}

            if suggested_numplayers:
                for result in suggested_numplayers.find_all("results"):
                    numplayers = result["numplayers"]
                    if "+" in numplayers:  # Skip ambiguous player counts like '10+'.
                        continue

                    best_votes, recommended_votes, not_recommended_votes = 0, 0, 0
                    for vote in result.find_all("result"):
                        if vote["value"] == "Best":
                            best_votes = int(vote["numvotes"])
                        elif vote["value"] == "Recommended":
                            recommended_votes = int(vote["numvotes"])
                        elif vote["value"] == "Not Recommended":
                            not_recommended_votes = int(vote["numvotes"])

                    vote_count = best_votes + recommended_votes + not_recommended_votes
                    best_percentage = round((best_votes / vote_count) * 100, 1) if vote_count else 0
                    recommended_percentage = round((recommended_votes / vote_count) * 100, 1) if vote_count else 0
                    not_recommended_percentage = round((not_recommended_votes / vote_count) * 100, 1) if vote_count else 0

                    player_count_data[numplayers] = {
                        'Best %': best_percentage,
                        'Best Votes': best_votes,
                        'Recommended %': recommended_percentage,
                        'Recommended Votes': recommended_votes,
                        'Not Recommended %': not_recommended_percentage,
                        'Not Recommended Votes': not_recommended_votes,
                        'Vote Count': vote_count
                    }

            player_count_data_dict[game_id] = player_count_data  # Add the player count data for the current game.

            if progress_bar:
                progress_bar.update(1)  # Update the progress bar if provided.

    return games, player_count_data_dict  # Return the updated games dictionary and the new player count data dictionary.

def main(username, games_to_fetch, output_csv_filename, batch_size):
    """
    The main function of the script, responsible for orchestrating the entire data collection,
    processing, and CSV writing process.
    """
    
    ###### START OF SCRIPT CODE ######
    
    print("\n**********************")

    # Initialize a session with a random user agent for web requests.
    session = create_session()

    # Initialize variables for loop control and data storage.
    fetched_games = 0
    current_page = 1
    games = {}

    # Debug mode to fetch a smaller set of games for testing.
    debug = False
    if debug:
        games_to_fetch = 10

    # Progress bar to visually track the game fetching progress.
    with tqdm(total=games_to_fetch, desc="Fetching games") as progress_bar:
        while fetched_games < games_to_fetch:
            # Fetch games from the current page.
            page_games = fetch_games(session, username, current_page)
            for game in page_games.values():
                if fetched_games >= games_to_fetch:
                    break
                fetched_games += 1
                games[game["Game ID"]] = game
                progress_bar.update(1)
            current_page += 1

    print("\n")

    # Fetch games owned by the user.
    games_owned = fetch_games_owned_api(session, username)

    print(f"Total owned games fetched: {len(games_owned)}")

    # Merge fetched games with owned games data.
    games = merge_games_and_update_owned(games, games_owned)

    print(f"Total games after merge: {len(games)}")

    print("\n")

    # Update game data with additional information and player count data.
    with tqdm(total=len(games), smoothing=0, desc="Updating game data") as progress_bar:
        games, player_count_data_dict = update_boardgame_data(games, batch_size=batch_size, progress_bar=progress_bar)

    print("\n")

    print(f"Total games in gamesid {len(games)}")
    print(f"Total line in playercount: {len(player_count_data_dict)}")

    # Write the merged and updated data to a CSV file.
    write_merged_data_to_csv(games, player_count_data_dict, output_csv_filename)

    print("Success!")

if __name__ == "__main__":
    args = get_args()  #Parse command-line arguments.
    
    # Pass the parsed arguments to your main function.
    main(args.username, args.fetch, args.output, args.batch_size)