"""
Ethiopian Date Converter for Python

High-performance Ethiopian calendar date conversion with native C implementation.
"""

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

from .date_classes import (
    EthiopicDate,
    GregorianDate,
)

from .constants import (
    ETHIOPIC_MONTHS,
    GREGORIAN_MONTHS,
    WEEKDAYS,
    JD_EPOCH_OFFSET_AMETE_ALEM,
    JD_EPOCH_OFFSET_AMETE_MIHRET,
    JD_EPOCH_OFFSET_GREGORIAN,
)

from .utils import (
    get_current_ethiopic_date,
    get_current_gregorian_date,
    generate_calendar,
    get_business_days,
    get_holidays,
)

__version__ = "1.0.0"
__author__ = "Abiy"
__email__ = "abiywondimu1@gmail.com"

__all__ = [
    # Core conversion functions
    "ethiopic_to_gregorian",
    "gregorian_to_ethiopic",
    "is_valid_ethiopic_date", 
    "is_valid_gregorian_date",
    "is_gregorian_leap",
    
    # Julian Day Number functions
    "ethiopic_to_jdn",
    "gregorian_to_jdn", 
    "jdn_to_ethiopic",
    "jdn_to_gregorian",
    "get_day_of_week",
    
    # Date classes
    "EthiopicDate",
    "GregorianDate",
    
    # Constants
    "ETHIOPIC_MONTHS",
    "GREGORIAN_MONTHS", 
    "WEEKDAYS",
    "JD_EPOCH_OFFSET_AMETE_ALEM",
    "JD_EPOCH_OFFSET_AMETE_MIHRET", 
    "JD_EPOCH_OFFSET_GREGORIAN",
    
    # Utilities
    "get_current_ethiopic_date",
    "get_current_gregorian_date",
    "generate_calendar",
    "get_business_days", 
    "get_holidays",
]
