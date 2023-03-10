import requests
import json
import re
# scrape
from bs4 import BeautifulSoup



headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def getPhonetic(word):
    # filter punctuation
    word = re.sub('[^\w\'-]','', word)
    # if word has ' , substitutes ' with g to handle words like thinkin', waitin'
    if re.search('\'$', word):
        word = re.sub('\'$', 'g', word)

    url = 'https://dictionary.cambridge.org/us/dictionary/english/' + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    if soup.find('div', class_='pos-header dpos-h') is None:
        return None

    phonetic = soup.find(
        'div', class_='pos-header dpos-h').find_all('span', 'ipa dipa lpr-2 lpl-1')

    output = []
    
    for phon in phonetic:
        output.append(phon.get_text())

    return output


def getSpellings(word):
    # filter punctuation
    word = re.sub('[^\w\'-]','', word)
    # if word has ' , substitutes ' with g to handle words like thinkin', waitin'
    originWord = word.lower() 
    if re.search('\'$', word):
        word = re.sub('\'$', 'g', word)

    url = 'https://dictionary.cambridge.org/us/dictionary/english/' + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    if soup.find('div', 'pos-header dpos-h') is None:
        return None
    
    spellings = soup.find('div', 'pos-header dpos-h').find('span', 'hw dhw')
    altSpell = soup.find('div', 'pos-header dpos-h').find('span', 'v dv lmr-0')

    output = [spellings.get_text()]

    if altSpell != None:
        output.append(altSpell.get_text())

    if re.search('\'$', originWord):
        output.append(originWord)

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

def generate_json_output():
    user_input = input("Enter a sentence or word: ")

    words = user_input.split()

    for word in words:
        print(packJSON(word))


generate_json_output()