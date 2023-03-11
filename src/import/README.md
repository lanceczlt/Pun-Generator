# Import
Modules implementing the `Import` aspect of PunGenT.

An `Importer` takes a stream of input and inserts it into a database.

The particular formats depend on the module

## Input/Output formats
| module name                 | Input                         | Database |
| --------------------------- | ----------------------------- | -------- |
| importer_json_to_sqlite.py  | Line-separated JSON via STDIN | SQLite3  |

## example usages
```sh
cat data/top100.txt | python3 importer_json_to_sqlite.py '/path/to/db/instance'
```
```sh
python3 src/query/query_missing_phonetics.py /tmp/demo/db.sqlite | python3 src/fetch/cambridge_dict_scrape.py --stdin | python3 src/import/importer_json_to_sqlite.py /tmp/demo/db.sqlite
```
