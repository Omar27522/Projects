import os
import csv
from collections import defaultdict, Counter

search_dir = 'search'
prefix_length = 6
headers_printed = False

# Map prefix -> list of website names
prefix_to_webnames = defaultdict(list)

for fname in os.listdir(search_dir):
    if fname.lower().endswith('.csv'):
        with open(os.path.join(search_dir, fname), newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Print headers for debugging
            if not headers_printed:
                print(f"Headers in {fname}: {reader.fieldnames}")
                headers_printed = True
            for i, row in enumerate(reader):
                variant = row.get('Item Variant Number ', '') or row.get('Item Variant Number', '')
                website_name = row.get('Website Name', '').strip()
                if variant and len(variant) >= prefix_length:
                    prefix = variant[:prefix_length]
                    if website_name:
                        prefix_to_webnames[prefix].append(website_name)

# For each prefix, show the most common website names
print("\nPrefix to Website Name Patterns:")
for prefix, names in sorted(prefix_to_webnames.items(), key=lambda x: -len(x[1])):
    name_counts = Counter(names)
    top_names = name_counts.most_common(5)
    print(f"{prefix}: {len(names)} occurrences. Top website names: {top_names}")
