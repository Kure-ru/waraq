import sqlite3

import pytest

from waraq.csv_import import clean_row
from waraq.store import get_conn, insert_vocab


# ---------------------------------------------------------------------------
# clean_row
# ---------------------------------------------------------------------------

def test_clean_row_converts_empty_strings_to_none():
    row = {"word": "kalima", "transliteration": "", "gloss": "word", "tags": ""}

    cleaned = clean_row(row)

    assert cleaned["transliteration"] is None
    assert cleaned["word"] == "kalima"  # non-empty values pass through untouched


def test_clean_row_splits_hash_delimited_tags():
    row = {"word": "kalima", "tags": "#food# drink #"}

    cleaned = clean_row(row)

    assert cleaned["tags"] == ["food", "drink"]


def test_clean_row_missing_tags_becomes_empty_list():
    row = {"word": "kalima", "tags": ""}

    cleaned = clean_row(row)

    assert cleaned["tags"] == []


# ---------------------------------------------------------------------------
# insert_vocab
# ---------------------------------------------------------------------------

@pytest.fixture
def conn():
    c = get_conn(":memory:")
    yield c
    c.close()


def test_insert_vocab_duplicate_returns_none(conn):
    first_id = insert_vocab(conn, word="kalima", source="001")
    assert first_id is not None

    second_id = insert_vocab(conn, word="kalima", source="001")
    assert second_id is None


def test_insert_vocab_malformed_row_returns_none(conn):
    result = insert_vocab(conn, word=None, grammar_point=None, source="001")
    assert result is None

    count = conn.execute("SELECT COUNT(*) FROM vocab").fetchone()[0]
    assert count == 0


def test_check_constraint_rejects_row_with_no_word_or_grammar_point(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO vocab (word, grammar_point, source) VALUES (?, ?, ?)",
            (None, None, "001"),
        )


def test_unique_index_rejects_duplicate_label_and_source(conn):
    conn.execute("INSERT INTO vocab (word, source) VALUES (?, ?)", ("kalima", "001"))

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO vocab (word, source) VALUES (?, ?)", ("kalima", "001")
        )