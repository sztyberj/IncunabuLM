import requests
import re
import os
import time

# --- Konfiguracja ---
API_BASE_URL = "https://wolnelektury.pl/api/"
MIN_BOOK_LENGTH_CHARS = 100
END_OF_TEXT_TOKEN = "<|endoftext|>"
OUTPUT_FILE = "poezja_sredniowiecze_oswiecenie.txt"

# --- Konfiguracja filtrowania ---
# Skrypt pobierze książki tylko z tych epok i rodzajów literackich.
# Zmiana tych list pozwala łatwo dostosować zbiór danych.
ALLOWED_EPOCHS = {'sredniowiecze', 'renesans', 'barok', 'oswiecenie'}
ALLOWED_KINDS = {'liryka'}

# Słownik "stop-słów" do podstawowego filtrowania językowego.
STOP_WORDS = {
    'english': {'the', 'and', 'for', 'with', 'that', 'this', 'you', 'was'},
    'german': {'das', 'der', 'die', 'und', 'ist', 'ein', 'ich', 'mit'},
    'latin': {'et', 'in', 'est', 'cum', 'ad', 'quod', 'qui', 'non', 'ut'},
    'french': {'de', 'la', 'le', 'et', 'est', 'un', 'une', 'à', 'pour'},
    'ukrainian': {'і', 'в', 'на', 'з', 'та', 'що', 'не', 'до', 'як'},
    'lithuanian': {'ir', 'yra', 'kad', 'į', 'su', 'kaip', 'iš', 'bet'}
}
LANGUAGE_DETECTION_THRESHOLD = 5
LANGUAGE_SAMPLE_CHARS = 2000

def is_polish(text: str) -> bool:
    """
    Sprawdza, czy tekst jest prawdopodobnie w języku polskim,
    analizując próbkę pod kątem występowania obcych stop-słów.
    """
    sample = text[:LANGUAGE_SAMPLE_CHARS].lower()
    words = re.findall(r'\b\w+\b', sample)
    
    for lang, stop_words_set in STOP_WORDS.items():
        count = sum(1 for word in words if word in stop_words_set)
        if count > LANGUAGE_DETECTION_THRESHOLD:
            print(f"      ... odrzucono (wykryto język: {lang}, znaleziono {count} słów kluczowych).")
            return False
    return True

def remove_latin(text: str) -> str:
    """
    Usuwa popularne, samodzielne słowa łacińskie z tekstu,
    które często występują w starszej poezji.
    """
    latin_words_pattern = r'\b(et|in|est|cum|ad|quod|qui|non|ut|de|aut|sed|per|quo|sunt|enim|vero|etiam|nam|autem|tamen|ita|sic|vel|ac|ab|ex|hic|ille|is|idem|ipse|iste|hic|haec|hoc|nunc|tunc|semper|saecula|saeculorum|amen)\b'
    cleaned_text = re.sub(latin_words_pattern, '', text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text) # Usuwa nadmiarowe spacje po usunięciu słów
    return cleaned_text

def clean_text(text: str, title: str, authors: list) -> str:
    """
    Czyści tekst z niepotrzebnych elementów: stopki, metadanych, tytułów,
    autorów oraz wtrąceń łacińskich.
    """
    cleaned_text = text
    # Usunięcie stopki i informacji o źródle
    footer_patterns = [
        r'-----*', r'Przypisy', r'Ten utwór nie jest objęty majątkowym prawem autorskim', r'Źródło:'
    ]
    footer_regex = re.compile(r'(' + '|'.join(footer_patterns) + r')', re.IGNORECASE)
    cleaned_text = footer_regex.split(cleaned_text, 1)[0]
    
    # Usunięcie nagłówka Wolnych Lektur
    last_dash_index = cleaned_text.rfind('---')
    if last_dash_index != -1:
        cleaned_text = cleaned_text[last_dash_index + 3:]
        
    # Usunięcie tytułu i autora z tekstu
    if title:
        cleaned_text = re.sub(re.escape(title), '', cleaned_text, flags=re.IGNORECASE)
    for author_info in authors:
        full_name = author_info.get("name", "")
        if full_name:
            cleaned_text = re.sub(re.escape(full_name), '', cleaned_text, flags=re.IGNORECASE)
            # Dodatkowo usuń samo nazwisko, jeśli jest wystarczająco długie
            if ' ' in full_name:
                last_name = full_name.split()[-1]
                if len(last_name) > 3:
                    cleaned_text = re.sub(re.escape(last_name), '', cleaned_text, flags=re.IGNORECASE)
                    
    # Usunięcie różnych znaczników i metadanych
    cleaned_text = re.sub(r'^.*ISBN.*$', '', cleaned_text, flags=re.MULTILINE)
    date_pattern = r'^\s*(poniedziałek|wtorek|środa|czwartek|piątek|sobota|niedziela),\s*\d{1,2}\s+\w+\s+\d{4}\s*$'
    cleaned_text = re.sub(date_pattern, '', cleaned_text, flags=re.MULTILINE | re.IGNORECASE)
    chapter_regex = r'^\s*(ROZDZIAŁ|rozdział|KSIĘGA|Księga|PIEŚŃ|Pieśń|AKT|Akt)\s+[IVXLCDM\d]+\s*$'
    cleaned_text = re.sub(chapter_regex, '', cleaned_text, flags=re.MULTILINE)
    page_regex = r'\[\s*strona\s+\d+\s*\]'
    cleaned_text = re.sub(page_regex, '', cleaned_text)
    
    # Wywołanie nowej funkcji do usuwania łaciny
    cleaned_text = remove_latin(cleaned_text)
    
    # Normalizacja pustych linii
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
    return cleaned_text.strip()

