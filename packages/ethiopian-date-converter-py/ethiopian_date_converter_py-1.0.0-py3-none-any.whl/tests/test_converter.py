"""
Test cases for Ethiopian date converter core functions.
"""

import pytest
from ethiopian_date_converter import (
    ethiopic_to_gregorian,
    gregorian_to_ethiopic,
    is_valid_ethiopic_date,
    is_valid_gregorian_date,
    is_gregorian_leap,
    ethiopic_to_jdn,
    gregorian_to_jdn,
    jdn_to_ethiopic,
    jdn_to_gregorian,
    get_day_of_week,
)

class TestBasicConversion:
    """Test basic date conversion functions."""
    
    def test_ethiopic_to_gregorian_new_year(self):
        """Test Ethiopian New Year conversion."""
        result = ethiopic_to_gregorian(2017, 1, 1)
        expected = {"year": 2024, "month": 9, "day": 11}
        assert result == expected
    
    def test_ethiopic_to_gregorian_christmas(self):
        """Test Ethiopian Christmas conversion."""
        result = ethiopic_to_gregorian(2017, 4, 29)
        expected = {"year": 2025, "month": 1, "day": 7}
        assert result == expected
    
    def test_ethiopic_to_gregorian_timkat(self):
        """Test Ethiopian Timkat conversion."""
        result = ethiopic_to_gregorian(2017, 5, 11)
        expected = {"year": 2025, "month": 1, "day": 19}
        assert result == expected
    
    def test_gregorian_to_ethiopic_new_year(self):
        """Test reverse conversion for New Year."""
        result = gregorian_to_ethiopic(2024, 9, 11)
        expected = {"year": 2017, "month": 1, "day": 1}
        assert result == expected
    
    def test_gregorian_to_ethiopic_christmas(self):
        """Test reverse conversion for Christmas."""
        result = gregorian_to_ethiopic(2025, 1, 7)
        expected = {"year": 2017, "month": 4, "day": 29}
        assert result == expected
    
    def test_round_trip_consistency(self):
        """Test round-trip conversion consistency."""
        original = {"year": 2017, "month": 7, "day": 15}
        
        # Ethiopian -> Gregorian -> Ethiopian
        gregorian = ethiopic_to_gregorian(original["year"], original["month"], original["day"])
        back_to_ethiopic = gregorian_to_ethiopic(gregorian["year"], gregorian["month"], gregorian["day"])
        
        assert back_to_ethiopic == original
    
    def test_leap_year_pagume(self):
        """Test leap year Pagume conversion."""
        # 2015 EC is a leap year (2015 % 4 == 3)
        result = ethiopic_to_gregorian(2015, 13, 6)
        expected = {"year": 2023, "month": 9, "day": 11}
        assert result == expected

class TestValidation:
    """Test date validation functions."""
    
    def test_valid_ethiopic_dates(self):
        """Test valid Ethiopian dates."""
        assert is_valid_ethiopic_date(2017, 1, 1) == True
        assert is_valid_ethiopic_date(2017, 12, 30) == True
        assert is_valid_ethiopic_date(2015, 13, 6) == True  # Leap year Pagume
        assert is_valid_ethiopic_date(2016, 13, 5) == True  # Non-leap year Pagume
    
    def test_invalid_ethiopic_dates(self):
        """Test invalid Ethiopian dates."""
        assert is_valid_ethiopic_date(2017, 0, 1) == False  # Invalid month
        assert is_valid_ethiopic_date(2017, 14, 1) == False  # Invalid month
        assert is_valid_ethiopic_date(2017, 1, 0) == False  # Invalid day
        assert is_valid_ethiopic_date(2017, 1, 31) == False  # Invalid day
        assert is_valid_ethiopic_date(2016, 13, 6) == False  # Non-leap year Pagume
        assert is_valid_ethiopic_date(2017, 13, 7) == False  # Invalid Pagume day
    
    def test_valid_gregorian_dates(self):
        """Test valid Gregorian dates."""
        assert is_valid_gregorian_date(2024, 1, 1) == True
        assert is_valid_gregorian_date(2024, 2, 29) == True  # Leap year
        assert is_valid_gregorian_date(2024, 12, 31) == True
    
    def test_invalid_gregorian_dates(self):
        """Test invalid Gregorian dates."""
        assert is_valid_gregorian_date(2024, 0, 1) == False  # Invalid month
        assert is_valid_gregorian_date(2024, 13, 1) == False  # Invalid month
        assert is_valid_gregorian_date(2024, 1, 0) == False  # Invalid day
        assert is_valid_gregorian_date(2024, 1, 32) == False  # Invalid day
        assert is_valid_gregorian_date(2023, 2, 29) == False  # Non-leap year
    
    def test_gregorian_leap_years(self):
        """Test Gregorian leap year detection."""
        assert is_gregorian_leap(2024) == True
        assert is_gregorian_leap(2023) == False
        assert is_gregorian_leap(2000) == True  # Divisible by 400
        assert is_gregorian_leap(1900) == False  # Divisible by 100 but not 400

