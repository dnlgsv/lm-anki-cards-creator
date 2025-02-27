"""Streamlit App: Anki Cards Creator.

This app generates Anki flashcards for a list of vocabulary words using a language model
to derive card details and a text-to-speech service to create corresponding audio files.
It produces JSON files with card data and an Anki package that includes audio references.
"""

import json
import os
import random

import genanki
import streamlit as st
import streamlit.components.v1 as components
from llama_cpp import Llama

from anki_utils import create_anki_deck
from main import generate_cards_from_words, parse_file
from streamlit_utils import render_phone_preview


def main():
    """Streamlit app for generating Anki flashcards."""
    st.set_page_config(
        page_title="Anki Cards Creator", layout="wide", initial_sidebar_state="expanded"
    )

    with open("prompts/prompt.json") as f:
        prompt = json.load(f)

    # Sidebar for configuration.
    st.sidebar.header("Configuration")
    input_method = st.sidebar.radio("Input method", ("Text Input", "File Upload"))

    words = []
    if input_method == "Text Input":
        words_input = st.sidebar.text_area(
            "Enter words (comma-separated)",
            value="Furthermore, Moreover, In addition to this",
        )
        if words_input:
            words = [word.strip() for word in words_input.split(",") if word.strip()]
    else:
        uploaded_file = st.sidebar.file_uploader("Upload a text file", type=["txt"])
        if uploaded_file is not None:
            words = parse_file(uploaded_file.read())
    st.sidebar.write(f"Words to process: {len(words)}")

    context_field = st.sidebar.text_area(
        "Context/topic",
        value="",
        help="Provide a context/topic in which the words will be used.",
    )
    context = ""
    if context_field:
        context = f"\nUse the next context/topic when writing examples: {context_field}"
    if context:
        prompt += context

    # Additional settings.
    deck_name = st.sidebar.text_input("Deck Name", value="IELTS Vocabulary")
    audio_format = st.sidebar.selectbox("Audio Format", options=["mp3", "wav"], index=0)
    model_path = st.sidebar.text_input("Model", value="models/gemma-2-2b-it-Q8_0.gguf")
    device = st.sidebar.selectbox("Device", options=["mps", "cpu", "cuda"], index=0)
    n_gpu_layers = st.sidebar.number_input(
        "Number of GPU Layers", min_value=0, value=8, step=1
    )

    # Button to start generation.
    if st.sidebar.button("Generate Anki Deck"):
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
        with open("data/json files/cards_data.json", "w") as f:
            json.dump(cards_data, f, indent=4)
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

    # Sample flashcards
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = [
            {
                "expression": "Ambiguous",
                "part_of_speech": "adjective",
                "cefr_level": "B2",
                "definition": "Open to more than one interpretation; having a double meaning; unclear or inexact because a choice between alternatives has not been made.",
                "examples": [
                    "The instructions were ambiguous, so I wasn't sure how to proceed.",
                    "She gave an ambiguous smile that could have meant anything.",
                ],
                "synonyms": ["unclear", "vague", "equivocal"],
                "antonyms": ["clear", "obvious", "unambiguous"],
                "collocations": [
                    "ambiguous statement",
                    "ambiguous terms",
                    "ambiguous language",
                ],
                "russian": ["двусмысленный", "неоднозначный"],
                "topics": ["communication", "language"],
            },
            {
                "expression": "Perseverance",
                "part_of_speech": "noun",
                "cefr_level": "B2",
                "definition": "Continued effort to do or achieve something despite difficulties, failure, or opposition.",
                "examples": [
                    "His perseverance finally paid off when he got the job.",
                    "It takes perseverance to learn a musical instrument.",
                ],
                "synonyms": ["persistence", "determination", "tenacity"],
                "antonyms": ["laziness", "indolence", "surrender"],
                "collocations": [
                    "show perseverance",
                    "require perseverance",
                    "perseverance pays off",
                ],
                "russian": ["настойчивость", "упорство"],
                "topics": ["behavior", "personality", "success"],
            },
            {
                "expression": "Procrastinate",
                "part_of_speech": "verb",
                "cefr_level": "B1",
                "definition": "To delay or postpone action; to put off doing something, especially out of habitual carelessness or laziness.",
                "examples": [
                    "I always procrastinate when it comes to doing my taxes.",
                    "Don't procrastinate - the deadline is tomorrow!",
                ],
                "synonyms": ["delay", "postpone", "defer"],
                "antonyms": ["act", "advance", "expedite"],
                "collocations": ["tend to procrastinate", "chronic procrastinator"],
                "russian": ["откладывать на потом", "медлить"],
                "topics": ["behavior", "time management"],
            },
        ]

    # Navigation state
    if "current_card_index" not in st.session_state:
        st.session_state.current_card_index = 0

    # Single page layout with two main columns
    col_editor, col_preview = st.columns([1, 1])

    with col_editor:
        st.subheader("Edit Flashcard")

        current_card = st.session_state.flashcards[st.session_state.current_card_index]

        # Edit basic text fields
        expression = st.text_input("Expression", current_card.get("expression", ""))
        current_card["expression"] = expression

        part_of_speech = st.text_input(
            "Part of Speech", current_card.get("part_of_speech", "")
        )
        current_card["part_of_speech"] = part_of_speech

        cefr_level = st.selectbox(
            "CEFR Level",
            options=["A1", "A2", "B1", "B2", "C1", "C2"],
            index=["A1", "A2", "B1", "B2", "C1", "C2"].index(
                current_card.get("cefr_level", "A1")
            ),
        )
        current_card["cefr_level"] = cefr_level

        definition = st.text_area("Definition", current_card.get("definition", ""))
        current_card["definition"] = definition

        # For list-type fields
        examples = st.text_area(
            "Examples (one per line)", "\n".join(current_card.get("examples", []))
        )
        current_card["examples"] = [
            line.strip() for line in examples.splitlines() if line.strip()
        ]

        col1, col2 = st.columns(2)

        with col1:
            synonyms = st.text_input(
                "Synonyms (comma separated)",
                ", ".join(current_card.get("synonyms", [])),
            )
            current_card["synonyms"] = [
                s.strip() for s in synonyms.split(",") if s.strip()
            ]

            antonyms = st.text_input(
                "Antonyms (comma separated)",
                ", ".join(current_card.get("antonyms", [])),
            )
            current_card["antonyms"] = [
                a.strip() for a in antonyms.split(",") if a.strip()
            ]

        with col2:
            collocations = st.text_input(
                "Collocations (comma separated)",
                ", ".join(current_card.get("collocations", [])),
            )
            current_card["collocations"] = [
                c.strip() for c in collocations.split(",") if c.strip()
            ]

            russian = st.text_input(
                "Russian Translations (comma separated)",
                ", ".join(current_card.get("russian", [])),
            )
            current_card["russian"] = [
                r.strip() for r in russian.split(",") if r.strip()
            ]

        topics = st.text_input(
            "Topics (comma separated)", ", ".join(current_card.get("topics", []))
        )
        current_card["topics"] = [t.strip() for t in topics.split(",") if t.strip()]

        # Card management buttons
        st.markdown("---")
        st.subheader("Card Management")

        col_add, col_del = st.columns(2)
        with col_add:
            if st.button("Add New Card", use_container_width=True):
                st.session_state.flashcards.append(
                    {
                        "expression": "New Flashcard",
                        "part_of_speech": "",
                        "cefr_level": "A1",
                        "definition": "",
                        "examples": [],
                        "synonyms": [],
                        "antonyms": [],
                        "collocations": [],
                        "russian": [],
                        "topics": [],
                    }
                )
                st.session_state.current_card_index = (
                    len(st.session_state.flashcards) - 1
                )
                st.success("New card added!")
                st.experimental_rerun()

        with col_del:
            if len(st.session_state.flashcards) > 1:
                if st.button("Delete Current Card", use_container_width=True):
                    st.session_state.flashcards.pop(st.session_state.current_card_index)
                    st.session_state.current_card_index = min(
                        st.session_state.current_card_index,
                        len(st.session_state.flashcards) - 1,
                    )
                    st.success("Card deleted!")
                    st.experimental_rerun()

    with col_preview:
        # st.info(f"Card {st.session_state.current_card_index + 1} of {len(st.session_state.flashcards)}")

        # Phone preview
        st.markdown("#### Phone Display")
        current_card = st.session_state.flashcards[st.session_state.current_card_index]
        preview_html = render_phone_preview(current_card, True)
        # st.markdown(preview_html, unsafe_allow_html=True)
        components.html(preview_html, height=800)

        # Card navigation buttons
        col_prev, col_rand, col_next = st.columns(3)

        with col_prev:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_card_index = (
                    st.session_state.current_card_index - 1
                ) % len(st.session_state.flashcards)

        with col_rand:
            if st.button("🔀 Random", use_container_width=True):
                st.session_state.current_card_index = random.randint(
                    0, len(st.session_state.flashcards) - 1
                )

        with col_next:
            if st.button("➡️ Next", use_container_width=True):
                st.session_state.current_card_index = (
                    st.session_state.current_card_index + 1
                ) % len(st.session_state.flashcards)


if __name__ == "__main__":
    main()
