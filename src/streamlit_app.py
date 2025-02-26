"""Streamlit App: Anki Cards Creator.

This app generates Anki flashcards for a list of vocabulary words using a language model
to derive card details and a text-to-speech service to create corresponding audio files.
It produces JSON files with card data and an Anki package that includes audio references.
"""

import json
import os

import genanki
import streamlit as st
from llama_cpp import Llama

from anki_utils import create_anki_deck
from main import (
    generate_cards_from_words,
    parse_file,
)


def main():
    """Streamlit app for generating Anki flashcards."""
    # Load the prompt once.
    with open("prompts/prompt.json") as f:
        prompt = json.load(f)

    st.title("Anki Cards Creator")
    st.markdown(
        """
    This app generates Anki flashcards for vocabulary words using a language model and a text-to-speech service.
    """
    )

    # Sidebar for configuration.
    st.sidebar.header("Configuration")
    input_method = st.radio("Input method", ("Text Input", "File Upload"))
    context_field = st.text_area(
        "Context/topic",
        value="",
        help="Provide a context/topic in which the words will be used.",
    )
    context = ""
    if context_field:
        context = f"\nUse the next context/topic when writing examples: {context_field}"
    if context:
        prompt += context

    words = []
    if input_method == "Text Input":
        words_input = st.text_area(
            "Enter words (comma-separated)",
            value="Furthermore, Moreover, In addition to this",
        )
        if words_input:
            words = [word.strip() for word in words_input.split(",") if word.strip()]
    else:
        uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
        if uploaded_file is not None:
            words = parse_file(uploaded_file.read())
    st.write(f"Words to process: {len(words)}")

    # Additional settings.
    deck_name = st.sidebar.text_input("Deck Name", value="IELTS Vocabulary")
    audio_format = st.sidebar.selectbox("Audio Format", options=["mp3", "wav"], index=0)
    model_path = st.sidebar.text_input("Model", value="models/gemma-2-2b-it-Q8_0.gguf")
    device = st.sidebar.selectbox("Device", options=["mps", "cpu", "cuda"], index=0)
    n_gpu_layers = st.sidebar.number_input(
        "Number of GPU Layers", min_value=0, value=8, step=1
    )

    # Button to start generation.
    if st.button("Generate Anki Deck"):
        if not words:
            st.error("Please provide some words either via text input or file upload.")
            return

        # Initialize the model.
        model = Llama(
            model_path=model_path,
            n_ctx=8192,
            device=device,
            n_gpu_layers=n_gpu_layers if device in ("mps", "cuda") else 0,
            verbose=False,
        )

        cards_data = generate_cards_from_words(
            model, prompt, words, audio_format=audio_format
        )
        st.write(cards_data, unsafe_allow_html=True)

        # Create the Anki deck.
        my_deck = create_anki_deck(cards_data, deck_name=deck_name)

        # Export Anki deck package.
        package = genanki.Package(my_deck)
        audio_folder = "data/audio"
        package.media_files = [
            os.path.join(audio_folder, f)
            for f in os.listdir(audio_folder)
            if f.endswith(audio_format)
        ]
        os.makedirs("data/anki_decks", exist_ok=True)
        output_path = os.path.join("data/anki_decks", "cards.apkg")
        package.write_to_file(output_path)
        st.success("Anki deck package created.")

        # Provide a download link.
        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Anki Deck",
                data=f,
                file_name="cards.apkg",
                mime="application/octet-stream",
            )


if __name__ == "__main__":
    main()