class TestJulianDayNumber:
    """Test Julian Day Number functions."""
    
    def test_ethiopic_jdn_conversion(self):
        """Test Ethiopian to JDN conversion."""
        jdn = ethiopic_to_jdn(2017, 1, 1)
        back_to_ethiopic = jdn_to_ethiopic(jdn)
        expected = {"year": 2017, "month": 1, "day": 1}
        assert back_to_ethiopic == expected
    
    def test_gregorian_jdn_conversion(self):
        """Test Gregorian to JDN conversion."""
        jdn = gregorian_to_jdn(2024, 9, 11)
        back_to_gregorian = jdn_to_gregorian(jdn)
        expected = {"year": 2024, "month": 9, "day": 11}
        assert back_to_gregorian == expected
    
    def test_cross_calendar_jdn_consistency(self):
        """Test JDN consistency across calendars."""
        # Ethiopian New Year 2017
        ethiopic_jdn = ethiopic_to_jdn(2017, 1, 1)
        gregorian_jdn = gregorian_to_jdn(2024, 9, 11)
        assert ethiopic_jdn == gregorian_jdn
    
    def test_day_of_week(self):
        """Test day of week calculation."""
        # Ethiopian New Year 2017 (2024-09-11) is a Wednesday
        jdn = ethiopic_to_jdn(2017, 1, 1)
        day_of_week = get_day_of_week(jdn)
        assert day_of_week == 2  # Wednesday (0=Monday, 2=Wednesday)

class TestErrorHandling:
    """Test error handling for invalid inputs."""
    
    def test_invalid_ethiopic_date_raises_error(self):
        """Test that invalid Ethiopian dates raise ValueError."""
        with pytest.raises(ValueError):
            ethiopic_to_gregorian(2017, 13, 7)  # Invalid Pagume day
    
    def test_invalid_gregorian_date_raises_error(self):
        """Test that invalid Gregorian dates raise ValueError."""
        with pytest.raises(ValueError):
            gregorian_to_ethiopic(2023, 2, 29)  # Invalid leap day

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_year_boundaries(self):
        """Test conversions at year boundaries."""
        # Last day of Ethiopian year 2016
        result = ethiopic_to_gregorian(2016, 13, 5)
        assert result["year"] == 2024
        assert result["month"] == 9
        assert result["day"] == 10
        
        # First day of Ethiopian year 2017
        result = ethiopic_to_gregorian(2017, 1, 1)
        assert result["year"] == 2024
        assert result["month"] == 9
        assert result["day"] == 11
    
    def test_leap_year_transitions(self):
        """Test leap year transitions."""
        # Last day of leap year Pagume
        result = ethiopic_to_gregorian(2015, 13, 6)
        
        # First day of next year
        next_year = ethiopic_to_gregorian(2016, 1, 1)
        
        # Should be consecutive days
        jdn1 = ethiopic_to_jdn(2015, 13, 6)
        jdn2 = ethiopic_to_jdn(2016, 1, 1)
        assert jdn2 == jdn1 + 1
    
    def test_month_boundaries(self):
        """Test conversions at month boundaries."""
        # Last day of month
        result1 = ethiopic_to_gregorian(2017, 1, 30)
        
        # First day of next month
        result2 = ethiopic_to_gregorian(2017, 2, 1)
        
        # Calculate JDNs to verify they're consecutive
        jdn1 = ethiopic_to_jdn(2017, 1, 30)
        jdn2 = ethiopic_to_jdn(2017, 2, 1)
        assert jdn2 == jdn1 + 1
