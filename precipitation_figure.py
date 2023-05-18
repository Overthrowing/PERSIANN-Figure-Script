# Plot generator for the PERSIANN database around the Houston area.
# Author: David Rodriguez Sanchez (david.rodriguez24@tamu.edu)
# Date: May 15 2023

import os

from netCDF4 import Dataset as netCDFFile
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs

from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

shp_name = os.path.join("Shapefile", "County.shp")

# The PERSIANN timestep from download.
timestep = 1

def read_NCDF4(filename):
    dataset = netCDFFile(filename, 'r')

    lon = dataset['lon'][:]
    lat = dataset['lat'][:]
    datetime = dataset['datetime'][:]

    precip = dataset['precip'][:]

    return (lon, lat, datetime, precip)


def plot_data(filename, params):
    data_lon, data_lat, data_datetime, data_precip = read_NCDF4(filename)
    for window in range(len(data_precip)):

        ax = plt.axes(projection=ccrs.PlateCarree())

        shape = ShapelyFeature(Reader(shp_name).geometries(), ccrs.PlateCarree(), facecolor='none')
        ax.add_feature(shape)
        ax.set_extent(
            [data_lon[0], data_lon[-1], data_lat[0], data_lat[-1]], # map region boundaries.
            crs=ccrs.PlateCarree()
        )

        # Creating grid lines
        grid_lines = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True)
        grid_lines.top_labels = False
        grid_lines.right_labels = False
        grid_lines.xformatter = LONGITUDE_FORMATTER
        grid_lines.yformatter = LATITUDE_FORMATTER

        plt.contourf(data_lon, data_lat, data_precip[window, :, : ], 60, cmap='plasma',
                 transform=ccrs.PlateCarree())

        cmap = mpl.cm.plasma
        bounds = [0, 10, 20, 30, 40, 50]

        plt.colorbar(mappable=mpl.cm.ScalarMappable(norm=mpl.colors.BoundaryNorm(bounds, cmap.N, extend='both'), cmap=cmap))

        plt.title(params['Title'] + f" ({(window * timestep * 60 * 60)}-{(window + 1) * timestep * 60 * 60} sec UTC)")

        if not os.path.exists(os.path.join("out", params['Date'])):
            os.mkdir(os.path.join("out", params['Date']))

        figure_out = os.path.join("out", params['Date'], f"{params['Date']}_{window * timestep}_{(window + 1) * timestep}")
        if not os.path.exists("out"):
            os.mkdir("out")

        plt.savefig(figure_out)
        plt.close()


# Change for the corresponding NCDF4 dataset.
filename = 'PERSIANN-files/PERSIANN_20230507/PERSIANN_2023-05-17080330pm.nc'

# Parameters to change the title and date of case.
params = {
    'Title' : 'May 07 Case',
    'Date'  : '20230507'
}

plot_data(filename, params)
print("Done.")
