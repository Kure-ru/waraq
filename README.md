# waraq

A level-locked Arabic conversation partner.

## 0. Database schema

SQLite database (`waraq.db`), created automatically on first run at the
path given by `--db` (defaults to `waraq.db` in the current directory).

- **`vocab`**: word, transliteration, gloss, root, part of speech,
  grammar point, `related_to` (self-referencing FK, e.g. for broken
  plurals pointing back to their singular), date learned, source.
- **`vocab_tag`**: join table mapping vocab entries to one or more tags
  (e.g. scenario tags like `ordering-coffee`).

Constraints enforced at the DB level:

- Every entry must have a `word` or a `grammar_point` (or both), enforced
  via a `CHECK` constraint.
- Duplicates are rejected via a unique index on
  `COALESCE(word, grammar_point) + source`.

## a. CLI — add and retrieve words (`vocab_cli.py`)

### Adding an entry

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

#### Fields

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

### Listing / retrieving entries

```bash
python vocab_cli.py list
python vocab_cli.py list --tag ordering-coffee
python vocab_cli.py list -t ordering-coffee
```

- Without `--tag`: lists everything in the store, ordered by date learned.
- With `--tag`: filters to entries carrying that tag, via `get_by_tag` in
  `store.py`.

Output is formatted as `#id: label - gloss`, where `label` falls back from
`word` to `grammar_point` when the word field is empty.

## b. Bulk import from CSV

Imports a CSV of vocab entries in a single pass (tested against a seed
CSV file).

Tags within a CSV cell are `#`-delimited (not comma), to avoid clashing
with the CSV's own column delimiter.
