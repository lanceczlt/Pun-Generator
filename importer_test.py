import unittest
import importer_json_to_sqlite as im
import sqlite3 as sql

"""
Tests for importer_json_to_sqlite
Some tests merely check that the input does not crash the program
"""


class ImportTestBase(unittest.TestCase):
    """provides setup that creates an in-memory DB"""

    def setUp(self):
        self.conn = sql.connect(":memory:")
        self.cursor = self.conn.cursor()
        im.create_all_tables(self.cursor)


class ImportWord(ImportTestBase):
    def test_single_values(self):
        im.import_item_word(
            self.cursor,
            {
                "type": "word",
                "spellings": "potato",
                "phonetics": "pəˈteɪ.təʊ",
                "source": {"site_name": "testing"},
            },
        )

        self.assertEqual(
            ("potato", "pəˈteɪ.təʊ"),
            self.cursor.execute(
                "SELECT word, phonetic FROM word_phonetic").fetchone(),
        )
        pass

    def test_multi_values(self):
        im.import_item_word(
            self.cursor,
            {
                "type": "word",
                "spellings": ["theatre", "theater"],
                "phonetics": ["ˈθiː.ə.t̬ɚ", "ˈθɪə.tər"],
                "source": {"site_name": "testing"},
            },
        )
        self.assertEqual(
            [
                ("theater", "ˈθiː.ə.t̬ɚ"),
                ("theater", "ˈθɪə.tər"),
            ],
            list(self.cursor.execute("SELECT word, phonetic FROM word_phonetic")),
        )
        pass


class AltPhraseSplitting(unittest.TestCase):
    """
    Testing alternative phrase splitter
    """

    def test_en_contractions(self):
        self.assertEqual(
            {
                "this",
                "is",
                "an",
                "ordinary",
                "english-sentence",
                "with",
                "some",
                "varying",
                "punctu4t1on",
                "e.g",
                "dog-eat-dog",
                "shouldn't",
                "we",
                "just",
                "get",
                "along",
                "they'll",
                "i'm",
                "jason's",
            },
            im.alt_phrase_to_words(
                "This... is an, 'ORDINARY!' English-sentence   with some (varying) #punctu4t1on@. e.g. dog-eat-dog ?!shouldN't wE@ just,- get along they'll, I'm Jason's?"
            )
        )

    def test_es(self):
        self.assertEqual(
            {
                "hay",
                "4",
                "estadounidenses",
                "secuestrados",
                "en",
                "méxico",
                "qué",
                "saben",
                "las",
                "autoridades",
            },
            im.alt_phrase_to_words(
                "Hay 4 estadounidenses secuestrados en México: ¿qué saben las autoridades?"
            )
        )


class PhraseSplitting(unittest.TestCase):
    def test_english(self):
        self.assertEqual(
            {
                "this",
                "is",
                "an",
                "ordinary",
                "english",
                "sentence",
                "with",
                "some",
                "varying",
                "punctu4t1on",
            },
            im.phrase_to_words(
                "This... is an, 'ORDINARY!' English-sentence   with some (varying) #punctu4t1on@."
            ),
        )

    def test_english_with_apostrophes(self):
        self.assertEqual(
            {"i'm", "sorry", "ms", "jackson"},
            im.phrase_to_words("I'm sorry, Ms. Jackson,"),
        )

    def test_english_with_titles(self):
        # todo: decide if this is the appropriate output (omitting .)
        self.assertEqual(
            {"dr", "mr", "mrs", "walter", "jr", "sr", "esq", "ms", "jackson"},
            im.phrase_to_words(
                "Dr. Mr. Mrs. Walter Jr., Sr., Esq., Ms. Jackson,"),
        )

    def test_spanish(self):
        self.assertEqual(
            {
                "me",
                "gusta",
                "hay",
                "4",
                "estadounidenses",
                "secuestrados",
                "en",
                "méxico",
                "qué",
                "saben",
                "las",
                "autoridades",
            },
            im.phrase_to_words(
                "¡me gusta! Hay 4 estadounidenses secuestrados en México: ¿qué saben las autoridades?"
            ),
        )

    def test_russian(self):
        self.assertEqual(
            {
                "вместо",
                "холодного",
                "и",
                "горького",
                "этот",
                "напиток",
                "в",
                "европе",
                "превратился",
                "к",
                "началу",
                "xvii",
                "века",
                "в",
                "горячий",
                "сладкий",
            },
            im.phrase_to_words(
                "Вместо холодного и горького, этот напиток в Европе превратился к началу XVII века в горячий и сладкий."
            ),
        )

    def test_chinese(self):
        print(im.phrase_to_words("小洞不补，大洞吃苦。"))
        self.assertEqual(
            {
                "小",
                "洞",
                "不",
                "补",
                "大",
                "吃",
                "苦",
            },
            im.phrase_to_words("小洞不补，大洞吃苦。")
        )


class ImportPhrase(ImportTestBase):
    def test_single_phrase(self):
        im.import_item_phrase(
            self.cursor,
            {"type": "phrase", "phrase": "this is my phrase", "source": {}},
        )

    def test_multi_phrase(self):
        im.import_item_phrase(
            self.cursor,
            {
                "type": "phrase",
                "phrases": ["salt and pepper", "salt of the earth"],
                "source": {"foo": "bar", "nufoo": "nubar"},
            },
        )


class ImportWordAssoc(ImportTestBase):
    def test_missing_assoc(self):
        im.import_item_word_assoc(
            self.cursor, {"type": "word_assoc", "source": {}})
        im.import_item_word_assoc(
            self.cursor, {"type": "word_assoc", "assocs": [], "source": {}}
        )

    def test_missing_assoc_items(self):
        im.import_item_word_assoc(
            self.cursor,
            {
                "type": "word_assoc",
                "assocs": [
                    {"word1": "apple"},
                    {"word2": "banana"},
                    {"word1": "apple", "word2": "banana"},
                ],
                "source": {},
            },
        )

    def test_single_values(self):
        im.import_item_word_assoc(
            self.cursor,
            {
                "type": "word_assoc",
                "assoc": {"word1": "apple", "word2": "fruit", "type": "is-a"},
                "source": {"name": "unittesting"},
            },
        )

    def test_multi_values(self):
        im.import_item_word_assoc(
            self.cursor,
            {
                "type": "word_assoc",
                "assocs": [
                    {"word1": "smoothie", "word2": "breakfast", "type": "is-a"},
                    {"word1": "smoothie", "word2": "drink", "type": "is-a"},
                    {"word1": "juice", "word2": "drink", "type": "is-a"},
                ],
                "source": {"name": "test"},
            },
        )


if __name__ == "__main__":
    unittest.main()
