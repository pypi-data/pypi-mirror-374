"""
A tide prediction toolkit for Python
====================================

pyTMD is a Python-based tidal prediction software for estimating ocean,
load, solid Earth and pole tides.

The package works using scientific Python packages (numpy, scipy and pyproj)
combined with data storage in netCDF4 and HDF5 and mapping using
matplotlib and cartopy

Documentation is available at https://pytmd.readthedocs.io
"""
import pyTMD.arguments
import pyTMD.astro
import pyTMD.compute
import pyTMD.ellipse
import pyTMD.interpolate
import pyTMD.math
import pyTMD.predict
import pyTMD.spatial
import pyTMD.tools
import pyTMD.utilities
import pyTMD.version
from pyTMD import io
from pyTMD import solve
from pyTMD.crs import crs

# Deprecated functions
from pyTMD.compute_tide_corrections import (
    compute_corrections,
    compute_tide_corrections,
    compute_LPET_corrections,
    compute_LPT_corrections,
    compute_OPT_corrections,
    compute_SET_corrections,
)

# get version information
__version__ = pyTMD.version.version
# read model database
models = io.load_database()
__models__ = {key:list(val.keys()) for key, val in models.items()}
