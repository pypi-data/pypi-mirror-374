#!/usr/bin/env python
u"""
compute.py
Written by Tyler Sutterley (09/2025)
Calculates tidal elevations for correcting elevation or imagery data
Calculates tidal currents at locations and times

Ocean and Load Tides
Uses OTIS format tidal solutions provided by Oregon State University and ESR
    http://volkov.oce.orst.edu/tides/region.html
    https://www.esr.org/research/polar-tide-models/list-of-polar-tide-models/
    ftp://ftp.esr.org/pub/datasets/tmd/
Global Tide Model (GOT) solutions provided by Richard Ray at GSFC
or Finite Element Solution (FES) models provided by AVISO

Long-Period Equilibrium Tides (LPET)
Calculates long-period equilibrium tidal elevations for correcting
elevation or imagery data from the summation of fifteen spectral lines
    https://doi.org/10.1111/j.1365-246X.1973.tb03420.x

Load Pole Tides (LPT)
Calculates radial load pole tide displacements following IERS Convention
(2010) guidelines for correcting elevation or imagery data
    https://iers-conventions.obspm.fr/chapter7.php

Ocean Pole Tides (OPT)
Calculates radial ocean pole load tide displacements following IERS Convention
(2010) guidelines for correcting elevation or imagery data
    https://iers-conventions.obspm.fr/chapter7.php

Solid Earth Tides (SET)
Calculates radial Solid Earth tide displacements following IERS Convention
(2010) guidelines for correcting elevation or imagery data
    https://iers-conventions.obspm.fr/chapter7.php
Or by using a tide potential catalog following Cartwright and Tayler (1971)

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
    scipy: Scientific Tools for Python
        https://docs.scipy.org/doc/
    netCDF4: Python interface to the netCDF C library
        https://unidata.github.io/netcdf4-python/netCDF4/index.html
    pyproj: Python interface to PROJ library
        https://pypi.org/project/pyproj/
    timescale: Python tools for time and astronomical calculations
        https://pypi.org/project/timescale/

PROGRAM DEPENDENCIES:
    time.py: utilities for calculating time operations
    spatial: utilities for reading, writing and operating on spatial data
    utilities.py: download and management utilities for syncing files
    arguments.py: load the nodal corrections for tidal constituents
    astro.py: computes the basic astronomical mean longitudes
    crs.py: Coordinate Reference System (CRS) routines
    predict.py: predict tide values using harmonic constants
    io/model.py: retrieves tide model parameters for named tide models
    io/OTIS.py: extract tidal harmonic constants from OTIS tide models
    io/ATLAS.py: extract tidal harmonic constants from netcdf models
    io/GOT.py: extract tidal harmonic constants from GSFC GOT models
    io/FES.py: extract tidal harmonic constants from FES tide models
    interpolate.py: interpolation routines for spatial data

UPDATE HISTORY:
    Updated 09/2025: added wrapper for calculating solid earth tides
        using a tide potential catalog following Cartwright and Tayler (1971)
    Updated 08/2025: convert angles with numpy radians and degrees functions
        pass kwargs to computation of long-period equilibrium tides
        use timescale shortcut wrapper functions to create Timescale objects
    Updated 07/2025: mask mean pole values prior to valid epoch of convention
        add a default directory for tide models
    Updated 05/2025: added option to select constituents to read from model
    Updated 12/2024: moved check points function as compute.tide_masks
    Updated 11/2024: expose buffer distance for cropping tide model data
    Updated 10/2024: compute delta times based on corrections type
        simplify by using wrapper functions to read and interpolate constants
        added option to append equilibrium amplitudes for node tides
    Updated 09/2024: use JSON database for known model parameters
        drop support for the ascii definition file format
        use model class attributes for file format and corrections
        add keyword argument to select nodal corrections type
        fix to use case insensitive assertions of string argument values
        add model attribute for tide model bulk frequencies
    Updated 08/2024: allow inferring only specific minor constituents
        use prediction functions for pole tides in cartesian coordinates
        use rotation matrix to convert from cartesian to spherical
    Updated 07/2024: assert that data type is a known value
        make number of days to convert JD to MJD a variable
        added option to crop tide models to the domain of the input data
        added option to use JSON format definition files
        renamed format for ATLAS to ATLAS-compact
        renamed format for netcdf to ATLAS-netcdf
        renamed format for FES to FES-netcdf and added FES-ascii
        renamed format for GOT to GOT-ascii and added GOT-netcdf
        drop use of heights when converting to cartesian coordinates
        use prediction function to calculate cartesian tide displacements
    Updated 06/2024: use np.clongdouble instead of np.longcomplex
    Updated 04/2024: use wrapper to importlib for optional dependencies
    Updated 02/2024: changed class name for ellipsoid parameters to datum
    Updated 01/2024: made the inference of minor constituents an option
        refactored lunisolar ephemerides functions
        renamed module to compute and added tidal currents function
    Updated 12/2023: use new crs class for coordinate reprojection
    Updated 08/2023: changed ESR netCDF4 format to TMD3 format
    Updated 05/2023: use timescale class for time conversion operations
        use defaults from eop module for pole tide and EOP files
        add option for using higher resolution ephemerides from JPL
    Updated 04/2023: added function for radial solid earth tides
        using pathlib to define and expand paths
    Updated 03/2023: add basic variable typing to function inputs
        added function for long-period equilibrium tides
        added function for radial load pole tides
        added function for radial ocean pole tides
    Updated 12/2022: refactored tide read and prediction programs
    Updated 11/2022: place some imports within try/except statements
        use f-strings for formatting verbose or ascii output
    Updated 05/2022: added ESR netCDF4 formats to list of model types
        updated keyword arguments to read tide model programs
        added option to apply flexure to heights for applicable models
    Updated 04/2022: updated docstrings to numpy documentation format
    Updated 12/2021: added function to calculate a tidal time series
        verify coordinate dimensions for each input data type
        added option for converting from LORAN times to UTC
    Updated 09/2021: refactor to use model class for files and attributes
    Updated 07/2021: can use numpy datetime arrays as input time variable
        added function for determining the input spatial variable type
        added check that tide model directory is accessible
    Updated 06/2021: added new Gr1km-v2 1km Greenland model from ESR
        add try/except for input projection strings
    Updated 05/2021: added option for extrapolation cutoff in kilometers
    Updated 03/2021: added TPXO9-atlas-v4 in binary OTIS format
        simplified netcdf inputs to be similar to binary OTIS read program
    Updated 02/2021: replaced numpy bool to prevent deprecation warning
    Updated 12/2020: added valid data extrapolation with nearest_extrap
    Updated 11/2020: added model constituents from TPXO9-atlas-v3
    Updated 08/2020: using builtin time operations.
        calculate difference in leap seconds from start of epoch
        using conversion protocols following pyproj-2 updates
    Updated 07/2020: added function docstrings, FES2014 and TPXO9-atlas-v2
        use merged delta time files combining biannual, monthly and daily files
    Updated 03/2020: added TYPE, TIME, FILL_VALUE and METHOD options
    Written 03/2020
"""
from __future__ import print_function, annotations

import logging
import pathlib
import numpy as np
from io import IOBase
import scipy.interpolate
import pyTMD.crs
import pyTMD.io
import pyTMD.io.model
import pyTMD.predict
import pyTMD.spatial
import pyTMD.utilities
import timescale.eop
import timescale.time
# attempt imports
pyproj = pyTMD.utilities.import_dependency('pyproj')

__all__ = [
    "corrections",
    "tide_elevations",
    "tide_currents",
    "tide_masks",
    "LPET_elevations",
    "LPT_displacements",
    "OPT_displacements",
    "SET_displacements"
]

# number of days between the Julian day epoch and MJD
_jd_mjd = 2400000.5

# default working data directory for tide models
_default_directory = pyTMD.utilities.get_data_path('data')

# PURPOSE: wrapper function for computing values
def corrections(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        CORRECTION: str = 'ocean',
        **kwargs
    ):
    """
    Wrapper function to compute tide corrections at points and times

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    CORRECTION: str, default 'ocean'
        Correction type to compute

            - ``'ocean'``: ocean tide from model constituents
            - ``'load'``: load tide from model constituents
            - ``'LPET'``: long-period equilibrium tide
            - ``'LPT'``: solid earth load pole tide
            - ``'OPT'``: ocean pole tide
            - ``'SET'``: solid earth tide
    **kwargs: dict
        keyword arguments for correction functions

    Returns
    -------
    values: np.ndarray
        tidal correction at coordinates and time in meters
    """
    if CORRECTION.lower() in ('ocean', 'load'):
        return tide_elevations(x, y, delta_time, **kwargs)
    elif (CORRECTION.upper() == 'LPET'):
        return LPET_elevations(x, y, delta_time, **kwargs)
    elif (CORRECTION.upper() == 'LPT'):
        return LPT_displacements(x, y, delta_time, **kwargs)
    elif (CORRECTION.upper() == 'OPT'):
        return OPT_displacements(x, y, delta_time, **kwargs)
    elif (CORRECTION.upper() == 'SET'):
        return SET_displacements(x, y, delta_time, **kwargs)
    else:
        raise ValueError(f'Unrecognized correction type: {CORRECTION}')

