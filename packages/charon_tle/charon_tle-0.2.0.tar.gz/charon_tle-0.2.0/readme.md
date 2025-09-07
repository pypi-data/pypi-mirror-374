# Charon

A Python tool for downloading and processing TLE (Two-Line Element) data from CelesTrak.

## Features

- Download TLE data from CelesTrak for various satellite constellations
- Extract catalog IDs from TLE data
- Filter satellites with DTC (Direct to Cell) capability
- Filter TLE data by specific catalog IDs
- Support for custom URLs
- Command-line interface and Python API

## Installation

```bash
pip install charon_tle
``` 

# Quick Start

# Python API Usage

```python
from charon import CharonTLE

# Initialize
charon = CharonTLE()

# Download TLE data
tle_content = charon.download_tle('starlink')

# Extract all catalog IDs
cat_ids = charon.extract_catid(tle_content)
print(f"Found {len(cat_ids)} satellites")

# Extract DTC catalog IDs
dtc_ids = charon.extract_catid(tle_content, keyword='DTC')  
print(f"Found {len(dtc_ids)} DTC satellites")

# Filter by catalog IDs
filtered_tle = charon.filter_tle_by_catid(tle_content, ['58705', '58706'])

# Save to file
charon.save_tle(filtered_tle, 'filtered.tle')

# Use custom URL
custom_tle = charon.download_tle('custom', 
    custom_url='https://celestrak.org/NORAD/elements/gp.php?GROUP=oneweb&FORMAT=tle')
print(custom_tle)
```

# dev 

```bash
uv add --dev pytest pytest-cov black isort flake8
```
