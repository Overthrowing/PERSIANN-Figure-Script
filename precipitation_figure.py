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

from math import ceil

import glob
import contextlib
from PIL import Image
import re


import numpy as np
import datetime as dt

# Change for the corresponding NCDF4 dataset.
# filename = "Time Interval Test/PDIR-RECT-3hr-2017081700-2017081721/PDIR_2023-07-15035748pm.nc"
filename = "Time Interval Test/Test 2/PDIR-RECT-3hr-2021060100-2021080100/PDIR_2023-07-17101421am_202106.nc"
# filename ="Time Interval Test/PDIR-RECT-3hr-2017081700-2017081721/PDIR_2023-07-15035748pm.nc"

# Parameters to change the title and date of case.
params = {
    "Title": "Hurricane Nicholas data - PDIR",
    "Output-dir-name": "Test",
    "Date": "20210914-15",
}

# The PERSIANN timestep from download (number of hours in each window).
timestep = 3


def read_NCDF4(filename):
    dataset = netCDFFile(filename, "r")

    lon = dataset["lon"][:]
    lat = dataset["lat"][:]
    datetime = dataset["datetime"][:]

    precip = dataset["precip"][:]

    return (lon, lat, datetime, precip)


def plot_data(filename, params):
    data_lon, data_lat, data_datetime, data_precip = read_NCDF4(filename)

    # Grab the start date for the data from the user
    start_date = input(
        "Enter start date for the date (MM/DD) or press enter if this value is unknown: "
    )
    if start_date:
        start_date = dt.datetime.strptime(start_date, "%m/%d")

    # Calculate data for the histogram.
    precip_sums = [
        np.array(data_precip[window, :, :]).sum() for window in range(len(data_precip))
    ]
    total_precip = sum(precip_sums)

    times = [window * timestep * 60 * 60 for window in range(len(data_precip))]
    num_days = int((len(times) * timestep) / 24)

    # Plot data for each window.
    for window in range(len(data_precip)):
        # Create figure
        fig = plt.figure(figsize=(14, 4))
        ax1 = fig.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())
        ax2 = fig.add_subplot(1, 2, 2)
        # Create contour plot
        ax1.set_title(
            params["Title"]
            + f" ({(window * timestep * 60 * 60)}-{(window + 1) * timestep * 60 * 60} sec UTC)"
        )
        shape = ShapelyFeature(
            Reader(shp_name).geometries(), ccrs.PlateCarree(), facecolor="none"
        )
        ax1.add_feature(shape)
        ax1.set_extent(
            [
                data_lon[0],
                data_lon[-1],
                data_lat[0],
                data_lat[-1],
            ],  # map region boundaries.
            crs=ccrs.PlateCarree(),
        )

        # Creating grid lines
        grid_lines = ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True)
        grid_lines.top_labels = False
        grid_lines.right_labels = False
        grid_lines.xformatter = LONGITUDE_FORMATTER
        grid_lines.yformatter = LATITUDE_FORMATTER

        ax1.contourf(
            data_lon,
            data_lat,
            data_precip[window, :, :],
            60,
            cmap="plasma",
            transform=ccrs.PlateCarree(),
        )

        # Add colorbar
        cmap = mpl.cm.plasma
        bounds = [0, 10, 20, 30, 40, 50]
        plt.colorbar(
            mappable=mpl.cm.ScalarMappable(
                norm=mpl.colors.BoundaryNorm(bounds, cmap.N, extend="both"), cmap=cmap
            ),
            ax=ax1,
        )

        # Create histogram
        ax2.set_title(
            "Proportion of Percipitation over Time (Red Indicates Current Window)"
        )
        ax2.set_ylabel("Proportion of Precipitation")

        n, bins, patches = ax2.hist(
            times, bins=len(times), weights=precip_sums / total_precip
        )
        patches[window].set_facecolor("red")
        if num_days <= 2:
            ax2.set_xticks(
                np.arange(0, max(times), 3600 * 6),
                [f"{i}:00" for i in range(0, int(max(times) / 3600), 6)],
            )
            ax2.set_xlabel("Time Elapsed (Hours)")
        else:
            step = ceil(num_days / 9)
            days = list(range(0, num_days, step))
            if start_date:
                ax2.set_xticks(
                    np.arange(0, max(times), 3600 * 24 * step),
                    [
                        (start_date + dt.timedelta(days=i)).strftime("%m/%d")
                        for i in days
                    ],
                )
                ax2.set_xlabel("Date")
            else:
                ax2.set_xticks(
                    np.arange(0, max(times), 3600 * 24 * step),
                    [f"Day {i}" for i in days],
                )
                ax2.set_xlabel("Time Elapsed (Days)")

        # Generating the necessary directories.
        if not os.path.exists(os.path.join("out", params["Output-dir-name"])):
            os.mkdir(os.path.join("out", params["Output-dir-name"]))
        if not os.path.exists("out"):
            os.mkdir("out")

        fig.tight_layout()

        figure_out = os.path.join(
            "out",
            params["Output-dir-name"],
            f"[{window}] {params['Date']}_{window * timestep}_{(window + 1) * timestep}",
        )

        fig.savefig(figure_out, bbox_inches="tight")
        plt.close()
        print(f"Saved figure {figure_out}.")


def generate_gif(image_dir, output_file, frame_duration=0.3):
    with contextlib.ExitStack() as stack:
        # Lazily load images
        print(sorted(glob.glob(image_dir + "/*.png"), key=lambda x: int(re.search(r'\d+', x).group())))
        imgs = (
            stack.enter_context(Image.open(f))
            for f in sorted(glob.glob(image_dir + "/*.png"), key=lambda x: int(re.search(r'\d+', x).group()))
        )

        img = next(imgs)

        img.save(
            fp=output_file,
            format="GIF",
            append_images=imgs,
            save_all=True,
            duration=frame_duration * 1000,
            loop=0,
        )


shp_name = os.path.join("Shapefile", "County.shp")
#plot_data(filename, params)
generate_gif(
    os.path.join("out", params["Output-dir-name"]),
    os.path.join("out", f"{params['Date']}.gif"),
    0.3,
)
print("Done.")