# PURPOSE: compute tides at points and times using tide model algorithms
def tide_elevations(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        DIRECTORY: str | pathlib.Path | None = _default_directory,
        MODEL: str | None = None,
        GZIP: bool = False,
        DEFINITION_FILE: str | pathlib.Path | IOBase | None = None,
        CROP: bool = False,
        BOUNDS: list | np.ndarray | None = None,
        BUFFER: int | float | None = None,
        EPSG: str | int = 4326,
        EPOCH: list | tuple = (2000, 1, 1, 0, 0, 0),
        TYPE: str | None = 'drift',
        TIME: str = 'UTC',
        METHOD: str = 'spline',
        EXTRAPOLATE: bool = False,
        CUTOFF: int | float = 10.0,
        CORRECTIONS: str | None = None,
        CONSTITUENTS: list | None = None,
        INFER_MINOR: bool = True,
        MINOR_CONSTITUENTS: list | None = None,
        APPEND_NODE: bool = False,
        APPLY_FLEXURE: bool = False,
        FILL_VALUE: float = np.nan,
        **kwargs
    ):
    """
    Compute ocean or load tides at points and times from
    model constituents

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    DIRECTORY: str or NoneType, default None
        working data directory for tide models
    MODEL: str or NoneType, default None
        Tide model to use in correction
    GZIP: bool, default False
        Tide model files are gzip compressed
    DEFINITION_FILE: str, pathlib.Path, io.IOBase or NoneType, default None
        Tide model definition file for use
    CROP: bool, default False
        Crop tide model data to (buffered) bounds
    BOUNDS: list, np.ndarray or NoneType, default None
        Boundaries for cropping tide model data
    BUFFER: int, float or NoneType, default None
        Buffer distance for cropping tide model data
    EPSG: int, default: 4326 (WGS84 Latitude and Longitude)
        Input coordinate system
    EPOCH: tuple, default (2000,1,1,0,0,0)
        Time period for calculating delta times
    TYPE: str or NoneType, default 'drift'
        Input data type

            - ``None``: determined from input variable dimensions
            - ``'drift'``: drift buoys or satellite/airborne altimetry
            - ``'grid'``: spatial grids or images
            - ``'time series'``: time series at a single point
    TIME: str, default 'UTC'
        Time type if need to compute leap seconds to convert to UTC

            - ``'GPS'``: leap seconds needed
            - ``'LORAN'``: leap seconds needed (LORAN = GPS + 9 seconds)
            - ``'TAI'``: leap seconds needed (TAI = GPS + 19 seconds)
            - ``'UTC'``: no leap seconds needed
            - ``'datetime'``: numpy datatime array in UTC
    METHOD: str
        Interpolation method

            - ```bilinear```: quick bilinear interpolation
            - ```spline```: scipy bivariate spline interpolation
            - ```linear```, ```nearest```: scipy regular grid interpolations

    EXTRAPOLATE: bool, default False
        Extrapolate with nearest-neighbors
    CUTOFF: int or float, default 10.0
        Extrapolation cutoff in kilometers

        Set to ``np.inf`` to extrapolate for all points
    CORRECTIONS: str or None, default None
        Nodal correction type, default based on model
    CONSTITUENTS: list or None, default None
        Specify constituents to read from model
    INFER_MINOR: bool, default True
        Infer the height values for minor tidal constituents
    MINOR_CONSTITUENTS: list or None, default None
        Specify constituents to infer
    APPEND_NODE: bool, default False
        Append equilibrium amplitudes for node tides
    APPLY_FLEXURE: bool, default False
        Apply ice flexure scaling factor to height values

        Only valid for models containing flexure fields
    FILL_VALUE: float, default np.nan
        Output invalid value

    Returns
    -------
    tide: np.ndarray
        tidal elevation in meters
    """

    # check that tide directory is accessible
    if DIRECTORY is not None:
        DIRECTORY = pathlib.Path(DIRECTORY).expanduser()
        if not DIRECTORY.exists():
            raise FileNotFoundError("Invalid tide directory")

    # validate input arguments
    assert TIME.lower() in ('gps', 'loran', 'tai', 'utc', 'datetime')
    assert METHOD.lower() in ('bilinear', 'spline', 'linear', 'nearest')

    # get parameters for tide model
    if DEFINITION_FILE is not None:
        model = pyTMD.io.model(DIRECTORY).from_file(DEFINITION_FILE)
    else:
        model = pyTMD.io.model(DIRECTORY, compressed=GZIP).elevation(MODEL)

    # determine input data type based on variable dimensions
    if not TYPE:
        TYPE = pyTMD.spatial.data_type(x, y, delta_time)
    assert TYPE.lower() in ('grid', 'drift', 'time series')
    # reform coordinate dimensions for input grids
    # or verify coordinate dimension shapes
    if (TYPE.lower() == 'grid') and (np.size(x) != np.size(y)):
        x,y = np.meshgrid(np.copy(x),np.copy(y))
    elif (TYPE.lower() == 'grid'):
        x = np.atleast_2d(x)
        y = np.atleast_2d(y)
    elif TYPE.lower() in ('time series', 'drift'):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

    # converting x,y from EPSG to latitude/longitude
    crs1 = pyTMD.crs().from_input(EPSG)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    lon, lat = transformer.transform(x.flatten(), y.flatten())

    # verify that delta time is an array
    delta_time = np.atleast_1d(delta_time)
    # convert delta times or datetimes objects to timescale
    if (TIME.lower() == 'datetime'):
        ts = timescale.from_datetime(delta_time.flatten())
    else:
        ts = timescale.from_deltatime(delta_time,
            epoch=EPOCH, standard=TIME)
    # number of time points
    nt = len(ts)

    # read tidal constants and interpolate to grid points
    amp, ph, c = model.extract_constants(lon, lat,
        type=model.type, constituents=CONSTITUENTS,
        crop=CROP, bounds=BOUNDS, buffer=BUFFER, method=METHOD,
        extrapolate=EXTRAPOLATE, cutoff=CUTOFF,
        append_node=APPEND_NODE, apply_flexure=APPLY_FLEXURE)
    # calculate complex phase in radians for Euler's
    cph = -1j*ph*np.pi/180.0
    # calculate constituent oscillation
    hc = amp*np.exp(cph)

    # nodal corrections to apply
    nodal_corrections = CORRECTIONS or model.corrections
    # minor constituents to infer
    minor_constituents = MINOR_CONSTITUENTS or model.minor
    # delta time (TT - UT1) for tide model
    if nodal_corrections in ('OTIS','ATLAS','TMD3','netcdf'):
        # use delta time at 2000.0 to match TMD outputs
        deltat = np.zeros_like(ts.tt_ut1)
    else:
        # use interpolated delta times
        deltat = ts.tt_ut1

    # calculate tide values for input data type
    if (TYPE.lower() == 'grid'):
        ny,nx = np.shape(x)
        tide = np.ma.zeros((ny,nx,nt),fill_value=FILL_VALUE)
        tide.mask = np.zeros((ny,nx,nt),dtype=bool)
        for i in range(nt):
            TIDE = pyTMD.predict.map(ts.tide[i], hc, c,
                deltat=deltat[i], corrections=nodal_corrections)
            # calculate values for minor constituents by inference
            if INFER_MINOR:
                MINOR = pyTMD.predict.infer_minor(ts.tide[i], hc, c,
                    deltat=deltat[i], corrections=nodal_corrections,
                    minor=minor_constituents)
            else:
                MINOR = np.ma.zeros_like(TIDE)
            # add major and minor components and reform grid
            tide[:,:,i] = np.reshape((TIDE+MINOR), (ny,nx))
            tide.mask[:,:,i] = np.reshape((TIDE.mask | MINOR.mask), (ny,nx))
    elif (TYPE.lower() == 'drift'):
        tide = np.ma.zeros((nt), fill_value=FILL_VALUE)
        tide.mask = np.any(hc.mask,axis=1)
        tide.data[:] = pyTMD.predict.drift(ts.tide, hc, c,
            deltat=deltat, corrections=nodal_corrections)
        # calculate values for minor constituents by inference
        if INFER_MINOR:
            minor = pyTMD.predict.infer_minor(ts.tide, hc, c,
                deltat=deltat, corrections=nodal_corrections,
                minor=minor_constituents)
            tide.data[:] += minor.data[:]
    elif (TYPE.lower() == 'time series'):
        nstation = len(x)
        tide = np.ma.zeros((nstation,nt), fill_value=FILL_VALUE)
        tide.mask = np.zeros((nstation,nt),dtype=bool)
        for s in range(nstation):
            HC = hc[s,None,:]
            TIDE = pyTMD.predict.time_series(ts.tide, HC, c,
                deltat=deltat, corrections=nodal_corrections)
            # calculate values for minor constituents by inference
            if INFER_MINOR:
                MINOR = pyTMD.predict.infer_minor(ts.tide, HC, c,
                    deltat=deltat, corrections=nodal_corrections,
                    minor=minor_constituents)
            else:
                MINOR = np.ma.zeros_like(TIDE)
            # add major and minor components
            tide.data[s,:] = TIDE.data[:] + MINOR.data[:]
            tide.mask[s,:] = (TIDE.mask | MINOR.mask)
    # replace invalid values with fill value
    tide.data[tide.mask] = tide.fill_value

    # return the ocean or load tide correction
    return tide

