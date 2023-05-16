# PERSIANN-Figure-Script

**Dependencies**: Cartopy, Matplotlib, Python 3.10.

**Description**: Figure generator for the PERSIANN precipitation data set around the Houston area.

**Usage** ::
```
python precipitation_figure.py
```

The code itself does require some modifications to run smoothly. At the bottom of the script, one can modify the title, date, and directory path to the PERSIANN dataset.
```
# Change for the corresponding NCDF4 dataset.
filename = 'PERSIANN-20230427_00_21/PERSIANN_2023-05-11090801am.nc'

# Parameters to change the title and date of case.
params = {
    'Title' : 'April 27 Case',
    'Date'  : '20230427'
}
```

Apart from these two fields. The reader does not need to perform any other modification to the script.
The output of the files can be found in the `out` directory.