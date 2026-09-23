from datetime import date
import sqlite3

import pytest

from waraq.csv_import import clean_row
from waraq.store import get_conn
from waraq.insert import InsertResult, insert_vocab


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
    assert second_id == InsertResult(vocab_id=None, status='duplicate', detail="UNIQUE constraint failed: index 'idx_vocab_label_source'")


def test_insert_vocab_malformed_row_returns_none(conn):
    result = insert_vocab(conn, word=None, grammar_point=None, source="001")
    assert result == InsertResult(vocab_id=None, status='Error: provide either word or grammar_point', detail=None)

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

def test_insert_vocab_defaults_date_learned_to_today(conn):
    result = insert_vocab(conn, word="kalima", source="001")

    row = conn.execute(
        "SELECT date_learned FROM vocab WHERE id = ?", (result.vocab_id,)
    ).fetchone()

    assert row["date_learned"] == date.today().isoformat()


def test_insert_vocab_preserves_explicit_date_learned(conn):
    result = insert_vocab(conn, word="kalima", source="001", date_learned="2020-01-01")

    row = conn.execute(
        "SELECT date_learned FROM vocab WHERE id = ?", (result.vocab_id,)
    ).fetchone()

    assert row["date_learned"] == "2020-01-01"