# PURPOSE: compute tides at points and times using tide model algorithms
def tide_currents(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        DIRECTORY: str | pathlib.Path | None = _default_directory,
        MODEL: str | None = None,
        GZIP: bool = False,
        DEFINITION_FILE: str | pathlib.Path | IOBase | None = None,
        CROP: bool = False,
        BOUNDS: list | np.ndarray | None = None,
        BUFFER: int | float | None = None,
        EPSG: str | int = 4326,
        EPOCH: list | tuple = (2000, 1, 1, 0, 0, 0),
        TYPE: str | None = 'drift',
        TIME: str = 'UTC',
        METHOD: str = 'spline',
        EXTRAPOLATE: bool = False,
        CUTOFF: int | float = 10.0,
        CORRECTIONS: str | None = None,
        CONSTITUENTS: list | None = None,
        INFER_MINOR: bool = True,
        MINOR_CONSTITUENTS: list | None = None,
        FILL_VALUE: float = np.nan,
        **kwargs
    ):
    """
    Compute ocean tide currents at points and times from
    model constituents

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    DIRECTORY: str or NoneType, default None
        working data directory for tide models
    MODEL: str or NoneType, default None
        Tide model to use in correction
    GZIP: bool, default False
        Tide model files are gzip compressed
    DEFINITION_FILE: str, pathlib.Path, io.IOBase or NoneType, default None
        Tide model definition file for use
    CROP: bool, default False
        Crop tide model data to (buffered) bounds
    BOUNDS: list, np.ndarray or NoneType, default None
        Boundaries for cropping tide model data
    BUFFER: int, float or NoneType, default None
        Buffer distance for cropping tide model data
    EPSG: int, default: 4326 (WGS84 Latitude and Longitude)
        Input coordinate system
    EPOCH: tuple, default (2000,1,1,0,0,0)
        Time period for calculating delta times
    TYPE: str or NoneType, default 'drift'
        Input data type

            - ``None``: determined from input variable dimensions
            - ``'drift'``: drift buoys or satellite/airborne altimetry
            - ``'grid'``: spatial grids or images
            - ``'time series'``: time series at a single point
    TIME: str, default 'UTC'
        Time type if need to compute leap seconds to convert to UTC

            - ``'GPS'``: leap seconds needed
            - ``'LORAN'``: leap seconds needed (LORAN = GPS + 9 seconds)
            - ``'TAI'``: leap seconds needed (TAI = GPS + 19 seconds)
            - ``'UTC'``: no leap seconds needed
            - ``'datetime'``: numpy datatime array in UTC
    METHOD: str
        Interpolation method

            - ```bilinear```: quick bilinear interpolation
            - ```spline```: scipy bivariate spline interpolation
            - ```linear```, ```nearest```: scipy regular grid interpolations

    EXTRAPOLATE: bool, default False
        Extrapolate with nearest-neighbors
    CUTOFF: int or float, default 10.0
        Extrapolation cutoff in kilometers

        Set to ``np.inf`` to extrapolate for all points
    CORRECTIONS: str or None, default None
        Nodal correction type, default based on model
    CONSTITUENTS: list or None, default None
        Specify constituents to read from model
    INFER_MINOR: bool, default True
        Infer the height values for minor tidal constituents
    MINOR_CONSTITUENTS: list or None, default None
        Specify constituents to infer
    FILL_VALUE: float, default np.nan
        Output invalid value

    Returns
    -------
    tide: dict
        tidal currents in cm/s

        u: np.ndarray
            horizontal transport velocities
        v: np.ndarray
            vertical transport velocities
    """

    # check that tide directory is accessible
    if DIRECTORY is not None:
        DIRECTORY = pathlib.Path(DIRECTORY).expanduser()
        if not DIRECTORY.exists():
            raise FileNotFoundError("Invalid tide directory")

    # validate input arguments
    assert TIME.lower() in ('gps', 'loran', 'tai', 'utc', 'datetime')
    assert METHOD.lower() in ('bilinear', 'spline', 'linear', 'nearest')

    # get parameters for tide model
    if DEFINITION_FILE is not None:
        model = pyTMD.io.model(DIRECTORY).from_file(DEFINITION_FILE)
    else:
        model = pyTMD.io.model(DIRECTORY, compressed=GZIP).current(MODEL)

    # determine input data type based on variable dimensions
    if not TYPE:
        TYPE = pyTMD.spatial.data_type(x, y, delta_time)
    assert TYPE.lower() in ('grid', 'drift', 'time series')
    # reform coordinate dimensions for input grids
    # or verify coordinate dimension shapes
    if (TYPE.lower() == 'grid') and (np.size(x) != np.size(y)):
        x,y = np.meshgrid(np.copy(x),np.copy(y))
    elif (TYPE.lower() == 'grid'):
        x = np.atleast_2d(x)
        y = np.atleast_2d(y)
    elif TYPE.lower() in ('time series', 'drift'):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

    # converting x,y from EPSG to latitude/longitude
    crs1 = pyTMD.crs().from_input(EPSG)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    lon, lat = transformer.transform(x.flatten(), y.flatten())

    # verify that delta time is an array
    delta_time = np.atleast_1d(delta_time)
    # convert delta times or datetimes objects to timescale
    if (TIME.lower() == 'datetime'):
        ts = timescale.from_datetime(delta_time.flatten())
    else:
        ts = timescale.from_deltatime(delta_time,
            epoch=EPOCH, standard=TIME)
    # number of time points
    nt = len(ts)

    # python dictionary with tide model data
    tide = {}
    # iterate over u and v currents
    for t in model.type:
        # read tidal constants and interpolate to grid points
        amp, ph, c = model.extract_constants(lon, lat,
            type=t, constituents=CONSTITUENTS,
            crop=CROP, bounds=BOUNDS, buffer=BUFFER, method=METHOD,
            extrapolate=EXTRAPOLATE, cutoff=CUTOFF)
        # calculate complex phase in radians for Euler's
        cph = -1j*ph*np.pi/180.0
        # calculate constituent oscillation
        hc = amp*np.exp(cph)

        # nodal corrections to apply
        nodal_corrections = CORRECTIONS or model.corrections
        # minor constituents to infer
        minor_constituents = MINOR_CONSTITUENTS or model.minor
        # delta time (TT - UT1) for tide model
        if nodal_corrections in ('OTIS','ATLAS','TMD3','netcdf'):
            # use delta time at 2000.0 to match TMD outputs
            deltat = np.zeros_like(ts.tt_ut1)
        else:
            # use interpolated delta times
            deltat = ts.tt_ut1

        # predict tidal currents at time
        if (TYPE.lower() == 'grid'):
            ny,nx = np.shape(x)
            tide[t] = np.ma.zeros((ny,nx,nt),fill_value=FILL_VALUE)
            tide[t].mask = np.zeros((ny,nx,nt),dtype=bool)
            for i in range(nt):
                TIDE = pyTMD.predict.map(ts.tide[i], hc, c,
                    deltat=deltat[i], corrections=nodal_corrections)
                # calculate values for minor constituents by inference
                if INFER_MINOR:
                    MINOR = pyTMD.predict.infer_minor(ts.tide[i], hc, c,
                        deltat=deltat[i], corrections=nodal_corrections,
                        minor=minor_constituents)
                else:
                    MINOR = np.ma.zeros_like(TIDE)
                # add major and minor components and reform grid
                tide[t][:,:,i] = np.reshape((TIDE+MINOR), (ny,nx))
                tide[t].mask[:,:,i] = np.reshape((TIDE.mask | MINOR.mask), (ny,nx))
        elif (TYPE.lower() == 'drift'):
            tide[t] = np.ma.zeros((nt), fill_value=FILL_VALUE)
            tide[t].mask = np.any(hc.mask,axis=1)
            tide[t].data[:] = pyTMD.predict.drift(ts.tide, hc, c,
                deltat=deltat, corrections=nodal_corrections)
            # calculate values for minor constituents by inference
            if INFER_MINOR:
                minor = pyTMD.predict.infer_minor(ts.tide, hc, c,
                    deltat=deltat, corrections=nodal_corrections,
                    minor=minor_constituents)
                tide[t].data[:] += minor.data[:]
        elif (TYPE.lower() == 'time series'):
            nstation = len(x)
            tide[t] = np.ma.zeros((nstation,nt), fill_value=FILL_VALUE)
            tide[t].mask = np.zeros((nstation,nt),dtype=bool)
            for s in range(nstation):
                HC = hc[s,None,:]
                TIDE = pyTMD.predict.time_series(ts.tide, HC, c,
                    deltat=deltat, corrections=nodal_corrections)
                # calculate values for minor constituents by inference
                if INFER_MINOR:
                    MINOR = pyTMD.predict.infer_minor(ts.tide, HC, c,
                        deltat=deltat, corrections=nodal_corrections,
                        minor=minor_constituents)
                else:
                    MINOR = np.ma.zeros_like(TIDE)
                # add major and minor components
                tide[t].data[s,:] = TIDE.data[:] + MINOR.data[:]
                tide[t].mask[s,:] = (TIDE.mask | MINOR.mask)
        # replace invalid values with fill value
        tide[t].data[tide[t].mask] = tide[t].fill_value

    # return the ocean tide currents
    return tide

