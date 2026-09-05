import csv

from store import get_conn, insert_vocab

def check_empty(row):
    return {col: (val if val else None) for col, val in row.items()}

def format_tags(row):
    tags = row['tags']

    formatted_tags = [t.strip() for t in (tags or "").split("#") if t.strip()]
    return {**row, 'tags': formatted_tags}

def clean_row(row):
    return format_tags(check_empty(row))

def main():
    conn = get_conn('waraq.db')
    inserted = 0
    skipped = []

    with open('seed.csv', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            d = clean_row(row)
            vocab_id = insert_vocab(
                conn, word=d['word'], translit=d['transliteration'],
                gloss=d['gloss'], root=d['root'], pos=d['pos'],
                grammar_point=d['grammar_point'], related_to=d['related_to'],
                date_learned=d['date_learned'], source=d['source'], tags=d['tags'],
            )
            if vocab_id is None:
                skipped.append(d.get('word') or d.get('grammar_point') or '<blank row>')
            else:
                inserted += 1

    conn.close()
    print(f"Inserted: {inserted}")

    if skipped:
        print(f"Skipped ({len(skipped)}): {', '.join(skipped)}")

if __name__ == "__main__":
    main()