"""Module: Anki Cards Creator.

This module generates Anki flashcards for a list of vocabulary words using a language model
to derive card details and a text-to-speech service to create corresponding audio files.
It produces JSON files with card data and an Anki package that includes audio references.
"""

import json
import os
from pprint import pprint

import genanki
from llama_cpp import Llama

from anki_utils import create_anki_deck
from audio_utils import TextToSpeech

with open("prompts/prompt.json") as f:
    prompt = json.load(f)

words = ["Furthermore", "Moreover", "In addition to this"]


def get_expression_card_info(model, expression: str) -> dict:
    """Generate card information for a given expression by interacting with a language model.

    Parameters:
        model: An object that provides the method create_chat_completion for generating responses,
               and a reset method to clear the model's state. Typically, this is an interface to a chat-based
               language model.
        expression (str): The expression to analyze. It is inserted into the prompt and sent to the language model.

    Returns:
        dict: A dictionary containing card information for the expression. The dictionary is created by parsing
              a JSON segment from the language model's response. The returned dictionary also includes the original
              expression under the key "expression".

    Notes:
        - The function constructs a chat completion request with a predefined prompt which must be defined externally as 'prompt'.
        - The response from the language model is expected to include a JSON object embedded in a formatted text.
        - After processing the response, the model is reset using model.reset().
        - A zero temperature is used to ensure deterministic responses from the language model.
    """
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
    pprint(answer)
    expression_card_info = answer[answer.find("json") + 4 :].replace("```", "").strip()
    expression_card_info = json.loads(expression_card_info)
    expression_card_info["expression"] = expression
    model.reset()

    return expression_card_info


def generate_cards_from_words(
    model, words_list: list[str], audio_format: str = "mp3"
) -> list[dict]:
    """Generate Anki cards from a list of words by creating JSON data and corresponding audio files.

    This function iterates over each word in the provided list, generates card information using
    an external function (get_expression_card_info), and then saves the card data as a JSON file.
    In addition, it creates audio files for the word's expression, definition, and examples using
    a TextToSpeech service. The generated audio files are referenced in the card data with sound
    tags, making the output ready for integration with tools like Anki.
    Parameters:
        model: An instance or object required by get_expression_card_info to generate card details.
        words_list (list[str]): A list of words for which the cards are to be created.
        audio_format (str, optional): The file format for the generated audio files (default is "mp3").

    Returns:
        list[dict]: A list where each element is a dictionary containing card details including:
            - 'expression', 'definition', and 'examples' keys with corresponding text.
            - 'audio_expression', 'audio_definition', and 'audio_examples' keys containing sound
              tags that reference the corresponding audio files.
    Side Effects:
        - Creates a JSON file per word in the "data/processed_expressions" directory.
        - Creates audio files in the "data/audio" directory.
        - Outputs progress information to the console.
    """
    cards = []
    n = len(words_list)
    print(f"Number of words to generate cards for: {n}")
    for idx, w in enumerate(words_list):
        print("-/-" * 20)
        print(f"Generating card for '{w}': {idx}/{n}")
        card_data = get_expression_card_info(model, w)
        with open(
            f"data/processed_expressions/{w.lower().replace(' ', '_')}.json", "w"
        ) as f:
            json.dump(card_data, f, indent=4)
        voicer = TextToSpeech()

        # Generate audio files for the word, definition, and example
        # word
        audio_word_filename = f"{w.lower().replace(' ', '_')}_expression.{audio_format}"
        voicer.text_to_speech_elevenlabs(
            card_data["expression"], f"data/audio/{audio_word_filename}"
        )

        # definition
        audio_definition_filename = (
            f"{w.lower().replace(' ', '_')}_definition.{audio_format}"
        )
        voicer.text_to_speech_elevenlabs(
            card_data["definition"], f"data/audio/{audio_definition_filename}"
        )

        # examples
        audio_example_filename = (
            f"{w.lower().replace(' ', '_')}_examples.{audio_format}"
        )
        voicer.text_to_speech_elevenlabs(
            card_data["examples"], f"data/audio/{audio_example_filename}"
        )

        # Add audio tags to the card data
        card_data["audio_expression"] = (
            f"[sound:{audio_word_filename}]" if audio_word_filename else ""
        )
        card_data["audio_definition"] = (
            f"[sound:{audio_definition_filename}]" if audio_definition_filename else ""
        )
        card_data["audio_examples"] = (
            f"[sound:{audio_example_filename}]" if audio_example_filename else ""
        )

        cards.append(card_data)
    return cards


if __name__ == "__main__":
    device = "mps"
    n_gpu_layers = 8
    model_path = "models/gemma-2-2b-it-Q8_0.gguf"
    # model_path = "../models/gemma-2-9b-it-Q6_K_L.gguf"
    # model_path = "../models/Qwen2.5-7B-Instruct-Q8_0.gguf"
    model = Llama(
        model_path=model_path,
        n_ctx=8192,
        device=device,
        n_gpu_layers=n_gpu_layers if device in ("mps", "cuda") else 0,
        verbose=False,
    )
    cards_data = generate_cards_from_words(model, words)
    print("Done generating cards.")
    print("len(cards_data):", len(cards_data))
    my_deck = create_anki_deck(cards_data, deck_name="Danya_IELTS_Vocabulary_Deck_3")
    # To export:
    package = genanki.Package(my_deck)
    audio_folder = "data/audio"
    package.media_files = [
        os.path.join(audio_folder, f)
        for f in os.listdir(audio_folder)
        if f.endswith(".mp3")
    ]

    package.write_to_file("Danya_IELTS_Vocabulary_Deck_3.apkg")
    print("Deck created with", len(cards_data), "words (1 card each).")
