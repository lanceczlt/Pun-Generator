import argparse
import sqlite3 as sql
from collections.abc import Iterator

"""
Queries the DB for words missing phonetic entries.
"""


def select_words_without_phonetics(cursor: sql.Cursor) -> Iterator[str]:
    """
    Selects the words without corresponding phonetic entries.
    Returns the Cursor, which can be used as an iterator for the result
    """
    # select word spelling where word_id not in phonetics
    # todo: treat alt_spellings as duplicates?
    # there should be a more efficient way but I don't see it right now
    a = cursor.execute(
        """
        SELECT spelling
        FROM word_spelling AS ws
        WHERE NOT EXISTS
        (
            SELECT 1
            FROM word_phonetic AS wp
            WHERE ws.word_id = wp.word_id
        )
        """
    ).fetchall()
    return (row[0] for row in a)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Query missing phonetics",
        description="""
        Queries the given SQLite DB for words missing phonetic entries.
        """,
    )
    parser.add_argument("db_path", help="path to the DB instance to connect to")
    # TODO: add support for tag filtering
    # parser.add_argument( tag filter )

    args = parser.parse_args()
    conn_path = args.db_path
    conn = sql.connect(conn_path)
    cursor = conn.cursor()

    for s in select_words_without_phonetics(cursor):
        print(s)
