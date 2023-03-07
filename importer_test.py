import unittest
import importer_json_to_sqlite as im
import sqlite3 as sql


class ImportWord(unittest.TestCase):
    def setUp(self):
        self.conn = sql.connect(":memory:")
        self.cursor = self.conn.cursor()
        im.create_all_tables(self.cursor)

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
            self.cursor.execute("SELECT word, phonetic FROM word_phonetic").fetchone(),
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
            im.phrase_to_words("Dr. Mr. Mrs. Walter Jr., Sr., Esq., Ms. Jackson,"),
        )

    def test_spanish(self):
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
            im.phrase_to_words(
                "Hay 4 estadounidenses secuestrados en México: ¿qué saben las autoridades?"
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


if __name__ == "__main__":
    unittest.main()