# PURPOSE: check if points are within a tide model domain
def tide_masks(x: np.ndarray, y: np.ndarray,
        DIRECTORY: str | pathlib.Path | None = _default_directory,
        MODEL: str | None = None,
        GZIP: bool = False,
        DEFINITION_FILE: str | pathlib.Path | IOBase | None = None,
        EPSG: str | int = 4326,
        METHOD: str = 'spline'
    ):
    """
    Check if points are within a tide model domain

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    DIRECTORY: str or NoneType, default None
        working data directory for tide models
    MODEL: str or NoneType, default None
        Tide model to use
    GZIP: bool, default False
        Tide model files are gzip compressed
    DEFINITION_FILE: str or NoneType, default None
        Tide model definition file for use
    EPSG: str or int, default: 4326 (WGS84 Latitude and Longitude)
        Input coordinate system
    METHOD: str, default 'spline'
        interpolation method

            - ```bilinear```: quick bilinear interpolation
            - ```spline```: scipy bivariate spline interpolation
            - ```linear```, ```nearest```: scipy regular grid interpolations

    Returns
    -------
    valid: bool
        array describing if input coordinate is within model domain
    """

    # check that tide directory is accessible
    if DIRECTORY is not None:
        DIRECTORY = pathlib.Path(DIRECTORY).expanduser()
        if not DIRECTORY.exists():
            raise FileNotFoundError("Invalid tide directory")

    # get parameters for tide model
    if DEFINITION_FILE is not None:
        model = pyTMD.io.model(DIRECTORY).from_file(DEFINITION_FILE)
    else:
        model = pyTMD.io.model(DIRECTORY, compressed=GZIP).elevation(MODEL)

    # input shape of data
    idim = np.shape(x)
    # converting x,y from input coordinate reference system
    crs1 = pyTMD.crs().from_input(EPSG)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    lon, lat = transformer.transform(
        np.atleast_1d(x).flatten(), np.atleast_1d(y).flatten()
    )

    # read tidal constants and interpolate to grid points
    if model.format in ('OTIS','ATLAS-compact','TMD3'):
        # if reading a single OTIS solution
        xi, yi, hz, mz, iob, dt = pyTMD.io.OTIS.read_otis_grid(
            pathlib.Path(model.grid_file).expanduser())
        # invert model mask
        mz = np.logical_not(mz)
        # adjust dimensions of input coordinates to be iterable
        # run wrapper function to convert coordinate systems of input lat/lon
        X, Y = pyTMD.crs().convert(lon, lat, model.projection, 'F')
    elif (model.format == 'ATLAS-netcdf'):
        # if reading a netCDF OTIS atlas solution
        xi, yi, hz = pyTMD.io.ATLAS.read_netcdf_grid(
            pathlib.Path(model.grid_file).expanduser(),
            compressed=model.compressed, type=model.type)
        # copy bathymetry mask
        mz = np.copy(hz.mask)
        # copy latitude and longitude and adjust longitudes
        X,Y = np.copy([lon,lat]).astype(np.float64)
        lt0, = np.nonzero(X < 0)
        X[lt0] += 360.0
    elif model.format in ('GOT-ascii', 'GOT-netcdf'):
        # if reading a NASA GOT solution
        hc, xi, yi, c = pyTMD.io.GOT.read_ascii_file(
            pathlib.Path(model.model_file[0]).expanduser(),
            compressed=model.compressed)
        # copy tidal constituent mask
        mz = np.copy(hc.mask)
        # copy latitude and longitude and adjust longitudes
        X, Y = np.copy([lon,lat]).astype(np.float64)
        lt0, = np.nonzero(X < 0)
        X[lt0] += 360.0
    elif (model.format == 'FES-netcdf'):
        # if reading a FES netCDF solution
        hc, xi, yi = pyTMD.io.FES.read_netcdf_file(
            pathlib.Path(model.model_file[0]).expanduser(),
            compressed=model.compressed, type=model.type,
            version=model.version)
        # copy tidal constituent mask
        mz = np.copy(hc.mask)
        # copy latitude and longitude and adjust longitudes
        X, Y = np.copy([lon,lat]).astype(np.float64)
        lt0, = np.nonzero(X < 0)
        X[lt0] += 360.0

    # interpolate masks
    if (METHOD == 'bilinear'):
        # replace invalid values with nan
        mz1 = pyTMD.interpolate.bilinear(xi, yi, mz, X, Y)
        mask = np.floor(mz1).astype(mz.dtype)
    elif (METHOD == 'spline'):
        f1 = scipy.interpolate.RectBivariateSpline(xi, yi, mz.T,
            kx=1, ky=1)
        mask = np.floor(f1.ev(X, Y)).astype(mz.dtype)
    else:
        # use scipy regular grid to interpolate values
        r1 = scipy.interpolate.RegularGridInterpolator((yi, xi), mz,
            method=METHOD, bounds_error=False, fill_value=1)
        mask = np.floor(r1.__call__(np.c_[y, x])).astype(mz.dtype)

    # reshape to original dimensions
    valid = np.logical_not(mask).reshape(idim).astype(mz.dtype)
    # replace points outside model domain with invalid
    valid &= (X >= xi.min()) & (X <= xi.max())
    valid &= (Y >= yi.min()) & (Y <= yi.max())
    # return the valid mask
    return valid

