"""
Question ID generation module.

Generates unique question IDs in the format:
<TOOL_PREFIX>-<YYYYMMDD>-<HHMMSS>IST-<DAY>-<RANDOM_SUFFIX>

Example: TR-20251126-105433IST-WED-QX18
"""

import random
import string
from datetime import datetime
import pytz


def generate_question_id(tool_prefix: str) -> str:
    """
    Generate a unique question ID with IST timezone.
    
    Args:
        tool_prefix: Tool prefix (TR, CR, DB, AR, GP)
        
    Returns:
        Question ID in format: <TOOL_PREFIX>-<YYYYMMDD>-<HHMMSS>IST-<DAY>-<RANDOM_SUFFIX>
        
    Example:
        >>> generate_question_id("TR")
        'TR-20251126-105433IST-WED-QX18'
    """
    # Validate tool prefix
    valid_prefixes = ["TR", "CR", "DB", "AR", "GP"]
    if tool_prefix not in valid_prefixes:
        raise ValueError(f"Invalid tool prefix. Must be one of {valid_prefixes}")
    
    # Get current time in IST
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    
    # Format date: YYYYMMDD
    date_str = now.strftime("%Y%m%d")
    
    # Format time: HHMMSS
    time_str = now.strftime("%H%M%S")
    
    # Get day of week abbreviation: MON, TUE, WED, etc.
    day_abbr = now.strftime("%a").upper()
    
    # Generate random 4-character uppercase alphanumeric suffix
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # Combine all parts
    question_id = f"{tool_prefix}-{date_str}-{time_str}IST-{day_abbr}-{suffix}"
    
    return question_id

