"""Utility functions for creating Anki decks from card data."""

import genanki


def create_anki_deck(
    cards_data: list[dict], deck_name: str = "My Vocabulary Deck"
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
        cards_data (list[dict]): A list of dictionaries containing card information.
        deck_name (str, optional): The name of the deck.

    Returns:
        genanki.Deck: The constructed Anki deck.
    """
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

    for card in cards_data:
        # Convert lists to strings
        examples_str = "<br>".join(card["examples"]) if card["examples"] else ""
        synonyms_str = ", ".join(card["synonyms"]) if card["synonyms"] else ""
        antonyms_str = ", ".join(card["antonyms"]) if card["antonyms"] else ""
        collocations_str = (
            ", ".join(card["collocations"]) if card["collocations"] else ""
        )
        russian_str = ", ".join(card["russian"]) if card["russian"] else ""
        topics_str = ", ".join(card["topics"]) if card["topics"] else ""

        note = genanki.Note(
            model=model,
            fields=[
                card["expression"],
                card["definition"],
                examples_str,
                synonyms_str,
                antonyms_str,
                collocations_str,
                card["part_of_speech"],
                card["audio_expression"],
                card["audio_definition"],
                card["audio_examples"],
                russian_str,
                topics_str,
            ],
        )
        deck.add_note(note)

    return deck
