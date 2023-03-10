import requests
import os
import json
from bs4 import BeautifulSoup
import re

# used to convert language code to name (e.g. "en" --> "English")
from iso639 import Lang

# load env to access Genius API token
from dotenv import load_dotenv
load_dotenv()


def scrape_genius(url):
    """Scrapes lyrics from the input Genius Lyrics song url

    Args:
        url (string): A link to a Genius Lyrics song page

    Returns:
        list: A list of the scraped lyrics
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    lyrics = soup.find_all(
        'div', class_='Lyrics__Container-sc-1ynbvzw-6 YYrds')

    result_string = ""

    for tag in lyrics:
        # replace <br> tags with line break for readability
        for br in tag.find_all("br"):
            br.replace_with("\n")

        result_string += re.sub(r'\[.*?\]', "", tag.get_text())

    return result_string.splitlines()


def fetch_genius(artist):
    """Scrapes all relevant song lyrics related to input artist.

    Args:
        artist (string): An artist to search for 

    Returns:
        list: A list of JSON where each JSON contains 
            a unique set of lowercase phrases from one of the artist's song lyrics along with relevant metadata
    """
    client_access_token = os.getenv("CLIENT_ACCESS_TOKEN")
    search_term = artist
    genius_search_url = f"http://api.genius.com/search?q={search_term}&access_token={client_access_token}"

    response = requests.get(genius_search_url)
    json_data = response.json()
    url_list = json_data['response']['hits']
    output_json_list = []

    for hit in url_list:
        song_title = hit['result']['title']
        song_url = hit['result']['url']
        artist_name = hit['result']['primary_artist']['name']
        iso_code = hit['result']['language']

        # convert iso639-1 code to language name
        try:
            lg = Lang(iso_code)
            language = lg.name
        except:
            language = iso_code

        source = {
            "site_name": "Genius",
            "url": song_url,
            "song_title": song_title.replace('\u200b', ''),
            "user_search": search_term,
            "artist": artist_name.replace('\u200b', ''),
            "language": language
        }

        # list of scraped lyrics separated by line
        song_lyrics = scrape_genius(song_url)

        phrases = set()

        for line in song_lyrics:
            # filter out empty lines
            if line == '':
                continue

            # lowercase for consistency, may need to clean out certain characters in the future
            cleaned_phrase = line.lower()
            phrases.add(cleaned_phrase)

        song_json = {
            "type": "phrase",
            "phrases": list(phrases),
            "source": source
        }

        output_json_list.append(json.dumps(song_json))

    return output_json_list


# def test_genius_fetch():
#     artist = input("Enter an artist's name:")
#     json_list = fetch_genius(artist)
#     for json in json_list:
#         print(json)


# test_genius_fetch()

def main():
    artist = input("Enter an artist's name:")
    json_list = fetch_genius(artist)
    for json in json_list:
        print(json)


if __name__ == "__main__":
    main()
