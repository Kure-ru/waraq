import pytest

from waraq.store import get_conn, get_known_vocab
from waraq.insert import insert_vocab

@pytest.fixture
def conn():
    c = get_conn(":memory:")
    yield c
    c.close()

@pytest.fixture
def seeded(conn):
    entries = [
        # word,          source, date_learned,  tags
        ("qahwa",        "001", "2026-09-08", ["ordering-coffee", "drinks"]),  # multi-tag
        ("shukran",      "001", "2026-09-08", ["greeting-phrase"]),
        ("mara7be bik",  "002", "2026-09-15", ["greeting-phrase"]),            # on boundary
        ("sukkar",       "002", "2026-09-15", ["ordering-coffee"]),            # on boundary
        ("ma",           "003", "2026-09-22", ["ordering-coffee"]),            # after boundary
        ("kitab",        "003", "2026-09-22", []),                             # no tags at all
    ]
    for word, source, learned, tags in entries:
        result = insert_vocab(conn, word=word, source=source, date_learned=learned)
        for tag in tags:
            conn.execute(
                "INSERT INTO vocab_tag (vocab_id, tag) VALUES (?, ?)",
                (result.vocab_id, tag),
            )
    conn.commit()
    return conn


def test_get_known_vocab_by_tag(seeded):
    vocab_list = get_known_vocab(seeded, tag="greeting-phrase")

    words = [dict(v)["word"] for v in vocab_list]
    assert words == ["shukran", "mara7be bik"]

def test_get_known_vocab_by_date(seeded):
    vocab_list = get_known_vocab(seeded, before_date="2026-09-15")

    words = [dict(v)["word"] for v in vocab_list]
    assert words == ["qahwa", "shukran"]

def test_get_known_vocab(seeded):
    vocab_list = get_known_vocab(seeded)

    words = [dict(v)["word"] for v in vocab_list]
    assert words == ["qahwa", "shukran", "mara7be bik", "sukkar", "ma", "kitab"]