# PURPOSE: compute long-period equilibrium tidal elevations
def LPET_elevations(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        EPSG: str | int = 4326,
        EPOCH: list | tuple = (2000, 1, 1, 0, 0, 0),
        TYPE: str | None = 'drift',
        TIME: str = 'UTC',
        **kwargs
    ):
    """
    Compute long-period equilibrium tidal elevations at points and times

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    EPSG: int, default: 4326 (WGS84 Latitude and Longitude)
        Input coordinate system
    EPOCH: tuple, default (2000,1,1,0,0,0)
        Time period for calculating delta times
    TYPE: str or NoneType, default 'drift'
        Input data type

            - ``None``: determined from input variable dimensions
            - ``'drift'``: drift buoys or satellite/airborne altimetry
            - ``'grid'``: spatial grids or images
            - ``'time series'``: time series at a single point
    TIME: str, default 'UTC'
        Time type if need to compute leap seconds to convert to UTC

            - ``'GPS'``: leap seconds needed
            - ``'LORAN'``: leap seconds needed (LORAN = GPS + 9 seconds)
            - ``'TAI'``: leap seconds needed (TAI = GPS + 19 seconds)
            - ``'UTC'``: no leap seconds needed
            - ``'datetime'``: numpy datatime array in UTC
    FILL_VALUE: float, default np.nan
        Output invalid value

    Returns
    -------
    tide_lpe: np.ndarray
        long-period equilibrium tide at coordinates and time in meters
    """

    # validate input arguments
    assert TIME.lower() in ('gps', 'loran', 'tai', 'utc', 'datetime')
    # determine input data type based on variable dimensions
    if not TYPE:
        TYPE = pyTMD.spatial.data_type(x, y, delta_time)
    assert TYPE.lower() in ('grid', 'drift', 'time series')
    # reform coordinate dimensions for input grids
    # or verify coordinate dimension shapes
    if (TYPE.lower() == 'grid') and (np.size(x) != np.size(y)):
        x,y = np.meshgrid(np.copy(x),np.copy(y))
    elif (TYPE.lower() == 'grid'):
        x = np.atleast_2d(x)
        y = np.atleast_2d(y)
    elif TYPE.lower() in ('time series', 'drift'):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

    # converting x,y from EPSG to latitude/longitude
    crs1 = pyTMD.crs().from_input(EPSG)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    lon, lat = transformer.transform(x.flatten(), y.flatten())

    # verify that delta time is an array
    delta_time = np.atleast_1d(delta_time)
    # convert delta times or datetimes objects to timescale
    if (TIME.lower() == 'datetime'):
        ts = timescale.from_datetime(delta_time.flatten())
    else:
        ts = timescale.from_deltatime(delta_time,
            epoch=EPOCH, standard=TIME)
    # number of time points
    nt = len(ts)
    # convert tide times to dynamic time
    tide_time = ts.tide + ts.tt_ut1

    # predict long-period equilibrium tides at time
    if (TYPE == 'grid'):
        ny,nx = np.shape(x)
        tide_lpe = np.zeros((ny,nx,nt))
        for i in range(nt):
            lpet = pyTMD.predict.equilibrium_tide(
                tide_time[i], lat, **kwargs)
            tide_lpe[:,:,i] = np.reshape(lpet, (ny,nx))
    elif (TYPE == 'drift'):
        tide_lpe = pyTMD.predict.equilibrium_tide(
            tide_time, lat, **kwargs)
    elif (TYPE == 'time series'):
        nstation = len(x)
        tide_lpe = np.zeros((nstation,nt))
        for s in range(nstation):
            tide_lpe[s,:] = pyTMD.predict.equilibrium_tide(
                tide_time, lat[s], **kwargs)

    # return the long-period equilibrium tide elevations
    return tide_lpe

# PURPOSE: compute radial load pole tide displacements
# following IERS Convention (2010) guidelines
def LPT_displacements(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        EPSG: str | int = 4326,
        EPOCH: list | tuple = (2000, 1, 1, 0, 0, 0),
        TYPE: str | None = 'drift',
        TIME: str = 'UTC',
        ELLIPSOID: str = 'WGS84',
        CONVENTION: str = '2018',
        FILL_VALUE: float = np.nan,
        **kwargs
    ):
    """
    Compute radial load pole tide displacements at points and times
    following IERS Convention (2010) guidelines

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    EPSG: int, default: 4326 (WGS84 Latitude and Longitude)
        Input coordinate system
    EPOCH: tuple, default (2000,1,1,0,0,0)
        Time period for calculating delta times
    TYPE: str or NoneType, default 'drift'
        Input data type

            - ``None``: determined from input variable dimensions
            - ``'drift'``: drift buoys or satellite/airborne altimetry
            - ``'grid'``: spatial grids or images
            - ``'time series'``: time series at a single point
    TIME: str, default 'UTC'
        Time type if need to compute leap seconds to convert to UTC

            - ``'GPS'``: leap seconds needed
            - ``'LORAN'``: leap seconds needed (LORAN = GPS + 9 seconds)
            - ``'TAI'``: leap seconds needed (TAI = GPS + 19 seconds)
            - ``'UTC'``: no leap seconds needed
            - ``'datetime'``: numpy datatime array in UTC
    ELLIPSOID: str, default 'WGS84'
        Ellipsoid for calculating Earth parameters
    CONVENTION: str, default '2018'
        IERS Mean or Secular Pole Convention

            - ``'2003'``
            - ``'2010'``
            - ``'2015'``
            - ``'2018'``
    FILL_VALUE: float, default np.nan
        Output invalid value

    Returns
    -------
    Srad: np.ndarray
        solid earth pole tide at coordinates and time in meters
    """

    # validate input arguments
    assert TIME.lower() in ('gps', 'loran', 'tai', 'utc', 'datetime')
    assert ELLIPSOID.upper() in pyTMD.spatial._ellipsoids
    assert CONVENTION.isdigit() and CONVENTION in timescale.eop._conventions
    # determine input data type based on variable dimensions
    if not TYPE:
        TYPE = pyTMD.spatial.data_type(x, y, delta_time)
    assert TYPE.lower() in ('grid', 'drift', 'time series')
    # reform coordinate dimensions for input grids
    # or verify coordinate dimension shapes
    if (TYPE.lower() == 'grid') and (np.size(x) != np.size(y)):
        x,y = np.meshgrid(np.copy(x),np.copy(y))
    elif (TYPE.lower() == 'grid'):
        x = np.atleast_2d(x)
        y = np.atleast_2d(y)
    elif TYPE.lower() in ('time series', 'drift'):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

    # converting x,y from EPSG to latitude/longitude
    crs1 = pyTMD.crs().from_input(EPSG)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    lon,lat = transformer.transform(x.flatten(), y.flatten())

    # verify that delta time is an array
    delta_time = np.atleast_1d(delta_time)
    # convert delta times or datetimes objects to timescale
    if (TIME.lower() == 'datetime'):
        ts = timescale.from_datetime(delta_time.flatten())
    else:
        ts = timescale.from_deltatime(delta_time,
            epoch=EPOCH, standard=TIME)

    # number of time points
    nt = len(ts)

    # earth and physical parameters for ellipsoid
    units = pyTMD.spatial.datum(ellipsoid=ELLIPSOID, units='MKS')
    # tidal love/shida numbers appropriate for the load tide
    hb2 = 0.6207
    lb2 = 0.0836

    # convert from geodetic latitude to geocentric latitude
    # calculate X, Y and Z from geodetic latitude and longitude
    X,Y,Z = pyTMD.spatial.to_cartesian(lon.flatten(), lat.flatten(),
        a_axis=units.a_axis, flat=units.flat)
    # calculate geocentric latitude and convert to degrees
    latitude_geocentric = np.degrees(np.arctan(Z / np.sqrt(X**2.0 + Y**2.0)))
    npts = len(latitude_geocentric)
    # geocentric colatitude and longitude in radians
    theta = np.radians(90.0 - latitude_geocentric)
    phi = np.radians(lon.flatten())

    # compute normal gravity at spatial location
    # p. 80, Eqn.(2-199)
    gamma_0 = units.gamma_0(theta)

    # rotation matrix for converting from cartesian coordinates
    R = np.zeros((npts, 3, 3))
    R[:,0,0] = np.cos(phi)*np.cos(theta)
    R[:,1,0] = -np.sin(phi)
    R[:,2,0] = np.cos(phi)*np.sin(theta)
    R[:,0,1] = np.sin(phi)*np.cos(theta)
    R[:,1,1] = np.cos(phi)
    R[:,2,1] = np.sin(phi)*np.sin(theta)
    R[:,0,2] = -np.sin(theta)
    R[:,2,2] = np.cos(theta)

    # calculate radial displacement at time
    if (TYPE == 'grid'):
        ny,nx = np.shape(x)
        Srad = np.ma.zeros((ny,nx,nt), fill_value=FILL_VALUE)
        Srad.mask = np.zeros((ny,nx,nt),dtype=bool)
        XYZ = np.c_[X, Y, Z]
        for i in range(nt):
            # calculate load pole tides in cartesian coordinates
            dxi = pyTMD.predict.load_pole_tide(ts.tide[i], XYZ,
                deltat=ts.tt_ut1[i],
                gamma_0=gamma_0,
                omega=units.omega,
                h2=hb2,
                l2=lb2,
                convention=CONVENTION
            )
            # calculate components of load pole tides
            S = np.einsum('ti...,tji...->tj...', dxi, R)
            smask = np.reshape(np.any(dxi.mask, axis=1), (ny,nx))
            # reshape to output dimensions
            Srad.data[:,:,i] = np.reshape(S[:,2], (ny,nx))
            Srad.mask[:,:,i] = np.isnan(Srad.data[:,:,i]) | smask
    elif (TYPE == 'drift'):
        # calculate load pole tides in cartesian coordinates
        XYZ = np.c_[X, Y, Z]
        dxi = pyTMD.predict.load_pole_tide(ts.tide, XYZ,
            deltat=ts.tt_ut1,
            gamma_0=gamma_0,
            omega=units.omega,
            h2=hb2,
            l2=lb2,
            convention=CONVENTION
        )
        # calculate components of load pole tides
        S = np.einsum('ti...,tji...->tj...', dxi, R)
        smask = np.any(dxi.mask, axis=1)
        # reshape to output dimensions
        Srad = np.ma.zeros((nt), fill_value=FILL_VALUE)
        Srad.data[:] = S[:,2].copy()
        Srad.mask = np.isnan(Srad.data) | smask
    elif (TYPE == 'time series'):
        nstation = len(x)
        Srad = np.ma.zeros((nstation,nt), fill_value=FILL_VALUE)
        Srad.mask = np.zeros((nstation,nt),dtype=bool)
        for s in range(nstation):
            # convert coordinates to column arrays
            XYZ = np.repeat(np.c_[X[s], Y[s], Z[s]], nt, axis=0)
            # calculate load pole tides in cartesian coordinates
            dxi = pyTMD.predict.load_pole_tide(ts.tide, XYZ,
                deltat=ts.tt_ut1,
                gamma_0=gamma_0[s],
                omega=units.omega,
                h2=hb2,
                l2=lb2,
                convention=CONVENTION
            )
            # calculate components of load pole tides
            S = np.einsum('ti...,ji...->tj...', dxi, R[s,:,:])
            smask = np.any(dxi.mask, axis=1)
            # reshape to output dimensions
            Srad.data[s,:] = S[:,2].copy()
            Srad.mask[s,:] = np.isnan(Srad.data[s,:]) | smask

    # replace invalid data with fill values
    Srad.data[Srad.mask] = Srad.fill_value

    # return the load pole tide displacements
    return Srad

