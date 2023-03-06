import sqlite3
import argparse
import json
import re
import sys
import io
from collections.abc import Iterable

"""
TODO: handle versioning
"""


# https://www.sqlite.org/withoutrowid.html
# to be considered: using 'withoutrowid'
tables: list[tuple[str, list[str]]] = [
    (
        "tag",
        [
            "tag_id INTEGER PRIMARY KEY",
            "name TEXT",
        ],
    ),
    (
        "metadata",
        [
            "metadata_id INTEGER PRIMARY KEY",
            "tag_id INTEGER",
            "val TEXT",
            "FOREIGN KEY(tag_id) REFERENCES tag(tag_id)",
        ],
    ),
    ("source", ["src_id INTEGER PRIMARY KEY"]),
    (
        "source_metadata",
        [
            "metadata_id INTEGER PRIMARY KEY",
            "src_id INTEGER",
            "FOREIGN KEY(metadata_id) REFERENCES metadata(metadata_id)",
            "FOREIGN KEY(src_id) REFERENCES source(src_id)",
        ],
    ),
    (
        "alt_spelling",
        [
            "word1 TEXT",
            "word2 TEXT",
            "PRIMARY KEY (word1, word2)",
        ],
    ),
    (
        "word_phonetic",
        [
            "word TEXT",
            "phonetic TEXT",
            "PRIMARY KEY (word, phonetic)",
        ],
    ),
    (
        "word_src",
        [
            "word TEXT",
            "src_id INTEGER",
            "PRIMARY KEY (word, src_id)",
            "FOREIGN KEY (src_id) REFERENCES source(src_id)",
        ],
    ),
    (
        "word_assoc",
        [
            "word1 TEXT",
            "word2 TEXT",
            "src_id INTEGER",
            "PRIMARY KEY (word1, word2, src_id)",
            "FOREIGN KEY (src_id) REFERENCES source(src_id)",
        ],
    ),
    (
        "phrase",
        [
            "phrase_id INTEGER PRIMARY KEY",
            "phrase TEXT",
        ],
    ),
    (
        "phrase_src",
        [
            "phrase_id INTEGER PRIMARY KEY",
            "src_id INTEGER",
            "FOREIGN KEY(src_id) REFERENCES source(src_id)",
            "FOREIGN KEY(phrase_id) REFERENCES phrase(phrase_id)",
        ],
    ),
    (
        "phrase_words",
        [
            "phrase_id INTEGER",
            "word TEXT",
            "PRIMARY KEY (phrase_id, word)",
            "FOREIGN KEY(phrase_id) REFERENCES phrase(phrase_id)",
        ],
    ),
]


def table_to_statement(table_name: str, table_attrs: list[str]):
    return f"CREATE TABLE IF NOT EXISTS {table_name}({','.join(table_attrs)})"


def create_all_tables(cursor: sqlite3.Cursor):
    for name, fields in tables:
        cursor.execute(table_to_statement(name, fields))


# cached tag_name -> tag_id
CACHED_TAG_IDS: dict[str, int] = {}


def tag_to_id(cursor: sqlite3.Cursor, tag_name: str) -> int:
    """
    Inserts the tag if it does not exist already and returns the ID
    """
    cached_id = CACHED_TAG_IDS.get(tag_name)
    if cached_id is not None:
        return cached_id

    row: tuple[int] | None = cursor.execute(
        "SELECT tag_id FROM tag WHERE tag.name == ?", [tag_name]
    ).fetchone()
    if row is None:
        cursor.execute("INSERT INTO tag(name) VALUES(?)", [tag_name])
        id = cursor.lastrowid
    else:
        id = row[0]

    assert (
        id is not None
    )  # just to convince mypy. not handling failed insertions anyway

    CACHED_TAG_IDS[tag_name] = id
    return id


def insert_metadata(cursor: sqlite3.Cursor, tag_id: int, val: str):
    """
    Inserts a single metadata entry and returns the metadata_id
    """
    cursor.execute("INSERT INTO metadata(tag_id, val) VALUES(?, ?)", (tag_id, val))
    return cursor.lastrowid


def insert_source(cursor: sqlite3.Cursor, source: dict[str, str | list[str]]) -> int:
    """
    Inserts a source object and returns the new ID
    """
    src_id = source_to_id(cursor)
    for tag_name, val in source.items():
        vals = [val] if isinstance(val, str) else val
        tag_id = tag_to_id(cursor, tag_name)
        for v in vals:
            metadata_id = insert_metadata(cursor, tag_id, v)
            insert_source_metadata(cursor, metadata_id, src_id)

    return src_id  # type: ignore


def source_to_id(cursor: sqlite3.Cursor):
    """
    Inserts the source and returns the new ID
    """
    cursor.execute("INSERT INTO source() DEFAULT VALUES")
    return cursor.lastrowid


def insert_source_metadata(cursor: sqlite3.Cursor, metadata_id: int, src_id: int):
    """
    Inserts a record connecting the metadata_id and src_id
    Does not return anything
    """
    cursor.execute(
        "INSERT OR IGNORE INTO source_metadata(metadata_id, src_id) VALUES(?, ?)",
        (metadata_id, src_id),
    )


def insert_spellings(cursor: sqlite3.Cursor, words: Iterable[str]):
    """
    Takes a sequence of words and inserts them as equivalent spellings for each other
    For space and time, only entries involving the lexicographically lowest word are made
    """
    lowest = min(words)
    params = ((lowest, word) for word in words if word != lowest)
    cursor.executemany(
        "INSERT OR IGNORE INTO alt_spelling(word1, word2) VALUES(?, ?)", params
    )


