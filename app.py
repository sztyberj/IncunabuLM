import streamlit as st
from PIL import Image
import config
import requests

# --- Page config
st.set_page_config(page_title="IncunabuLM", layout="wide")

@st.cache_resource
def load_resources():
    """
    Load style.css and scribe.png

    return: ModelOutput (response: str)
    """

    with open(config.CSS) as f:
        style = f.read()

    image = Image.open(config.IMAGE_PATH)
    return image, style

def format_as_poem(text: str) -> str:
    # Replace punctuation with punctuation + line break for better readability.
    text = text.replace('. ', '.<br>')
    text = text.replace('? ', '?<br>')
    text = text.replace('! ', '!<br>')
    text = text.replace('; ', ';<br>')
    return text

def main():
    """
    Main logic. Build app, get hiperparams, show prediction from API" 
    """

    try:
        scribe_image, style = load_resources()
        st.markdown(f'<style>{style}</style>', unsafe_allow_html=True)

        if 'generated_text' not in st.session_state:
            st.session_state.generated_text = "Czekam na twe słowa, panie..."

        st.markdown('<h1 class="title-font">📜 IncunabuLM 📜</h1>', unsafe_allow_html=True)
        st.write("---")

        # --- Main app ---
        col1, col2, col3 = st.columns([1.5, 2.5, 1.5])

        # Left column
        with col1:
            st.image(scribe_image, use_container_width=True)
            prompt = st.text_area(
                "Wpisz początek zdania:",
                "A gdy Bolesław Chrobry na tronie zasiadł...",
                height=150,
                key="prompt_input"
            )
            button_pressed = st.button("Pisz!", type="primary", use_container_width=True)

        # Middle column
        with col2:
            formatted_output = format_as_poem(st.session_state.generated_text)
            st.markdown(
                f'<div class="output-container" style="height: 100%;">{formatted_output}</div>',
                unsafe_allow_html=True
            )

        # Right column
        with col3:
            st.markdown("#### Ustawienia Pisma")
            temperature = st.slider("Temperatura:", min_value=0.1, max_value=2.0, value=1.0, key="temp_slider")
            top_k = st.slider("Top K:", min_value=1, max_value=100, value=50, key="topk_slider")
            repetition_penalty = st.slider("Kara za powtórzenia:", min_value=1.0, max_value=2.0, value=1.2, key="rep_pen_slider")
            max_tokens = st.slider(
                "Długość pisma (w tokenach):",
                min_value=20, max_value=500, value=150,
                key="max_length_slider"
            )
        
        # Generation logic
        if button_pressed:
            if st.session_state.prompt_input:
                with st.spinner("Skryba kreśli słowa na pergaminie..."):
                    data_to_predict = {
                        "context" : prompt,
                        "max_tokens" : max_tokens,
                        "temperature" : temperature,
                        "top_k" : top_k,
                        "repetition_penalty" : repetition_penalty
                    }
                    response = requests.post(
                        config.API_URL, 
                        json=data_to_predict,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    response.raise_for_status()

                    result = response.json()
                    st.session_state.generated_text = result["response"]
                    st.rerun()
            else:
                st.warning("Mistrzu, podaj choć słowo, bym mógł zacząć...")

    except FileNotFoundError:
        st.error(
            "Błąd: Nie znaleziono potrzebnych plików. Upewnij się, że ścieżki w pliku config.py są poprawne."
        )
    except Exception as e:
        st.error(f"Wystąpił błąd godny pożałowania: {e}")

if __name__ == "__main__":
    main()