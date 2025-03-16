"""Utility functions for text-to-speech conversion to voice cards text."""

import os

from dotenv import load_dotenv
from elevenlabs import ElevenLabs, save
from gtts import gTTS

load_dotenv()


class TextToSpeech:
    """Class to convert text to speech using gTTS and ElevenLabs.

    Provides utility functions to generate MP3 files from text.
    """

    def __init__(self) -> None:
        """Initialize the TextToSpeech client with the ElevenLabs API key."""
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def text_to_speech_gtts(
        self, text: str, filename: str, language: str = "en"
    ) -> str:
        """Convert text to speech using gTTS and save as an MP3 file.

        Returns the filename of the MP3 file.
        If text is empty, returns an empty string.
        """
        if os.path.exists(filename):
            return filename

        if not text:
            return ""

        tts = gTTS(text=text, lang=language)
        tts.save(filename)
        return filename

    def text_to_speech_elevenlabs(self, text: str, filename: str) -> str:
        """Convert text to speech using ElevenLabs and save as an MP3 file.

        Returns the filename of the MP3 file.
        If text is empty, returns an empty string.
        """
        if os.path.exists(filename):
            return filename

        if not text:
            return ""

        if isinstance(text, list):
            text = " ".join(text)

        audio = self.client.text_to_speech.convert(
            voice_id="onwK4e9ZLuTAKqWW03F9",  # Daniel's voice ID
            model_id="eleven_turbo_v2_5",  # Model ID for Turbo v2.5
            text=text,
        )

        save(audio, filename)  # To save the audio to a file
        return filename