# PURPOSE: compute radial load pole tide displacements
# following IERS Convention (2010) guidelines
def OPT_displacements(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        EPSG: str | int = 4326,
        EPOCH: list | tuple = (2000, 1, 1, 0, 0, 0),
        TYPE: str | None = 'drift',
        TIME: str = 'UTC',
        ELLIPSOID: str = 'WGS84',
        CONVENTION: str = '2018',
        METHOD: str = 'spline',
        FILL_VALUE: float = np.nan,
        **kwargs
    ):
    """
    Compute radial ocean pole tide displacements at points and times
    following IERS Convention (2010) guidelines

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    EPSG: int, default: 4326 (WGS84 Latitude and Longitude)
        Input coordinate system
    EPOCH: tuple, default (2000,1,1,0,0,0)
        Time period for calculating delta times
    TYPE: str or NoneType, default 'drift'
        Input data type

            - ``None``: determined from input variable dimensions
            - ``'drift'``: drift buoys or satellite/airborne altimetry
            - ``'grid'``: spatial grids or images
            - ``'time series'``: time series at a single point
    TIME: str, default 'UTC'
        Time type if need to compute leap seconds to convert to UTC

            - ``'GPS'``: leap seconds needed
            - ``'LORAN'``: leap seconds needed (LORAN = GPS + 9 seconds)
            - ``'TAI'``: leap seconds needed (TAI = GPS + 19 seconds)
            - ``'UTC'``: no leap seconds needed
            - ``'datetime'``: numpy datatime array in UTC
    ELLIPSOID: str, default 'WGS84'
        Ellipsoid for calculating Earth parameters
    CONVENTION: str, default '2018'
        IERS Mean or Secular Pole Convention

            - ``'2003'``
            - ``'2010'``
            - ``'2015'``
            - ``'2018'``
    METHOD: str
        Interpolation method

            - ```bilinear```: quick bilinear interpolation
            - ```spline```: scipy bivariate spline interpolation
            - ```linear```, ```nearest```: scipy regular grid interpolations
    FILL_VALUE: float, default np.nan
        Output invalid value

    Returns
    -------
    Urad: np.ndarray
        ocean pole tide at coordinates and time in meters
    """

    # validate input arguments
    assert TIME.lower() in ('gps', 'loran', 'tai', 'utc', 'datetime')
    assert ELLIPSOID.upper() in pyTMD.spatial._ellipsoids
    assert CONVENTION.isdigit() and CONVENTION in timescale.eop._conventions
    assert METHOD.lower() in ('bilinear', 'spline', 'linear', 'nearest')
    # determine input data type based on variable dimensions
    if not TYPE:
        TYPE = pyTMD.spatial.data_type(x, y, delta_time)
    assert TYPE.lower() in ('grid', 'drift', 'time series')
    # reform coordinate dimensions for input grids
    # or verify coordinate dimension shapes
    if (TYPE.lower() == 'grid') and (np.size(x) != np.size(y)):
        x,y = np.meshgrid(np.copy(x),np.copy(y))
    elif (TYPE.lower() == 'grid'):
        x = np.atleast_2d(x)
        y = np.atleast_2d(y)
    elif TYPE.lower() in ('time series', 'drift'):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

    # converting x,y from EPSG to latitude/longitude
    crs1 = pyTMD.crs().from_input(EPSG)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    lon,lat = transformer.transform(x.flatten(), y.flatten())

    # verify that delta time is an array
    delta_time = np.atleast_1d(delta_time)
    # convert delta times or datetimes objects to timescale
    if (TIME.lower() == 'datetime'):
        ts = timescale.from_datetime(delta_time.flatten())
    else:
        ts = timescale.from_deltatime(delta_time,
            epoch=EPOCH, standard=TIME)
    # number of time points
    nt = len(ts)

    # earth and physical parameters for ellipsoid
    units = pyTMD.spatial.datum(ellipsoid=ELLIPSOID, units='MKS')
    # mean equatorial gravitational acceleration [m/s^2]
    ge = 9.7803278
    # density of sea water [kg/m^3]
    rho_w = 1025.0
    # tidal love number differential (1 + kl - hl) for pole tide frequencies
    gamma = 0.6870 + 0.0036j

    # convert from geodetic latitude to geocentric latitude
    # calculate X, Y and Z from geodetic latitude and longitude
    X,Y,Z = pyTMD.spatial.to_cartesian(lon.flatten(), lat.flatten(),
        a_axis=units.a_axis, flat=units.flat)
    # calculate geocentric latitude and convert to degrees
    latitude_geocentric = np.degrees(np.arctan(Z / np.sqrt(X**2.0 + Y**2.0)))
    npts = len(latitude_geocentric)
    # geocentric colatitude and longitude in radians
    theta = np.radians(90.0 - latitude_geocentric)
    phi = np.radians(lon.flatten())

    # read and interpolate ocean pole tide map from Desai (2002)
    ur, un, ue = pyTMD.io.IERS.extract_coefficients(lon.flatten(),
        latitude_geocentric, method=METHOD)
    # rotation matrix for converting to/from cartesian coordinates
    R = np.zeros((npts, 3, 3))
    R[:,0,0] = np.cos(phi)*np.cos(theta)
    R[:,0,1] = -np.sin(phi)
    R[:,0,2] = np.cos(phi)*np.sin(theta)
    R[:,1,0] = np.sin(phi)*np.cos(theta)
    R[:,1,1] = np.cos(phi)
    R[:,1,2] = np.sin(phi)*np.sin(theta)
    R[:,2,0] = -np.sin(theta)
    R[:,2,2] = np.cos(theta)
    Rinv = np.linalg.inv(R)

    # calculate pole tide displacements in Cartesian coordinates
    # coefficients reordered to N, E, R to match IERS rotation matrix
    UXYZ = np.einsum('ti...,tji...->tj...', np.c_[un, ue, ur], R)

    # calculate radial displacement at time
    if (TYPE == 'grid'):
        ny,nx = np.shape(x)
        Urad = np.ma.zeros((ny,nx,nt), fill_value=FILL_VALUE)
        Urad.mask = np.zeros((ny,nx,nt),dtype=bool)
        XYZ = np.c_[X, Y, Z]
        for i in range(nt):
            # calculate ocean pole tides in cartesian coordinates
            dxi = pyTMD.predict.ocean_pole_tide(ts.tide[i], XYZ, UXYZ,
                deltat=ts.tt_ut1[i],
                a_axis=units.a_axis,
                gamma_0=ge,
                GM=units.GM,
                omega=units.omega,
                rho_w=rho_w,
                g2=gamma,
                convention=CONVENTION
            )
            # calculate components of ocean pole tides
            U = np.einsum('ti...,tji...->tj...', dxi, Rinv)
            umask = np.reshape(np.any(dxi.mask, axis=1), (ny,nx))
            # reshape to output dimensions
            Urad.data[:,:,i] = np.reshape(U[:,2], (ny,nx))
            Urad.mask[:,:,i] = np.isnan(Urad.data[:,:,i]) | umask
    elif (TYPE == 'drift'):
        # calculate ocean pole tides in cartesian coordinates
        XYZ = np.c_[X, Y, Z]
        dxi = pyTMD.predict.ocean_pole_tide(ts.tide, XYZ, UXYZ,
            deltat=ts.tt_ut1,
            a_axis=units.a_axis,
            gamma_0=ge,
            GM=units.GM,
            omega=units.omega,
            rho_w=rho_w,
            g2=gamma,
            convention=CONVENTION
        )
        # calculate components of ocean pole tides
        U = np.einsum('ti...,tji...->tj...', dxi, Rinv)
        umask = np.any(dxi.mask, axis=1)
        # convert to masked array
        Urad = np.ma.zeros((nt), fill_value=FILL_VALUE)
        Urad.data[:] = U[:,2].copy()
        Urad.mask = np.isnan(Urad.data) | umask
    elif (TYPE == 'time series'):
        nstation = len(x)
        Urad = np.ma.zeros((nstation,nt), fill_value=FILL_VALUE)
        Urad.mask = np.zeros((nstation,nt),dtype=bool)
        for s in range(nstation):
            # convert coordinates to column arrays
            XYZ = np.repeat(np.c_[X[s], Y[s], Z[s]], nt, axis=0)
            uxyz = np.repeat(np.atleast_2d(UXYZ[s,:]), nt, axis=0)
            # calculate ocean pole tides in cartesian coordinates
            dxi = pyTMD.predict.ocean_pole_tide(ts.tide, XYZ, uxyz,
                deltat=ts.tt_ut1,
                a_axis=units.a_axis,
                gamma_0=ge,
                GM=units.GM,
                omega=units.omega,
                rho_w=rho_w,
                g2=gamma,
                convention=CONVENTION
            )
            # calculate components of ocean pole tides
            U = np.einsum('ti...,ji...->tj...', dxi, Rinv[s,:,:])
            umask = np.any(dxi.mask, axis=1)
            # reshape to output dimensions
            Urad.data[s,:] = U[:,2].copy()
            Urad.mask[s,:] = np.isnan(Urad.data[s,:]) | umask

    # replace invalid data with fill values
    Urad.data[Urad.mask] = Urad.fill_value

    # return the ocean pole tide displacements
    return Urad

