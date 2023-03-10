import sqlite3 as sql
import argparse
import requests
import itertools as its
from collections.abc import Iterable

API_BASE_URL = "https://api.datamuse.com/words"


def find_rhymes_api(word: str) -> Iterable[str]:
    params = {
        "rel_rhy": word,
        "max": 500,
    }
    response = requests.get(API_BASE_URL, params=params)
    response.raise_for_status()
    return (result["word"] for result in response.json())


def find_rhymes(cursor: sql.Cursor, input: list[str], mode: str) -> Iterable[str]:
    words: list[str]

    if mode == "phrase":
        words = list(its.chain.from_iterable(item.split() for item in input))
    elif mode == "word":
        words = input

    rhyming_words: set[str] = set()
    for word in words:
        rhyming_words.update(find_rhymes_api(word))

    rhyming_phrases: set[Tuple[str, str]] = set()
    for word in rhyming_words:
        query = "SELECT phrase FROM phrase WHERE phrase LIKE ?"
        # limiting to 20 for each word currently
        for row in cursor.execute(query, (f"% {word}",)).fetchmany(20):
            rhyming_phrases.add((word, row[0]))

    results = []
    for phrase_tuple in rhyming_phrases:
        rhyme_word = phrase_tuple[0]
        phrase = phrase_tuple[1]
        rhymed_phrase = phrase.replace(f" {rhyme_word}", f" {words[0]}")
        result = f"original phrase: {phrase}\nrhymed phrase: {rhymed_phrase}\n"
        results.append(result)

    return results




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="punDB rhyme querier (Python)",
        description="""
        Querys a DB instance for rhymes
        """,
    )
    parser.add_argument("db_path", 
        help="path to the DB instance to connect to"
    )
    parser.add_argument("input",
        nargs="+",
        help="the input to find related rhymes for",
    )
    parser.add_argument( "--std-in",
        help="if present, read input from stdin. each line corresponds to an input",
    )
    parser.add_argument("--mode",
        # took out phrase for now
        choices=["word", "wordblob"],
        default="word",
        help="""
        how to interpret the input.
        word: each item is a word.
        wordblob: each item is split into words.
        phrase: each item is a phrase""",
    )

    args = parser.parse_args()

    conn_path = args.db_path
    conn = sql.connect(conn_path)
    cursor: sql.Cursor = conn.cursor()

    input: list[str] = args.input
    mode: str = args.mode

    # todo: handle stdin, etc
    print(f"INPUT: {input}")
    for result in find_rhymes(cursor, input, mode):
        print(result)