"""Utility functions for creating Anki decks from card data."""

from typing import Any

import genanki

try:
    from .exceptions import AnkiDeckError
    from .logger import get_logger
except ImportError:
    # Fallback for script execution
    from src.exceptions import AnkiDeckError  # type: ignore
    from src.logger import get_logger  # type: ignore

logger = get_logger(__name__)


def create_anki_deck(
    cards_data: list[dict[str, Any]], deck_name: str = "My Vocabulary Deck"
) -> genanki.Deck:
    """Creates an Anki deck from a list of card data dictionaries.

    Each card in cards_data should be a dictionary with the following keys:
        - expression: str
        - definition: str
        - examples: list[str]
        - synonyms: list[str]
        - antonyms: list[str]
        - collocations: list[str]
        - part_of_speech: str
        - audio_expression: str
        - audio_definition: str
        - audio_examples: str
        - russian: list[str]
        - topics: list[str]

    The function converts lists to strings where necessary and creates a
    genanki.Note for each card, adding it to the deck.

    Args:
        cards_data: A list of dictionaries containing card information.
        deck_name: The name of the deck.

    Returns:
        The constructed Anki deck.

    Raises:
        AnkiDeckError: If deck creation fails
    """
    if not cards_data:
        logger.warning("No card data provided for deck creation")
        raise AnkiDeckError("Cannot create deck with empty card data")

    try:
        logger.info(f"Creating Anki deck '{deck_name}' with {len(cards_data)} cards")

        deck_id = abs(hash(deck_name)) % (10**10)
        deck = genanki.Deck(deck_id=deck_id, name=deck_name)

        model = genanki.Model(
            model_id=abs(hash("BasicOneCardRus")) % (10**10),
            name="BasicOneCardRus",
            fields=[
                {"name": "Expression"},
                {"name": "Definition"},
                {"name": "Examples"},
                {"name": "Synonyms"},
                {"name": "Antonyms"},
                {"name": "Collocations"},
                {"name": "PartOfSpeech"},
                {"name": "Audio_Expression"},
                {"name": "Audio_Definition"},
                {"name": "Audio_Examples"},
                {"name": "RussianTranslation"},
                {"name": "Topics"},
            ],
            templates=[
                {
                    "name": "Card 1 (Word Front)",
                    "qfmt": "{{Expression}}",
                    "afmt": (
                        '{{FrontSide}}<hr id="answer">'
                        "{{Audio_Expression}} <b>{{Expression}}</b><br>"
                        "Part of Speech: {{PartOfSpeech}}<br><br>"
                        "Russian: {{RussianTranslation}}<br>"
                        "{{Audio_Definition}} Definition: {{Definition}}<br><br>"
                        "{{Audio_Examples}} Examples: {{Examples}}<br><br>"
                        "Synonyms: {{Synonyms}}<br><br>"
                        "Antonyms: {{Antonyms}}<br><br>"
                        "Collocations: {{Collocations}}<br><br>"
                        "Topics: {{Topics}}"
                    ),
                }
            ],
        )

        success_count = 0
        for i, card in enumerate(cards_data):
            try:
                # Convert lists to strings with safe access
                examples_str = (
                    "<br>".join(card.get("examples", []))
                    if card.get("examples")
                    else ""
                )
                synonyms_str = (
                    ", ".join(card.get("synonyms", [])) if card.get("synonyms") else ""
                )
                antonyms_str = (
                    ", ".join(card.get("antonyms", [])) if card.get("antonyms") else ""
                )
                collocations_str = (
                    ", ".join(card.get("collocations", []))
                    if card.get("collocations")
                    else ""
                )
                russian_str = (
                    ", ".join(card.get("russian", [])) if card.get("russian") else ""
                )
                topics_str = (
                    ", ".join(card.get("topics", [])) if card.get("topics") else ""
                )

                note = genanki.Note(
                    model=model,
                    fields=[
                        card.get("expression", ""),
                        card.get("definition", ""),
                        examples_str,
                        synonyms_str,
                        antonyms_str,
                        collocations_str,
                        card.get("part_of_speech", ""),
                        card.get("audio_expression", ""),
                        card.get("audio_definition", ""),
                        card.get("audio_examples", ""),
                        russian_str,
                        topics_str,
                    ],
                )
                deck.add_note(note)
                success_count += 1

            except Exception as e:
                logger.error(f"Failed to create note for card {i}: {e}")
                continue

        logger.info(
            f"Successfully created deck with {success_count}/{len(cards_data)} cards"
        )
        return deck

    except Exception as e:
        logger.error(f"Failed to create Anki deck: {e}")
        raise AnkiDeckError(f"Failed to create Anki deck: {e}") from e
