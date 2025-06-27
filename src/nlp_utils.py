"""NLP utilities for the Anki Card Generator."""

import argparse
import re
import unicodedata
from collections import Counter
from typing import TextIO

import nltk
import streamlit as st

try:
    from .exceptions import FileProcessingError
    from .logger import get_logger
except ImportError:
    # Fallback for script execution
    from src.exceptions import FileProcessingError  # type: ignore
    from src.logger import get_logger  # type: ignore

# Download required NLTK data
try:
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)
except Exception:
    pass  # Fail silently if NLTK download fails

logger = get_logger(__name__)


def parse_words(args: argparse.Namespace) -> list[str]:
    """Parse the words either from a comma-separated string or from a file path.

    Args:
        args: Command line arguments containing words or file path

    Returns:
        List of parsed words

    Raises:
        ValueError: If neither words nor file is provided
        FileProcessingError: If file parsing fails
    """
    try:
        words = []
        if args.words:
            # Assume comma-separated words.
            words = [word.strip() for word in args.words.split(",") if word.strip()]
        elif args.file:
            words = parse_file(args.file)
        else:
            raise ValueError("Either --words or --file must be provided.")

        logger.info(f"Successfully parsed {len(words)} words")
        return words

    except Exception as e:
        logger.error(f"Failed to parse words: {e}")
        if isinstance(e, ValueError):
            raise
        raise FileProcessingError(f"Failed to parse words: {e}") from e


def parse_file(file_input: str | TextIO) -> list[str]:
    """Parse words from a file path or a file-like object (e.g., Streamlit UploadedFile).

    Args:
        file_input: File path string or file-like object

    Returns:
        List of parsed words

    Raises:
        FileProcessingError: If file processing fails
    """
    try:
        # If the input is file-like, it should have a 'read' attribute.
        if hasattr(file_input, "read"):
            content = file_input.read()
            # UploadedFile might return bytes; decode if needed.
            if isinstance(content, bytes):
                content = content.decode("utf-8")
        else:
            # Otherwise, assume it's a path and open it.
            with open(file_input, encoding="utf-8") as f:
                content = f.read()

        words = []
        # Split content into lines, then by commas, stripping whitespace.
        for line in content.splitlines():
            for word in line.split():
                clean_word = word.strip().rstrip(",.")
                if clean_word:
                    words.append(clean_word)

        logger.debug(f"Parsed {len(words)} words from file")
        return words

    except Exception as e:
        logger.error(f"Failed to parse file: {e}")
        raise FileProcessingError(f"Failed to parse file: {e}") from e


def clean_text(text: str) -> str:
    """Clean and preprocess text data."""
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation (you can adjust the regex to keep certain characters)
    text = re.sub(r"[^\w\s']", "", text)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def filter_tokens(
    tokens: list[str], stopwords: set = None, min_length: int = 2
) -> list[str]:
    """Filter tokens based on stopwords and minimum length."""
    if stopwords is None:
        # Default stopwords from NLTK
        stopwords = set(nltk.corpus.stopwords.words("english"))

    filtered = []
    for token in tokens:
        # Filter out numbers or tokens that are too short
        if token.isdigit() or len(token) < min_length:
            continue
        # Optionally filter stopwords
        if token in stopwords:
            continue
        filtered.append(token)
    return filtered


def extract_ngrams(tokens: list[str], n: int = 2, min_freq: int = 2) -> list[str]:
    """Extract n-grams from a list of tokens."""
    ngrams = zip(*[tokens[i:] for i in range(n)], strict=False)
    ngrams = [" ".join(gram) for gram in ngrams]
    freq = Counter(ngrams)
    # Return n-grams that occur at least min_freq times
    return [ng for ng, count in freq.items() if count >= min_freq]


def prepare_flashcard_candidates(file_input, stopwords: set = None):
    """Prepare flashcard candidates from a file input."""
    st.spinner("Prepare flashcard candidates...")
    # Assume parse_file handles both file path and stream uploader
    raw_content = parse_file(file_input)
    st.info(f"Number of words in the file: {len(raw_content)}")
    text = " ".join(raw_content)  # if parse_file returns a list of lines/words
    st.info(f"Total number of characters in the text: {len(text)}")
    cleaned = clean_text(text)
    # Simple split by whitespace
    tokens = cleaned.split()
    # Optionally filter tokens to remove stopwords
    filtered_tokens = filter_tokens(tokens, stopwords=stopwords)

    # Optionally extract phrases:
    bi_grams = extract_ngrams(filtered_tokens, n=2)
    st.info(bi_grams)
    # Optionally extract trigrams:
    tri_grams = extract_ngrams(filtered_tokens, n=3)
    st.info(tri_grams)

    # Remove candidates with less than 3 characters
    filtered_tokens = [token for token in filtered_tokens if len(token) > 3]

    # Remove duplicate words
    text = " ".join(sorted(set(text.split()), key=text.split().index))

    flashcard_candidates = bi_grams + tri_grams + filtered_tokens

    return ", ".join(flashcard_candidates)
