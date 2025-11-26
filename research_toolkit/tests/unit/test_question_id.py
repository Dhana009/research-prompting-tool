"""
Unit tests for question ID generation.

Tests question ID format: <TOOL_PREFIX>-<YYYYMMDD>-<HHMMSS>IST-<DAY>-<RANDOM_SUFFIX>
"""

import pytest
from datetime import datetime
import pytz
import re


class TestQuestionIDGeneration:
    """Test question ID generation with correct format."""
    
    def test_question_id_format(self):
        """Test question ID matches required format."""
        # This will fail until we implement the function
        from src.models.question import generate_question_id
        
        question_id = generate_question_id("TR")
        
        # Format: TR-20251126-105433IST-WED-QX18
        pattern = r"^(TR|CR|DB|AR|GP)-\d{8}-\d{6}IST-(MON|TUE|WED|THU|FRI|SAT|SUN)-[A-Z0-9]{4}$"
        assert re.match(pattern, question_id), f"Question ID {question_id} does not match format"
    
    def test_all_tool_prefixes(self):
        """Test all 5 tool prefixes generate valid IDs."""
        from src.models.question import generate_question_id
        
        prefixes = ["TR", "CR", "DB", "AR", "GP"]
        
        for prefix in prefixes:
            question_id = generate_question_id(prefix)
            assert question_id.startswith(prefix), f"ID {question_id} should start with {prefix}"
    
    def test_ist_timezone_conversion(self):
        """Test timestamp is in IST timezone."""
        from src.models.question import generate_question_id
        
        question_id = generate_question_id("TR")
        
        # Extract date and time from question ID
        # Format: TR-20251126-105433IST-WED-QX18
        parts = question_id.split("-")
        date_str = parts[1]  # YYYYMMDD
        time_str = parts[2].replace("IST", "")  # HHMMSS
        
        # Verify date format
        assert len(date_str) == 8, "Date should be YYYYMMDD format"
        assert len(time_str) == 6, "Time should be HHMMSS format"
        
        # Parse and verify it's a valid date/time
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        hour = int(time_str[:2])
        minute = int(time_str[2:4])
        second = int(time_str[4:6])
        
        # Should be valid datetime values
        assert 2020 <= year <= 2100, "Year should be reasonable"
        assert 1 <= month <= 12, "Month should be 1-12"
        assert 1 <= day <= 31, "Day should be 1-31"
        assert 0 <= hour <= 23, "Hour should be 0-23"
        assert 0 <= minute <= 59, "Minute should be 0-59"
        assert 0 <= second <= 59, "Second should be 0-59"
    
    def test_day_of_week_extraction(self):
        """Test day of week is correctly extracted and matches date."""
        from src.models.question import generate_question_id
        
        question_id = generate_question_id("TR")
        
        # Extract day from question ID
        # Format: TR-20251126-105433IST-WED-QX18
        parts = question_id.split("-")
        day_abbr = parts[3]  # WED
        
        # Verify day abbreviation is valid
        valid_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        assert day_abbr in valid_days, f"Day {day_abbr} should be one of {valid_days}"
        
        # Extract date and verify day matches
        date_str = parts[1]  # YYYYMMDD
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        
        # Get actual day of week for this date
        ist = pytz.timezone("Asia/Kolkata")
        dt = datetime(year, month, day, tzinfo=ist)
        actual_day = dt.strftime("%a").upper()
        
        assert day_abbr == actual_day, f"Day {day_abbr} should match actual day {actual_day} for date {date_str}"
    
    def test_uniqueness(self):
        """Test generated IDs are unique."""
        from src.models.question import generate_question_id
        
        # Generate multiple IDs
        ids = [generate_question_id("TR") for _ in range(100)]
        
        # All should be unique
        assert len(ids) == len(set(ids)), "Generated IDs should be unique"
    
    def test_random_suffix_format(self):
        """Test random suffix is 4 alphanumeric characters."""
        from src.models.question import generate_question_id
        
        question_id = generate_question_id("TR")
        
        # Extract suffix
        # Format: TR-20251126-105433IST-WED-QX18
        parts = question_id.split("-")
        suffix = parts[4]  # QX18
        
        # Should be 4 alphanumeric characters
        assert len(suffix) == 4, "Suffix should be 4 characters"
        assert suffix.isalnum(), "Suffix should be alphanumeric"
        assert suffix.isupper(), "Suffix should be uppercase"

