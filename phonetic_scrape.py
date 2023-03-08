import requests
import re
import json
# scrape
from bs4 import BeautifulSoup


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def getPhonetic(word):
    url = 'https://www.dictionary.com/browse/' + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    phonetic = soup.find(
        'span', class_='pron-spell-content css-7iphl0 evh0tcl1')
    
    if phonetic is None:
        return None

    phonetic = re.sub('[\[\]\']+', '', phonetic.get_text())

    # phonetic = re.sub(',[^,]*', "", phonetic.get_text())
    # phonetic = re.sub("\\W+", " ", phonetic)

    phoneticList = []
    prefix = []
    mid = []
    suffix = []

    if(len(phonetic.split(',')) == 1):
        return [phonetic.strip()]

    phonetic = phonetic.strip().replace(' ', '').split(',')

    for word in phonetic:

        prefPatt = re.search('^[^-]+', word)
        if prefPatt:
            lettersBef = prefPatt.group()
            prefix.append(lettersBef)

        midPatt = re.search('-[^-]+-', word)
        if midPatt:
            lettersMid = midPatt.group()
            mid.append(lettersMid)

        sufPatt = re.search('[^-]+$', word)
        if sufPatt:
            lettersAft = sufPatt.group()
            suffix.append(lettersAft)

    empty = []

    if(mid != empty):
        for pref in prefix:
            for mids in mid:
                for sufs in suffix:
                    phoneticList.append(pref + mids + sufs)
    else:
        for item in prefix:
            for suf in suffix:
                phoneticList.append(item + '-' + suf)

    return phoneticList


def getSpellings(word):
    url = 'https://www.dictionary.com/browse/' + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    spellings = soup.find('div', class_='css-jv03sw e1wg9v5m6')
    altSpell = soup.find('h3', class_='css-1flgti4 ea1n8qa2')

    if spellings is None:
        return None

    spellings = re.sub('[^a-zA-Z]', '', spellings.get_text())

    spellingList = [spellings]

    if(altSpell != None):
        altSpell = re.sub('[^\w\s]', '', altSpell.get_text())
        altSpell = re.sub('^or', '', altSpell)
        for alt in altSpell.split(' or '):
            spellingList.append(alt.strip())

    return spellingList


def packJSON(word):
    source = {
        "site_name": 'Dictionary.com',
        "URL": 'https://www.dictionary.com/browse/' + word,
    }

    json_schema = {
        "type": "word",
        "spellings": getSpellings(word),
        "phonetics": getPhonetic(word),
        "source": source
    }

    output = json.dumps(json_schema)
    return output


# print(packJSON('hello'))
# print(packJSON('adapter'))
# print(packJSON('glamor'))
