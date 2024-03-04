import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import csv
from tqdm.auto import tqdm
import time
import json
import os

def create_session():
    ua = UserAgent(browsers=['chrome', 'edge', 'firefox', 'safari'])
    headers = {'User-Agent': ua.random}

    session = requests.Session()
    session.headers.update(headers)
    return session

def fetch_games(session, username, page_number):
    url = f"https://boardgamegeek.com/search/boardgame/page/{page_number}?sort=avgrating&advsearch=1&q=&include%5Bdesignerid%5D=&include%5Bpublisherid%5D=&geekitemname=&range%5Byearpublished%5D%5Bmin%5D=&range%5Byearpublished%5D%5Bmax%5D=&range%5Bminage%5D%5Bmax%5D=&range%5Bnumvoters%5D%5Bmin%5D=100&range%5Bnumweights%5D%5Bmin%5D=&range%5Bminplayers%5D%5Bmax%5D=&range%5Bmaxplayers%5D%5Bmin%5D=&range%5Bleastplaytime%5D%5Bmin%5D=&range%5Bplaytime%5D%5Bmax%5D=&floatrange%5Bavgrating%5D%5Bmin%5D=&floatrange%5Bavgrating%5D%5Bmax%5D=&floatrange%5Bavgweight%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmax%5D=&colfiltertype=&searchuser={username}&playerrangetype=normal&B1=Submit&sortdir=desc"
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'collection_table'})

    games = {}

    for row in table.find_all('tr', {'id': re.compile(r'^row_')}):
        game_title_element = row.find_all('td')[2]
        game_title = game_title_element.a.text.strip()
        game_id = re.search(r'/boardgame(?:expansion)?/(\d+)', game_title_element.a['href']).group(1)

        if "boardgameexpansion" in game_title_element.a['href']:
            game_type = "Expansion"
        else:
            game_type = "Base Game"

        avg_rating = float(row.find_all('td')[4].text.strip())
        num_voters = int(row.find_all('td')[5].text.strip())

        weight = None
        weight_votes = None
        owned = 'Not Owned'

        games[game_id] = {
            'Game Title': game_title,
            'Type': game_type,
            'Game ID': game_id,
            'Average Rating': avg_rating,
            'Number of Voters': num_voters,
            'Weight': weight,
            'Weight Votes' : weight_votes,
            'Owned': owned
        }
            
    return games

def fetch_games_owned(session, username, page_number):
    url = f"https://boardgamegeek.com/search/boardgame/page/{page_number}?sort=bggrating&advsearch=1&q=&include%5Bdesignerid%5D=&include%5Bpublisherid%5D=&geekitemname=&range%5Byearpublished%5D%5Bmin%5D=&range%5Byearpublished%5D%5Bmax%5D=&range%5Bminage%5D%5Bmax%5D=&range%5Bnumvoters%5D%5Bmin%5D=&range%5Bnumweights%5D%5Bmin%5D=&range%5Bminplayers%5D%5Bmax%5D=&range%5Bmaxplayers%5D%5Bmin%5D=&range%5Bleastplaytime%5D%5Bmin%5D=&range%5Bplaytime%5D%5Bmax%5D=&floatrange%5Bavgrating%5D%5Bmin%5D=&floatrange%5Bavgrating%5D%5Bmax%5D=&floatrange%5Bavgweight%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmax%5D=&colfiltertype=owned&searchuser={username}&playerrangetype=normal&B1=Submit"
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'collection_table'})

    games_owned = {}

    for row in table.find_all('tr', {'id': re.compile(r'^row_')}):
        game_title_element = row.find_all('td')[2]
        game_title = game_title_element.a.text.strip()
        game_id = re.search(r'/boardgame(?:expansion)?/(\d+)', game_title_element.a['href']).group(1)
        
        if "boardgameexpansion" in game_title_element.a['href']:
            game_type = "Expansion"
        else:
            game_type = "Base Game"

        avg_rating = float(row.find_all('td')[4].text.strip())
        num_voters = int(row.find_all('td')[5].text.strip())

        weight = None
        weight_votes = None
        owned = 'Owned'
        
        games_owned[game_id] = {
            'Game Title': game_title,
            'Type': game_type,
            'Game ID': game_id,
            'Average Rating': avg_rating,
            'Number of Voters': num_voters,
            'Weight': weight,
            'Weight Votes' : weight_votes,
            'Owned': owned
        }

    return games_owned
  
