import pytest
from waraq.csv_import import clean_row
from waraq.store import get_conn

@pytest.fixture
def conn():
    c = get_conn(":memory:")
    yield c
    c.close()

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