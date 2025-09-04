"""
Utility functions for Ethiopian calendar operations.
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from .date_classes import EthiopicDate, GregorianDate
from .constants import ETHIOPIAN_HOLIDAYS

def get_current_ethiopic_date() -> EthiopicDate:
    """Get the current Ethiopian date."""
    return EthiopicDate.today()

def get_current_gregorian_date() -> GregorianDate:
    """Get the current Gregorian date."""
    return GregorianDate.today()

def generate_calendar(year: int, month: int, calendar_type: str = "ethiopic") -> Dict[str, Any]:
    """
    Generate a calendar for the specified month and year.
    
    Args:
        year: Year
        month: Month
        calendar_type: "ethiopic" or "gregorian"
    
    Returns:
        Dictionary containing calendar information
    """
    if calendar_type == "ethiopic":
        if month < 1 or month > 13:
            raise ValueError("Ethiopian month must be between 1 and 13")
        
        # Get number of days in the month
        if month == 13:  # Pagume
            days_in_month = 6 if ((year % 4) == 3) else 5
        else:
            days_in_month = 30
        
        # Get first day of month
        first_day = EthiopicDate(year, month, 1)
        first_day_jdn = first_day.to_jdn()
        first_weekday = first_day_jdn % 7  # 0=Monday
        
        # Generate calendar grid
        calendar_grid = []
        current_week = [None] * 7
        
        # Fill in empty days at the beginning
        for i in range(first_weekday):
            current_week[i] = None
        
        # Fill in the days of the month
        for day in range(1, days_in_month + 1):
            week_day = (first_weekday + day - 1) % 7
            current_week[week_day] = day
            
            if week_day == 6:  # End of week
                calendar_grid.append(current_week)
                current_week = [None] * 7
        
        # Add the last week if it has any days
        if any(day is not None for day in current_week):
            calendar_grid.append(current_week)
        
        return {
            "year": year,
            "month": month,
            "calendar_type": "ethiopic",
            "month_name": EthiopicDate(year, month, 1).get_month_name(),
            "days_in_month": days_in_month,
            "calendar_grid": calendar_grid,
            "holidays": get_holidays_in_month(year, month, "ethiopic")
        }
    
    elif calendar_type == "gregorian":
        if month < 1 or month > 12:
            raise ValueError("Gregorian month must be between 1 and 12")
        
        # Standard Gregorian calendar generation logic
        # This is a simplified version - you might want to use Python's calendar module
        import calendar
        
        cal = calendar.monthcalendar(year, month)
        
        return {
            "year": year,
            "month": month,
            "calendar_type": "gregorian",
            "month_name": GregorianDate(year, month, 1).get_month_name(),
            "calendar_grid": cal,
            "holidays": get_holidays_in_month(year, month, "gregorian")
        }
    
    else:
        raise ValueError("calendar_type must be 'ethiopic' or 'gregorian'")

def get_business_days(start_date: EthiopicDate, end_date: EthiopicDate, 
                     exclude_holidays: bool = True) -> int:
    """
    Calculate the number of business days between two Ethiopian dates.
    
    Args:
        start_date: Start date
        end_date: End date
        exclude_holidays: Whether to exclude holidays
    
    Returns:
        Number of business days
    """
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Check if it's a weekday (Monday=0, Sunday=6)
        day_of_week = current_date.to_jdn() % 7
        is_weekday = day_of_week < 5  # Monday to Friday
        
        # Check if it's a holiday
        is_holiday = exclude_holidays and current_date.is_holiday()
        
        if is_weekday and not is_holiday:
            business_days += 1
        
        current_date = current_date.add_days(1)
    
    return business_days

def get_holidays(year: int, calendar_type: str = "ethiopic") -> List[Dict[str, Any]]:
    """
    Get all holidays for a given year.
    
    Args:
        year: Year
        calendar_type: "ethiopic" or "gregorian"
    
    Returns:
        List of holiday dictionaries
    """
    holidays = []
    
    if calendar_type == "ethiopic":
        for holiday_name, date_tuple in ETHIOPIAN_HOLIDAYS.items():
            if date_tuple:  # Fixed date holidays
                month, day = date_tuple
                try:
                    holiday_date = EthiopicDate(year, month, day)
                    holidays.append({
                        "name": holiday_name,
                        "date": holiday_date,
                        "month": month,
                        "day": day,
                        "type": "fixed"
                    })
                except:
                    # Invalid date for this year (shouldn't happen for fixed holidays)
                    continue
    
    return holidays

def get_holidays_in_month(year: int, month: int, calendar_type: str = "ethiopic") -> List[Dict[str, Any]]:
    """Get holidays in a specific month."""
    all_holidays = get_holidays(year, calendar_type)
    return [h for h in all_holidays if h["month"] == month]

def calculate_age(birth_date: EthiopicDate, reference_date: Optional[EthiopicDate] = None) -> Dict[str, int]:
    """
    Calculate age from Ethiopian birth date.
    
    Args:
        birth_date: Birth date
        reference_date: Reference date (default: today)
    
    Returns:
        Dictionary with years, months, days
    """
    if reference_date is None:
        reference_date = EthiopicDate.today()
    
    if birth_date > reference_date:
        raise ValueError("Birth date cannot be in the future")
    
    years = reference_date.year - birth_date.year
    months = reference_date.month - birth_date.month
    days = reference_date.day - birth_date.day
    
    # Adjust for negative days
    if days < 0:
        months -= 1
        # Get days in previous month
        prev_month = reference_date.month - 1
        prev_year = reference_date.year
        if prev_month < 1:
            prev_month = 13
            prev_year -= 1
        
        days_in_prev_month = EthiopicDate(prev_year, prev_month, 1).get_days_in_month()
        days += days_in_prev_month
    
    # Adjust for negative months
    if months < 0:
        years -= 1
        months += 13
    
    return {
        "years": years,
        "months": months,
        "days": days
    }

def find_next_holiday(start_date: EthiopicDate, max_days: int = 365) -> Optional[Dict[str, Any]]:
    """
    Find the next holiday after the given date.
    
    Args:
        start_date: Starting date
        max_days: Maximum days to search
    
    Returns:
        Holiday information or None if no holiday found
    """
    current_date = start_date.add_days(1)
    
    for _ in range(max_days):
        if current_date.is_holiday():
            return {
                "name": current_date.get_holiday_name(),
                "date": current_date,
                "days_until": current_date.diff_days(start_date)
            }
        current_date = current_date.add_days(1)
    
    return None
