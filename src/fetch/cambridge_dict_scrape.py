import argparse
import json
import re
import sys
from collections.abc import Iterable
from string import punctuation

import requests

# scrape
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def getPhonetic(word) -> list[str] | None:
    # filter punctuation
    word = re.sub("[^\w'-]", "", word)
    # if word has ' , substitutes ' with g to handle words like thinkin', waitin'
    if re.search("'$", word):
        word = re.sub("'$", "g", word)

    url = "https://dictionary.cambridge.org/us/dictionary/english/" + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")

    if soup.find("div", class_="pos-header dpos-h") is None:
        return None

    phonetic = soup.find("div", class_="pos-header dpos-h").find_all(
        "span", "ipa dipa lpr-2 lpl-1"
    )

    output = []

    for phon in phonetic:
        output.append(phon.get_text())

    return output


def getSpellings(word) -> list[str] | None:
    # filter punctuation
    word = re.sub("[^\w'-]", "", word)
    # if word has ' , substitutes ' with g to handle words like thinkin', waitin'
    originWord = word.lower()
    if re.search("'$", word):
        word = re.sub("'$", "g", word)

    url = "https://dictionary.cambridge.org/us/dictionary/english/" + word
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")

    if soup.find("div", "pos-header dpos-h") is None:
        return None

    spellings = soup.find("div", "pos-header dpos-h").find("span", "hw dhw")
    altSpell = soup.find("div", "pos-header dpos-h").find("span", "v dv lmr-0")

    output = [spellings.get_text()]

    if altSpell != None:
        output.append(altSpell.get_text())

    if re.search("'$", originWord):
        output.append(originWord)

    return output


def packJSON(word) -> str | None:
    source = {
        "site_name": "Cambridge Dictionary",
        "type": "dictionary",
        "language": "english",
        "URL": "https://dictionary.cambridge.org/us/dictionary/english/" + word,
    }

    spellings = getSpellings(word)
    if spellings is None or not spellings:
        return None

    phonetics = getPhonetic(word)
    json_schema = {
        "type": "word",
        "spellings": spellings,
        # "phonetics": getPhonetic(word),
        "source": source,
    }
    if phonetics is not None and phonetics:
        json_schema["phonetics"] = phonetics

    output = json.dumps(json_schema)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="PunGenT dictionary scraper (Python)",
        description="""
        Finds phonetic spellings and alternate spellings for the input words.
        Input can be given through stdin, CL args, or else interactively
        """,
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="if passed, each line of Standard Input is treated as a word",
    )
    parser.add_argument(
        "word", nargs="*", help="input words passed through command line args"
    )
    args = parser.parse_args()
    items: Iterable[str]
    if args.stdin:
        items = sys.stdin
    elif args.word:
        items = args.word
    else:
        items = [input("Enter a sentence or word: ")]

    for item in items:
        words = item.split()
        for word in (w.strip(punctuation) for w in words):
            if not word.strip():
                continue
            json_str = packJSON(word)
            if json_str is not None:
                print(json_str)