# PURPOSE: compute solid earth tidal elevations
def SET_displacements(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        METHOD: str = 'ephemerides',
        **kwargs
    ):
    """
    Compute solid earth tidal elevations (body tides) at points and times

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    METHOD: str, default 'IERS'
        method for calculating solid earth tidal elevations

            - ``'ephemerides'``: following :cite:t:`Petit:2010tp` guidelines
            - ``'catalog'``: using tide potential catalogs
    """
    if (METHOD.lower() == 'ephemerides'):
        return _ephemeride_SET(
            x, y, delta_time,
            **kwargs
        )
    elif (METHOD.lower() == 'catalog'):
        return _catalog_SET(
            x, y, delta_time,
            **kwargs
        )
    else:
        raise ValueError(f"Invalid METHOD: {METHOD}")

# PURPOSE: compute solid earth tides following IERS conventions
def _ephemeride_SET(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        EPSG: str | int = 4326,
        EPOCH: list | tuple = (2000, 1, 1, 0, 0, 0),
        TYPE: str | None = 'drift',
        TIME: str = 'UTC',
        ELLIPSOID: str = 'WGS84',
        TIDE_SYSTEM: str = 'tide_free',
        EPHEMERIDES: str = 'approximate',
        **kwargs
    ):
    """
    Compute solid earth tidal elevations at points and times
    following IERS Convention (2010) guidelines

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    EPSG: int, default: 4326 (WGS84 Latitude and Longitude)
        Input coordinate system
    EPOCH: tuple, default (2000,1,1,0,0,0)
        Time period for calculating delta times
    TYPE: str or NoneType, default 'drift'
        Input data type

            - ``None``: determined from input variable dimensions
            - ``'drift'``: drift buoys or satellite/airborne altimetry
            - ``'grid'``: spatial grids or images
            - ``'time series'``: time series at a single point
    TIME: str, default 'UTC'
        Time type if need to compute leap seconds to convert to UTC

            - ``'GPS'``: leap seconds needed
            - ``'LORAN'``: leap seconds needed (LORAN = GPS + 9 seconds)
            - ``'TAI'``: leap seconds needed (TAI = GPS + 19 seconds)
            - ``'UTC'``: no leap seconds needed
            - ``'datetime'``: numpy datatime array in UTC
    ELLIPSOID: str, default 'WGS84'
        Ellipsoid for calculating Earth parameters
    TIDE_SYSTEM: str, default 'tide_free'
        Permanent tide system for the output solid Earth tide

            - ``'tide_free'``: no permanent direct and indirect tidal potentials
            - ``'mean_tide'``: permanent tidal potentials (direct and indirect)
    EPHEMERIDES: str, default 'approximate'
        Ephemerides for calculating Earth parameters

            - ``'approximate'``: approximate lunisolar parameters
            - ``'JPL'``: computed from JPL ephmerides kernel

    Returns
    -------
    tide_se: np.ndarray
        solid earth tide at coordinates and time in meters
    """

    # validate input arguments
    assert TIME.lower() in ('gps', 'loran', 'tai', 'utc', 'datetime')
    assert TIDE_SYSTEM.lower() in ('mean_tide', 'tide_free')
    assert EPHEMERIDES.lower() in ('approximate', 'jpl')
    # determine input data type based on variable dimensions
    if not TYPE:
        TYPE = pyTMD.spatial.data_type(x, y, delta_time)
    assert TYPE.lower() in ('grid', 'drift', 'time series')
    # reform coordinate dimensions for input grids
    # or verify coordinate dimension shapes
    if (TYPE.lower() == 'grid') and (np.size(x) != np.size(y)):
        x,y = np.meshgrid(np.copy(x),np.copy(y))
    elif (TYPE.lower() == 'grid'):
        x = np.atleast_2d(x)
        y = np.atleast_2d(y)
    elif TYPE.lower() in ('time series', 'drift'):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

    # converting x,y from EPSG to latitude/longitude
    crs1 = pyTMD.crs().from_input(EPSG)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    lon, lat = transformer.transform(x.flatten(), y.flatten())

    # verify that delta time is an array
    delta_time = np.atleast_1d(delta_time)
    # convert delta times or datetimes objects to timescale
    if (TIME.lower() == 'datetime'):
        ts = timescale.from_datetime(delta_time.flatten())
    else:
        ts = timescale.from_deltatime(delta_time,
            epoch=EPOCH, standard=TIME)
    # convert tide times to dynamical time
    tide_time = ts.tide + ts.tt_ut1
    # number of time points
    nt = len(ts)

    # earth and physical parameters for ellipsoid
    units = pyTMD.spatial.datum(ellipsoid=ELLIPSOID, units='MKS')

    # convert input coordinates to cartesian
    X, Y, Z = pyTMD.spatial.to_cartesian(lon, lat,
        a_axis=units.a_axis, flat=units.flat)
    # compute ephemerides for lunisolar coordinates
    SX, SY, SZ = pyTMD.astro.solar_ecef(ts.MJD, ephemerides=EPHEMERIDES)
    LX, LY, LZ = pyTMD.astro.lunar_ecef(ts.MJD, ephemerides=EPHEMERIDES)

    # geocentric latitude (radians)
    latitude_geocentric = np.arctan(Z / np.sqrt(X**2.0 + Y**2.0))
    npts = len(latitude_geocentric)
    # geocentric colatitude (radians)
    theta = (np.pi/2.0 - latitude_geocentric)
    # calculate longitude (radians)
    phi = np.arctan2(Y, X)
    # rotation matrix for converting from cartesian coordinates
    R = np.zeros((npts, 3, 3))
    R[:,0,0] = np.cos(phi)*np.cos(theta)
    R[:,1,0] = -np.sin(phi)
    R[:,2,0] = np.cos(phi)*np.sin(theta)
    R[:,0,1] = np.sin(phi)*np.cos(theta)
    R[:,1,1] = np.cos(phi)
    R[:,2,1] = np.sin(phi)*np.sin(theta)
    R[:,0,2] = -np.sin(theta)
    R[:,2,2] = np.cos(theta)

    # calculate radial displacement at time
    if (TYPE == 'grid'):
        ny,nx = np.shape(x)
        tide_se = np.zeros((ny,nx,nt))
        # convert coordinates to column arrays
        XYZ = np.c_[X, Y, Z]
        for i in range(nt):
            # reshape time to match spatial
            t = tide_time[i] + np.ones((ny*nx))
            # convert coordinates to column arrays
            SXYZ = np.repeat(np.c_[SX[i], SY[i], SZ[i]], ny*nx, axis=0)
            LXYZ = np.repeat(np.c_[LX[i], LY[i], LZ[i]], ny*nx, axis=0)
            # predict solid earth tides (cartesian)
            dxi = pyTMD.predict.solid_earth_tide(t,
                XYZ, SXYZ, LXYZ, a_axis=units.a_axis,
                tide_system=TIDE_SYSTEM)
            # calculate components of solid earth tides
            SE = np.einsum('ti...,tji...->tj...', dxi, R)
            # reshape to output dimensions
            tide_se[:,:,i] = np.reshape(SE[:,2], (ny,nx))
    elif (TYPE == 'drift'):
        # convert coordinates to column arrays
        XYZ = np.c_[X, Y, Z]
        SXYZ = np.c_[SX, SY, SZ]
        LXYZ = np.c_[LX, LY, LZ]
        # predict solid earth tides (cartesian)
        dxi = pyTMD.predict.solid_earth_tide(tide_time,
            XYZ, SXYZ, LXYZ, a_axis=units.a_axis,
            tide_system=TIDE_SYSTEM)
        # calculate components of solid earth tides
        SE = np.einsum('ti...,tji...->tj...', dxi, R)
        # reshape to output dimensions
        tide_se = SE[:,2].copy()
    elif (TYPE == 'time series'):
        nstation = len(x)
        tide_se = np.zeros((nstation,nt))
        # convert coordinates to column arrays
        SXYZ = np.c_[SX, SY, SZ]
        LXYZ = np.c_[LX, LY, LZ]
        for s in range(nstation):
            # convert coordinates to column arrays
            XYZ = np.repeat(np.c_[X[s], Y[s], Z[s]], nt, axis=0)
            # predict solid earth tides (cartesian)
            dxi = pyTMD.predict.solid_earth_tide(tide_time,
                XYZ, SXYZ, LXYZ, a_axis=units.a_axis,
                tide_system=TIDE_SYSTEM)
            # calculate components of solid earth tides
            SE = np.einsum('ti...,ji...->tj...', dxi, R[s,:,:])
            # reshape to output dimensions
            tide_se[s,:] = SE[:,2].copy()

    # return the solid earth tide displacements
    return tide_se

