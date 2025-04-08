import rasterio

# Input image
image_file='enhancened_sentinel_image.tif'

# Load red, green nad blue bands
with rasterio.open(image_file) as src:
    band_red = src.read(1)
    band_green = src.read(2)
    band_blue = src.read(3)

#### Calculate the NDI  Normalized Difference Index (Perez, 2000) ####
ndi = 128 * ((band_green.astype(float) - band_red.astype(float)) / (band_green.astype(float) + band_red.astype(float))) + 1

####    Normalized Green-Red Difference Index (Hunt et al, 2005) ######
ngrdi = (band_green.astype(float) - band_red.astype(float)) / (band_green.astype(float) + band_red.astype(float)) * 100

#### Green leaf index (Sonnentag, O. et. al, 2012) ####
gli = (2 * band_green.astype(float)  - band_red.astype(float) - band_blue.astype(float)) / (2 * band_green.astype(float)  + band_red.astype(float) + band_blue.astype(float)) * 100

# Output NDI as GeoTiff
with rasterio.open('ndi_sentinel_image.tif','w',**src.meta) as dst:
    dst.write(ndi, 1)

# Output NGRDI as GeoTiff
with rasterio.open('ngrdi_sentinel_image.tif','w',**src.meta) as dst:
    dst.write(ngrdi,1)

# Output GLI as GeoTiff
with rasterio.open('gli_sentinel_image.tif','w',**src.meta) as dst:
    dst.write(gli, 1)

