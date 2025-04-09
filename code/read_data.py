
# Import all necessary libraries
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal_array
from shapely.geometry import Polygon
import rasterio.features
import rasterstats
import pandas as pd


# Reading in the data from the path
data = pd.read_csv('./input/points_ppi.csv')

# Clean data
# Remove all missing data in rows (regardless which one of value is missing lon, lat or ppi)
data_clean = data.dropna()
# Remove all outliers from PPI since
data_clean = data_clean[data_clean['ppi'] < 1]

# Convert from WGS84 to HRTS3765
ppi_points = gpd.GeoDataFrame(data_clean, crs='epsg:4326', geometry=gpd.points_from_xy(data_clean.lon, data_clean.lat))
ppi_points = ppi_points.to_crs('EPSG:3765')
ppi_points.to_file(filename='ppi_points.shp', driver="ESRI Shapefile")

# Create polygon from coordinates (lon, lat) with external bounderies (using convex_hull function)
polygon_geom = Polygon(zip(data_clean["lon"], data_clean["lat"], data_clean['ppi'])).convex_hull
polygon_geom = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygon_geom])
# Convert from 4326(WGS) to 3765 (HTRS96)
polygon_geom = polygon_geom.to_crs('EPSG:3765')

# Save to shape file
polygon_geom.to_file(filename='ppi_polygon.shp', driver="ESRI Shapefile")

# name of our source image
src = "./input/sentinel-2.tif"

# load the source image into an array
arr = gdal_array.LoadFile(src)

# Open the raster data
ndi = rasterio.open('ndi_enhancened_sentinel_image.tif')

# Extract raster pixel (sentinel RGB image) using PPI locations from csv file
result1 = rasterstats.point_query(ppi_points.geometry, ndi.read(1),nodata = ndi.nodata, affine = ndi.transform,  interpolate='nearest')

# Remove outliers from data
ppi_points['ndi'] = result1
ppi_points = ppi_points[ppi_points['ndi'] < 230]
# Prepare the data
x = ppi_points['ndi']
y = ppi_points['ppi']

# Plot NDI VS PPI
plt.plot(x,y,'*')
plt.xlabel('$Normalized$ $Difference$ $Index$')
plt.ylabel('$Plant$ $Phenology$ $Index$')
plt.savefig('ndi_ppi.png')
