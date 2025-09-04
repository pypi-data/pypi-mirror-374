"""
Setup script for ethiopian-date-converter package.
"""

import os
import platform
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import subprocess

# Read version from __init__.py
def get_version():
    with open(os.path.join("ethiopian_date_converter", "__init__.py"), "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

# Read README
def get_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Ethiopian calendar date conversion for Python"

class CustomBuildExt(build_ext):
    """Custom build extension to compile the C library."""
    
    def build_extensions(self):
        # Build the shared library first
        self.build_shared_library()
        super().build_extensions()
    
    def build_shared_library(self):
        """Build the shared C library."""
        c_file = os.path.join("ethiopian_date_converter", "core", "ethiopic_calendar.c")
        
        if not os.path.exists(c_file):
            raise FileNotFoundError(f"C source file not found: {c_file}")
        
        # Determine library name and compilation command
        system = platform.system().lower()
        if system == "windows":
            lib_name = "ethiopic_calendar.dll"
            compile_cmd = ["gcc", "-shared", "-fPIC", "-O3", "-o"]
        elif system == "darwin":
            lib_name = "libethiopic_calendar.dylib"
            compile_cmd = ["gcc", "-shared", "-fPIC", "-O3", "-o"]
        else:
            lib_name = "libethiopic_calendar.so"
            compile_cmd = ["gcc", "-shared", "-fPIC", "-O3", "-o"]
        
        lib_path = os.path.join("ethiopian_date_converter", "core", lib_name)
        
        # Skip if library already exists
        if os.path.exists(lib_path):
            return
        
        # Compile the library
        try:
            cmd = compile_cmd + [lib_path, c_file]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Successfully compiled {lib_name}")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to compile C library: {e}")
            print("The package will attempt to compile at runtime.")
        except FileNotFoundError:
            print("Warning: GCC not found. The package will attempt to compile at runtime.")

# Define package data to include C source files and compiled libraries
package_data = {
    "ethiopian_date_converter": [
        "core/*.c",
        "core/*.h",
        "core/*.dll",
        "core/*.so", 
        "core/*.dylib",
    ]
}

setup(
    name="ethiopian-date-converter-py",
    version=get_version(),
    author="Abiy",
    author_email="abiywondimu1@gmail.com",
    description="Ethiopian calendar date conversion for Python",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/abiywondimu5758/ethiopian-date-converter",
    project_urls={
        "Bug Reports": "https://github.com/abiywondimu5758/ethiopian-date-converter/issues",
        "Source": "https://github.com/abiywondimu5758/ethiopian-date-converter",
        "Documentation": "https://github.com/abiywondimu5758/ethiopian-date-converter/tree/main/docs/python",
    },
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Office/Business :: Scheduling",
    ],
    keywords=[
        "ethiopian", "calendar", "date", "conversion", "gregorian", 
        "geez", "python", "datetime", "ethiopia", "amharic"
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    cmdclass={
        "build_ext": CustomBuildExt,
    },
    zip_safe=False,  # Due to shared library
    license="MIT",
)
