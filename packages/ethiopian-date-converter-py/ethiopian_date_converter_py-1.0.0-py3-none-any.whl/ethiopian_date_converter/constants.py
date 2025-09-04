"""
Constants for Ethiopian calendar date conversion.
"""

# Julian Day Number epoch offsets
JD_EPOCH_OFFSET_AMETE_ALEM = -285019
JD_EPOCH_OFFSET_AMETE_MIHRET = 1723856
JD_EPOCH_OFFSET_GREGORIAN = 1721426

# Ethiopian month names
ETHIOPIC_MONTHS = {
    "en": [
        "Meskerem", "Tikemt", "Hidar", "Tahsas", "Tir", "Yakatit",
        "Magabit", "Miazia", "Ginbot", "Sene", "Hamle", "Nehasse", "Pagume"
    ],
    "am": [
        "መስከረም", "ትክምት", "ህዳር", "ታህሳስ", "ጥር", "የካቲት",
        "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"
    ]
}

# Gregorian month names
GREGORIAN_MONTHS = {
    "en": [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
}

# Day of week names
WEEKDAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "am": ["ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "አርብ", "ቅዳሜ", "እሁድ"]
}

# Ethiopian holidays (month, day)
ETHIOPIAN_HOLIDAYS = {
    "Ethiopian New Year": (1, 1),
    "Finding of the True Cross": (1, 17),
    "Ethiopian Christmas": (4, 29),
    "Epiphany (Timkat)": (5, 11),
    "Battle of Adwa": (6, 23),
    "Good Friday": None,  # Variable date
    "Easter": None,       # Variable date
}

# Calendar metadata
ETHIOPIC_MONTHS_PER_YEAR = 13
ETHIOPIC_DAYS_PER_MONTH = 30
GREGORIAN_MONTHS_PER_YEAR = 12
