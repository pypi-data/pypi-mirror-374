"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

xSystem Validation Package

Declarative validation with type hints, automatic coercion, and Pydantic-style models.
"""

from .declarative import xModel, Field, ValidationError

__all__ = [
    "xModel",
    "Field", 
    "ValidationError",
]