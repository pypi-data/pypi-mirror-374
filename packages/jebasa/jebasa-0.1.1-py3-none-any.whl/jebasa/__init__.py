"""Jebasa: Japanese ebook audio subtitle aligner.

A Python package for creating synchronized subtitles from Japanese audiobooks and EPUB files
using Montreal Forced Aligner (MFA).
"""

__version__ = "0.1.1"
__author__ = "OCboy5"
__email__ = "your.email@example.com"

from jebasa.audio import AudioProcessor
from jebasa.text import TextProcessor
from jebasa.dictionary import DictionaryCreator
from jebasa.alignment import AlignmentRunner
from jebasa.subtitles import SubtitleGenerator
from jebasa.pipeline import JebasaPipeline

__all__ = [
    "AudioProcessor",
    "TextProcessor", 
    "DictionaryCreator",
    "AlignmentRunner",
    "SubtitleGenerator",
    "JebasaPipeline",
]