"""
Datetime Parsing Utilities
==========================

Production-grade datetime parsing for xSystem.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generated: 2025-01-27
"""

import re
from datetime import datetime, date, time, timezone, timedelta
from typing import Optional, Union, Dict, List
import logging

logger = logging.getLogger(__name__)


# Common datetime patterns
DATETIME_PATTERNS = [
    # ISO 8601 formats
    (r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(?:Z|([+-]\d{2}):?(\d{2}))?', 'iso_datetime'),
    (r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(?:\s*([+-]\d{2}):?(\d{2}))?', 'iso_datetime_space'),
    
    # Date only formats
    (r'(\d{4})-(\d{2})-(\d{2})', 'iso_date'),
    (r'(\d{2})/(\d{2})/(\d{4})', 'us_date'),  # MM/DD/YYYY
    (r'(\d{2})-(\d{2})-(\d{4})', 'eu_date'),  # DD-MM-YYYY
    (r'(\d{1,2})/(\d{1,2})/(\d{4})', 'us_date_short'),
    (r'(\d{1,2})-(\d{1,2})-(\d{4})', 'eu_date_short'),
    
    # Time only formats
    (r'(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.(\d+))?\s*(AM|PM)?', 'time_12h'),
    (r'(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.(\d+))?', 'time_24h'),
    
    # Relative formats
    (r'(\d+)\s*(second|minute|hour|day|week|month|year)s?\s*ago', 'relative_past'),
    (r'in\s*(\d+)\s*(second|minute|hour|day|week|month|year)s?', 'relative_future'),
    
    # Natural language
    (r'(yesterday|today|tomorrow)', 'natural_day'),
    (r'(now)', 'natural_now'),
]


def parse_datetime(text: str, default_timezone: Optional[timezone] = None) -> Optional[datetime]:
    """
    Parse datetime from text.
    
    Args:
        text: Text to parse
        default_timezone: Default timezone
        
    Returns:
        Parsed datetime or None
    """
    if not text or not isinstance(text, str):
        return None
    
    text = text.strip()
    tz = default_timezone or timezone.utc
    
    # Try ISO 8601 first
    try:
        if hasattr(datetime, 'fromisoformat'):
            if text.endswith('Z'):
                text_iso = text[:-1] + '+00:00'
            else:
                text_iso = text
            return datetime.fromisoformat(text_iso)
    except (ValueError, AttributeError):
        pass
    
    # Try common formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%m/%d/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            if tz and dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt
        except ValueError:
            continue
    
    return None


def parse_date(text: str) -> Optional[date]:
    """Parse date from text."""
    dt = parse_datetime(text)
    return dt.date() if dt else None


def parse_time(text: str) -> Optional[time]:
    """Parse time from text."""
    if not text or not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Try common time formats
    formats = [
        '%H:%M:%S',
        '%H:%M:%S.%f',
        '%H:%M',
        '%I:%M:%S %p',
        '%I:%M %p',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.time()
        except ValueError:
            continue
    
    return None


def parse_iso8601(text: str) -> Optional[datetime]:
    """Parse ISO 8601 datetime string."""
    try:
        if hasattr(datetime, 'fromisoformat'):
            if text.endswith('Z'):
                text = text[:-1] + '+00:00'
            return datetime.fromisoformat(text)
    except (ValueError, AttributeError):
        pass
    
    return parse_datetime(text)


def parse_timestamp(timestamp: Union[int, float, str]) -> Optional[datetime]:
    """Parse Unix timestamp to datetime."""
    try:
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        
        # Handle both seconds and milliseconds
        if timestamp > 1e10:  # Likely milliseconds
            timestamp = timestamp / 1000
        
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
    except (ValueError, OSError, OverflowError) as e:
        logger.debug(f"Failed to parse timestamp '{timestamp}': {e}")
        return None