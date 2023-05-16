# Plot generator for the PERSIANN database ()
# Author: David Rodriguez Sanchez (david.rodriguez24@tamu.edu)
#
#

import os

from netCDF4 import Dataset as netCDFFile
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs

from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

shp_name = os.path.join("PERSIANN-20230427_00_21", "Shapefile", "County.shp")

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

        plt.title(params['Title'] + f"({(window * 3 * 60 * 60)}-{(window + 1) * 3 * 60 * 60} sec UTC)")
        figure_out = os.path.join("PERSIANN-20230427_00_21", "out", f"{params['Date']}_{window * 3}_{(window + 1) * 3}")
        plt.savefig(figure_out)
        plt.close()


# Change for the corresponding NCDF4 dataset.
filename = 'PERSIANN-20230427_00_21/PERSIANN_2023-05-11090801am.nc'

params = {
    'Title' : 'April 27 Case',
    'Date'  : '20230427'
}

plot_data(filename, params)
