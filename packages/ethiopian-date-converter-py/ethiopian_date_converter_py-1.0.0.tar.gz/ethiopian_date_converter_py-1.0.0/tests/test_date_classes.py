"""
Test cases for Ethiopian and Gregorian date classes.
"""

import pytest
from ethiopian_date_converter import EthiopicDate, GregorianDate
from ethiopian_date_converter.date_classes import InvalidDateError

class TestEthiopicDate:
    """Test EthiopicDate class functionality."""
    
    def test_date_creation(self):
        """Test creating Ethiopian dates."""
        date = EthiopicDate(2017, 1, 1)
        assert date.year == 2017
        assert date.month == 1
        assert date.day == 1
    
    def test_invalid_date_creation(self):
        """Test that invalid dates raise errors."""
        with pytest.raises(InvalidDateError):
            EthiopicDate(2017, 13, 7)  # Invalid Pagume day
        
        with pytest.raises(InvalidDateError):
            EthiopicDate(2017, 0, 1)  # Invalid month
    
    def test_string_representation(self):
        """Test string representation."""
        date = EthiopicDate(2017, 1, 1)
        assert str(date) == "2017-01-01"
        assert repr(date) == "EthiopicDate(2017, 1, 1)"
    
    def test_conversion_to_gregorian(self):
        """Test conversion to Gregorian."""
        ethiopic = EthiopicDate(2017, 1, 1)
        gregorian = ethiopic.to_gregorian()
        
        assert isinstance(gregorian, GregorianDate)
        assert gregorian.year == 2024
        assert gregorian.month == 9
        assert gregorian.day == 11
    
    def test_from_gregorian(self):
        """Test creating Ethiopian date from Gregorian."""
        gregorian = GregorianDate(2024, 9, 11)
        ethiopic = EthiopicDate.from_gregorian(gregorian)
        
        assert ethiopic.year == 2017
        assert ethiopic.month == 1
        assert ethiopic.day == 1
    
    def test_add_days(self):
        """Test adding days."""
        date = EthiopicDate(2017, 1, 1)
        new_date = date.add_days(10)
        
        assert new_date.year == 2017
        assert new_date.month == 1
        assert new_date.day == 11
    
    def test_add_months(self):
        """Test adding months."""
        date = EthiopicDate(2017, 1, 15)
        new_date = date.add_months(2)
        
        assert new_date.year == 2017
        assert new_date.month == 3
        assert new_date.day == 15
    
    def test_add_months_year_overflow(self):
        """Test adding months with year overflow."""
        date = EthiopicDate(2017, 12, 15)
        new_date = date.add_months(3)
        
        assert new_date.year == 2018
        assert new_date.month == 2
        assert new_date.day == 15
    
    def test_add_years(self):
        """Test adding years."""
        date = EthiopicDate(2017, 1, 1)
        new_date = date.add_years(5)
        
        assert new_date.year == 2022
        assert new_date.month == 1
        assert new_date.day == 1
    
    def test_diff_days(self):
        """Test calculating day differences."""
        date1 = EthiopicDate(2017, 1, 1)
        date2 = EthiopicDate(2017, 1, 11)
        
        assert date2.diff_days(date1) == 10
        assert date1.diff_days(date2) == -10
    
    def test_leap_year_detection(self):
        """Test leap year detection."""
        leap_year_date = EthiopicDate(2015, 1, 1)  # 2015 % 4 == 3
        non_leap_year_date = EthiopicDate(2016, 1, 1)  # 2016 % 4 == 0
        
        assert leap_year_date.is_leap_year() == True
        assert non_leap_year_date.is_leap_year() == False
    
    def test_days_in_month(self):
        """Test getting days in month."""
        regular_month = EthiopicDate(2017, 1, 1)
        pagume_leap = EthiopicDate(2015, 13, 1)  # Leap year Pagume
        pagume_regular = EthiopicDate(2016, 13, 1)  # Regular year Pagume
        
        assert regular_month.get_days_in_month() == 30
        assert pagume_leap.get_days_in_month() == 6
        assert pagume_regular.get_days_in_month() == 5
    
    def test_month_names(self):
        """Test getting month names."""
        date = EthiopicDate(2017, 1, 1)
        
        assert date.get_month_name("en") == "Meskerem"
        assert date.get_month_name("am") == "መስከረም"
    
    def test_day_of_week(self):
        """Test getting day of week."""
        date = EthiopicDate(2017, 1, 1)  # Should be Wednesday
        
        assert date.get_day_of_week("en") == "Wednesday"
        assert date.get_day_of_week("am") == "ረቡዕ"
    
    def test_holiday_detection(self):
        """Test holiday detection."""
        new_year = EthiopicDate(2017, 1, 1)
        christmas = EthiopicDate(2017, 4, 29)
        regular_day = EthiopicDate(2017, 2, 15)
        
        assert new_year.is_holiday() == True
        assert new_year.get_holiday_name() == "Ethiopian New Year"
        
        assert christmas.is_holiday() == True
        assert christmas.get_holiday_name() == "Ethiopian Christmas"
        
        assert regular_day.is_holiday() == False
        assert regular_day.get_holiday_name() is None
    
    def test_formatting(self):
        """Test date formatting."""
        date = EthiopicDate(2017, 1, 1)
        
        assert date.format("YYYY-MM-DD") == "2017-01-01"
        assert date.format("DD MMMM YYYY", "en") == "01 Meskerem 2017"
        assert date.format("DDDD, DD MMMM YYYY", "en") == "Wednesday, 01 Meskerem 2017"
    
    def test_comparison_operators(self):
        """Test comparison operators."""
        date1 = EthiopicDate(2017, 1, 1)
        date2 = EthiopicDate(2017, 1, 2)
        date3 = EthiopicDate(2017, 1, 1)
        
        assert date1 < date2
        assert date2 > date1
        assert date1 <= date2
        assert date2 >= date1
        assert date1 == date3
        assert date1 != date2
    
    def test_jdn_conversion(self):
        """Test Julian Day Number conversion."""
        date = EthiopicDate(2017, 1, 1)
        jdn = date.to_jdn()
        
        # Create date from JDN
        date_from_jdn = EthiopicDate.from_jdn(jdn)
        assert date_from_jdn == date

