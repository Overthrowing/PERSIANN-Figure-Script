# Plot generator for the PERSIANN database around the Houston area.
# Author: David Rodriguez Sanchez (david.rodriguez24@tamu.edu)
# Date: May 17 2023

import os

# Src dependencies.
import lightning_dependencies.prepare_chargepol as process_chargepol

# Other dependencies
from netCDF4 import Dataset as netCDFFile
import matplotlib.pyplot as plt
import matplotlib as mpl

import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from math import sqrt
from scipy.stats import gaussian_kde
import numpy as np

# Path to PERSIANN .nc file.
# Path to Chargepol .csv file
PERSIANN = "PERSIANN-20230407/PERSIANN_2023-05-17081150am.nc"
Chargepol = "Chargepol/chargepol_20230407.csv"

params = {
    "Filename": "lighning_precip_out",
    "Title"   : "April 07 2023 Case",
    "Date"    : "20230407"
}

def createLocationList(data):
    negPos = [[],[]] # Index 0 are all longitudes, index 1 are all latitudes
    posPos = [[],[]]

    for index, event in enumerate(data['Charge']):
        if(event[0] == 'pos'):
            posPos[0].append(float(data['Location'][index][0]))
            posPos[1].append(float(data['Location'][index][1]))
        else:
            negPos[0].append(float(data['Location'][index][0]))
            negPos[1].append(float(data['Location'][index][1]))

    return (negPos, posPos)

def process_persiann(persiann_filepath):
    dataset = netCDFFile(persiann_filepath, 'r')

    lon = dataset['lon'][:]
    lat = dataset['lat'][:]
    datetime = dataset['datetime'][:]

    precip = dataset['precip'][:]

    return (lon, lat, datetime, precip)


def plot(chp_data, params):
    data_lon, data_lat, data_datetime, data_precip = process_persiann(PERSIANN)

    # Rationing matplotlib figure.
    fig = plt.figure(figsize=(11.7, 8.3))
    spec = fig.add_gridspec(3, 2)

    # Lightning Histogram
    ax00 = fig.add_subplot(spec[0,0])
    ax00_1 = ax00.twinx()
    timepoints = list()
    linewidth = .1
    for index, time in enumerate(chp_data["Timestamp"]):
        charge = chp_data["Charge"][index][0]
        if charge.strip() == "pos":
            ax00.plot([time, time + .001],
                    [chp_data["Charge"][index][1], chp_data["Charge"][index][1] + chp_data["Charge"][index][2]],
                    color=[1, 0.062, 0.019, 0.7], linewidth=linewidth)
        # Plotting negative events.
        if charge.strip() == "neg":
            ax00.plot([time, time + .001],
                    [chp_data["Charge"][index][1], chp_data["Charge"][index][1] + chp_data["Charge"][index][2]],
                    color=[0.062, 0.019, 1, 0.7], linewidth=linewidth)
        timepoints.append(time)

    density = gaussian_kde(timepoints)
    density.covariance_factor = lambda: .25
    density._compute_covariance()
    xs = np.linspace(timepoints[0], timepoints[-1], len(timepoints))
    ax00_1.plot(xs, density(xs), color=[0, 0, 0], marker=',')
    # Hiding y-axis values
    ax00_1.set_yticks([])

    ax00.set(ylim=[0, 15])
    ax00.set(xlabel="Time after 0 UTC (sec)", ylabel="Altitude (km)")
    ax00.xaxis.tick_top()
    ax00.xaxis.set_label_position('top')
    ax00.set_title("Lightning Information")

    # PERSIANN Historgram
    ax01 = fig.add_subplot(spec[0,1])

    # Lightning Houston Map scatter
    ax10 = fig.add_subplot(spec[1:,0], projection=ccrs.PlateCarree())
    neg, pos = createLocationList(chp_data)

    county_lines = ShapelyFeature(Reader(shp_name).geometries(), ccrs.PlateCarree(),
                                           facecolor='none', edgecolor='black', lw=1)
    ax10.add_feature(county_lines)

    # Zoom in on the Houston area by setting longitude/latitude parameters
    ax10.set_extent(
        [-98, -92, 28, 32],
        crs=ccrs.PlateCarree()
    )

    ax10.scatter(x=pos[1], y=pos[0], s=4, linewidth=.5, color=[1, 0.062, 0.019, .5],
               marker='+', transform=ccrs.PlateCarree())
    ax10.scatter(x=neg[1], y=neg[0], s=4, linewidth=.5, color=[0.062, 0.019, 1, .5],
               marker='_', transform=ccrs.PlateCarree())

    gl = ax10.gridlines(crs=ccrs.PlateCarree(), draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    # PERSIANN Houston Map contour
    ax11 = fig.add_subplot(spec[1:,1], projection=ccrs.PlateCarree())


    shape = ShapelyFeature(Reader(shp_name).geometries(), ccrs.PlateCarree(), facecolor='none')
    ax11.add_feature(shape)
    ax11.set_extent(
        [data_lon[0], data_lon[-1], data_lat[0], data_lat[-1]],  # map region boundaries.
        crs=ccrs.PlateCarree()
    )

    for window in range(len(data_precip)):
        ax11.contourf(data_lon, data_lat, data_precip[window, :, :], 60, cmap='plasma',
                     transform=ccrs.PlateCarree())

    # Creating grid lines
    grid_lines = ax11.gridlines(crs=ccrs.PlateCarree(), draw_labels=True)
    grid_lines.top_labels = False
    grid_lines.left_labels = False
    grid_lines.xformatter = LONGITUDE_FORMATTER
    grid_lines.yformatter = LATITUDE_FORMATTER

    for city in cities:
        ax11.text(cities[city][1], cities[city][0], city, horizontalalignment='center', color='white',
                  transform=ccrs.PlateCarree())

    cmap = mpl.cm.plasma
    bounds = [0, 10, 20, 30, 40, 50]

    plt.colorbar(ax=ax11,
                 mappable=mpl.cm.ScalarMappable(norm=mpl.colors.BoundaryNorm(bounds, cmap.N, extend='both'),cmap=cmap),
                 orientation='horizontal')

    # Overall Figure information
    fig.suptitle(params["Title"])

    plt.savefig(os.path.join("out", params["Filename"] + params["Date"] + ".pdf"))

    plt.close(fig)

cities = {
    "Houston": [29.7604, -95.3698],
    "College Station": [30.6280, -96.3344],
    "Galveston": [29.3013, -94.7977],
    "Beaumont": [30.0802, -94.1266]
}
shp_name = os.path.join("Shapefile", "County.shp")
chp_data = process_chargepol.get_data(Chargepol)

plot(chp_data, params)