def main():
    """Główna funkcja pobierająca i przetwarzająca dane."""
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    session = requests.Session()
    collected_texts = []
    total_size = 0

    print("Rozpoczynam pobieranie książek z wybranych epok i rodzajów literackich...")
    
    # --- ZOPTYMALIZOWANA LOGIKA POBIERANIA ---
    # Pętla iteruje po zdefiniowanych epokach i odpytuje API o książki tylko z danej epoki.
    for epoch_slug in ALLOWED_EPOCHS:
        print(f"\n--- Przetwarzam epokę: {epoch_slug.capitalize()} ---")
        try:
            epoch_url = f"{API_BASE_URL}epochs/{epoch_slug}/books/"
            response = session.get(epoch_url)
            response.raise_for_status()
            books_in_epoch = response.json()
            print(f"Znaleziono {len(books_in_epoch)} książek. Filtruję i pobieram...")

            for book_summary in books_in_epoch:
                book_url = book_summary.get("href")
                if not book_url: continue

                try:
                    # Sprawdzenie rodzaju literackiego i tytułu przed pobraniem pełnych danych
                    kind_slug = book_summary.get("kind", "").lower()
                    book_title = book_summary.get("title", "")
                    
                    if kind_slug not in ALLOWED_KINDS:
                        continue
                    
                    print(f"  -> Pasujący utwór: '{book_title}' (Rodzaj: {kind_slug.capitalize()})")
                    
                    time.sleep(0.1) # Mała przerwa, by nie obciążać API
                    book_details = session.get(book_url).json()
                    txt_url = book_details.get("txt")
                    
                    if txt_url:
                        print(f"    -> Weryfikuję i pobieram tekst...")
                        raw_text = session.get(txt_url).text
                        
                        if len(raw_text) < MIN_BOOK_LENGTH_CHARS:
                            print(f"      ... pomijam (zbyt krótki tekst).")
                            continue
                        
                        if not is_polish(raw_text):
                            continue

                        book_authors = book_details.get("authors", [])
                        cleaned_text = clean_text(raw_text, book_title, book_authors)
                        
                        if cleaned_text:
                            collected_texts.append(cleaned_text)
                            size_bytes = len(cleaned_text.encode('utf-8'))
                            total_size += size_bytes
                            print(f"      ... pobrano. Aktualny rozmiar zbioru: {total_size / (1024*1024):.2f} MB")

                except requests.exceptions.RequestException as e:
                    print(f"Błąd podczas sprawdzania książki {book_summary.get('title')}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Błąd podczas pobierania danych dla epoki {epoch_slug}: {e}")

    print("\nZapisywanie tekstów do pliku...")
    if collected_texts:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"\n{END_OF_TEXT_TOKEN}\n".join(collected_texts))
            f.write(f"\n{END_OF_TEXT_TOKEN}\n") # Dodatkowy token na końcu pliku
        print(f"Zapisano {len(collected_texts)} utworów do pliku '{OUTPUT_FILE}'.")
    else:
        print("Nie udało się pobrać żadnych tekstów pasujących do kryteriów.")

if __name__ == "__main__":
    main()