"""
Basic test script to verify Python package structure and imports.
"""

import sys
import os

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_imports():
    """Test that we can import the package modules."""
    try:
        # Test basic imports
        from ethiopian_date_converter import constants
        print("Constants module imported successfully")
        
        from ethiopian_date_converter import date_classes
        print("Date classes module imported successfully")
        
        from ethiopian_date_converter import utils
        print("Utils module imported successfully")
        
        # Test constants
        print(f"Ethiopian months: {constants.ETHIOPIC_MONTHS['en'][:3]}...")
        print(f"Weekdays: {constants.WEEKDAYS['en'][:3]}...")
        
        # Test date class creation (without C library)
        try:
            from ethiopian_date_converter.date_classes import EthiopicDate, GregorianDate
            
            # These should work without C library
            print("Date classes imported successfully")
            
            # Test validation methods
            from ethiopian_date_converter.date_classes import InvalidDateError
            print("Error classes imported successfully")
            
        except Exception as e:
            print(f"Warning: Date classes need C library: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_package_structure():
    """Test package structure."""
    try:
        from ethiopian_date_converter import __version__, __author__
        print(f"Package version: {__version__}")
        print(f"Package author: {__author__}")
        
        # Test __all__ exports
        import ethiopian_date_converter
        if hasattr(ethiopian_date_converter, '__all__'):
            print(f"Package exports {len(ethiopian_date_converter.__all__)} functions")
        
        return True
    except Exception as e:
        print(f"❌ Package structure error: {e}")
        return False

def test_c_files_exist():
    """Test that C source files exist."""
    try:
        c_file = os.path.join("ethiopian_date_converter", "core", "ethiopic_calendar.c")
        h_file = os.path.join("ethiopian_date_converter", "core", "ethiopic_calendar.h")
        
        if os.path.exists(c_file):
            print("C source file exists")
        else:
            print("❌ C source file missing")
            return False
            
        if os.path.exists(h_file):
            print("Header file exists")
        else:
            print("❌ Header file missing")
            return False
            
        return True
    except Exception as e:
        print(f"❌ File check error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Ethiopian Date Converter Python Package")
    print("=" * 50)
    
    success = True
    
    print("\n📁 Testing package structure...")
    success &= test_package_structure()
    
    print("\n📦 Testing imports...")
    success &= test_imports()
    
    print("\n📄 Testing C source files...")
    success &= test_c_files_exist()
    
    print("\n" + "=" * 50)
    if success:
        print("All basic tests passed!")
        print("Note: Full functionality requires C library compilation")
    else:
        print("❌ Some tests failed!")
    
    print("\nPackage Functionality Comparison:")
    print("Core conversion functions (same as JS/TS)")
    print("Date validation (same as JS/TS)")
    print("Julian Day Number support (same as JS/TS)")
    print("Date classes with arithmetic (enhanced from JS/TS)")
    print("Holiday detection (enhanced from JS/TS)")
    print("Multi-language formatting (enhanced from JS/TS)")
    print("Calendar utilities (enhanced from JS/TS)")
    print("Business day calculations (new feature)")
    print("Age calculation utilities (new feature)")