# PURPOSE: compute body tides following Cartwright and Tayler (1971)
def _catalog_SET(
        x: np.ndarray, y: np.ndarray, delta_time: np.ndarray,
        EPSG: str | int = 4326,
        EPOCH: list | tuple = (2000, 1, 1, 0, 0, 0),
        TYPE: str | None = 'drift',
        TIME: str = 'UTC',
        CATALOG: str = 'CTE1973',
        TIDE_SYSTEM: str = 'tide_free',
        EPHEMERIDES: str = 'IERS',
        INCLUDE_PLANETS: bool = False,
        **kwargs
    ):
    """
    Compute solid earth tidal elevations at points and times
    using a tide-potential catalog following :cite:t:`Cartwright:1971iz`

    Parameters
    ----------
    x: np.ndarray
        x-coordinates in projection EPSG
    y: np.ndarray
        y-coordinates in projection EPSG
    delta_time: np.ndarray
        seconds since EPOCH or datetime array
    EPSG: int, default: 4326 (WGS84 Latitude and Longitude)
        Input coordinate system
    EPOCH: tuple, default (2000,1,1,0,0,0)
        Time period for calculating delta times
    TYPE: str or NoneType, default 'drift'
        Input data type

            - ``None``: determined from input variable dimensions
            - ``'drift'``: drift buoys or satellite/airborne altimetry
            - ``'grid'``: spatial grids or images
            - ``'time series'``: time series at a single point
    TIME: str, default 'UTC'
        Time type if need to compute leap seconds to convert to UTC

            - ``'GPS'``: leap seconds needed
            - ``'LORAN'``: leap seconds needed (LORAN = GPS + 9 seconds)
            - ``'TAI'``: leap seconds needed (TAI = GPS + 19 seconds)
            - ``'UTC'``: no leap seconds needed
            - ``'datetime'``: numpy datatime array in UTC
    CATALOG: str, default 'CTE1973'
        Name of the tide potential catalog

            - ``'CTE1973'``: :cite:t:`Cartwright:1973em`
            - ``'HW1995'``: :cite:t:`Hartmann:1995jp`
            - ``'T1987'``: :cite:t:`Tamura:1987tp`
            - ``'W1990'``: Woodworth updates to ``'CTE1973'``
    TIDE_SYSTEM: str, default 'tide_free'
        Permanent tide system for the output solid Earth tide

            - ``'tide_free'``: no permanent direct and indirect tidal potentials
            - ``'mean_tide'``: permanent tidal potentials (direct and indirect)
    EPHEMERIDES: str, default 'IERS'
        Method for calculating astronomical mean longitudes

            - ``'Cartwright'``: use coefficients from David Cartwright
            - ``'Meeus'``: use coefficients from Meeus Astronomical Algorithms
            - ``'ASTRO5'``: use Meeus Astronomical coefficients from ``ASTRO5``
            - ``'IERS'``: convert from IERS Delaunay arguments
    INCLUDE_PLANETS: bool, default False
        Include tide potentials from planetary bodies

    Returns
    -------
    tide_se: np.ndarray
        solid earth tide at coordinates and time in meters
    """

    # validate input arguments
    assert TIME.lower() in ('gps', 'loran', 'tai', 'utc', 'datetime')
    assert TIDE_SYSTEM.lower() in ('mean_tide', 'tide_free')
    assert CATALOG in pyTMD.predict._tide_potential_table.keys()
    assert EPHEMERIDES.lower() in ('cartwright', 'meeus', 'astro5', 'iers')
    # determine input data type based on variable dimensions
    if not TYPE:
        TYPE = pyTMD.spatial.data_type(x, y, delta_time)
    assert TYPE.lower() in ('grid', 'drift', 'time series')
    # reform coordinate dimensions for input grids
    # or verify coordinate dimension shapes
    if (TYPE.lower() == 'grid') and (np.size(x) != np.size(y)):
        x,y = np.meshgrid(np.copy(x),np.copy(y))
    elif (TYPE.lower() == 'grid'):
        x = np.atleast_2d(x)
        y = np.atleast_2d(y)
    elif TYPE.lower() in ('time series', 'drift'):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

    # converting x,y from EPSG to latitude/longitude
    crs1 = pyTMD.crs().from_input(EPSG)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    lon, lat = transformer.transform(x.flatten(), y.flatten())

    # verify that delta time is an array
    delta_time = np.atleast_1d(delta_time)
    # convert delta times or datetimes objects to timescale
    if (TIME.lower() == 'datetime'):
        ts = timescale.from_datetime(delta_time.flatten())
    else:
        ts = timescale.from_deltatime(delta_time,
            epoch=EPOCH, standard=TIME)
    # number of time points
    nt = len(ts)

    # calculate radial displacement at time
    if (TYPE == 'grid'):
        ny,nx = np.shape(x)
        tide_se = np.zeros((ny,nx,nt))
        for i in range(nt):
            # reshape time to match spatial
            t = ts.tide[i] + np.ones((ny*nx))
            deltat = ts.tt_ut1 + np.ones((ny*nx))
            # calculate body tides
            SE = pyTMD.predict.body_tide(t, lon, lat, 
                deltat=deltat,
                method=EPHEMERIDES,
                tide_system=TIDE_SYSTEM,
                catalog=CATALOG,
                include_planets=INCLUDE_PLANETS,
                **kwargs)
            # reshape to output dimensions
            tide_se[:,:,i] = np.reshape(SE[:,2], (ny,nx))
    elif (TYPE == 'drift'):
        # calculate body tides
        SE = pyTMD.predict.body_tide(ts.tide, lon, lat, 
            deltat=ts.tt_ut1,
            method=EPHEMERIDES,
            tide_system=TIDE_SYSTEM,
            catalog=CATALOG,
            include_planets=INCLUDE_PLANETS,
            **kwargs)
        # reshape to output dimensions
        tide_se = SE[:,2].copy()
    elif (TYPE == 'time series'):
        nstation = len(x)
        tide_se = np.zeros((nstation,nt))
        for s in range(nstation):
            # calculate body tides
            SE = pyTMD.predict.body_tide(ts.tide, lon[s], lat[s], 
                deltat=ts.tt_ut1,
                method=EPHEMERIDES,
                tide_system=TIDE_SYSTEM,
                catalog=CATALOG,
                include_planets=INCLUDE_PLANETS,
                **kwargs)
            # reshape to output dimensions
            tide_se[s,:] = SE[:,2].copy()

    # return the solid earth tide displacements
    return tide_se
