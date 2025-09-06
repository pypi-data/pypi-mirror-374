"""
google_speech_pyplay: A library for text-to-speech synthesis using the Google Translate TTS API and pygame.

Key components:
- `Speech`: Handles text-to-speech processing and audio playback.
- `SpeechSegment`: Represents a segment of text-to-speech audio.
- `PreloaderThread`: Preloads text-to-speech data for smoother playback.
- `SUPPORTED_LANGUAGES`: A list of languages supported by the Google Translate TTS API.
- `LANGUAGES_OPTIONS`: A list of dictionaries containing supported languages for
  the Google Translate TTS API. Each dictionary includes a `value` (language
  code, e.g., 'de') and a `label` (human-readable description, e.g., 'German').

Usage:
    python -m google_speech_pyplay "Hello, world!" -l en
"""

import argparse

from .config import LANGUAGES_OPTIONS, SUPPORTED_LANGUAGES
from .preloader_thread import PreloaderThread
from .speech import Speech
from .speech_segment import SpeechSegment
from .version import version


def cl_main():
    """
    Command-line entry point for `google_speech_pyplay`.

    This function enables the use of `google_speech_pyplay` as a command-line utility. It parses
    user arguments, processes the input text for text-to-speech, and either plays the audio or saves
    it to an output file in MP3 format.

    Commands:
    - `speech` (positional argument): The text to synthesize into speech.
    - `-l, --lang`: The language code for the speech synthesis (default is "en").
    - `-o, --output`: File path to save the synthesized audio; if not specified, audio is played instead.
    """
    arg_parser = argparse.ArgumentParser(
        description="Google Speech",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument("speech", help="Text to play")
    arg_parser.add_argument(
        "-l",
        "--lang",
        choices=SUPPORTED_LANGUAGES,
        default="en",
        dest="lang",
        help="Language",
    )
    arg_parser.add_argument(
        "-o",
        "--output",
        default=None,
        dest="output",
        help="Outputs audio data to this file instead of playing it",
    )
    args = arg_parser.parse_args()

    speech = Speech(args.speech, args.lang)
    if args.output:
        speech.save(args.output)
    else:
        speech.play()


__all__ = [
    "version",
    "Speech",
    "SpeechSegment",
    "PreloaderThread",
    "SUPPORTED_LANGUAGES",
    "LANGUAGES_OPTIONS",
]


if __name__ == "__main__":
    cl_main()
