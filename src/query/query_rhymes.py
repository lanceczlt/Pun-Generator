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

    rhyming_phrases: List[Dict[str, str]] = []

    for word in rhyming_words:
         query = """
            SELECT DISTINCT s.name, m.val, p.phrase
            FROM phrase p
            JOIN phrase_src ps ON ps.phrase_id = p.phrase_id
            JOIN source s ON s.src_id = ps.src_id
            JOIN source_metadata sm ON sm.src_id = s.src_id
            JOIN metadata m ON m.metadata_id = sm.metadata_id
            WHERE p.phrase LIKE ? AND m.tag_id = 1
        """
         for row in cursor.execute(query, (f"% {word}",)):
            source_name, metadata_val, phrase = row
            metadata = {"source": source_name, "value": metadata_val}

            for rhyme_word in rhyming_words:
                rhymed_phrase = phrase.replace(f" {word}", f" {rhyme_word}")
                original_phrase = " ".join(input).replace(word, rhyme_word)

                rhyming_phrases.append({
                    "source_name": source_name,
                    "metadata": metadata,
                    "original_phrase": original_phrase,
                    "rhymed_phrase": rhymed_phrase
                })

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