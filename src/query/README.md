# Query
Modules implementing the `Query` aspect of PunGenT.

A `Query` module takes user input and returns relevant results from the database.

"Relevant" depends on the particular module.

## Input/Output
| module name                   | Input                                | Output                                         |
| ----------------------------- | ------------------------------------ | ---------------------------------------------- |
| `query_rhymes.py`             | words or phrase vs CL args or STDIN  | rhyming before-and-afters to STDOUT            |
| `query_missing_phonetics.py`  | Line-separated words via STDIN       | Stream of words without phonetic (IPA) entries |

## example usages
```sh
python3 query_rhymes.py 'path/to/db' --mode word happy
```

```sh
cat word_on_each_line.txt | python3 query_rhymes.py 'path/to/db' --mode word
```

```sh
python3 query_missing_phonetics.py 'path/to/db'
```


## dependencies
required libraries outside of the standard library
| module name                   | requests |
| ----------------------------- | -------- |
| `query_rhymes.py`             | +        |
| `query_missing_phonetics.py`  |          |

