import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

# Reading in the data from the path
data = pd.read_csv('./input/points_ppi.csv')

# Clean data
# Remove all missing data in rows (reagardless which one of value is missing lon, lat or ppi=
data_clean = data.dropna()
# Remove all outliers from PPI since
data_clean = data_clean[data_clean['ppi'] < 1]

# Read lon,lat and ppi values
x = data_clean['lon']
y = data_clean['lat']
z = data_clean['ppi']

# Define grid on which interpolation will be applied
xi,yi = np.meshgrid(np.linspace(min(x), max(x), 250),np.linspace(min(y), max(y), 250))

# Interpolate over xi,yi  using known data x,y and z values . We used cubic spline method for
# interpolation
zi = griddata((x, y), z, (xi, yi), method='cubic')

# Plot the results on contourf grid
cs =plt.contourf(xi, yi, zi , cmap="jet")
# Scatter plot of the points that make up the contour
plt.scatter(x, y, zorder=4, color='black', s=1)
# Labels and title
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Interpolation (cubic method) of PPI over study area ')
# Add colorbars
plt.colorbar(cs)
#plt.show()
# Save the figure
plt.savefig('./output/ppi_interpolation.png')
