"""Module: Anki Cards Creator.

This module generates Anki flashcards for a list of vocabulary words using a language model
to derive card details and a text-to-speech service to create corresponding audio files.
It produces JSON files with card data and an Anki package that includes audio references.
"""

import argparse
import json
import os

import genanki
from langchain_openai import ChatOpenAI
from llama_cpp import Llama

from anki_utils import create_anki_deck
from audio_utils import TextToSpeech
from nlp_utils import parse_words


def load_prompt() -> str:
    """Load the prompt from the JSON file."""
    with open("prompts/prompt.json") as f:
        prompt_data = json.load(f)
    # If it's a string, return it directly
    if isinstance(prompt_data, str):
        return prompt_data
    # Otherwise, try to get the "user" field
    return prompt_data.get("user", "")


class AnkiCardsGenerator:
    """Generate Anki cards from words using a language model."""

    def __init__(self):
        """Initialize the generator."""
        self.model = None
        self.device = "mps"
        self.n_gpu_layers = 8

    def generate_cards_from_words(
        self, model_name, prompt: str, words_list: list[str], audio_format: str = "mp3"
    ) -> list[dict]:
        """Generate Anki cards from a list of words."""
        return generate_cards_from_words(model_name, prompt, words_list, audio_format)


def get_expression_card_info(model_name, prompt: str, expression: str) -> dict:
    """Generate card information for a given expression by interacting with a language model."""
    if model_name.startswith("models"):
        model = Llama(
            model_path=model_path,
            n_ctx=8192,
            device=device,
            n_gpu_layers=n_gpu_layers if device in ("mps", "cuda") else 0,
            verbose=False,
        )
        response = model.create_chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": f"The expression to analyze is: ```{expression}```",
                },
                {"role": "assistant", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=500,
        )
        answer = response["choices"][0]["message"]["content"].strip()
        # Extract the JSON part from the response.
        expression_card_info = (
            answer[answer.find("json") + 4 :].replace("```", "").strip()
        )
    else:
        model = ChatOpenAI(model=model_name)
        expression_card_info = model.invoke(
            f"The expression to analyze is: ```{expression}```" + prompt
        ).content
    expression_card_info = json.loads(expression_card_info)
    expression_card_info["expression"] = expression
    # Remove 'Language learning' from topics.
    expression_card_info["topics"] = [
        topic
        for topic in expression_card_info["topics"]
        if topic.lower() != "language learning"
    ]
    if model_name.startswith("models"):
        model.reset()
    return expression_card_info


def generate_cards_from_words(
    model_name, prompt: str, words_list: list[str], audio_format: str = "mp3"
) -> list[dict]:
    """Generate Anki cards from a list of words by creating JSON data and corresponding audio files."""
    cards = []
    n = len(words_list)
    print(f"Number of words to generate cards for: {n}")
    for idx, word in enumerate(words_list):
        print("-/-" * 20)
        print(f"Generating card for '{word}': {idx + 1}/{n}")
        card_data = get_expression_card_info(model_name, prompt, word)
        output_json_path = (
            f"data/processed_expressions/{word.lower().replace(' ', '_')}.json"
        )
        with open(output_json_path, "w") as f:
            json.dump(card_data, f, indent=4)
        voicer = TextToSpeech()

        # Generate audio files for the word, definition, and example.
        audio_expression_filename = (
            f"{word.lower().replace(' ', '_')}_expression.{audio_format}"
        )
        voicer.text_to_speech_elevenlabs(
            card_data["expression"], f"data/audio/{audio_expression_filename}"
        )

        audio_definition_filename = (
            f"{word.lower().replace(' ', '_')}_definition.{audio_format}"
        )
        voicer.text_to_speech_elevenlabs(
            card_data["definition"], f"data/audio/{audio_definition_filename}"
        )

        audio_example_filename = (
            f"{word.lower().replace(' ', '_')}_examples.{audio_format}"
        )
        voicer.text_to_speech_elevenlabs(
            card_data["examples"], f"data/audio/{audio_example_filename}"
        )

        audio_collocations_filename = (
            f"{word.lower().replace(' ', '_')}_collocations.{audio_format}"
        )
        voicer.text_to_speech_elevenlabs(
            card_data["collocations"], f"data/audio/{audio_collocations_filename}"
        )

        audio_synonyms_filename = (
            f"{word.lower().replace(' ', '_')}_synonyms.{audio_format}"
        )
        voicer.text_to_speech_elevenlabs(
            card_data["synonyms"], f"data/audio/{audio_synonyms_filename}"
        )

        # Add audio tags to the card data.
        card_data["audio_expression"] = f"[sound:{audio_expression_filename}]"
        card_data["audio_definition"] = f"[sound:{audio_definition_filename}]"
        card_data["audio_examples"] = f"[sound:{audio_example_filename}]"
        card_data["audio_collocations"] = f"[sound:{audio_collocations_filename}]"
        card_data["audio_synonyms"] = f"[sound:{audio_synonyms_filename}]"

        cards.append(card_data)
    return cards


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Anki cards from words.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--words",
        type=str,
        help="Comma-separated list of words (e.g., 'word1, word2, word3').",
    )
    group.add_argument(
        "--file", type=str, help="Path to a text file containing words (one per line)."
    )
    parser.add_argument(
        "--audio_format",
        type=str,
        default="mp3",
        help="Audio file format (default: mp3).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/anki decks/cards.apkg",
        help="Output file path for card data.",
    )
    parser.add_argument(
        "--deck_name",
        type=str,
        default="Danya_IELTS_Vocabulary_Deck",
        help="Name of the Anki deck.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/gemma-2-2b-it-Q8_0.gguf",
        help="Path to the model file.",
    )

    args = parser.parse_args()

    words = parse_words(args)
    print("Words to process:", words)

    # Model configuration.
    device = "mps"
    n_gpu_layers = 8
    model_path = args.model
    model = Llama(
        model_path=model_path,
        n_ctx=8192,
        device=device,
        n_gpu_layers=n_gpu_layers if device in ("mps", "cuda") else 0,
        verbose=False,
    )

    cards_data = generate_cards_from_words(model, words, audio_format=args.audio_format)
    print("Done generating cards.")
    print("len(cards_data):", len(cards_data))
    my_deck = create_anki_deck(cards_data, deck_name=args.deck_name)

    # Export Anki deck package.
    package = genanki.Package(my_deck)
    audio_folder = "data/audio"
    package.media_files = [
        os.path.join(audio_folder, f)
        for f in os.listdir(audio_folder)
        if f.endswith(args.audio_format)
    ]

    package.write_to_file(args.output)
    print("Deck created with", len(cards_data), "words (1 card each).")
