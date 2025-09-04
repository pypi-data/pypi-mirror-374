from itertools import product
from scr.main.sentinel_2_band_downloader import Sentinel2_Band_Downloader

def main():
    # Specify the path where you want the log file to be created and the data saved
    output_base_path = "/home/beatriz/sentinel_lib/images"

    # Create an instance of Sentinel2_Band_Downloader
    sentinel_downloader = Sentinel2_Band_Downloader(output_base_path, False)

    # Call the connect_to_api method with your credentials
    username = "proj.pd.cpfl@gmail.com"
    password = "Dados_Sentinel2"
    access_token, refresh_token, dt_access_token = sentinel_downloader.connect_to_api(username, password)

    # Writing all filter necessary to search a product of Sentinel-2
    footprint = "POLYGON ((-51.306152 -29.850173, -51.308899 -30.095237, -51.056213 -30.11187, -51.04248 -29.857319, -51.306152 -29.850173))"
    start_date = "2023-01-01"
    end_date = "2023-01-07"
    cloud_cover = "20"
    type_str = "L2A"
    type_list = ["L1", "L2A"]
    platform_name = "SENTINEL-2"
    
    # filter_str = downloader.construct_query(footprint, start_date, end_date, cloud_cover, type_str, platform_name)
    filter_list = sentinel_downloader.construct_query(footprint, start_date, end_date, cloud_cover, type_str, platform_name)
    
    
    # Create a dict with the bands to download
    bands_dict = {"L1C":["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12", "TCI"],
                  "L2A":{"10m": ["AOT", "B02", "B03", "B04", "B08", "TCI", "WVP"],
                  "20m": ["AOT","B01", "B02", "B03", "B04", "B05","B06", "B07", "B8A", "B11", "B12", "SCL", "TCI", "WVP"],
                  "60m": ["AOT","B01", "B02", "B03", "B04", "B05","B06", "B07", "B8A", "B09","B11", "B12", "SCL", "TCI", "WVP"]}}
    
    # Download the data
    sentinel_downloader.download_sentinel2_bands(access_token, filter_list, bands_dict, dt_access_token, refresh_token, None)
    

if __name__ == "__main__":
    main()
    

    
