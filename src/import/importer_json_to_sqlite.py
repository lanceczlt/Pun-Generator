from string import punctuation
import sqlite3
import argparse
import json
import re
import sys
import io
from collections.abc import Iterable, Collection

"""
'recommended' API: functions prefixed with 'import_'

TODO: handle versioning,
    : improve handling of absent source
"""

# global constants

# used if word_assoc entry is missing 'type' field
DEFAULT_ASSOC_TYPE = "generic"

# used if no source was given
# sqlite supports None even for Primary Key. may eventually replace with special id
ABSENT_SOURCE_ID = None

# https://www.sqlite.org/withoutrowid.html
# to be considered: using 'withoutrowid'
# according to:
# https://www.sqlite.org/autoinc.html
# we probably don't need autoinc. Would primarily be a problem if
# we didn't enforce foreign key constraints when *deleting* rows
# no row deletion ATM
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
            "src_id INTEGER",
            "metadata_id INTEGER",
            "PRIMARY KEY (src_id, metadata_id)"
            "FOREIGN KEY(metadata_id) REFERENCES metadata(metadata_id)",
            "FOREIGN KEY(src_id) REFERENCES source(src_id)",
        ],
    ),
    (
        "word_spelling",
        [
            "word_id INTEGER PRIMARY KEY",
            "spelling TEXT NOT NULL UNIQUE",
        ],
    ),
    (
        "alt_spelling",
        [
            "word1_id INTEGER",
            "word2_id INTEGER",
            "PRIMARY KEY (word1_id, word2_id)",
            "FOREIGN KEY (word1_id) REFERENCES word_spelling(word_id)",
            "FOREIGN KEY (word2_id) REFERENCES word_spelling(word_id)",
        ],
    ),
    (
        "word_phonetic",
        [
            "word_id INTEGER",
            "phonetic TEXT",
            "PRIMARY KEY (word_id, phonetic)",
            "FOREIGN KEY (word_id) REFERENCES word_spelling(word_id)",
        ],
    ),
    (
        "word_src",
        [
            "word_id INTEGER",
            "src_id INTEGER",
            "PRIMARY KEY (word_id, src_id)",
            "FOREIGN KEY (word_id) REFERENCES word_spelling(word_id)",
            "FOREIGN KEY (src_id) REFERENCES source(src_id)",
        ],
    ),
    (
        "assoc_type",
        [
            "assoc_type_id INTEGER PRIMARY KEY",
            "name TEXT",
        ],
    ),
    (
        "word_assoc",
        [
            "word1_id INTEGER",
            "word2_id INTEGER",
            "src_id INTEGER",
            "assoc_type_id INTEGER",
            "PRIMARY KEY (word1_id, word2_id, src_id, assoc_type_id)",
            "FOREIGN KEY (word1_id) REFERENCES word_spelling(word_id)",
            "FOREIGN KEY (word2_id) REFERENCES word_spelling(word_id)",
            "FOREIGN KEY (src_id) REFERENCES source(src_id)",
            "FOREIGN KEY (assoc_type_id) REFERENCES assoc_type(assoc_type_id)",
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
            "word_id INTEGER",
            "PRIMARY KEY (phrase_id, word_id)",
            "FOREIGN KEY (phrase_id) REFERENCES phrase(phrase_id)",
            "FOREIGN KEY (word_id) REFERENCES word_spelling(word_id)",
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


# cached tag_name -> tag_id
CACHED_ASSOC_TYPE_IDS: dict[str, int] = {}


def assoc_type_to_id(cursor: sqlite3.Cursor, assoc_type: str) -> int:
    """
    Creates the word-assoc-type if it DNE. Returns its id
    """
    cached_id = CACHED_ASSOC_TYPE_IDS.get(assoc_type)
    if cached_id is not None:
        return cached_id

    row: tuple[int] | None = cursor.execute(
        "SELECT assoc_type_id FROM assoc_type WHERE assoc_type.name = ?", [assoc_type]
    ).fetchone()
    if row is None:
        cursor.execute("INSERT INTO assoc_type(name) VALUES(?)", [assoc_type])
        id = cursor.lastrowid
    else:
        id = row[0]

    assert (
        id is not None
    )  # just to convince mypy. not handling failed insertions anyway

    CACHED_ASSOC_TYPE_IDS[assoc_type] = id
    return id


def insert_metadata(cursor: sqlite3.Cursor, tag_id: int, val: str):
    """
    Inserts a single metadata entry and returns the metadata_id
    """
    cursor.execute("INSERT INTO metadata(tag_id, val) VALUES(?, ?)", (tag_id, val))
    return cursor.lastrowid


def insert_source(
    cursor: sqlite3.Cursor, source: dict[str, str | list[str]] | None
) -> int | None:
    """
    Inserts a source object and returns the new ID
    """
    if source is None:
        return ABSENT_SOURCE_ID

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
    cursor.execute("INSERT INTO source DEFAULT VALUES")
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


# cache
CACHED_WORD_SPELLING_IDS: dict[str, int] = {}


def spelling_to_id(cursor: sqlite3.Cursor, spelling: str):
    """
    Given a spelling, returns the word_id, creating an entry if needed.
    """
    cached_id = CACHED_WORD_SPELLING_IDS.get(spelling)
    if cached_id is not None:
        return cached_id

    row: tuple[int] | None = cursor.execute(
        "SELECT word_id FROM word_spelling WHERE word_spelling.spelling = ?",
        (spelling,),
    ).fetchone()

    if row is None:
        cursor.execute("INSERT INTO word_spelling(spelling) VALUES(?)", (spelling,))
        id = cursor.lastrowid
    else:
        id = row[0]
    assert id is not None
    CACHED_WORD_SPELLING_IDS[spelling] = id
    return id


def insert_spellings(cursor: sqlite3.Cursor, words: Collection[str]):
    """
    Takes a sequence of words (spellings) and inserts them as equivalent spellings for each other
    For space and time, only entries involving the lexicographically lowest word are made
    """
    lowest = spelling_to_id(cursor, min(words))
    params = [
        (lowest, spelling_to_id(cursor, word)) for word in words if word != lowest
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO alt_spelling(word1_id, word2_id) VALUES(?, ?)", params
    )


def insert_word_phonetic(
    cursor: sqlite3.Cursor, word_id: int, phonetics: Iterable[str]
):
    """
    Inserts all the phonetics as pronounciations for 'word', returns nothing
    """
    if not phonetics:
        return
    cursor.executemany(
        "INSERT OR IGNORE INTO word_phonetic(word_id, phonetic) VALUES(?, ?)",
        ((word_id, phon) for phon in phonetics),
    )


def insert_word_source(cursor: sqlite3.Cursor, word_id: int, src_id: int | None):
    """
    Inserts word-source, returns nothing
    """
    cursor.execute(
        "INSERT OR IGNORE INTO word_src(word_id, src_id) VALUES(?, ?)",
        (word_id, src_id),
    )


def insert_word_assocs(
    cursor: sqlite3.Cursor, assocs: Iterable[tuple[int, int, int | None, int]]
):
    """
    assocs: (word1, word2, src_id, assoc_type_id)*
    Inserts, returns nothingpython is genexpr recursive
    """
    cursor.executemany(
        "INSERT OR IGNORE INTO word_assoc(word1_id, word2_id, src_id, assoc_type_id) VALUES(?, ?, ?, ?)",
        assocs,
    )


def insert_phrase(cursor: sqlite3.Cursor, phrase: str):
    """
    Inserts a phrase and returns phrase id
    """
    cursor.execute("INSERT INTO phrase(phrase) VALUES(?)", [phrase])
    return cursor.lastrowid


def insert_phrase_source(cursor: sqlite3.Cursor, phrase_id: int, src_id: int | None):
    """
    Inserts source for phrase, returns nothing
    """
    cursor.execute("INSERT OR IGNORE INTO phrase_src(src_id) VALUES(?)", [src_id])


def insert_phrase_words(
    cursor: sqlite3.Cursor, phrase_id: int, word_ids: Iterable[int]
):
    """
    Inserts phrase word by word, returns nothing
    """
    cursor.executemany(
        "INSERT INTO phrase_words(phrase_id, word_id) VALUES(?, ?)",
        [(phrase_id, word_id) for word_id in word_ids],
    )


def __get_and_normalize(
    keys: Iterable[str], dic: dict[str, str | Collection[str]]
) -> None | Collection[str]:
    """
    Uses the first key in @keys to not map to None in @dic.
    Returns None if all of the keys did
    With that val, given a str or iterable of strs, returns equivalent iterable of strs.
    i.e., wraps single str into iterable
    """
    val = None
    for key in keys:
        val = dic.get(key)
        if val is None:
            continue
        return (val,) if isinstance(val, str) else val
    # no keys didn't produce None, so return None
    return None


def import_item(cursor: sqlite3.Cursor, obj: dict):
    """
    Insert the contents of a single word entry into the DB referenced by conn
    """
    match obj.get("type"):
        case None:
            print("received json with no type field")
        case "word" | "words":
            import_item_word(cursor, obj)
        case "assoc" | "word_assoc":
            import_item_word_assoc(cursor, obj)
        case "phrase" | "phrases":
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
    spellings = __get_and_normalize(("spellings", "spelling"), obj)
    if spellings is None or len(spellings) == 0:
        return
    insert_spellings(cursor, spellings)

    min_spelling_id = spelling_to_id(cursor, min(spellings))

    phonetics = __get_and_normalize(("phonetics", "phonetic"), obj)
    if phonetics is not None and len(phonetics) != 0:
        insert_word_phonetic(cursor, min_spelling_id, phonetics)

    source = obj.get("source")

    source_id = insert_source(cursor, source)
    insert_word_source(cursor, min_spelling_id, source_id)


def import_item_word_assoc(cursor: sqlite3.Cursor, obj: dict):
    """
    obj schema: {
        type: 'word_assoc' or 'assoc'
        assocs: [
            {
                word1: str,
                word2: str,
                type: str (optional, defaults to 'generic')
            },
        ],
        source: {}
    }
    """
    source = obj.get("source")
    source_id = insert_source(cursor, source)

    assocs = obj.get("assocs", obj.get("assoc"))
    if assocs is None or len(assocs) == 0:
        return
    if isinstance(assocs, dict):
        assocs = (assocs,)

    assoc_stream = [
        (
            spelling_to_id(cursor, assoc["word1"]),
            spelling_to_id(cursor, assoc["word2"]),
            source_id,
            assoc_type_to_id(cursor, assoc.get("type", "generic")),
        )
        for assoc in assocs
        if isinstance(assoc, dict) and "word1" in assoc and "word2" in assoc
    ]
    insert_word_assocs(cursor, assoc_stream)


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
    return {s.lower() for s in re.split(PHRASE_SPLITTER, phrase) if len(s) != 0}


def alt_phrase_to_words(phrase: str) -> set[str]:
    """Splits a string representing a phrase into a set of words. Preserves contractions and hyphenated words.
    e.g. dog-eat-dog and shouldn't will be preserved

    Note that abbreviations like "i.e." will be output as "i.e" and similarly "Dr." --> "dr"

    Args:
        phrase (str): String representing a phrase

    Returns:
        set[str]: A set of lowercase words with no leading or trailing punctuation
    """
    tokens = phrase.split()
    words = set()
    for token in tokens:
        words.add(token.lower().strip(punctuation + "¡¿"))

    return words


def import_item_phrase(cursor: sqlite3.Cursor, obj: dict):
    """
    obj schema: {
        type: 'phrase',
        phrase(s?): str | list[str],
        source: {}
    }
    """
    phrases = __get_and_normalize(("phrases", "phrase"), obj)
    if phrases is None:
        return

    source = obj.get("source")
    source_id = insert_source(cursor, source)

    for phrase in phrases:
        phrase_id = insert_phrase(cursor, phrase)
        insert_phrase_words(
            cursor,
            phrase_id,
            (spelling_to_id(cursor, word) for word in phrase_to_words(phrase)),
        )
        insert_phrase_source(cursor, phrase_id, source_id)


def import_item_paragraph(cursor: sqlite3.Cursor, obj: dict):
    """
    TODO: put schema
    """


def import_stream(cursor: sqlite3.Cursor, in_stream):
    """
    Custom delimiters should be applied via the 'newline' kw-arg when creating the stream.

    :param in_stream: file-like obj where readline() yields a single JSON instance
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
