import json
import csv  
import itertools
import os
import subprocess
from typing import List, Dict


def read_anime_quotes(anime_quotes_path: str) -> List[Dict]:
    anime_quotes = []
    with open(anime_quotes_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            anime_quotes.append(
                {
                    "type": "phrase",
                    "phrases": [row["Quote"]],
                    "source": {"name": row["Anime"], "author": row["Character"]},
                }
            )
    return anime_quotes

def read_formal_idioms(formal_idioms_path: str) -> List[Dict]:
    formal_idioms = []
    with open(formal_idioms_path, "r", encoding="utf-8") as f:
        phrases = [line.strip() for line in f]
        formal_idioms = [
            {"type": "phrase", "phrases": phrases, "source": {"name": "Formal Idioms"}}
        ]
    return formal_idioms

def read_common_phrases(phrases_path: str) -> List[Dict]:
    phrases = []
    with open(phrases_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            phrases.append(row["text"])
    return [{"type": "phrase", "phrases": phrases, "source": {"name": "Common Phrases"}}]


def read_static_idioms(static_idioms_path: str) -> List[Dict]:
    static_idioms = []
    with open(static_idioms_path, "r", encoding="utf-8") as f:
        phrases = [line.strip() for line in f]
        static_idioms = [
            {"type": "phrase", "phrases": phrases, "source": {"name": "Static Idioms"}}
        ]
    return static_idioms

def read_top_movies(top_5000_movies_path: str) -> List[Dict]:
    top_movies = []
    with open(top_5000_movies_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        source_name = next(reader)[0]
        phrases = [row[0] for row in reader]
        top_movies = [{"type": "phrase", "phrases": phrases, "source": {"name": source_name}}]
    return top_movies

def read_urban_dict(urbandict_words_path: str) -> List[Dict]:
    with open(urbandict_words_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        words = [row["word"] for row in reader]
    return [
        {
            "type": "phrase",
            "phrases": words,
            "source": {"name": "Urban Dictionary"},
        }
    ]

def import_data(data: List[Dict], batch_size: int, name: str):
    cmd = f'python3 import/importer_json_to_sqlite.py my_db.sqlite'
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        for item in batch:
            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
            p.communicate(json.dumps(item).encode())
            p.wait()

def main():
    data_dir = os.path.abspath(os.path.join(os.getcwd(), 'data'))

    anime_quotes_path = os.path.join(data_dir, 'anime_quotes.csv')
    formal_idioms_path = os.path.join(data_dir, 'formal_idioms.txt')
    phrases_path = os.path.join(data_dir, 'phrases.csv')
    static_idioms_path = os.path.join(data_dir, 'static_idioms.txt')
    top_5000_movies_path = os.path.join(data_dir, 'top_5000_movies.csv')
    urbandict_words_path = os.path.join(data_dir, 'urbandict_words.csv')

    anime_quotes = read_anime_quotes(anime_quotes_path)
    print(f"Importing {len(anime_quotes)} anime quotes...")
    import_data(anime_quotes, batch_size=100, name="anime quotes")

    formal_idioms = read_formal_idioms(formal_idioms_path)
    print(f"Importing {len(formal_idioms)} formal idioms...")
    import_data(formal_idioms, batch_size=100, name="formal idioms")

    phrases = read_common_phrases(phrases_path)
    print(f"Importing {len(phrases)} common phrases...")
    import_data(phrases, batch_size=100, name="common phrases")

    static_idioms = read_static_idioms(static_idioms_path)
    print(f"Importing {len(static_idioms)} static idioms...")
    import_data(static_idioms, batch_size=100, name="static idioms")

    top_movies = read_top_movies(top_5000_movies_path)
    print(f"Importing {len(top_movies)} top movies...")
    import_data(top_movies, batch_size=100, name="top movies")

    urban_dict = read_urban_dict(urbandict_words_path)
    print(f"Importing {len(urban_dict)} urban dictionary words...")
    import_data(urban_dict, batch_size=100, name="urban dictionary words")

    print("Importing into SQLite is done!")



if __name__ == "__main__":
    main()
