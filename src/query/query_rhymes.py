import sqlite3 as sql
import argparse
import requests
import itertools as its
import re
from collections.abc import Iterable
import json

API_BASE_URL = "https://api.datamuse.com/words"


def replace_word(string, word, substitution_word): return string.replace(
    word, substitution_word, 1)


def find_rhymes_api(word: str) -> Iterable[str]:
    params = {
        "rel_rhy": word,
        "max": 500,
    }
    response = requests.get(API_BASE_URL, params=params)
    response.raise_for_status()
    return (result["word"] for result in response.json())


def find_rhymes(cursor: sql.Cursor, input: list[str], mode: str, filters: list[str], nsfw_enabled: bool) -> Iterable[str]:
    words: list[str]

    if mode == "phrase":
        words = list(its.chain.from_iterable(item.split() for item in input))
    elif mode == "word": 
        words = input
    
    # for now...
    input_word = words[0]

    rhyming_words: set[str] = set()
    for word in words:
        rhyming_words.update(find_rhymes_api(word))

    rhyming_phrases: list[dict[str, str]] = []
    seen_phrases = set()

    query = """
        SELECT DISTINCT p.phrase, s.name, m.val
        FROM phrase p
        JOIN phrase_src ps ON ps.phrase_id = p.phrase_id
        JOIN source s ON s.src_id = ps.src_id
        JOIN source_metadata sm ON sm.src_id = s.src_id
        JOIN metadata m ON m.metadata_id = sm.metadata_id
        WHERE p.phrase LIKE ?
        AND s.name IN ({})
    """.format(",".join("?"*len(filters)))

    for rhyme_word in rhyming_words:
         params = (f"%{rhyme_word}%",) + tuple(filters)
         for row in cursor.execute(query, params):
            phrase, source_name, metadata = row
            phrase = phrase.lower()
            if phrase in seen_phrases:
                continue

            metadata = {"source": source_name}
            rhymed_phrase = replace_word(phrase, rhyme_word, input_word)

            rhyming_phrases.append({
                "original_phrase": phrase,
                "rhymed_phrase": rhymed_phrase,
                "metadata": metadata,
            })

            seen_phrases.add(phrase)

    return rhyming_phrases


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
    parser.add_argument("--std-in",
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
    parser.add_argument(
    "--filters",
    type=json.loads,
    default=[],
    help="JSON string representing a list of source names to include in the query results"
    )
    parser.add_argument(
    "--nsfw",
    action="store_true",
    default=True,
    help="include offensive words in the results"
    )

    args = parser.parse_args()

    conn_path = args.db_path
    conn = sql.connect(conn_path)
    cursor: sql.Cursor = conn.cursor()

    input: list[str] = args.input
    mode: str = args.mode
    filters: list[str] = args.filters
    nsfw_enabled = args.nsfw

    results = find_rhymes(cursor, input, mode, filters, nsfw_enabled)
    print(json.dumps(results))
