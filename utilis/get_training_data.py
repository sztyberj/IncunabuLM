import requests
import re
import os
import time

# --- Konfiguracja ---
API_BASE_URL = "https://wolnelektury.pl/api/"
MIN_BOOK_LENGTH_CHARS = 100
END_OF_TEXT_TOKEN = "<|endoftext|>"
OUTPUT_FILE = "oryginalne_dane_pl_content_filtered.txt"

# Słownik "stop-słów" do wykrywania i wykluczania języków obcych.
# Jeśli w próbce tekstu znajdzie się więcej niż `threshold` słów z którejkolwiek listy,
# tekst zostanie odrzucony.
STOP_WORDS = {
    'english': {'the', 'and', 'for', 'with', 'that', 'this', 'you', 'was'},
    'german': {'das', 'der', 'die', 'und', 'ist', 'ein', 'ich', 'mit'},
    'latin': {'et', 'in', 'est', 'cum', 'ad', 'quod', 'qui', 'non', 'ut'},
    'french': {'de', 'la', 'le', 'et', 'est', 'un', 'une', 'à', 'pour'},
    'ukrainian': {'і', 'в', 'на', 'з', 'та', 'що', 'не', 'до', 'як'},
    'lithuanian': {'ir', 'yra', 'kad', 'į', 'su', 'kaip', 'iš', 'bet'}
}
LANGUAGE_DETECTION_THRESHOLD = 5 # Próg (liczba słów), po którym tekst jest odrzucany
LANGUAGE_SAMPLE_CHARS = 2000 # Liczba znaków z początku tekstu do analizy

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
            print(f"     ... odrzucono (wykryto język: {lang}, znaleziono {count} słów kluczowych).")
            return False
    return True

def clean_text(text: str, title: str, authors: list) -> str:
    # Ta funkcja pozostaje bez zmian
    cleaned_text = text
    footer_patterns = [
        r'-----*', r'Przypisy', r'Ten utwór nie jest objęty majątkowym prawem autorskim', r'Źródło:'
    ]
    footer_regex = re.compile(r'(' + '|'.join(footer_patterns) + r')', re.IGNORECASE)
    cleaned_text = footer_regex.split(cleaned_text, 1)[0]
    last_dash_index = cleaned_text.rfind('---')
    if last_dash_index != -1:
        cleaned_text = cleaned_text[last_dash_index + 3:]
    if title:
        cleaned_text = re.sub(re.escape(title), '', cleaned_text, flags=re.IGNORECASE)
    for author_info in authors:
        full_name = author_info.get("name", "")
        if full_name:
            cleaned_text = re.sub(re.escape(full_name), '', cleaned_text, flags=re.IGNORECASE)
            last_name = full_name.split()[-1]
            if len(last_name) > 3:
                cleaned_text = re.sub(re.escape(last_name), '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'^.*ISBN.*$', '', cleaned_text, flags=re.MULTILINE)
    date_pattern = r'^\s*(poniedziałek|wtorek|środa|czwartek|piątek|sobota|niedziela),\s*\d{1,2}\s+\w+\s+\d{4}\s*$'
    cleaned_text = re.sub(date_pattern, '', cleaned_text, flags=re.MULTILINE | re.IGNORECASE)
    chapter_regex = r'^\s*(ROZDZIAŁ|rozdział|KSIĘGA|Księga|PIEŚŃ|Pieśń|AKT|Akt)\s+[IVXLCDM\d]+\s*$'
    cleaned_text = re.sub(chapter_regex, '', cleaned_text, flags=re.MULTILINE)
    page_regex = r'\[\s*strona\s+\d+\s*\]'
    cleaned_text = re.sub(page_regex, '', cleaned_text)
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
    return cleaned_text.strip()

def main():
    """Główna funkcja pobierająca i przetwarzająca dane."""
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    session = requests.Session()
    collected_texts = []
    total_size = 0

    print("Pobieram pełną listę autorów z API...")
    try:
        response = session.get(f"{API_BASE_URL}authors/")
        response.raise_for_status()
        all_authors = response.json()
        print(f"Znaleziono {len(all_authors)} autorów. Rozpoczynam sprawdzanie ich książek...")

        for author_summary in all_authors:
            author_slug = author_summary.get("slug")
            url = f"{API_BASE_URL}authors/{author_slug}/books/"
            print(f"\nSprawdzam autora: {author_slug}")
            try:
                books_response = session.get(url)
                books_response.raise_for_status()
                books = books_response.json()

                for book_summary in books:
                    book_url = book_summary.get("href")
                    if not book_url: continue
                    time.sleep(0.2)
                    book_details = session.get(book_url).json()
                    txt_url = book_details.get("txt")
                    book_title = book_details.get("title", "")
                    
                    if txt_url:
                        print(f"  -> Weryfikuję '{book_title}'...")
                        raw_text = session.get(txt_url).text
                        
                        # --- NOWA LOGIKA FILTROWANIA NA PODSTAWIE TREŚCI ---
                        if not is_polish(raw_text):
                            continue
                        # --------------------------------------------------

                        if len(raw_text) < MIN_BOOK_LENGTH_CHARS:
                            print(f"     ... pomijam (zbyt krótki tekst).")
                            continue
                        
                        book_authors = book_details.get("authors", [])
                        cleaned_text = clean_text(raw_text, book_title, book_authors)
                        
                        if cleaned_text:
                            collected_texts.append(cleaned_text)
                            size_bytes = len(cleaned_text.encode('utf-8'))
                            total_size += size_bytes
                            print(f"     ... pobrano. Aktualny rozmiar zbioru: {total_size / (1024*1024):.2f} MB")

            except requests.exceptions.RequestException as e:
                print(f"Błąd podczas sprawdzania książek dla {author_slug}: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania listy autorów: {e}")

    print("\nZapisywanie tekstów do plików...")
    if collected_texts:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"\n{END_OF_TEXT_TOKEN}\n".join(collected_texts))
            f.write(f"\n{END_OF_TEXT_TOKEN}\n")
        print(f"Zapisano {len(collected_texts)} utworów do pliku '{OUTPUT_FILE}'.")
    else:
        print("Nie udało się pobrać żadnych nowych tekstów.")

if __name__ == "__main__":
    main()