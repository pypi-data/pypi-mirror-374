# Sentinel-2 Band Downloader

## Overview

Sentinel-2 Band Downloader is a simple Python package that allows users to download individual bands from Sentinel-2 satellite data.

This package simplifies the process of connecting to the Sentinel API, retrieving product information, creating output folders, obtaining band links, and downloading bands.

## Installation

### Using pip

You can install the package using `pip`:

```bash
pip install Sentinel_2_band_downloader
```

### Clone repository
git clone https://github.com/beatriznattrodtdavila/Sentinel_2_band_downloader.git
cd Sentinel_2_band_downloader
pip install -e .

## Example

```python
# Import the Sentinel2_Band_Downloader class
from scr.main.sentinel_2_band_downloader import Sentinel2_Band_Downloader

# Initialize the downloader with log and output paths (replace "/path/to/output")
downloader = Sentinel2_Band_Downloader(output_base_path="/path/to/output")

# Connect to the Copernicus API (replace 'your_username' and 'your_password')
access_token, refresh_token, dt_access_token = sentinel_downloader.connect_to_api(username, password)

# Construct a query for Sentinel-2 products
""" The parameters must be like:
        footprint: str
            The spatial geometry (POLYGON) of the area of interest.
        start_date: str
            The start date for the time range of interest in the format 'YYYY-MM-DD'.
        end_date: str
            The end date for the time range of interest in the format 'YYYY-MM-DD'.
        cloud_cover_percentage: str
            The maximum allowable cloud cover percentage.
        type: str or list
            Type of MSI to download
        platform_name: str, optional
            The name of the Sentinel platform (default: 'SENTINEL-2').
"""
query_params = downloader.construct_query(footprint="your_footprint", start_date="start_date", 
                                          end_date="end_date", cloud_cover_percentage="cloud_cover", 
                                          type="your_type", platform_name="your_platform_name")


# Write the bands to download
bands_dict = {"L1C":["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12", "TCI"],
                  "L2A":{"10m": ["AOT", "B02", "B03", "B04", "B08", "TCI", "WVP"],
                  "20m": ["AOT","B01", "B02", "B03", "B04", "B05","B06", "B07", "B8A", "B11", "B12", "SCL", "TCI", "WVP"],
                  "60m": ["AOT","B01", "B02", "B03", "B04", "B05","B06", "B07", "B8A", "B09","B11", "B12", "SCL", "TCI", "WVP"]}}

# Download Sentinel2 Bands
downloader.download_sentinel2_bands(access_token, filter_list, bands_dict, dt_access_token, refresh_token, None)
```