"""
Core conversion functions using native C implementation via ctypes.
"""

import ctypes
import os
import platform
from typing import Dict, Tuple, Optional
from ctypes import c_int32, c_int64, c_bool, Structure, POINTER

class DateStruct(Structure):
    """C date_t structure."""
    _fields_ = [
        ("year", c_int32),
        ("month", c_int32),
        ("day", c_int32),
    ]

class EthiopicCalendarLib:
    """Wrapper for the native Ethiopian calendar C library."""
    
    def __init__(self):
        self._lib = None
        self._load_library()
        self._setup_functions()
    
    def _load_library(self):
        """Load the compiled C library."""
        lib_dir = os.path.join(os.path.dirname(__file__), "core")
        
        # Try to find the compiled library
        system = platform.system().lower()
        if system == "windows":
            lib_name = "ethiopic_calendar.dll"
        elif system == "darwin":
            lib_name = "libethiopic_calendar.dylib"
        else:
            lib_name = "libethiopic_calendar.so"
        
        lib_path = os.path.join(lib_dir, lib_name)
        
        if not os.path.exists(lib_path):
            # Try to compile the library if it doesn't exist
            self._compile_library(lib_dir, lib_name)
        
        try:
            self._lib = ctypes.CDLL(lib_path)
        except OSError as e:
            raise ImportError(f"Could not load Ethiopian calendar library: {e}")
    
    def _compile_library(self, lib_dir: str, lib_name: str):
        """Compile the C library on the fly."""
        import subprocess
        import tempfile
        
        c_file = os.path.join(lib_dir, "ethiopic_calendar.c")
        lib_path = os.path.join(lib_dir, lib_name)
        
        if not os.path.exists(c_file):
            raise FileNotFoundError(f"C source file not found: {c_file}")
        
        try:
            system = platform.system().lower()
            if system == "windows":
                # Try to compile with gcc (MinGW) or cl (MSVC)
                try:
                    subprocess.run([
                        "gcc", "-shared", "-fPIC", "-O3",
                        "-o", lib_path, c_file
                    ], check=True, capture_output=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    subprocess.run([
                        "cl", "/LD", "/O2", f"/Fe:{lib_path}", c_file
                    ], check=True, capture_output=True)
            else:
                # Unix-like systems
                subprocess.run([
                    "gcc", "-shared", "-fPIC", "-O3",
                    "-o", lib_path, c_file
                ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to compile C library: {e}")
    
    def _setup_functions(self):
        """Setup function signatures for the C library."""
        # is_gregorian_leap
        self._lib.is_gregorian_leap.argtypes = [c_int32]
        self._lib.is_gregorian_leap.restype = c_bool
        
        # is_valid_gregorian_date
        self._lib.is_valid_gregorian_date.argtypes = [c_int32, c_int32, c_int32]
        self._lib.is_valid_gregorian_date.restype = c_bool
        
        # is_valid_ethiopic_date
        self._lib.is_valid_ethiopic_date.argtypes = [c_int32, c_int32, c_int32]
        self._lib.is_valid_ethiopic_date.restype = c_bool
        
        # gregorian_to_jdn
        self._lib.gregorian_to_jdn.argtypes = [c_int32, c_int32, c_int32]
        self._lib.gregorian_to_jdn.restype = c_int64
        
        # ethiopic_to_jdn
        self._lib.ethiopic_to_jdn.argtypes = [c_int32, c_int32, c_int32, c_int64]
        self._lib.ethiopic_to_jdn.restype = c_int64
        
        # jdn_to_gregorian
        self._lib.jdn_to_gregorian.argtypes = [c_int64]
        self._lib.jdn_to_gregorian.restype = DateStruct
        
        # jdn_to_ethiopic
        self._lib.jdn_to_ethiopic.argtypes = [c_int64, c_int64]
        self._lib.jdn_to_ethiopic.restype = DateStruct
        
        # ethiopic_to_gregorian
        self._lib.ethiopic_to_gregorian.argtypes = [c_int32, c_int32, c_int32, c_int64]
        self._lib.ethiopic_to_gregorian.restype = DateStruct
        
        # gregorian_to_ethiopic
        self._lib.gregorian_to_ethiopic.argtypes = [c_int32, c_int32, c_int32]
        self._lib.gregorian_to_ethiopic.restype = DateStruct
        
        # guess_era
        self._lib.guess_era.argtypes = [c_int64]
        self._lib.guess_era.restype = c_int64

# Global library instance
_lib = None

def _get_lib() -> EthiopicCalendarLib:
    """Get or create the library instance."""
    global _lib
    if _lib is None:
        _lib = EthiopicCalendarLib()
    return _lib

# Constants
JD_EPOCH_OFFSET_AMETE_ALEM = -285019
JD_EPOCH_OFFSET_AMETE_MIHRET = 1723856
JD_EPOCH_OFFSET_GREGORIAN = 1721426

def ethiopic_to_gregorian(year: int, month: int, day: int, era: Optional[int] = None) -> Dict[str, int]:
    """
    Convert Ethiopian date to Gregorian date.
    
    Args:
        year: Ethiopian year
        month: Ethiopian month (1-13)
        day: Ethiopian day (1-30, or 1-6 for Pagume)
        era: Ethiopian era (optional, auto-detected if None)
    
    Returns:
        Dictionary with 'year', 'month', 'day' keys
    
    Raises:
        ValueError: If the Ethiopian date is invalid
    """
    lib = _get_lib()
    
    if not lib._lib.is_valid_ethiopic_date(year, month, day):
        raise ValueError(f"Invalid Ethiopian date: {year}-{month}-{day}")
    
    if era is None:
        jdn = lib._lib.ethiopic_to_jdn(year, month, day, JD_EPOCH_OFFSET_AMETE_MIHRET)
        era = lib._lib.guess_era(jdn)
    
    result = lib._lib.ethiopic_to_gregorian(year, month, day, era)
    return {
        "year": result.year,
        "month": result.month,
        "day": result.day
    }

def gregorian_to_ethiopic(year: int, month: int, day: int) -> Dict[str, int]:
    """
    Convert Gregorian date to Ethiopian date.
    
    Args:
        year: Gregorian year
        month: Gregorian month (1-12)
        day: Gregorian day
    
    Returns:
        Dictionary with 'year', 'month', 'day' keys
    
    Raises:
        ValueError: If the Gregorian date is invalid
    """
    lib = _get_lib()
    
    if not lib._lib.is_valid_gregorian_date(year, month, day):
        raise ValueError(f"Invalid Gregorian date: {year}-{month}-{day}")
    
    result = lib._lib.gregorian_to_ethiopic(year, month, day)
    return {
        "year": result.year,
        "month": result.month,
        "day": result.day
    }

def is_valid_ethiopic_date(year: int, month: int, day: int) -> bool:
    """Check if an Ethiopian date is valid."""
    lib = _get_lib()
    return lib._lib.is_valid_ethiopic_date(year, month, day)

def is_valid_gregorian_date(year: int, month: int, day: int) -> bool:
    """Check if a Gregorian date is valid."""
    lib = _get_lib()
    return lib._lib.is_valid_gregorian_date(year, month, day)

def is_gregorian_leap(year: int) -> bool:
    """Check if a Gregorian year is a leap year."""
    lib = _get_lib()
    return lib._lib.is_gregorian_leap(year)

def ethiopic_to_jdn(year: int, month: int, day: int, era: Optional[int] = None) -> int:
    """Convert Ethiopian date to Julian Day Number."""
    lib = _get_lib()
    
    if era is None:
        era = JD_EPOCH_OFFSET_AMETE_MIHRET
    
    return lib._lib.ethiopic_to_jdn(year, month, day, era)

def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """Convert Gregorian date to Julian Day Number."""
    lib = _get_lib()
    return lib._lib.gregorian_to_jdn(year, month, day)

def jdn_to_ethiopic(jdn: int, era: Optional[int] = None) -> Dict[str, int]:
    """Convert Julian Day Number to Ethiopian date."""
    lib = _get_lib()
    
    if era is None:
        era = JD_EPOCH_OFFSET_AMETE_MIHRET
    
    result = lib._lib.jdn_to_ethiopic(jdn, era)
    return {
        "year": result.year,
        "month": result.month,
        "day": result.day
    }

def jdn_to_gregorian(jdn: int) -> Dict[str, int]:
    """Convert Julian Day Number to Gregorian date."""
    lib = _get_lib()
    result = lib._lib.jdn_to_gregorian(jdn)
    return {
        "year": result.year,
        "month": result.month,
        "day": result.day
    }

def get_day_of_week(jdn: int) -> int:
    """
    Get day of week from Julian Day Number.
    
    Returns:
        0=Monday, 1=Tuesday, ..., 6=Sunday
    """
    return int(jdn % 7)
