import requests
import json
# scrape
from bs4 import BeautifulSoup


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def getPhonetic(word):
    url = 'https://dictionary.cambridge.org/us/dictionary/english/' + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    phonetic = soup.find(
        'div', class_='pos-header dpos-h').find_all('span', 'ipa dipa lpr-2 lpl-1')

    output = []
    for phon in phonetic:
        output.append(phon.get_text())

    return output


def getSpellings(word):
    url = 'https://dictionary.cambridge.org/us/dictionary/english/' + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    spellings = soup.find('div', 'pos-header dpos-h').find('span', 'hw dhw')
    altSpell = soup.find('div', 'pos-header dpos-h').find('span', 'v dv lmr-0')

    output = [spellings.get_text(), altSpell.get_text()]
    return output


def packJSON(word):
    source = {
        "site_name": 'Cambridge Dictionary',
        "URL": 'https://dictionary.cambridge.org/us/dictionary/english/' + word,
    }

    json_schema = {
        "type": "word",
        "spellings": getSpellings(word),
        "phonetics": getPhonetic(word),
        "source": source
    }

    output = json.dumps(json_schema)
    return output


# print(packJSON('adapter'))
