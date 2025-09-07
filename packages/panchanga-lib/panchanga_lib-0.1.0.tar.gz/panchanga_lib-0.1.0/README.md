This is your project's main documentation, which will be displayed on PyPI and GitHub.

Markdown

# Panchanga Library

A simple, accurate, and easy-to-use Python library for Panchanga calculations.

## Dependencies

This library requires **pyswisseph**, a Python wrapper for the Swiss Ephemeris library. The core Swiss Ephemeris data files are also required.

## Installation

You can install `panchanga-lib` directly from PyPI using pip:

```bash
pip install panchanga-lib

To complete the setup, you must install the Swiss Ephemeris data files. On most Debian/Ubuntu-based systems, you can use:

Bash

sudo apt-get install libastro-swe-dev
For other operating systems, please refer to the pyswisseph documentation for instructions on how to set up the necessary ephemeris data.

Usage

from panchanga_lib import PanchangaEngine

# Create an instance for a specific location and timezone
# For example, Hyderabad, India
eng = PanchangaEngine(
    lat=17.3850, 
    lon=78.4867, 
    timezone="Asia/Kolkata", 
    masa_system="amanta"
)

# Get today's panchanga details
info = eng.get_now()

# Access the details
print(f"Today's Date and Time: {info.datetime}")
print(f"Weekday: {info.weekday_en}")
print(f"Tithi: {info.tithi_en} ({info.tithi_end_time})")
print(f"Nakshatra: {info.nakshatra_en} ({info.nakshatra_end_time})")


***

### 3. `panchanga-lib/src/panchanga_lib/__init__.py`
This file makes your directory a Python package and controls what is imported by default.

```python
from .panchanga import PanchangaEngine, PanchangaInfo