class TestGregorianDate:
    """Test GregorianDate class functionality."""
    
    def test_date_creation(self):
        """Test creating Gregorian dates."""
        date = GregorianDate(2024, 9, 11)
        assert date.year == 2024
        assert date.month == 9
        assert date.day == 11
    
    def test_invalid_date_creation(self):
        """Test that invalid dates raise errors."""
        with pytest.raises(InvalidDateError):
            GregorianDate(2023, 2, 29)  # Invalid leap day
        
        with pytest.raises(InvalidDateError):
            GregorianDate(2024, 13, 1)  # Invalid month
    
    def test_string_representation(self):
        """Test string representation."""
        date = GregorianDate(2024, 9, 11)
        assert str(date) == "2024-09-11"
        assert repr(date) == "GregorianDate(2024, 9, 11)"
    
    def test_conversion_to_ethiopic(self):
        """Test conversion to Ethiopian."""
        gregorian = GregorianDate(2024, 9, 11)
        ethiopic = gregorian.to_ethiopic()
        
        assert isinstance(ethiopic, EthiopicDate)
        assert ethiopic.year == 2017
        assert ethiopic.month == 1
        assert ethiopic.day == 1
    
    def test_from_ethiopic(self):
        """Test creating Gregorian date from Ethiopian."""
        ethiopic = EthiopicDate(2017, 1, 1)
        gregorian = GregorianDate.from_ethiopic(ethiopic)
        
        assert gregorian.year == 2024
        assert gregorian.month == 9
        assert gregorian.day == 11
    
    def test_leap_year_detection(self):
        """Test leap year detection."""
        leap_year = GregorianDate(2024, 1, 1)
        non_leap_year = GregorianDate(2023, 1, 1)
        
        assert leap_year.is_leap_year() == True
        assert non_leap_year.is_leap_year() == False
    
    def test_month_names(self):
        """Test getting month names."""
        date = GregorianDate(2024, 9, 11)
        assert date.get_month_name("en") == "September"
    
    def test_day_of_week(self):
        """Test getting day of week."""
        date = GregorianDate(2024, 9, 11)  # Should be Wednesday
        assert date.get_day_of_week("en") == "Wednesday"
    
    def test_formatting(self):
        """Test date formatting."""
        date = GregorianDate(2024, 9, 11)
        
        assert date.format("YYYY-MM-DD") == "2024-09-11"
        assert date.format("DD MMMM YYYY", "en") == "11 September 2024"
    
    def test_jdn_conversion(self):
        """Test Julian Day Number conversion."""
        date = GregorianDate(2024, 9, 11)
        jdn = date.to_jdn()
        
        # Create date from JDN
        date_from_jdn = GregorianDate.from_jdn(jdn)
        assert date_from_jdn == date

class TestCrossCalendarConsistency:
    """Test consistency between Ethiopian and Gregorian calendars."""
    
    def test_round_trip_conversion(self):
        """Test round-trip conversion consistency."""
        # Ethiopian -> Gregorian -> Ethiopian
        ethiopic_original = EthiopicDate(2017, 7, 15)
        gregorian = ethiopic_original.to_gregorian()
        ethiopic_back = gregorian.to_ethiopic()
        
        assert ethiopic_original == ethiopic_back
        
        # Gregorian -> Ethiopian -> Gregorian
        gregorian_original = GregorianDate(2024, 12, 25)
        ethiopic = gregorian_original.to_ethiopic()
        gregorian_back = ethiopic.to_gregorian()
        
        assert gregorian_original == gregorian_back
    
    def test_jdn_consistency(self):
        """Test JDN consistency across calendars."""
        ethiopic = EthiopicDate(2017, 1, 1)
        gregorian = GregorianDate(2024, 9, 11)
        
        assert ethiopic.to_jdn() == gregorian.to_jdn()
