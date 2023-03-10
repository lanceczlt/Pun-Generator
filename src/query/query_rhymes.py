import sqlite3 as sql
import argparse
import sys
import io
from collections.abc import Iterable


def find_rhymes(cursor: sql.Cursor, input: str) -> Iterable[str]:
    """"""
    return ()


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
        # took out wordblob for now
        choices=["word", "phrase"],
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
    cursor = conn.cursor()

    input = args.input
    # todo: handle stdin, etc

    for result in find_rhymes(cursor, input):
        # todo: consider buffering, delayed flushing
        print(result)