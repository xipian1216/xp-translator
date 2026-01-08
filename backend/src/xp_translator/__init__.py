"""
XP Translator Backend Package
"""

__version__ = "1.0.0"
__author__ = "XP Translator Team"

from .api import app
from .models import TranslationRequest, TranslationResponse
from .clients import DeepSeekClient, MockAIClient

__all__ = [
    "app",
    "TranslationRequest",
    "TranslationResponse",
    "DeepSeekClient",
    "MockAIClient",
]