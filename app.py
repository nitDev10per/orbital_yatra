import pystac_client
import planetary_computer
import odc.stac
import matplotlib.pyplot as plt
from pystac.extensions.eo import EOExtension as eo
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from flask_cors import CORS
import json
import os
import io
import geopandas as gpd
import shapely.geometry
import pandas as pd
from datetime import datetime, timedelta

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

## INPUTS : coordinate, start_date, end_date, cloud_cover 
app = Flask(__name__)
CORS(app, resources={r"/fetch": {"origins": "http://127.0.0.1:5500"}})  # Allow only this specific origin


@app.route('/')
def default_route():
    return redirect(url_for('index'))
    
@app.route('/request/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        coordinates = json.loads(request.form['coordinates']);
        start_date = request.form.get('start_date');
        end_date = request.form.get('end_date');
        cloud_cover = json.loads(request.form['cloud_cover'])*100;
        
        print('Coordinates: ',coordinates)
        print('Cloud_cover request:',cloud_cover)
        print('Start date: ',start_date)
        print('Date type: ', type(start_date))
        print('CC type:',type(cloud_cover))
        
        def create_bounding_box(coordinates, width=0.05, height=0.05):
            lat, lon = coordinates
            
            # Calculate the bounding box
            # bbox = [
            #     lon - width / 2,  # Min longitude
            #     lat - height / 2,  # Min latitude
            #     lon + width / 2,  # Max longitude
            #     lat + height / 2   # Max latitude
            # ]
            bbox = [
                lon - width / 2,  # Min longitude
                lat - height / 2,  # Min latitude
                lon + width / 2,  # Max longitude
                lat + height / 2   # Max latitude
            ]
            return bbox
        
        # Define the coordinate
        #coordinates = [47.43405, -123.390455]  # [latitude, longitude]

        # Create the bounding box
        bounding_box = create_bounding_box(coordinates)
        print(bounding_box)

        bbox_of_interest = bounding_box # [-122.2751, 47.5469, -121.9613, 47.7458]
       # bbox_of_interest =[-122.2751, 47.5469, -121.9613, 47.7458]
        time_of_interest = f"{start_date}/{end_date}" #"2021-01-01/2023-12-31"
        
        lat, lon = coordinates
        
        # Define the relative path (e.g., "static/images/your_image.tiff")
        relative_path = "static/WRS2_descending_0/"
        
        # Get the absolute path by joining Flask's root directory and the relative path
        absolute_path = os.path.join(app.root_path, relative_path)
        
        # Ensure the directory exists
        os.makedirs(absolute_path, exist_ok=True)
        
        file_name = 'WRS2_descending.shp'
         
        # Load shapefile using geopandas
        shapefile = os.path.join(absolute_path, file_name)
        wrs = gpd.read_file(shapefile)
        
        point = shapely.geometry.Point(lon, lat)
        mode = 'D'

        # Function to check if a point is within a geometry and matches the mode
        def checkPoint(row, point, mode):
            if point.within(row.geometry) and row['MODE'] == mode:
                return True
            else:
                return False

        # Filter rows based on the point and mode
        matching_features = wrs[wrs.apply(lambda row: checkPoint(row, point, mode), axis=1)]

        if not matching_features.empty:
            wrs_path = (matching_features.iloc[0]['PATH'])
            wrs_row = (matching_features.iloc[0]['ROW'])
            print('Path: ', wrs_path, 'Row: ', wrs_row)
        else:
            print("No matching features found in the WRS-2 grid")    
        
        row_wrs = str(wrs_row).zfill(3)
        path_wrs = str(wrs_path).zfill(3)

        # print(row_wrs, path_wrs)
        search_l8 = catalog.search(
            collections=["landsat-c2-l2"],
            bbox=bbox_of_interest,
            datetime=time_of_interest,
            query = {
                        "eo:cloud_cover": {"lt": 30},
                        "platform": {"eq": "landsat-8"},
                        "landsat:wrs_path": {"eq": f"{path_wrs}"},
                        "landsat:wrs_row": {"eq": f"{row_wrs}"}}
        )
        items = search_l8.item_collection()
        # print(f"Returned {len(items)} Items")

        selected_item_l8 = max(items, key=lambda item: item.datetime) #and min(items, key=lambda item: eo.ext(item).cloud_cover)
            
        search_l9 = catalog.search(
            collections=["landsat-c2-l2"],
            bbox=bbox_of_interest,
            datetime=time_of_interest,
            query = {
                        "eo:cloud_cover": {"lt": 30},
                        "platform": {"eq": "landsat-9"},
                        "landsat:wrs_path": {"eq": f"{path_wrs}"},
                        "landsat:wrs_row": {"eq": f"{row_wrs}"}}
        )
        items = search_l9.item_collection()
        # print(f"Returned {len(items)} Items")

        selected_item_l9 = max(items, key=lambda item: item.datetime) #and min(items, key=lambda item: eo.ext(item).cloud_cover)
        
        # Compare the dates and select the item with the latest date
        if selected_item_l9.datetime.date() > selected_item_l8.datetime.date():
            selected_item = selected_item_l9
        else:
            selected_item = selected_item_l8

        print(
            f"Choosing {selected_item.id} from {selected_item.datetime.date()}"
            + f" with {selected_item.properties['eo:cloud_cover']}% cloud cover"
        )

        import requests
        # Download the file
        response = requests.get(selected_item.assets['mtl.xml'].href)
        
        # Define the relative path (e.g., "static/images/your_image.tiff")
        relative_path = "static/Metadata/"
        
        # Get the absolute path by joining Flask's root directory and the relative path
        absolute_path = os.path.join(app.root_path, relative_path)
        
        # Ensure the directory exists
        os.makedirs(absolute_path, exist_ok=True)
        
        file_name = 'mtl.xml'
        
        file_path = os.path.join(absolute_path, file_name)
        
        if response.status_code == 200:
            # Save the file locally
            output_path = file_path  # Specify your desired output path
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print("Metadata file saved")
        else:
            print('Error saving metadata file')
        
        # Extracting WRS-2 Extent shapefile
        def extract_features_to_geojson(shapefile_path, row_value, path_value, output_geojson):
            # Load the shapefile
            gdf = gpd.read_file(shapefile_path)

            # Filter the GeoDataFrame based on ROW and PATH values
            filtered_gdf = gdf[(gdf['ROW'] == row_value) & (gdf['PATH'] == path_value)]

            # Check if any features were found
            if filtered_gdf.empty:
                print("No features found with the specified ROW and PATH values.")
                return

            # Save the filtered features to a GeoJSON file
            filtered_gdf.to_file(output_geojson, driver='GeoJSON')
            print(f"Extracted features saved to {output_geojson}")

        # Example usage
        row_value = wrs_row  # Replace with the desired ROW value
        path_value = wrs_path  # Replace with the desired PATH value
        
        # Define the relative path (e.g., "static/images/your_image.tiff")
        relative_path = "static/Footprint/"
        
        # Get the absolute path by joining Flask's root directory and the relative path
        absolute_path = os.path.join(app.root_path, relative_path)
        
        # Ensure the directory exists
        os.makedirs(absolute_path, exist_ok=True)
        
        file_name = 'wrs2_extent.geojson'
         
        # Load shapefile using geopandas
        output_footprint_geojson = os.path.join(absolute_path, file_name)# Output GeoJSON path

        extract_features_to_geojson(shapefile, row_value, path_value, output_footprint_geojson)

        ## Extracting landsat passes date and time
        
        import pandas as pd
        from datetime import datetime, timedelta

        # Extract the initial date, time, and platform
        initial_date = selected_item.datetime.date()
        initial_time = str(selected_item.datetime).split(' ')[1].split('.')[0]
        initial_platform = selected_item.properties['platform']

        # Create lists to hold the data
        dates = []
        times = []
        platforms = []

        # Add the first entry
        dates.append(initial_date)
        times.append(initial_time)
        platforms.append(initial_platform)

        # Determine the next platform based on the initial one
        next_platform = 'landsat-8' if initial_platform == 'landsat-9' else 'landsat-9'

        # Generate additional entries
        num_entries = 20  # Adjust the number of entries as needed
        for i in range(1, num_entries):
            # Add 8 days to the date
            new_date = initial_date + timedelta(days=i * 8)
            dates.append(new_date)
            
            # Keep the same time
            times.append(initial_time)
            
            # Alternate the platform
            platforms.append(next_platform)
            # Switch to the other platform for the next iteration
            next_platform = 'landsat-8' if next_platform == 'landsat-9' else 'landsat-9'


        # Create a DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Time (+/- 00:15:00 hrs in UTC)': times,
            'Platform': platforms
        })

        # Print the resulting DataFrame
        # print(df)

        # Get the current date
        current_date = datetime.now().date()

        # Filter the DataFrame for dates after the current date
        filtered_df = df[df['Date'] >= current_date]

        # Print the filtered DataFrame
        print(filtered_df)

        ## Tiles url

        response = requests.get(selected_item.assets['tilejson'].href)

        decoded_response = response.content.decode('utf-8')

        response_dict = json.loads(decoded_response)
        tile_url = response_dict['tiles'][0] # For Tile layer of the Landsat scene

        ## Getting the image and downloading it 

        bands_of_interest = ["red", "green", "blue", "nir08", "swir16", "swir22"]

        data = odc.stac.stac_load(
            [selected_item], bands=bands_of_interest, bbox=bbox_of_interest
        ).isel(time=0)

        # xarray_data = data[["red", "green", "blue"]].to_array()
        xarray_data = data[bands_of_interest].to_array()

        import xarray as xr
        import rioxarray
        
        epsg= selected_item.properties['proj:epsg']
        xarray_data.rio.write_crs(f"EPSG:{epsg}", inplace=True)
        
        # Define the relative path (e.g., "static/images/your_image.tiff")
        relative_path = "static/Image/"
        
        # Get the absolute path by joining Flask's root directory and the relative path
        absolute_path = os.path.join(app.root_path, relative_path)
        
        # Ensure the directory exists
        os.makedirs(absolute_path, exist_ok=True)
        
        file_name = 'output_image.tif'
        
        file_path = os.path.join(absolute_path, file_name)

        # Save the DataArray as a GeoTIFF
        xarray_data.rio.to_raster(file_path)
        print("Raster data saved")
        
        # Changing crs of the raster to EPSG:4326
        import rasterio
        from rasterio.warp import calculate_default_transform, reproject, Resampling

        def change_crs(input_tif, output_tif, target_crs='EPSG:4326'):
            with rasterio.open(input_tif) as src:
                print("CRS:", src.crs)
                # Calculate the transform and dimensions for the target CRS
                transform, width, height = calculate_default_transform(
                    src.crs, target_crs, src.width, src.height, *src.bounds
                )
                
                # Create metadata for the output file
                metadata = src.meta.copy()
                metadata.update({
                    'crs': target_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                
                # Write the reprojected data to the new file
                with rasterio.open(output_tif, 'w', **metadata) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs,
                            resampling=Resampling.nearest
                        )

        # Example usage
        input_tif = file_path
        
        # Define the relative path (e.g., "static/images/your_image.tiff")
        relative_path = "static/Image/"
        
        # Get the absolute path by joining Flask's root directory and the relative path
        absolute_path = os.path.join(app.root_path, relative_path)
        
        # Ensure the directory exists
        os.makedirs(absolute_path, exist_ok=True)
        
        file_name = 'output_image_epsg4326.tif'
        
        file_path = os.path.join(absolute_path, file_name)
        
        change_crs(input_tif, file_path)

        print(f"CRS changed to EPSG:4326 and saved to {file_path}.")
        
        
        ## CLIPPING THE RASTER TO GET THE 3*3 GRID
        from pyproj import Transformer
        from shapely.geometry import box
        import numpy as np
        
        def create_polygon(tif_path, coordinate):
            # Open the GeoTIFF image
            with rasterio.open(tif_path) as src:
                # Get the transform and CRS
                transform = src.transform
                crs = src.crs
                
                # Create a transformer to convert WGS 84 to the raster CRS
                transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
                transformed_coordinate = transformer.transform(coordinate[0], coordinate[1])
                
                # Convert the transformed coordinate to pixel indices
                col, row = ~transform * transformed_coordinate
                
                # Round to the nearest pixel index
                row = int(np.round(row))
                col = int(np.round(col))
                
                # Define the window for the 3x3 grid
                min_col = col - 1
                max_col = col + 2
                min_row = row - 1
                max_row = row + 2
                
                # Get the bounds of the bounding box in the raster CRS
                minx, miny = transform * (min_col, min_row)
                maxx, maxy = transform * (max_col, max_row)
                
                # Create a bounding box polygon
                polygon = box(miny, minx, maxy, maxx)
                
                return polygon, crs

        def save_polygon_to_shapefile(polygon, crs, output_shapefile):
            # Create a GeoDataFrame
            gdf = gpd.GeoDataFrame({'geometry': [polygon]}, crs=crs)
            
            # Save to shapefile
            gdf.to_file(output_shapefile)

        def clip_with_polygon(tif_path, shapefile_path, output_path):
            # Read the shapefile using geopandas
            gdf = gpd.read_file(shapefile_path)
            
            # Extract geometries
            shapes = [feature["geometry"] for feature in gdf.__geo_interface__['features']]

            # Open the raster file
            with rasterio.open(tif_path) as src:
                # Clip the raster using the polygon shapes
                out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
                
                # Update the metadata
                metadata = src.meta.copy()
                metadata.update({
                    'height': out_image.shape[1],
                    'width': out_image.shape[2],
                    'transform': out_transform
                })

                # Save the clipped raster to a new file
                with rasterio.open(output_path, 'w', **metadata) as dst:
                    dst.write(out_image)
        
        # file_name = 'output_image.tif'
        
        # file_path = os.path.join(absolute_path, file_name)
        tif_path = file_path
        
        # Define the relative path (e.g., "static/images/your_image.tiff")
        relative_path = "static/Image/"
        
        # Get the absolute path by joining Flask's root directory and the relative path
        absolute_path = os.path.join(app.root_path, relative_path)
        
        # Ensure the directory exists
        os.makedirs(absolute_path, exist_ok=True)
        
        file_name = 'clipped_3x3_polygon.shp'
        
        file_path = os.path.join(absolute_path, file_name)
        
        output_shapefile = file_path
        
        file_name = 'clipped_3x3_image.tif'
        file_path = os.path.join(absolute_path, file_name)
        
        output_path = file_path

        # Create polygon and save to shapefile
        polygon, crs = create_polygon(tif_path, coordinates)
        save_polygon_to_shapefile(polygon, crs, output_shapefile)

        # Clip raster using the polygon shapefile
        clip_with_polygon(tif_path, output_shapefile, output_path)

        print("Clipped raster image saved to:", output_path)
        
        ## EXTRACTING PIXEL VALUES as a DF
        from rasterio.windows import Window
        
        # Function to convert lat/long to pixel indices in the raster's coordinate system (CRS)
        def latlong_to_pixel(lon, lat, dataset):
            # Get the raster's CRS
            raster_crs = dataset.crs
            # Define the transformation from WGS84 (EPSG:4326) to the raster's CRS
            transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
            # Transform lat/lon to the raster's CRS
            lon, lat = transformer.transform(lon, lat)

            # Transform geographic coordinates to image coordinates (pixel indices)
            row, col = dataset.index(lon, lat)
            
            return row, col

        # Function to extract pixel values for all bands at a specific lat/long
        def extract_pixel_values(lat, lon, raster_file):
            # Open the raster file
            with rasterio.Env(GDAL_CACHEMAX=512):  # Set GDAL cache to 512 MB
                with rasterio.open(raster_file) as dataset:
                    # Convert latitude and longitude to row/column
                    try:
                        row, col = latlong_to_pixel(lon, lat, dataset)
                       
                        # Check if the row and column are within the valid range of the raster
                        if row < 0 or col < 0 or row >= dataset.height or col >= dataset.width:
                            raise IndexError("The latitude/longitude is outside the bounds of the raster image.")
                    except IndexError as e:
                        print(f"Error: {e}")
                        return None

                    # List to store the pixel values from all bands
                    pixel_values = []
                    
                    # Use a small window around the pixel to read only necessary data (1x1 window)
                    window = Window(col, row, 1, 1)

                    # Loop through all bands and extract the pixel value at (row, col)
                    for i in range(1, dataset.count + 1):  # Band indices start from 1
                        band_data = dataset.read(i, window=window)  # Read only the window (small area)
                        pixel_value = band_data[0, 0]  # Since window is 1x1, get the single value
                        pixel_values.append(pixel_value)
                     
                    # Create a DataFrame with band numbers and pixel values
                    band_names = ['Red (B4)','Green (B3)','Blue (B2)','NIR (B5)','SWIR-1 (B6)', 'SWIR-2 (B7)']
                    #band_names = [f'Band {i+1}' for i in range(len(pixel_values))]
                    # Specify the constants
                    multiply_constant = 0.0000275  # Example constant for multiplication
                    add_constant = -0.2      # Example constant for addition

                    # Modify pixel values by multiplying and adding the constants
                    modified_pixel_values = [(value * multiply_constant) + add_constant for value in pixel_values]

                    # Create a DataFrame with band numbers and modified pixel values
                    band_names = ['Red (B4)', 'Green (B3)', 'Blue (B2)', 'NIR (B5)', 'SWIR-1 (B6)', 'SWIR-2 (B7)']
                    
                    df = pd.DataFrame({'Band': band_names, 'Value': modified_pixel_values})
            
            return df

        pixel_df = extract_pixel_values(lat, lon, output_path)

        if pixel_df is not None:
            # Print the DataFrame with pixel values for each band
            print(f"Pixel values at Lat: {lat}, Long: {lon}")
            print(pixel_df)
        
        pass_dates_df_json = filtered_df.to_dict(orient='records')  
        pixel_df_json = pixel_df.to_dict(orient='records')  
        
        # Prepare the response
        
        # Define the relative path (e.g., "static/images/your_image.tiff")
        relative_path = "static/Metadata/"
        
        # Get the absolute path by joining Flask's root directory and the relative path
        absolute_path = os.path.join(app.root_path, relative_path)
        
        # Ensure the directory exists
        os.makedirs(absolute_path, exist_ok=True)
        
        file_name = 'mtl.xml'
        
        metadata_path = os.path.join(absolute_path, file_name)
        
        latest_pass_date = str(selected_item.datetime.date())
        latest_pass_platform = selected_item.properties['platform']
        
        response = {
            'pass_dates_landsat': pass_dates_df_json,
            'pixel_values_landsat': pixel_df_json,
            'tile_url':tile_url,
            'metadata_path': selected_item.assets['mtl.txt'].href,
            'latest_pass_date':latest_pass_date,
            'latest_pass_platform':latest_pass_platform
        }

        # Return the JSON response
        return jsonify(response)
    else:
        return render_template("index.html")     
    
if __name__ == "__main__":
    app.run(debug=True)