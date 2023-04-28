import sqlite3
from typing import List

def read_nsfw_words(file_path: str) -> List[str]:
    with open(file_path, "r") as file:
        return [word.strip() for word in file.readlines()]

def update_phrases_with_nsfw_words(db_path: str, nsfw_words: List[str]):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    nsfw_word_ids = []
    for word in nsfw_words:
        cursor.execute("SELECT word_id FROM word_spelling WHERE spelling = ?", (word,))
        result = cursor.fetchone()
        if result:
            nsfw_word_ids.append(result[0])

    for word_id in nsfw_word_ids:
        cursor.execute(
            "UPDATE phrase SET is_nsfw = 1 WHERE phrase_id IN (SELECT phrase_id FROM phrase_words WHERE word_id = ?)",
            (word_id,),
        )

    conn.commit()
    conn.close()

def main():
    nsfw_words_file = "data/nsfw_words.txt"
    nsfw_words = read_nsfw_words(nsfw_words_file)

    db_path = "./my_db.sqlite"
    update_phrases_with_nsfw_words(db_path, nsfw_words)

if __name__ == "__main__":
    main()
