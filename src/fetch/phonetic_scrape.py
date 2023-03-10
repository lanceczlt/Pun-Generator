import requests
import re
import json
# scrape
from bs4 import BeautifulSoup


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def getPhonetic(word):

    word = re.sub('[^\w\'-]','', word)
    phoneticSing = False
    if re.search('\'$', word):
        word = re.sub('\'$', 'g', word)
        phoneticSing = True
    # if re.search('’$', word):
    #     word = re.sub('’$', 'g', word)

    word = re.sub('\'','-', word)
    url = 'https://www.dictionary.com/browse/' + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    if soup.find('span', class_='pron-spell-content css-7iphl0 evh0tcl1') is None:
        return None

    phonetic = soup.find(
        'span', class_='pron-spell-content css-7iphl0 evh0tcl1')
    


    phonetic = re.sub('[\[\]\']+', '', phonetic.get_text())

    # phonetic = re.sub(',[^,]*', "", phonetic.get_text())
    # phonetic = re.sub("\\W+", " ", phonetic)

    phoneticList = []
    prefix = []
    mid = []
    suffix = []

    if phoneticSing:
        suffix.append('sing')

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
    
    word = re.sub('[^\w\'-]','', word)
    originWord = word.lower()
  
    if re.search('\'$', word):
        word = re.sub('\'$', 'g', word)
    # if re.search('’$', word):
    #     word = re.sub('’$', '\'', word)
    #     originWord = word.lower()
    #     word = re.sub('\'$', 'g', word)


    word = re.sub('\'','-', word)
    url = 'https://www.dictionary.com/browse/' + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    if soup.find('div', class_='css-jv03sw e1wg9v5m6') is None:
        return None

    spellings = soup.find('div', class_='css-jv03sw e1wg9v5m6')
    altSpell = soup.find('h3', class_='css-1flgti4 ea1n8qa2')
    spellings = re.sub('[0-9]', '', spellings.get_text())

    spellingList = [spellings]

    if(altSpell != None):
        altSpell = re.sub('[^\w\s]', '', altSpell.get_text())
        altSpell = re.sub('^or', '', altSpell)
        for alt in altSpell.split(' or '):
            spellingList.append(alt.strip())

    if re.search('\'$', originWord):
        spellingList.append(originWord)
    # if re.search('’$', originWord):
    #     spellingList.append(originWord)

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


def generate_json_output():
    user_input = input("Enter a sentence or word: ")

    words = user_input.split()

    for word in words: 
        print(packJSON(word))

generate_json_output()
