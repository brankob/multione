 # Load you remote sensing image
src = "sentinel_2.tif"
# Read image file
img = cv2.imread(src, cv2.IMREAD_COLOR)
# Read all metadata necessary to use for writing in final (output file) ie. coordinates, CRS
dataset1 = gdal.Open(src)
projection = dataset1.GetProjection()
geotransform = dataset1.GetGeoTransform()

#Convert from RGB to greyscale for applying CLAHE
img = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)
# Apply CLAHE filter to greyscale image
clahe = cv2.createCLAHE(clipLimit=5,tileGridSize=(8,8))
# On the 0 to 'L' channel, 1 to 'a' channel, and 2 to 'b' channel
img[:,:,0] = clahe.apply(img[:,:,0])

# Convert from greyscale to RGB
enhanced_image = cv2.cvtColor(img, cv2.COLOR_Lab2RGB)
# Output file
out_file='enhancened_sentinel_image.tif'
# Write file
cv2.imwrite(out_file,enhanced_image)
# Add all necessary info to geotif file i.e  coordinates, CRS
dataset2 = gdal.Open(out_file, gdal.GA_Update)
dataset2.SetGeoTransform( geotransform )
dataset2.SetProjection( projection )
