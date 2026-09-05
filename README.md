# waraq

## vocab_cli.py

A command-line tool for logging entries into the known-vocabulary store. The
foundation for the level-locked Arabic conversation partner. Add words and
grammar points one at a time as you learn them, and list what's already
logged.

## Setup

```bash
python vocab_cli.py add --db waraq.db ...
```

The database file is created automatically on first run, at the path given
by `--db` (defaults to `waraq.db` in the current directory). The schema
(`vocab` and `vocab_tag` tables) is created if it doesn't already exist.

## Adding an entry

Every entry is either a **word** or a **grammar point** — at least one of
the two is required; the database itself enforces this and the CLI will
refuse to insert an entry missing both.

```bash
python vocab_cli.py add \
  --word "كتاب" \
  --translit "kitab" \
  --gloss "book" \
  --root "k-t-b" \
  --pos noun \
  --date-learned 2026-09-12 \
  --source "Assimil unit 3" \
  --tags "ordering-coffee,introducing-yourself"
```

```bash
python vocab_cli.py add \
  --grammar-point "negating equational sentences (ma/laysa)" \
  --date-learned 2026-09-12 \
  --source "teacher notes session 12" \
  --tags "introducing-yourself"
```

### Fields

| Flag              | Meaning                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| `--word`          | The word in Arabic script                                                                         |
| `--translit`      | Transliteration (Latin script)                                                                    |
| `--gloss`         | English meaning                                                                                   |
| `--root`          | The root letters (e.g. `k-t-b`)                                                                   |
| `--pos`           | Part of speech                                                                                    |
| `--grammar-point` | A grammar rule, when there's no single word to log                                                |
| `--related-to`    | ID of another entry this one is derived from (e.g. a broken plural pointing back to its singular) |
| `--date-learned`  | Defaults to today if omitted                                                                      |
| `--source`        | Where you learned it (book, lesson, notes)                                                        |
| `--tags`          | Comma-separated, no spaces required — e.g. `ordering-coffee,introducing-yourself`                 |

Each tag becomes its own row in `vocab_tag`, so an entry can carry any
number of tags.

## Listing entries

```bash
python vocab_cli.py list
python vocab_cli.py list --tag ordering-coffee
python vocab_cli.py list -t ordering-coffee
```

Without `--tag`, lists everything in the store ordered by date learned.
With `--tag`, filters to entries carrying that tag.
