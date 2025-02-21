## Overview
lm-anki-cards-creator leverages both small and large language models to generate Anki decks automatically or through user interaction. It simplifies the process of creating effective flashcards for studying and reviewing content from various sources.

## Features
- **Automatic Generation:** Easily create flashcards from input text using advanced language models.
- **Manual Customization:** Tailor generated cards to your specific needs before finalizing your deck.
- **Multi-Model Support:** Utilize different language models based on the task, balancing speed and accuracy.

## Installation
1. Clone this repository:
    ```
    git clone https://github.com/yourusername/lm-anki-cards-creator.git
    ```
2. Navigate to the project directory:
    ```
    cd lm-anki-cards-creator
    ```
3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage
- **Automatic Mode:** Run the script with the `--auto` flag for complete automatic deck creation.
  ```
  python main.py --auto input.txt
  ```
- **Manual Mode in UI:** Run the script without the `--auto` flag to manually customize the deck in the UI.
  ```
  python main.py input.txt
  ```
