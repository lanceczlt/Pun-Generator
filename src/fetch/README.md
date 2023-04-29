# Fetch
Modules implementing the `Fetch` aspect of PunGenT.

A `Fetch` module takes user input and returns a stream of data from the database.

The type of user input and the format of the output depends on the particular module.

## Input/Output
| module name                   | Input                                   | Output                                         |
| ----------------------------- | --------------------------------------- | ---------------------------------------------- |
| `cambridge_dict_scrape.py`    | words via CL args, STDIN or interactive | lines of JSON (word schema) to STDOUT          |
| `genius.py`                   | interactive                             | lines of JSON (phrase schema) to STDOUT        |
| `genius_top100.py`            | automatic, no input                     | lines of JSON (phrase schema) to STDOUT        |
| `phonetic_scrape.py`          | interactive                             | lines of JSON (word schema) to STDOUT          |
| `wikipedia_scrape.py`         | interactive                             | lines of JSON (phrase schema) to STDOUT        |

## example usages
```sh
cat list_of_words.txt | python3 cambridge_dict_scrape.py --stdin
```

```sh
python3 cambridge_dict_scrape.py These Words are the input
```

```sh
python3 cambridge_dict_scrape.py
'Enter a sentence or word: '[type here]
```

```sh
python3 genius.py
'Enter an artist's name: '[type artist name here]
```

```sh
python3 genius_top100.py
(chrome browser window will pop-up and be controlled automatically)
```

```sh
python3 phonetic_scrape.py
'Enter a sentence or word: '[type here]
```

```sh
python3 wikipedia_scrape.py
'Enter a term to search in Wikipedia:'[type here]
```

## dependencies
required libraries outside of the standard library
| module name                   | Selenium | BeautifulSoup4 | requests | iso639_lang | dotenv | wikipedia |
| ----------------------------- | -------- | -------------- | -------- | ----------- | ------ | --------- |
| `cambridge_dict_scrape.py`    |          | +              | +        |             |        |           |
| `genius.py`                   |          | +              | +        | +           | +      |           |
| `genius_top100.py`            | +        | +              | +        | +           | +      |           |
| `phonetic_scrape.py`          |          | +              | +        |             |        |           |
| `wikipedia.py`                |          | +              | +        |             |        | +         |

### additional requirements
`genius.py` and `genius_top100.py` require a Genius API token. See the respective scripts for more information.
