import random

INPUT_FILE = 'data/raw/poezja.txt'
OUTPUT_FILE = 'data/raw/poezja.txt'
SEPARATOR = '<|endoftext|>'


print(f"Wczytywanie danych z pliku: {INPUT_FILE}...")

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    documents = list(filter(None, [doc.strip() for doc in content.split(SEPARATOR)]))
    
    if not documents:
        raise ValueError("Nie znaleziono żadnych utworów do wymieszania. Sprawdź separator.")

    print(f"Znaleziono {len(documents)} utworów.")

    random.shuffle(documents)
    print("Utwory zostały wymieszane.")

    shuffled_content = f"\n{SEPARATOR}\n".join(documents)
    shuffled_content += f"\n{SEPARATOR}\n"

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(shuffled_content)

    print(f"Zapisano wymieszane dane do pliku: {OUTPUT_FILE}")

except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku '{INPUT_FILE}'.")
except Exception as e:
    print(f"Wystąpił nieoczekiwany błąd: {e}")