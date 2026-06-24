import csv
import json

posts = []

try:
    # Use DictReader which handles quoted fields and newlines correctly
    with open('posts_template.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        print(f"Fieldnames: {reader.fieldnames}")

        for i, row in enumerate(reader, start=1):
            if i <= 3:
                print(f"Row {i}: {row}")

            if not row.get('id'):
                print(f"  → Skipped: no id")
                continue

            try:
                post_id = int(row['id'].strip())
                title = row.get('title', '').strip()
                text = row.get('text', '').strip()

                if title or text:
                    posts.append({
                        'id': post_id,
                        'title': title,
                        'text': text
                    })
                else:
                    print(f"  → Skipped: empty title and text")
            except ValueError as e:
                print(f"  → Skipped: {e}")

    print(f"\nTotal rows processed: {i if 'i' in locals() else 0}")
    print(f"Posts created: {len(posts)}")

    if posts:
        with open('posts.json', 'w') as f:
            json.dump(posts, f, indent=2)
        print(f"✓ Success! Saved to posts.json")
    else:
        print("✗ No posts were parsed. Check the output above.")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