def insert_word_phonetic(cursor: sqlite3.Cursor, word: str, phonetics: Iterable[str]):
    """
    Inserts all the phonetics as pronounciations for 'word', returns nothing
    """
    if not phonetics:
        return
    cursor.executemany(
        "INSERT OR IGNORE INTO word_phonetic(word, phonetic) VALUES(?, ?)",
        ((word, phon) for phon in phonetics),
    )


def insert_word_source(cursor: sqlite3.Cursor, word: str, src_id: int):
    """
    Inserts word-source, returns nothing
    """
    cursor.execute(
        "INSERT OR IGNORE INTO word_src(word, src_id) VALUES(?, ?)", (word, src_id)
    )


def insert_word_assoc(cursor: sqlite3.Cursor, word1: str, word2: str, src_id: int):
    """
    Inserts, returns nothing
    """
    cursor.execute(
        "INSERT OR IGNORE INTO word_assoc(word1, word2, src_id) VALUES(?, ?, ?)",
        (word1, word2, src_id),
    )


def insert_phrase(cursor: sqlite3.Cursor, phrase: str):
    """
    Inserts a phrase and returns phrase id
    """
    cursor.execute("INSERT INTO phrase(phrase) VALUES(?)", [phrase])
    return cursor.lastrowid


def insert_phrase_source(cursor: sqlite3.Cursor, phrase_id: int, src_id: int):
    """
    Inserts source for phrase, returns nothing
    """
    cursor.execute("INSERT OR IGNORE INTO phrase_src(src_id) VALUES(?)", [src_id])


def insert_phrase_words(cursor: sqlite3.Cursor, phrase_id: int, words: Iterable[str]):
    """
    Inserts phrase word by word, returns nothing
    """
    cursor.executemany(
        "INSERT INTO phrase(phrase_id, word) VALUES(?, ?)",
        ((phrase_id, word) for word in words),
    )


def import_item(cursor: sqlite3.Cursor, obj: dict):
    """
    Insert the contents of a single word entry into the DB referenced by conn
    """
    match obj.get("type"):
        case None:
            print("received json with no type field")
        case "word":
            import_item_word(cursor, obj)
        case "phrase":
            import_item_phrase(cursor, obj)
        case "paragraph":
            import_item_paragraph(cursor, obj)
        case _:
            print(f"unrecognized json with type {obj['type']}")


def import_item_word(cursor: sqlite3.Cursor, obj: dict):
    """
    obj schema: {
        type: 'word',
        spellings: str | list[str],
        phonetics: str | list[str],
        source: {},
    }
    """
    spellings = obj.get("spellings")
    if spellings is None:
        return
    insert_spellings(cursor, spellings)

    phonetics = obj.get("phonetics")
    if phonetics is not None:
        insert_word_phonetic(cursor, min(spellings), phonetics)

    source = obj.get("source")
    if source is not None:
        source_id = insert_source(cursor, source)
        insert_word_source(cursor, min(spellings), source_id)


PHRASE_SPLITTER = re.compile(r"\W+")


def phrase_to_words(phrase: str) -> set[str]:
    """
    Placeholder.
    Split a string representing a phrase into a set of words.
    Splits on nonword sequences.
    """
    # this is a cursed problem
    # P <= NP <<< NLP
    # todo: remove 's from \w+ 's (\W+|$).
    # todo: replace ' quotes with " ? or vice versa?
    return {s.lower() for s in re.split(PHRASE_SPLITTER, phrase)}


def import_item_phrase(cursor: sqlite3.Cursor, obj: dict):
    """
    obj schema: {
        type: 'phrase',
        phrase(s?): str | list[str],
        source: {}
    }
    """
    phrases = obj.get("phrases")
    if phrases is None:
        if "phrase" in obj:
            phrases = obj["phrase"]
        else:
            return

    if isinstance(phrases, str):
        phrases = [phrases]

    source = obj.get("source")
    if source is not None:
        source_id = insert_source(cursor, source)

    for phrase in phrases:
        phrase_id = insert_phrase(cursor, phrase)
        insert_phrase_words(cursor, phrase_id, phrase_to_words(phrase))
        if source is not None:
            insert_phrase_source(cursor, phrase_id, source_id)


def import_item_paragraph(cursor: sqlite3.Cursor, obj: dict):
    """
    TODO: put schema
    """


def import_stream(cursor: sqlite3.Cursor, in_stream):
    """
    Custom delimiters should be applied via the 'newline' kw-arg when creating the stream.

    :param in_stream: should support readline()
    """
    for line in in_stream:
        item = json.loads(line)
        import_item(cursor, item)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="punDB importer (Python)",
        description="""
        Imports a stream of DB entries encoded as JSON from STDIN into an DB instance.
        Items should be separated by 'sep', and 'sep' should not appear in the data of an entry
        """,
    )
    parser.add_argument("db_path", help="path to the DB instance to connect to")
    parser.add_argument(
        "--sep",
        nargs="?",
        dest="sep",
        default="\n",
        help="entry separator in stdin. newline by default",
    )

    args = parser.parse_args()

    conn_path = args.db_path
    conn = sqlite3.connect(conn_path)
    cursor = conn.cursor()

    create_all_tables(cursor)

    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, newline=args.sep)
    sys.stdin.reconfigure(newline=args.sep)
    stream = sys.stdin

    import_stream(cursor, stream)
