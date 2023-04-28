import requests
import os
import json
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from genius import scrape_genius
import requests
import re
import chromedriver_autoinstaller
# used to convert language code to name (e.g. "en" --> "English")
from iso639 import Lang

# load env to access Genius API token
from dotenv import load_dotenv
load_dotenv()

chromedriver_autoinstaller.install()

"""
TODO: Abstract retrieval of song metadata.

Currently, songs URLs are either 
    - retrieved via the Genius API search (which already yields song metadata)
    - scraped from top 100 charts using Selenium (along with song_id)

--> Write a function that takes in flexible arguments so it can output song metadata for either option
--> Goal is to end up with scrape lyrics function, retrieve metadata function, output as JSON function
"""


def get_top100_urls():
    """Uses Selenium ChromeDriver to scrape page links to the top 100 songs on Genius.com.
    These links are then passed to top100_link_to_api(url) where the page is scraped for lyrics and song_id.
    song_id is then used to query the Genius API and retrieve relevant metadata about the song.
    """
    url = 'https://genius.com/'

    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)

    top100_container = driver.find_element(By.ID, "top-songs")

    load_more_button = top100_container.find_element(
        By.CSS_SELECTOR, "div[class='SquareButton-sc-109lda7-0 gsoAZX']")

    while load_more_button is not None:
        load_more_button.click()
        time.sleep(2)
        try:
            load_more_button = top100_container.find_element(
                By.CSS_SELECTOR, "div[class='SquareButton-sc-109lda7-0 gsoAZX']")
        except NoSuchElementException:
            load_more_button = None
            pass

    time.sleep(2)
    songs_div = top100_container.find_element(
        By.CSS_SELECTOR, "div[class='PageGridFull-sc-18uuafq-0 kfrnFZ']")
    songs = songs_div.find_elements(By.TAG_NAME, "a")
    links = []
    for song in songs:
        links.append(song.get_attribute("href"))

    driver.close()

    # now scrape and get metadata from Genius api using the links
    for link in links:
        top100_link_to_api(link)


def top100_link_to_api(url):
    """Using a link to a Genius song lyrics page, scrapes and finds its song_id
    and uses that song_id to access relevant song metadata (artist, title, language, etc.)

    Args:
        url (string): a link to a Genius song lyrics page
    """

    client_access_token = os.getenv("CLIENT_ACCESS_TOKEN")

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    song_id_container = soup.find(
        "meta", content=re.compile("^genius://songs/"))
    song_id = re.sub(r"^genius://songs/", "", song_id_container['content'])

    genius_song_search_url = f"http://api.genius.com/songs/{song_id}"
    response = requests.get(genius_song_search_url, {
                            'access_token': client_access_token})
    json_data = response.json()
    song_metadata = json_data['response']['song']
    song_title = song_metadata['title']
    song_url = url
    artist_name = song_metadata['primary_artist']['name']
    iso_code = song_metadata['language']

    # convert iso639-1 code to language name
    try:
        lg = Lang(iso_code)
        language = lg.name
    except:
        language = iso_code

    source = {
        "name": "Genius",
        "url": song_url,
        "song_title": song_title.replace('\u200b', ''),
        "artist": artist_name.replace('\u200b', ''),
        "language": language,
        "from": "Genius | Top 100 Charts",
    }

    lyrics = scrape_genius(url)
    phrases = set()

    for line in lyrics:
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

    print(json.dumps(song_json))


if __name__ == "__main__":
    get_top100_urls()
