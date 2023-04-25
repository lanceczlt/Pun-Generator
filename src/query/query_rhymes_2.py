import sqlite3 as sql
import argparse
import itertools as its
from collections.abc import Iterable

API_BASE_URL = "https://api.datamuse.com/words"


def find_rhymes(cursor: sql.Cursor, words: list[str]) -> Iterable[str]:
    # get word_ids for spelling
    # get phonetics for word
    # store in table
    # get other phonetics that share subseq of phonetic
    # get spellings for those word_ids
    query1 = f"\
    CREATE TEMPORARY TABLE table1\
    AS \
    (SELECT word_phonetic.word_id, word_phonetic.phonetic\
    FROM word_phonetic\
    INNER JOIN word_spelling\
      ON word_phonetic.word_id = word_spelling.word_id\
    WHERE word_spelling.spelling in ({','.join('?' for i in words)}));\
    "
    cursor.execute(query1, tuple(words))
    # get longest phonetic, as upper bound for loop
    (max_length,) = cursor.execute(
        "SELECT max(length(phonetic)) FROM table1"
    ).fetchone()
    # loop through subsequences of phonetics
    # for i from 1 to max_length, get last i chars of phonetic
    query2 = "SELECT word_phonetic.phonetic from word_phonetic WHERE substr(word_phonetic.phonetic, -?) "
    #
    res = cursor.executemany(
        query2, ((i,) for i in range(1, max_length + 1))
    ).fetchall()
    return (s for s in res)


def find_rhymes(cursor: sql.Cursor, input: list[str], mode: str) -> Iterable[str]:
    words: list[str]

    if mode == "phrase":
        words = list(its.chain.from_iterable(item.split() for item in input))
    elif mode == "word":
        words = input

    rhyming_words: set[str] = set()
    rhyming_words.update(find_rhymes(cursor, words))

    rhyming_phrases: set[tuple[str, str]] = set()
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
    parser.add_argument("db_path", help="path to the DB instance to connect to")
    parser.add_argument(
        "input",
        nargs="+",
        help="the input to find related rhymes for",
    )
    parser.add_argument(
        "--std-in",
        help="if present, read input from stdin. each line corresponds to an input",
    )
    parser.add_argument(
        "--mode",
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