def merge_games_and_update_owned(games, games_owned):
    
    for game_id, game_owned in games_owned.items():
        if game_id in games:
            games[game_id]['Owned'] = 'Owned'
        else:
            game_owned['Owned'] = 'Owned'
            games[game_id] = game_owned
    return games

    fieldnames = list(games.values())[0].keys()

    if player_count_data_dict is not None:
        fieldnames.update(['Num Players', 'Best', 'Recommended', 'Not Recommended'])

    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for game_id, game in games.items():
            if player_count_data_dict is not None:
                player_count_data = player_count_data_dict.get(game_id, [])

                for data in player_count_data:
                    row_data = game.copy()
                    row_data.update(data)
                    writer.writerow(row_data)

                if not player_count_data:
                    writer.writerow(game)
            else:
                writer.writerow(game)

    output_data = []

    for game_id, game in games.items():
        player_count_data = player_count_data_dict.get(game_id, [])

        for data in player_count_data:
            row_data = game.copy()
            row_data.update(data)
            output_data.append(row_data)

        if not player_count_data:
            output_data.append(game)

    with open(file_name, 'w', encoding='utf-8') as jsonfile:
        json.dump(output_data, jsonfile, ensure_ascii=False, indent=4)

def write_merged_data_to_csv(games, player_count_data_dict, csv_filename):
    # Merge player_count_data_dict with games
    merged_data = []
    
    for game_id, player_count_data in player_count_data_dict.items():
        if game_id in games:
            for player_count, player_data in player_count_data.items():
                row = {
                    'Game Title': games[game_id]['Game Title'],
                    'Game ID': game_id,
                    'Year': games[game_id]['Year'],
                    'Average Rating': games[game_id]['Average Rating'],
                    'Number of Voters': games[game_id]['Number of Voters'],
                    'Weight': games[game_id]['Weight'],
                    'Weight Votes': games[game_id]['Weight Votes'],
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
                merged_data.append(row)

    # Write the merged data to CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(merged_data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in merged_data:
            writer.writerow(row)

def update_boardgame_data(games, batch_size=100, progress_bar=None):
    game_ids = list(games.keys())
    
    # Initialize an empty dictionary to store the player count data for all games
    player_count_data_dict = {}

    for i in range(0, len(game_ids), batch_size):
        batch_ids = game_ids[i:i + batch_size]
        game_ids_param = ",".join(map(str, batch_ids))
        url = f"https://boardgamegeek.com/xmlapi2/thing?id={game_ids_param}&stats=1"

        retries = 0
        while True:
            response = requests.get(url)
            time.sleep(1.5)

            error_codes = [400, 401, 403, 404, 408, 429, 500, 503]

            if response.status_code in error_codes:
                retries += 1
                print(f"Error {response.status_code}. Retrying... ({retries})")
                if retries >= 50:
                    input("Uh oh... something went wrong")
                    raise Exception("50 retries reached. Stopping.")
                    
                time.sleep(10)
                continue

            retries = 0
            break

        soup = BeautifulSoup(response.text, "xml")
               
        items = soup.find_all("item")        

        for item in items:
            game_id = item["id"]
            
            year_pub = item.yearpublished["value"] 

            games[game_id]['Year'] = year_pub

            num_weights = int(item.statistics.ratings.numweights["value"])
            average_weight = round(float(item.statistics.ratings.averageweight["value"]), 2)

            games[game_id]['Weight'] = average_weight
            games[game_id]['Weight Votes'] = num_weights

            # Extract the suggested number of players data
            suggested_numplayers = item.find("poll", {"name": "suggested_numplayers"})

            # Initialize an empty dictionary to store the player count data for the current game
            player_count_data = {}

            if suggested_numplayers is not None:
                for result in suggested_numplayers.find_all("results"):
                    numplayers = result["numplayers"]

                    if "+" in numplayers:
                        continue

                    best_votes = 0
                    recommended_votes = 0
                    not_recommended_votes = 0

                    for vote in result.find_all("result"):
                        if vote["value"] == "Best":
                            best_votes = int(vote["numvotes"])
                        elif vote["value"] == "Recommended":
                            recommended_votes = int(vote["numvotes"])
                        elif vote["value"] == "Not Recommended":
                            not_recommended_votes = int(vote["numvotes"])

                    vote_count = best_votes + recommended_votes + not_recommended_votes

                    if vote_count == 0:
                        best_percentage = 0
                        recommended_percentage = 0
                        not_recommended_percentage = 0
                    else:
                        best_percentage = round((best_votes / vote_count) * 100, 1)
                        recommended_percentage = round((recommended_votes / vote_count) * 100, 1)
                        not_recommended_percentage = round((not_recommended_votes / vote_count) * 100, 1)

                    player_count_data[numplayers] = {
                        'Best %': best_percentage,
                        'Best Votes': best_votes,
                        'Recommended %': recommended_percentage,
                        'Recommended Votes': recommended_votes,
                        'Not Recommended %': not_recommended_percentage,
                        'Not Recommended Votes': not_recommended_votes,
                        'Vote Count': vote_count
                    }

            # Add the player count data for the current game to the player_count_data_dict
            player_count_data_dict[game_id] = player_count_data
            
            if progress_bar:
                progress_bar.update(1)

    return games, player_count_data_dict

def main():
    
    print("\n**********************")
    
    session = create_session()
    
    #parameters
    games_to_fetch = 5000
    batch_size = 500
    input_pollid_filename = "PollIDLibrary.csv"
    output_csv_filename = "PlayerCountDataList.csv"
    username = "Percy0715"

    fetched_games = 0
    current_page = 1
    games = {}
    
    debug = False
    
    if debug:
        games_to_fetch = 10
    
    with tqdm(total=games_to_fetch, desc="Fetching games") as progress_bar:
        while fetched_games < games_to_fetch:
            page_games = fetch_games(session, username, current_page)
            for game in page_games.values():
                if fetched_games >= games_to_fetch:
                    break
                fetched_games += 1
                games[game["Game ID"]] = game
                progress_bar.update(1)  # Move the progress bar update here
            current_page += 1
        
    games_owned = {}
    current_page = 1
    
    print("\n")
    
    # Code to fetch owned games
    if debug:
        games_owned_count = 0

        while True:
            print(f"Fetching owned games of BBG username {username}: page {current_page}")
            new_games_owned = fetch_games_owned(session, username, current_page)

            for game in new_games_owned.values():
                games_owned[game["Game ID"]] = game
                games_owned_count += 1

                if games_owned_count == 10:
                    break

            if games_owned_count == 10:
                break

            if len(new_games_owned) < 50:
                break
            else:
                current_page += 1
    else:
        while True:
            print(f"Fetching owned games of BBG username {username}: page {current_page}")
            new_games_owned = fetch_games_owned(session, username, current_page)

            for game in new_games_owned.values():
                games_owned[game["Game ID"]] = game

            if len(new_games_owned) < 50:
                break
            else:
                current_page += 1

    print(f"Total owned games fetched: {len(games_owned)}")

    games = merge_games_and_update_owned(games, games_owned)
       
    print(f"Total games after merge: {len(games)}")
    
    # Create a new dictionary for player count data
    player_count_data_dict = {}

    # Fetch weights, poll IDs, and player count data for each game
    missing_weights = []
    missing_weight_votes = []
    missing_poll_ids = []
    missing_player_data = []
    
    print("\n")
    
    with tqdm(total=len(games),smoothing=0,desc="Updating game data") as progress_bar:
        games, player_count_data_dict = update_boardgame_data(games, batch_size=batch_size, progress_bar=progress_bar)
     
    print("\n")
  
    print(f"Total games in gamesid {len(games)}")
    print(f"Total line in playercount: {len(player_count_data_dict)}")
    
    write_merged_data_to_csv(games, player_count_data_dict, output_csv_filename)
    
    print(f"Success!")
    time.sleep(5)

if __name__ == "__main__":
    main()

