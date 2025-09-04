"""
Date classes for Ethiopian and Gregorian calendars.
"""

from datetime import datetime
from typing import Optional, Union, Dict, Any
from .converter import (
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
from .constants import ETHIOPIC_MONTHS, GREGORIAN_MONTHS, WEEKDAYS, ETHIOPIAN_HOLIDAYS

class InvalidDateError(ValueError):
    """Raised when an invalid date is provided."""
    pass

class EthiopicDate:
    """Ethiopian calendar date with full functionality."""
    
    def __init__(self, year: int, month: int, day: int):
        """
        Create an Ethiopian date.
        
        Args:
            year: Ethiopian year
            month: Ethiopian month (1-13)
            day: Ethiopian day (1-30, or 1-6 for Pagume)
        
        Raises:
            InvalidDateError: If the date is invalid
        """
        if not is_valid_ethiopic_date(year, month, day):
            raise InvalidDateError(f"Invalid Ethiopian date: {year}-{month}-{day}")
        
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_gregorian(cls, gregorian_date: 'GregorianDate') -> 'EthiopicDate':
        """Create Ethiopian date from Gregorian date."""
        converted = gregorian_to_ethiopic(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        return cls(converted["year"], converted["month"], converted["day"])
    
    @classmethod
    def from_jdn(cls, jdn: int, era: Optional[int] = None) -> 'EthiopicDate':
        """Create Ethiopian date from Julian Day Number."""
        converted = jdn_to_ethiopic(jdn, era)
        return cls(converted["year"], converted["month"], converted["day"])
    
    @classmethod
    def today(cls) -> 'EthiopicDate':
        """Get today's Ethiopian date."""
        today = datetime.now()
        gregorian = GregorianDate(today.year, today.month, today.day)
        return cls.from_gregorian(gregorian)
    
    @classmethod
    def is_valid(cls, year: int, month: int, day: int) -> bool:
        """Check if the given Ethiopian date is valid."""
        return is_valid_ethiopic_date(year, month, day)
    
    def to_gregorian(self) -> 'GregorianDate':
        """Convert to Gregorian date."""
        converted = ethiopic_to_gregorian(self.year, self.month, self.day)
        return GregorianDate(converted["year"], converted["month"], converted["day"])
    
    def to_jdn(self, era: Optional[int] = None) -> int:
        """Convert to Julian Day Number."""
        return ethiopic_to_jdn(self.year, self.month, self.day, era)
    
    def add_days(self, days: int) -> 'EthiopicDate':
        """Add days to the date."""
        jdn = self.to_jdn() + days
        return EthiopicDate.from_jdn(jdn)
    
    def add_months(self, months: int) -> 'EthiopicDate':
        """Add months to the date."""
        new_month = self.month + months
        new_year = self.year
        
        while new_month > 13:
            new_month -= 13
            new_year += 1
        while new_month < 1:
            new_month += 13
            new_year -= 1
        
        # Adjust day if necessary (e.g., Pagume has fewer days)
        new_day = min(self.day, self._get_days_in_month(new_year, new_month))
        
        return EthiopicDate(new_year, new_month, new_day)
    
    def add_years(self, years: int) -> 'EthiopicDate':
        """Add years to the date."""
        new_year = self.year + years
        # Adjust day if necessary (leap year considerations)
        new_day = min(self.day, self._get_days_in_month(new_year, self.month))
        return EthiopicDate(new_year, self.month, new_day)
    
    def diff_days(self, other: 'EthiopicDate') -> int:
        """Calculate difference in days between two dates."""
        return self.to_jdn() - other.to_jdn()
    
    def get_day_of_week(self, locale: str = "en") -> str:
        """Get day of week name."""
        dow_index = get_day_of_week(self.to_jdn())
        return WEEKDAYS[locale][dow_index]
    
    def get_month_name(self, locale: str = "en") -> str:
        """Get month name."""
        return ETHIOPIC_MONTHS[locale][self.month - 1]
    
    def is_leap_year(self) -> bool:
        """Check if the year is a leap year in Ethiopian calendar."""
        return (self.year % 4) == 3
    
    def get_days_in_month(self) -> int:
        """Get number of days in the current month."""
        return self._get_days_in_month(self.year, self.month)
    
    def _get_days_in_month(self, year: int, month: int) -> int:
        """Get number of days in a specific month."""
        if month == 13:  # Pagume
            return 6 if ((year % 4) == 3) else 5
        return 30
    
    def is_holiday(self) -> bool:
        """Check if the date is a holiday."""
        for holiday, date_tuple in ETHIOPIAN_HOLIDAYS.items():
            if date_tuple and date_tuple == (self.month, self.day):
                return True
        return False
    
    def get_holiday_name(self) -> Optional[str]:
        """Get holiday name if the date is a holiday."""
        for holiday, date_tuple in ETHIOPIAN_HOLIDAYS.items():
            if date_tuple and date_tuple == (self.month, self.day):
                return holiday
        return None
    
    def format(self, format_string: str = "YYYY-MM-DD", locale: str = "en") -> str:
        """
        Format the date according to the given pattern.
        
        Supported patterns:
        - YYYY: 4-digit year
        - MM: 2-digit month
        - DD: 2-digit day
        - MMMM: Full month name
        - DDDD: Full day name
        """
        result = format_string
        result = result.replace("YYYY", f"{self.year:04d}")
        result = result.replace("MM", f"{self.month:02d}")
        result = result.replace("DD", f"{self.day:02d}")
        result = result.replace("MMMM", self.get_month_name(locale))
        result = result.replace("DDDD", self.get_day_of_week(locale))
        return result
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"EthiopicDate({self.year}, {self.month}, {self.day})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, EthiopicDate):
            return False
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, EthiopicDate):
            return NotImplemented
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        return self < other or self == other
    
    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if not isinstance(other, EthiopicDate):
            return NotImplemented
        return (self.year, self.month, self.day) > (other.year, other.month, other.day)
    
    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        return self > other or self == other

class GregorianDate:
    """Gregorian calendar date with conversion capabilities."""
    
    def __init__(self, year: int, month: int, day: int):
        """
        Create a Gregorian date.
        
        Args:
            year: Gregorian year
            month: Gregorian month (1-12)
            day: Gregorian day
        
        Raises:
            InvalidDateError: If the date is invalid
        """
        if not is_valid_gregorian_date(year, month, day):
            raise InvalidDateError(f"Invalid Gregorian date: {year}-{month}-{day}")
        
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_ethiopic(cls, ethiopic_date: EthiopicDate) -> 'GregorianDate':
        """Create Gregorian date from Ethiopian date."""
        converted = ethiopic_to_gregorian(ethiopic_date.year, ethiopic_date.month, ethiopic_date.day)
        return cls(converted["year"], converted["month"], converted["day"])
    
    @classmethod
    def from_jdn(cls, jdn: int) -> 'GregorianDate':
        """Create Gregorian date from Julian Day Number."""
        converted = jdn_to_gregorian(jdn)
        return cls(converted["year"], converted["month"], converted["day"])
    
    @classmethod
    def today(cls) -> 'GregorianDate':
        """Get today's Gregorian date."""
        today = datetime.now()
        return cls(today.year, today.month, today.day)
    
    @classmethod
    def is_valid(cls, year: int, month: int, day: int) -> bool:
        """Check if the given Gregorian date is valid."""
        return is_valid_gregorian_date(year, month, day)
    
    def to_ethiopic(self) -> EthiopicDate:
        """Convert to Ethiopian date."""
        converted = gregorian_to_ethiopic(self.year, self.month, self.day)
        return EthiopicDate(converted["year"], converted["month"], converted["day"])
    
    def to_jdn(self) -> int:
        """Convert to Julian Day Number."""
        return gregorian_to_jdn(self.year, self.month, self.day)
    
    def is_leap_year(self) -> bool:
        """Check if the year is a leap year."""
        return is_gregorian_leap(self.year)
    
    def get_day_of_week(self, locale: str = "en") -> str:
        """Get day of week name."""
        dow_index = get_day_of_week(self.to_jdn())
        return WEEKDAYS[locale][dow_index]
    
    def get_month_name(self, locale: str = "en") -> str:
        """Get month name."""
        return GREGORIAN_MONTHS[locale][self.month - 1]
    
    def format(self, format_string: str = "YYYY-MM-DD", locale: str = "en") -> str:
        """Format the date according to the given pattern."""
        result = format_string
        result = result.replace("YYYY", f"{self.year:04d}")
        result = result.replace("MM", f"{self.month:02d}")
        result = result.replace("DD", f"{self.day:02d}")
        result = result.replace("MMMM", self.get_month_name(locale))
        result = result.replace("DDDD", self.get_day_of_week(locale))
        return result
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"GregorianDate({self.year}, {self.month}, {self.day})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, GregorianDate):
            return False
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, GregorianDate):
            return NotImplemented
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)
