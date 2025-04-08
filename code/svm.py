import fiona
import rasterio as rio
import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import  matplotlib.pyplot as plt
import seaborn as sns

#Input files
raster_loc = "enhancened_sentinel_image.tif"
# Vector data with PPI points
points_loc = "ppi_points.shp"
# Temporary shape file
temp_point_loc = "temp_y_points.shp"
# Define distinct classes for PPI
lulc_name = ['1', '2', '3', '4','5']

# Read bands from input raster
with rio.open(raster_loc) as img:
    bands = img.count
#print("bands of input image:", bands)

# Create a list of feature names
features = ["band" + str(i) for i in range(1,bands+1)]
print('Bands names:', features)
f_len=len(features)

#Read points from shapefile
points = gpd.read_file(points_loc)

# Add a new column "id" with range of points
points['id'] = range(len(points))
# Save the new point file with 'id'
points.to_file(temp_point_loc)

# Converts GetDataFrame to DataFrame and remove the 'geometry' column
points_df = pd.DataFrame(points.drop(columns='geometry'))
#Initialize an empty DataFrame to store sampled values
sampled = pd.DataFrame()

#Read input shapefile with Fiona and iterate over each feature
with fiona.open(temp_point_loc) as shp:
    for feature in shp:
        #print(feature)
        siteID = feature['properties']['ppi']
        coords = feature['geometry']['coordinates']
        # Read pixel values at the given coordinates using Rasterio
        with rio.open(raster_loc) as stack_src:
            values = [v for v in stack_src.sample([coords])]

        # Create a temporary DataFrame for the sampled values
        temp_df = pd.DataFrame(values, columns=features)
        # Set PPI data into five clasess for easier  interpretation of data
        if (siteID <= 0.2):                      # IF PPI is smaller and equal 0.2 then put into 1 class
            temp_df['id'] = 1
        elif ((siteID > 0.2) and (siteID <= 0.4)):# IF PPI is greater then 0.2 and smaller then 0.4 put into 2 class
            temp_df['id'] = 2
        elif ((siteID > 0.4) and (siteID <= 0.6)):# IF PPI is greater then 0.4 and smaller then 0.6 put into 3 class
            temp_df['id'] = 3
        elif ((siteID > 0.6) and (siteID <= 0.8)):# IF PPI is greater then 0.6  and smaller then 0.8 put into 4 class
            temp_df['id'] = 4
        else:
            temp_df['id'] = 5   # IF PPI is greater then 0.8 put into 5 class
        sampled = sampled._append(temp_df, ignore_index=True)

# Split the data into features (X) and labels (Y)
X = np.ravel(sampled.iloc[:,:f_len].values)
Y = np.round(np.tile(np.ravel(sampled.iloc[:,f_len:4].values),3))

# Split the data into training and testing sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.35, stratify=Y)

# Initialize and train a SVM classifier
clf = SVC(kernel='rbf')

#Reshape train and test data to 2d array
X_train = X_train.reshape(-1, 1)
Y_train = Y_train.reshape(-1, 1)
X_test = X_test.reshape(-1, 1)
Y_train = Y_train.reshape(-1, 1)

# Fit train data
clf.fit(X_train, Y_train)

#Make predictions on the test data
Y_pred = clf.predict(X_test)

# Evaluate the classifier performance
accuracy = accuracy_score(Y_test, Y_pred)
# Generate report
report = classification_report(Y_test, Y_pred)
# Generate confusion matrix
confusion = confusion_matrix(Y_test, Y_pred)

# Print evaluation data
print(f"Accuracy: {accuracy * 100: .2f}%")
# print(report)
print("Confusion Matrix:\n", confusion)

# Plot the confusion matrix
cm_percent = confusion / np.sum(confusion)
plt.figure(figsize=(7,7), facecolor ='w', edgecolor='k')
sns.set(font_scale=1.5)
sns.heatmap(cm_percent, xticklabels=lulc_name, yticklabels=lulc_name, cmap="jet", annot=True, fmt='.2%',
           cbar=False, linewidths=2,linecolor='black')
plt.title('SVM')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()


#######        This part of the procedure is used for saving classified data in GeoTiff format   ########## 
"""
# Export the prediction results as geotiff file
out_file = "svm.tif"

# Resize original geotif to smaller resolution otherwise prediction model consume large amount of time
# We reduced resolution from X=Y=>30m to X=Y=>100m per cell
# Define name of new raster file with resolution 100mX100m
raster_loc = 'output_small_res.tif'
gdal.Warp('output_small_res.tif', raster_loc, xRes=100, yRes=100)

# Read all necessary information from geotif for analyzing and saving into file
with rio.open(raster_loc) as img:
    img_arr = img.read()
    bands = img_arr.shape[0]
    height, width = img_arr.shape[1], img_arr.shape[2]
    crs = img.crs
    transform = img.transform

#Reshape the input data for prediction
img_n = np.moveaxis(img_arr,0 , -1)
img_n = img_n.reshape(-1, f_len)
img_n = img_n.reshape(-1, 1)

# Perform predictions o the entire raster
pred_full = clf.predict(img_n)

# Reshape prediction data into geotiff f
img_reshape = pred_full.reshape( height, width, f_len)
img_reshape = np.moveaxis(img_reshape,-1 , 0)

#Export the results
out_raster = rio.open(out_file, 'w',driver='GTiff', height=height, width=width, count=3,
                      dtype='uint8', crs=crs, transform=transform, nodata=255)
out_raster.write(img_reshape)
out_raster.close()

"""
