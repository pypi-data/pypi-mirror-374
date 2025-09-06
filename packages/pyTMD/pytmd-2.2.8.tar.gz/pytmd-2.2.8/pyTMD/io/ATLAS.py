#!/usr/bin/env python
u"""
ATLAS.py
Written by Tyler Sutterley (08/2025)

Reads files for a tidal model and makes initial calculations to run tide program
Includes functions to extract tidal harmonic constants from OTIS tide models for
    given locations
netCDF4 files can be been compressed using gzip

Reads netCDF4 ATLAS tidal solutions provided by Oregon State University and ESR
    http://volkov.oce.orst.edu/tides/region.html
    https://www.esr.org/research/polar-tide-models/list-of-polar-tide-models/
    ftp://ftp.esr.org/pub/datasets/tmd/

INPUTS:
    ilon: longitude to interpolate
    ilat: latitude to interpolate
    grid_file: grid file for model (can be gzipped)
    model_files: list of model files for each constituent (can be gzipped)

OPTIONS:
    type: tidal variable to run
        z: heights
        u: horizontal transport velocities
        U: horizontal depth-averaged transport
        v: vertical transport velocities
        V: vertical depth-averaged transport
    method: interpolation method
        bilinear: quick bilinear interpolation
        spline: scipy bivariate spline interpolation
        linear, nearest: scipy regular grid interpolations
    extrapolate: extrapolate model using nearest-neighbors
    cutoff: extrapolation cutoff in kilometers
        set to np.inf to extrapolate for all points
    compressed: input netCDF4 files are gzip compressed
    scale: scaling factor for converting to output units

OUTPUTS:
    amplitude: amplitudes of tidal constituents
    phase: phases of tidal constituents
    D: bathymetry of tide model
    constituents: list of model constituents

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
    scipy: Scientific Tools for Python
        https://docs.scipy.org/doc/
    netCDF4: Python interface to the netCDF C library
        https://unidata.github.io/netcdf4-python/netCDF4/index.html

PROGRAM DEPENDENCIES:
    interpolate.py: interpolation routines for spatial data

UPDATE HISTORY:
    Updated 08/2025: use numpy degree to radian conversions
        added option to gap fill when reading constituent grids
    Updated 11/2024: expose buffer distance for cropping tide model data
    Updated 10/2024: fix error when using default bounds in extract_constants
    Updated 07/2024: added crop and bounds keywords for trimming model data
    Updated 02/2024: changed variable for setting global grid flag to is_global
    Updated 10/2023: add generic wrapper function for reading constituents
    Updated 04/2023: using pathlib to define and expand tide model paths
    Updated 03/2023: add basic variable typing to function inputs
    Updated 12/2022: refactor tide read programs under io
        new functions to read and interpolate from constituents class
        new functions to output ATLAS formatted netCDF4 files
        refactored interpolation routines into new module
    Updated 11/2022: place some imports within try/except statements
        use f-strings for formatting verbose or ascii output
    Updated 07/2022: fix setting of masked array data to NaN
    Updated 05/2022: reformat arguments to extract_netcdf_constants definition
        changed keyword arguments to camel case
    Updated 04/2022: updated docstrings to numpy documentation format
    Updated 12/2021: adjust longitude convention based on model longitude
    Updated 09/2021: fix cases where there is no mask on constituent files
    Updated 07/2021: added check that tide model files are accessible
    Updated 06/2021: add warning for tide models being entered as string
    Updated 05/2021: added option for extrapolation cutoff in kilometers
    Updated 03/2021: add extrapolation check where there are no invalid points
        prevent ComplexWarning for fill values when calculating amplitudes
        simplified inputs to be similar to binary OTIS read program
    Updated 02/2021: set invalid values to nan in extrapolation
        replaced numpy bool to prevent deprecation warning
    Updated 12/2020: added valid data extrapolation with nearest_extrap
        replace tostring with tobytes to fix DeprecationWarning
    Updated 11/2020: create function to read bathymetry and spatial coordinates
    Updated 09/2020: set bounds error to false for regular grid interpolations
        adjust dimensions of input coordinates to be iterable
        reduce number of interpolations by copying bathymetry mask to variables
    Updated 08/2020: replaced griddata with scipy regular grid interpolators
    Updated 07/2020: added function docstrings. separate bilinear interpolation
        changed TYPE variable to keyword argument. update griddata interpolation
    Updated 06/2020: use argmin and argmax in bilinear interpolation
    Written 09/2019
"""
from __future__ import division, annotations

import copy
import gzip
import uuid
import logging
import pathlib
import datetime
import warnings
import numpy as np
import pyTMD.version
import pyTMD.io.constituents
import pyTMD.interpolate
from pyTMD.utilities import import_dependency

# attempt imports
netCDF4 = import_dependency('netCDF4')

__all__ = [
    "extract_constants",
    "read_constants",
    "interpolate_constants",
    "read_netcdf_grid",
    "read_netcdf_file",
    "read_netcdf_elevation",
    "read_netcdf_transport",
    "output_netcdf_grid",
    "output_netcdf_elevation",
    "output_netcdf_transport",
    "_extend_array",
    "_extend_matrix",
    "_crop",
    "_shift"
]

# PURPOSE: extract harmonic constants from tide models at coordinates
def extract_constants(
        ilon: np.ndarray, ilat: np.ndarray,
        grid_file: str | pathlib.Path | None = None,
        model_files: str | list | pathlib.Path | None = None,
        **kwargs
    ):
    """
    Reads files for ATLAS netCDF4 tidal models

    Makes initial calculations to run the tide program

    Spatially interpolates tidal constituents to input coordinates

    Parameters
    ----------
    ilon: np.ndarray
        longitude to interpolate
    ilat: np.ndarray
        latitude to interpolate
    grid_file: str, pathlib.Path or NoneType, default None
        grid file for model
    model_files: str, list, pathlib.Path or NoneType, default None
        list of model files for each constituent
    type: str, default 'z'
        Tidal variable to read

            - ``'z'``: heights
            - ``'u'``: horizontal transport velocities
            - ``'U'``: horizontal depth-averaged transport
            - ``'v'``: vertical transport velocities
            - ``'V'``: vertical depth-averaged transport
    crop: bool, default False
        Crop tide model data to (buffered) bounds
    bounds: list or NoneType, default None
        Boundaries for cropping tide model data
    buffer: int, float or NoneType, default None
        Buffer angle for cropping tide model data
    method: str, default 'spline'
        Interpolation method

            - ``'bilinear'``: quick bilinear interpolation
            - ``'spline'``: scipy bivariate spline interpolation
            - ``'linear'``, ``'nearest'``: scipy regular grid interpolations
    extrapolate: bool, default False
        Extrapolate model using nearest-neighbors
    cutoff: float, default 10.0
        Extrapolation cutoff in kilometers

        Set to ``np.inf`` to extrapolate for all points
    compressed: bool, default False
        Input files are gzip compressed
    scale: float, default 1.0
        Scaling factor for converting to output units

    Returns
    -------
    amplitude: np.ndarray
        amplitudes of tidal constituents
    phase: np.ndarray
        phases of tidal constituents
    D: np.ndarray
        bathymetry of tide model
    constituents: list
        Tide model constituent names
    """
    # set default keyword arguments
    kwargs.setdefault('type', 'z')
    kwargs.setdefault('crop', False)
    kwargs.setdefault('bounds', None)
    kwargs.setdefault('buffer', None)
    kwargs.setdefault('method', 'spline')
    kwargs.setdefault('extrapolate', False)
    kwargs.setdefault('cutoff', 10.0)
    kwargs.setdefault('compressed', True)
    kwargs.setdefault('scale', 1.0)
    # raise warnings for deprecated keyword arguments
    deprecated_keywords = dict(TYPE='type', METHOD='method',
        EXTRAPOLATE='extrapolate', CUTOFF='cutoff',
        GZIP='compressed', SCALE='scale')
    for old,new in deprecated_keywords.items():
        if old in kwargs.keys():
            warnings.warn(f"""Deprecated keyword argument {old}.
                Changed to '{new}'""", DeprecationWarning)
            # set renamed argument to not break workflows
            kwargs[new] = copy.copy(kwargs[old])

    # raise warning if model files are entered as a string or path
    if isinstance(model_files, (str, pathlib.Path)):
        warnings.warn("Tide model is entered as a string")
        model_files = [model_files]

    # check that grid file is accessible
    grid_file = pathlib.Path(grid_file).expanduser()
    if not grid_file.exists():
        raise FileNotFoundError(str(grid_file))

    # read the tide grid file for bathymetry and spatial coordinates
    lon, lat, bathymetry = read_netcdf_grid(grid_file, kwargs['type'],
        compressed=kwargs['compressed'])

    # adjust dimensions of input coordinates to be iterable
    ilon = np.atleast_1d(np.copy(ilon))
    ilat = np.atleast_1d(np.copy(ilat))
    # default bounds if cropping
    xmin, xmax = np.min(ilon), np.max(ilon)
    ymin, ymax = np.min(ilat), np.max(ilat)
    bounds = kwargs['bounds'] or [xmin, xmax, ymin, ymax]
    # grid step size of tide model
    dlon = lon[1] - lon[0]
    # default buffer if cropping data
    buffer = kwargs['buffer'] or 4*dlon
    # if global: extend limits
    is_global = False

    # crop bathymetry data to (buffered) bounds
    # or adjust longitudinal convention to fit tide model
    if kwargs['crop'] and np.any(bounds):
        mlon, mlat = np.copy(lon), np.copy(lat)
        bathymetry, lon, lat = _crop(bathymetry, mlon, mlat,
            bounds=bounds,
            buffer=buffer
        )
    elif (np.min(ilon) < 0.0) & (np.max(lon) > 180.0):
        # input points convention (-180:180)
        # tide model convention (0:360)
        ilon[ilon < 0.0] += 360.0
    elif (np.max(ilon) > 180.0) & (np.min(lon) < 0.0):
        # input points convention (0:360)
        # tide model convention (-180:180)
        ilon[ilon > 180.0] -= 360.0

    # replace original values with extend arrays/matrices
    if np.isclose(lon[-1] - lon[0], 360.0 - dlon):
        lon = _extend_array(lon, dlon)
        bathymetry = _extend_matrix(bathymetry)
        # set global grid flag
        is_global = True
    # create masks
    bathymetry.mask = (bathymetry.data == 0)
    # determine if any input points are outside of the model bounds
    invalid = (ilon < lon.min()) | (ilon > lon.max()) | \
              (ilat < lat.min()) | (ilat > lat.max())

    # number of points
    npts = len(ilon)
    # interpolate bathymetry and mask to output points
    if (kwargs['method'] == 'bilinear'):
        # replace invalid values with nan
        bathymetry.data[bathymetry.mask] = np.nan
        # use quick bilinear to interpolate values
        D = pyTMD.interpolate.bilinear(lon, lat, bathymetry, ilon, ilat,
            fill_value=np.ma.default_fill_value(np.dtype(float)))
        # replace nan values with fill_value
        D.mask[:] |= np.isnan(D.data)
        D.data[D.mask] = D.fill_value
    elif (kwargs['method'] == 'spline'):
        # use scipy bivariate splines to interpolate values
        D = pyTMD.interpolate.spline(lon, lat, bathymetry, ilon, ilat,
            reducer=np.ceil, kx=1, ky=1)
    else:
        # use scipy regular grid to interpolate values for a given method
        D = pyTMD.interpolate.regulargrid(lon, lat, bathymetry, ilon, ilat,
            method=kwargs['method'], reducer=np.ceil, bounds_error=False)

    # u and v are velocities in cm/s
    if kwargs['type'] in ('v','u'):
        unit_conv = (D.data/100.0)
    # h is elevation values in m
    # U and V are transports in m^2/s
    elif kwargs['type'] in ('z','V','U'):
        unit_conv = 1.0

    # number of constituents
    nc = len(model_files)
    # list of constituents
    constituents = []
    # amplitude and phase
    ampl = np.ma.zeros((npts, nc))
    ampl.mask = np.zeros((npts, nc), dtype=bool)
    ph = np.ma.zeros((npts, nc))
    ph.mask = np.zeros((npts, nc), dtype=bool)
    # read and interpolate each constituent
    for i, model_file in enumerate(model_files):
        # check that model file is accessible
        model_file = pathlib.Path(model_file).expanduser()
        if not model_file.exists():
            raise FileNotFoundError(str(model_file))
        # read constituent from netCDF4 file
        hc, cons = read_netcdf_file(model_file, kwargs['type'],
            compressed=kwargs['compressed'])
        # append constituent to list
        constituents.append(cons)
        # crop tide model data to (buffered) bounds
        if kwargs['crop'] and np.any(bounds):
            hc, _, _ = _crop(hc, mlon, mlat,
                bounds=bounds,
                buffer=buffer
            )
        # replace original values with extend matrices
        if is_global:
            hc = _extend_matrix(hc)
        # update constituent mask with bathymetry mask
        hc.mask[:] |= bathymetry.mask[:]
        # interpolate amplitude and phase of the constituent
        if (kwargs['method'] == 'bilinear'):
            # replace invalid values with nan
            hc.data[hc.mask] = np.nan
            hci = pyTMD.interpolate.bilinear(lon, lat, hc, ilon, ilat,
                dtype=hc.dtype)
            # mask invalid values
            hci.mask[:] |= np.copy(D.mask)
            hci.data[hci.mask] = hci.fill_value
        elif (kwargs['method'] == 'spline'):
            # use scipy bivariate splines to interpolate values
            hci = pyTMD.interpolate.spline(lon, lat, hc, ilon, ilat,
                dtype=hc.dtype,
                reducer=np.ceil,
                kx=1, ky=1)
            # mask invalid values
            hci.mask[:] |= np.copy(D.mask)
            hci.data[hci.mask] = hci.fill_value
        else:
            # use scipy regular grid to interpolate values
            hci = pyTMD.interpolate.regulargrid(lon, lat, hc, ilon, ilat,
                dtype=hc.dtype,
                method=kwargs['method'],
                reducer=np.ceil,
                bounds_error=False)
            # mask invalid values
            hci.mask[:] |= np.copy(D.mask)
            hci.data[hci.mask] = hci.fill_value
        # extrapolate data using nearest-neighbors
        if kwargs['extrapolate'] and np.any(hci.mask):
            # find invalid data points
            inv, = np.nonzero(hci.mask)
            # replace invalid values with nan
            hc.data[hc.mask] = np.nan
            # extrapolate points within cutoff of valid model points
            hci[inv] = pyTMD.interpolate.extrapolate(lon, lat, hc,
                ilon[inv], ilat[inv], dtype=hc.dtype,
                cutoff=kwargs['cutoff'])
        # convert units
        # amplitude and phase of the constituent
        ampl.data[:,i] = np.abs(hci.data)/unit_conv
        ampl.mask[:,i] = np.copy(hci.mask)
        ph.data[:,i] = np.arctan2(-np.imag(hci.data), np.real(hci.data))
        ph.mask[:,i] = np.copy(hci.mask)
        # update mask to invalidate points outside model domain
        ampl.mask[:,i] |= invalid
        ph.mask[:,i] |= invalid

    # convert amplitude from input units to meters
    amplitude = ampl*kwargs['scale']
    # convert phase to degrees
    phase = np.degrees(ph)
    phase[phase < 0] += 360.0
    # return the interpolated values
    return (amplitude, phase, D, constituents)

# PURPOSE: read harmonic constants from tide models
def read_constants(
        grid_file: str | pathlib.Path | None = None,
        model_files: str | list | pathlib.Path | None = None,
        **kwargs
    ):
    """
    Reads files for ATLAS netCDF4 tidal models

    Parameters
    ----------
    grid_file: str, pathlib.Path or NoneType, default None
        grid file for model
    model_files: str, list, pathlib.Path or NoneType, default None
        list of model files for each constituent
    type: str, default 'z'
        Tidal variable to read

            - ``'z'``: heights
            - ``'u'``: horizontal transport velocities
            - ``'U'``: horizontal depth-averaged transport
            - ``'v'``: vertical transport velocities
            - ``'V'``: vertical depth-averaged transport
    compressed: bool, default False
        Input files are gzip compressed
    gap_fill: bool, default False
        Gap fill missing data in constituents
    crop: bool, default False
        Crop tide model data to (buffered) bounds
    bounds: list or NoneType, default None
        Boundaries for cropping tide model data
    buffer: int or float, default 0
        Buffer angle for cropping tide model data

    Returns
    -------
    constituents: obj
        complex form of tide model constituents
    """
    # set default keyword arguments
    kwargs.setdefault('type', 'z')
    kwargs.setdefault('compressed', True)
    kwargs.setdefault('gap_fill', False)
    kwargs.setdefault('crop', False)
    kwargs.setdefault('bounds', None)
    kwargs.setdefault('buffer', 0)

    # raise warning if model files are entered as a string or path
    if isinstance(model_files, (str, pathlib.Path)):
        warnings.warn("Tide model is entered as a string")
        model_files = [model_files]

    # check that grid file is accessible
    grid_file = pathlib.Path(grid_file).expanduser()
    if not grid_file.exists():
        raise FileNotFoundError(str(grid_file))

    # read the tide grid file for bathymetry and spatial coordinates
    lon, lat, bathymetry = read_netcdf_grid(grid_file, kwargs['type'],
        compressed=kwargs['compressed'])
    is_global = False

    # crop bathymetry data to (buffered) bounds
    if kwargs['crop'] and np.any(kwargs['bounds']):
        mlon, mlat = np.copy(lon), np.copy(lat)
        bathymetry, lon, lat = _crop(bathymetry, mlon, mlat,
            bounds=kwargs['bounds'],
            buffer=kwargs['buffer'],
        )
    # grid step size of tide model
    dlon = lon[1] - lon[0]
    # replace original values with extend arrays/matrices
    if np.isclose(lon[-1] - lon[0], 360.0 - dlon):
        lon = _extend_array(lon, dlon)
        bathymetry = _extend_matrix(bathymetry)
        is_global = True
    # save output constituents
    constituents = pyTMD.io.constituents(
        longitude=lon,
        latitude=lat,
        bathymetry=bathymetry.data,
        mask=bathymetry.mask
        )

    # read each model constituent
    for i, model_file in enumerate(model_files):
        # check that model file is accessible
        model_file = pathlib.Path(model_file).expanduser()
        if not model_file.exists():
            raise FileNotFoundError(str(model_file))
        # read constituent from netCDF4 file
        hc, cons = read_netcdf_file(model_file, kwargs['type'],
            compressed=kwargs['compressed'])
        # crop tide model data to (buffered) bounds
        if kwargs['crop'] and np.any(kwargs['bounds']):
            hc, lon, lat = _crop(hc, mlon, mlat,
                bounds=kwargs['bounds'],
                buffer=kwargs['buffer'],
            )
        # replace original values with extend matrices
        if is_global:
            hc = _extend_matrix(hc)
        # set constituent masks
        hc.mask[:] |= bathymetry.mask[:]
        # gap fill missing data in constituent
        if kwargs['gap_fill']:
            hc = pyTMD.interpolate.inpaint(lon, lat, hc, **kwargs)
        # append extended constituent
        constituents.append(cons,  hc)

    # return the complex form of the model constituents
    return constituents

# PURPOSE: interpolate constants from tide models to input coordinates
def interpolate_constants(
        ilon: np.ndarray,
        ilat: np.ndarray,
        constituents,
        **kwargs
    ):
    """
    Interpolate constants from ATLAS tidal models to input coordinates

    Makes initial calculations to run the tide program

    Parameters
    ----------
    ilon: np.ndarray
        longitude to interpolate
    ilat: np.ndarray
        latitude to interpolate
    constituents: obj
        Tide model constituents (complex form)
    type: str, default 'z'
        Tidal variable to read

            - ``'z'``: heights
            - ``'u'``: horizontal transport velocities
            - ``'U'``: horizontal depth-averaged transport
            - ``'v'``: vertical transport velocities
            - ``'V'``: vertical depth-averaged transport
    method: str, default 'spline'
        Interpolation method

            - ``'bilinear'``: quick bilinear interpolation
            - ``'spline'``: scipy bivariate spline interpolation
            - ``'linear'``, ``'nearest'``: scipy regular grid interpolations
    extrapolate: bool, default False
        Extrapolate model using nearest-neighbors
    cutoff: float, default 10.0
        Extrapolation cutoff in kilometers

        Set to ``np.inf`` to extrapolate for all points
    scale: float, default 1.0
        Scaling factor for converting to output units

    Returns
    -------
    amplitude: np.ndarray
        amplitudes of tidal constituents
    phase: np.ndarray
        phases of tidal constituents
    D: np.ndarray
        bathymetry of tide model
    """
    # set default keyword arguments
    kwargs.setdefault('type', 'z')
    kwargs.setdefault('method', 'spline')
    kwargs.setdefault('extrapolate', False)
    kwargs.setdefault('cutoff', 10.0)
    kwargs.setdefault('scale', 1.0)
    # verify that constituents are valid class instance
    assert isinstance(constituents, pyTMD.io.constituents)
    # extract model coordinates
    lon = np.copy(constituents.longitude)
    lat = np.copy(constituents.latitude)

    # adjust dimensions of input coordinates to be iterable
    ilon = np.atleast_1d(np.copy(ilon))
    ilat = np.atleast_1d(np.copy(ilat))
    # adjust longitudinal convention of input latitude and longitude
    # to fit tide model convention
    if (np.min(ilon) < 0.0) & (np.max(lon) > 180.0):
        # input points convention (-180:180)
        # tide model convention (0:360)
        ilon[ilon < 0.0] += 360.0
    elif (np.max(ilon) > 180.0) & (np.min(lon) < 0.0):
        # input points convention (0:360)
        # tide model convention (-180:180)
        ilon[ilon > 180.0] -= 360.0
    # determine if any input points are outside of the model bounds
    invalid = (ilon < lon.min()) | (ilon > lon.max()) | \
              (ilat < lat.min()) | (ilat > lat.max())

    # number of points
    npts = len(ilon)
    # create masked array of model bathymetry
    bathymetry = np.ma.array(constituents.bathymetry,
        mask=constituents.mask, fill_value=0.0)
    # interpolate bathymetry and mask to output points
    if (kwargs['method'] == 'bilinear'):
        # replace invalid values with nan
        bathymetry.data[bathymetry.mask] = np.nan
        # use quick bilinear to interpolate values
        D = pyTMD.interpolate.bilinear(lon, lat, bathymetry, ilon, ilat,
            fill_value=np.ma.default_fill_value(np.dtype(float)))
        # replace nan values with fill_value
        D.mask[:] |= np.isnan(D.data)
        D.data[D.mask] = D.fill_value
    elif (kwargs['method'] == 'spline'):
        # use scipy bivariate splines to interpolate values
        D = pyTMD.interpolate.spline(lon, lat, bathymetry, ilon, ilat,
            reducer=np.ceil, kx=1, ky=1)
    else:
        # use scipy regular grid to interpolate values for a given method
        D = pyTMD.interpolate.regulargrid(lon, lat, bathymetry, ilon, ilat,
            method=kwargs['method'], reducer=np.ceil, bounds_error=False)

    # u and v are velocities in cm/s
    if kwargs['type'] in ('v','u'):
        unit_conv = (D.data/100.0)
    # h is elevation values in m
    # U and V are transports in m^2/s
    elif kwargs['type'] in ('z','V','U'):
        unit_conv = 1.0

    # number of constituents
    nc = len(constituents)
    # amplitude and phase
    ampl = np.ma.zeros((npts, nc))
    ampl.mask = np.zeros((npts, nc), dtype=bool)
    ph = np.ma.zeros((npts, nc))
    ph.mask = np.zeros((npts, nc), dtype=bool)
    # default complex fill value
    fill_value = np.ma.default_fill_value(np.dtype(complex))
    # interpolate each constituent
    for i, c in enumerate(constituents.fields):
        # get model constituent
        hc = constituents.get(c)
        # interpolate amplitude and phase of the constituent
        if (kwargs['method'] == 'bilinear'):
            # replace invalid values with nan
            hc.data[hc.mask] = np.nan
            hci = pyTMD.interpolate.bilinear(lon, lat, hc, ilon, ilat,
                fill_value=fill_value,
                dtype=hc.dtype)
            # mask invalid values
            hci.mask[:] |= np.copy(D.mask)
            hci.data[hci.mask] = hci.fill_value
        elif (kwargs['method'] == 'spline'):
            # replace invalid values with fill value
            hc.data[hc.mask] = fill_value
            # use scipy splines to interpolate values
            hci = pyTMD.interpolate.spline(lon, lat, hc, ilon, ilat,
                fill_value=fill_value,
                dtype=hc.dtype,
                reducer=np.ceil,
                kx=1, ky=1)
            # mask invalid values
            hci.mask[:] |= np.copy(D.mask)
            hci.data[hci.mask] = hci.fill_value
        else:
            # replace invalid values with fill value
            hc.data[hc.mask] = fill_value
            # use scipy regular grid to interpolate values
            hci = pyTMD.interpolate.regulargrid(lon, lat, hc, ilon, ilat,
                fill_value=fill_value,
                dtype=hc.dtype,
                method=kwargs['method'],
                reducer=np.ceil,
                bounds_error=False)
            # mask invalid values
            hci.mask[:] |= np.copy(D.mask)
            hci.data[hci.mask] = hci.fill_value
        # extrapolate data using nearest-neighbors
        if kwargs['extrapolate'] and np.any(hci.mask):
            # find invalid data points
            inv, = np.nonzero(hci.mask)
            # replace invalid values with nan
            hc[hc.mask] = np.nan
            # extrapolate points within cutoff of valid model points
            hci[inv] = pyTMD.interpolate.extrapolate(lon, lat, hc,
                ilon[inv], ilat[inv], dtype=hc.dtype,
                cutoff=kwargs['cutoff'])
        # convert units
        # amplitude and phase of the constituent
        ampl.data[:,i] = np.abs(hci.data)/unit_conv
        ampl.mask[:,i] = np.copy(hci.mask)
        ph.data[:,i] = np.arctan2(-np.imag(hci.data), np.real(hci.data))
        ph.mask[:,i] = np.copy(hci.mask)
        # update mask to invalidate points outside model domain
        ampl.mask[:,i] |= invalid
        ph.mask[:,i] |= invalid

    # convert amplitude from input units to meters
    amplitude = ampl*kwargs['scale']
    # convert phase to degrees
    phase = np.degrees(ph)
    phase[phase < 0] += 360.0
    # return the interpolated values
    return (amplitude, phase, D)

# PURPOSE: read grid file
def read_netcdf_grid(
        input_file: str | pathlib.Path,
        variable: str,
        **kwargs
    ):
    """
    Read grid file to extract model coordinates and bathymetry

    Parameters
    ----------
    input_file: str or pathlib.Path
        input grid file
    variable: str
        Tidal variable to read

            - ``'z'``: heights
            - ``'u'``: horizontal transport velocities
            - ``'U'``: horizontal depth-averaged transport
            - ``'v'``: vertical transport velocities
            - ``'V'``: vertical depth-averaged transport

    compressed: bool, default False
        Input file is gzip compressed

    Returns
    -------
    lon: np.ndarray
        longitudinal coordinates of input grid
    lat: np.ndarray
        latitudinal coordinates of input grid
    bathymetry: np.ndarray
        model bathymetry
    """
    # set default keyword arguments
    kwargs.setdefault('compressed', False)
    # read the netcdf format tide grid file
    input_file = pathlib.Path(input_file).expanduser()
    # reading a combined global solution with localized solutions
    if kwargs['compressed']:
        # read gzipped netCDF4 file
        f = gzip.open(input_file, 'rb')
        fileID = netCDF4.Dataset(uuid.uuid4().hex, 'r', memory=f.read())
    else:
        fileID = netCDF4.Dataset(input_file, 'r')
    # variable dimensions
    nx = fileID.dimensions['nx'].size
    ny = fileID.dimensions['ny'].size
    # allocate numpy masked array for bathymetry
    bathymetry = np.ma.zeros((ny,nx))
    # read bathymetry and coordinates for variable type
    if (variable == 'z'):
        # get bathymetry at nodes
        bathymetry.data[:,:] = fileID.variables['hz'][:,:].T
        # read latitude and longitude at z-nodes
        lon = fileID.variables['lon_z'][:].copy()
        lat = fileID.variables['lat_z'][:].copy()
    elif variable in ('U','u'):
        # get bathymetry at u-nodes
        bathymetry.data[:,:] = fileID.variables['hu'][:,:].T
        # read latitude and longitude at u-nodes
        lon = fileID.variables['lon_u'][:].copy()
        lat = fileID.variables['lat_u'][:].copy()
    elif variable in ('V','v'):
        # get bathymetry at v-nodes
        bathymetry.data[:,:] = fileID.variables['hv'][:,:].T
        # read latitude and longitude at v-nodes
        lon = fileID.variables['lon_v'][:].copy()
        lat = fileID.variables['lat_v'][:].copy()
    # set bathymetry mask
    bathymetry.mask = (bathymetry.data == 0.0)
    # close the grid file
    fileID.close()
    f.close() if kwargs['compressed'] else None
    return (lon, lat, bathymetry)

# PURPOSE: wrapper function for reading netCDF4 constituent files
def read_netcdf_file(
        input_file: str | pathlib.Path,
        variable: str,
        **kwargs
    ):
    """
    Wrapper function for reading netCDF4 files to extract
    real and imaginary components for constituent

    Parameters
    ----------
    input_file: str or pathlib.Path
        input transport file
    variable: str
        Tidal variable to read

            - ``'z'``: heights
            - ``'u'``: horizontal transport velocities
            - ``'U'``: horizontal depth-averaged transport
            - ``'v'``: vertical transport velocities
            - ``'V'``: vertical depth-averaged transport

    compressed: bool, default False
        Input file is gzip compressed

    Returns
    -------
    hc: np.ndarray
        tidal constituent
    con: str
        tidal constituent ID
    """
    if (variable == 'z'):
        # read constituent from elevation file
        return read_netcdf_elevation(input_file, **kwargs)
    elif variable in ('U','u','V','v'):
        # read constituent from transport file
        return read_netcdf_transport(input_file, variable, **kwargs)

# PURPOSE: read elevation file to extract real and imaginary components for
# constituent
def read_netcdf_elevation(
        input_file: str | pathlib.Path,
        **kwargs
    ):
    """
    Read elevation file to extract real and imaginary components for constituent

    Parameters
    ----------
    input_file: str or pathlib.Path
        input elevation file
    compressed: bool, default False
        Input file is gzip compressed

    Returns
    -------
    hc: np.ndarray
        tidal elevation
    con: str
        tidal constituent ID
    """
    # set default keyword arguments
    kwargs.setdefault('compressed', False)
    # read the netcdf format tide elevation file
    input_file = pathlib.Path(input_file).expanduser()
    # reading a combined global solution with localized solutions
    if kwargs['compressed']:
        # read gzipped netCDF4 file
        f = gzip.open(input_file, 'rb')
        fileID = netCDF4.Dataset(uuid.uuid4().hex, 'r', memory=f.read())
    else:
        fileID = netCDF4.Dataset(input_file, 'r')
    # constituent name
    con = fileID.variables['con'][:].tobytes().decode('utf8')
    # variable dimensions
    nx = fileID.dimensions['nx'].size
    ny = fileID.dimensions['ny'].size
    # real and imaginary components of elevation
    hc = np.ma.zeros((ny,nx), dtype=np.complex64)
    hc.mask = np.zeros((ny,nx), dtype=bool)
    hc.data.real[:,:] = fileID.variables['hRe'][:,:].T
    hc.data.imag[:,:] = fileID.variables['hIm'][:,:].T
    # close the file
    fileID.close()
    f.close() if kwargs['compressed'] else None
    # return the elevation and constituent
    return (hc, con.strip())

# PURPOSE: read transport file to extract real and imaginary components for
# constituent
def read_netcdf_transport(
        input_file: str | pathlib.Path,
        variable: str,
        **kwargs
    ):
    """
    Read transport file to extract real and imaginary components for constituent

    Parameters
    ----------
    input_file: str or pathlib.Path
        input transport file
    variable: str
        Tidal variable to read

            - ``'u'``: horizontal transport velocities
            - ``'U'``: horizontal depth-averaged transport
            - ``'v'``: vertical transport velocities
            - ``'V'``: vertical depth-averaged transport

    compressed: bool, default False
        Input file is gzip compressed

    Returns
    -------
    hc: np.ndarray
        tidal transport
    con: str
        tidal constituent ID
    """
    # set default keyword arguments
    kwargs.setdefault('compressed', False)
    # read the netcdf format tide transport file
    input_file = pathlib.Path(input_file).expanduser()
    # reading a combined global solution with localized solutions
    if kwargs['compressed']:
        # read gzipped netCDF4 file
        f = gzip.open(input_file, 'rb')
        fileID = netCDF4.Dataset(uuid.uuid4().hex, 'r', memory=f.read())
    else:
        fileID = netCDF4.Dataset(input_file, 'r')
    # constituent name
    con = fileID.variables['con'][:].tobytes().decode('utf8')
    # variable dimensions
    nx = fileID.dimensions['nx'].size
    ny = fileID.dimensions['ny'].size
    # real and imaginary components of transport
    hc = np.ma.zeros((ny,nx), dtype=np.complex64)
    hc.mask = np.zeros((ny,nx), dtype=bool)
    if variable in ('U','u'):
        hc.data.real[:,:] = fileID.variables['uRe'][:,:].T
        hc.data.imag[:,:] = fileID.variables['uIm'][:,:].T
    elif variable in ('V','v'):
        hc.data.real[:,:] = fileID.variables['vRe'][:,:].T
        hc.data.imag[:,:] = fileID.variables['vIm'][:,:].T
    # close the file
    fileID.close()
    f.close() if kwargs['compressed'] else None
    # return the transport components and constituent
    return (hc, con.strip())

# PURPOSE: output grid file in ATLAS netCDF format
def output_netcdf_grid(
        FILE: str | pathlib.Path,
        hz: np.ndarray,
        hu: np.ndarray,
        hv: np.ndarray,
        lon_z: np.ndarray,
        lat_z: np.ndarray,
        lon_u: np.ndarray,
        lat_u: np.ndarray,
        lon_v: np.ndarray,
        lat_v: np.ndarray
    ):
    """
    Writes grid parameters to netCDF4 files in ATLAS format

    Parameters
    ----------
    FILE: str or pathlib.Path
        output ATLAS grid file name
    hz: np.ndarray
        model bathymetry at z-nodes
    hu: np.ndarray
        model bathymetry at u-nodes
    hv: np.ndarray
        model bathymetry at v-nodes
    lon_z: np.ndarray
        longitude coordinates at z-nodes
    lat_z: np.ndarray
        latitude coordinates at z-nodes
    lon_u: np.ndarray
        longitude coordinates at u-nodes
    lat_u: np.ndarray
        latitude coordinates at u-nodes
    lon_v: np.ndarray
        longitude coordinates at v-nodes
    lat_v: np.ndarray
        latitude coordinates at v-nodes
    """
    # tilde-expand output file
    FILE = pathlib.Path(FILE).expanduser()
    # opening NetCDF file for writing
    fileID = netCDF4.Dataset(FILE, 'w', format="NETCDF4")
    # define the NetCDF dimensions
    ny, nx = np.shape(hz)
    fileID.createDimension('nx', nx)
    fileID.createDimension('ny', ny)
    # defining the NetCDF variables
    nc = {}
    nc['lon_z'] = fileID.createVariable('lon_z', lon_z.dtype, ('nx',))
    nc['lat_z'] = fileID.createVariable('lat_z', lat_z.dtype, ('ny',))
    nc['lon_u'] = fileID.createVariable('lon_u', lon_u.dtype, ('nx',))
    nc['lat_u'] = fileID.createVariable('lat_u', lat_u.dtype, ('ny',))
    nc['lon_v'] = fileID.createVariable('lon_v', lon_v.dtype, ('nx',))
    nc['lat_v'] = fileID.createVariable('lat_v', lat_v.dtype, ('ny',))
    nc['hz'] = fileID.createVariable('hz', hz.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    nc['hu'] = fileID.createVariable('hu', hu.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    nc['hv'] = fileID.createVariable('hv', hv.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    # filling the NetCDF variables
    nc['lon_z'][:] = lon_z[:]
    nc['lat_z'][:] = lat_z[:]
    nc['lon_u'][:] = lon_u[:]
    nc['lat_u'][:] = lat_u[:]
    nc['lon_v'][:] = lon_v[:]
    nc['lat_v'][:] = lat_v[:]
    nc['hz'][:] = hz[:].T
    nc['hu'][:] = hu[:].T
    nc['hv'][:] = hv[:].T
    # define variable attributes
    for TYPE in ('z','u','v'):
        # set variable attributes for coordinates
        nc[f'lon_{TYPE}'].setncattr('units', 'degrees_east')
        long_name = f'longitude of {TYPE.upper()} nodes'
        nc[f'lon_{TYPE}'].setncattr('long_name', long_name)
        nc[f'lat_{TYPE}'].setncattr('units', 'degrees_north')
        long_name = f'latitude of {TYPE.upper()} nodes'
        nc[f'lat_{TYPE}'].setncattr('long_name', long_name)
        # set variable attributes for bathymetry
        long_name = f'Bathymetry at {TYPE.upper()} nodes'
        nc[f'h{TYPE}'].setncattr('units', 'meters')
        nc[f'h{TYPE}'].setncattr('long_name', long_name)
        nc[f'h{TYPE}'].setncattr('field', 'bath, scalar')
    # add global attributes
    fileID.title = "ATLAS bathymetry file"
    fileID.type = "OTIS grid file"
    # add attribute for date created
    fileID.date_created = datetime.datetime.now().isoformat()
    # add attributes for software information
    fileID.software_reference = pyTMD.version.project_name
    fileID.software_version = pyTMD.version.full_version
    # Output NetCDF structure information
    logging.info(str(FILE))
    logging.info(list(fileID.variables.keys()))
    # Closing the NetCDF file
    fileID.close()

# PURPOSE: output elevation file in ATLAS netCDF format
def output_netcdf_elevation(
        FILE: str | pathlib.Path,
        h: np.ndarray,
        lon_z: np.ndarray,
        lat_z: np.ndarray,
        constituent: str
    ):
    """
    Writes elevation constituents to netCDF4 files in ATLAS format

    Parameters
    ----------
    FILE: str or pathlib.Path
        output ATLAS elevation file name
    h: np.ndarray
        Eulerian form of tidal elevation oscillation
    lon_z: np.ndarray
        longitude coordinates at z-nodes
    lat_z: np.ndarray
        latitude coordinates at z-nodes
    constituent: str
        tidal constituent ID
    """
    # tilde-expand output file
    FILE = pathlib.Path(FILE).expanduser()
    # opening NetCDF file for writing
    fileID = netCDF4.Dataset(FILE, 'w', format="NETCDF4")
    # define the NetCDF dimensions
    ny, nx = np.shape(h)
    fileID.createDimension('nx', nx)
    fileID.createDimension('ny', ny)
    fileID.createDimension('nct', 4)
    # defining the NetCDF variables
    nc = {}
    nc['lon_z'] = fileID.createVariable('lon_z', lon_z.dtype, ('nx',))
    nc['lat_z'] = fileID.createVariable('lat_z', lat_z.dtype, ('ny',))
    nc['hRe'] = fileID.createVariable('hRe', h.real.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    nc['hIm'] = fileID.createVariable('hIm', h.imag.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    # filling the NetCDF variables
    nc['lon_z'][:] = lon_z[:]
    nc['lat_z'][:] = lat_z[:]
    nc['hRe'][:] = h.real[:].T
    nc['hIm'][:] = h.imag[:].T
    # define variable attributes
    complexpart = dict(Re='Real part', Im='Imag part')
    # set variable attributes for coordinates
    nc['lon_z'].setncattr('units', 'degrees_east')
    nc['lon_z'].setncattr('long_name', 'longitude of Z nofloatdes')
    nc['lat_z'].setncattr('units', 'degrees_north')
    nc['lat_z'].setncattr('long_name', 'latitude of Z nodes')
    # set variable attributes for tidal constituents
    for COMP in ('Re','Im'):
        key = f'h{COMP}'
        long_name = f'Tidal elevation complex amplitude, {complexpart[COMP]}'
        field = (f'{COMP}(h), scalar; '
            f'amp=abs(hRe+i*hIm); '
            f'GMT phase=atan2(-hIm,hRe)/pi*180;')
        # set variable attributes
        nc[key].setncattr('units', 'millimeter')
        nc[key].setncattr('long_name', long_name)
        nc[key].setncattr('field', field)
    # define and fill constituent ID
    nc['con'] = fileID.createVariable('con', 'S1', ('nct',))
    con = [char.encode('utf8') for char in constituent.ljust(4)]
    nc['con'][:] = np.array(con, dtype='S1')
    nc['con'].setncattr('_Encoding', 'utf8')
    nc['con'].setncattr('long_name', "tidal constituent")
    # add global attributes
    fileID.title = "ATLAS tidal elevation file"
    fileID.type = "OTIS elevation file"
    # add attribute for date created
    fileID.date_created = datetime.datetime.now().isoformat()
    # add attributes for software information
    fileID.software_reference = pyTMD.version.project_name
    fileID.software_version = pyTMD.version.full_version
    # Output NetCDF structure information
    logging.info(str(FILE))
    logging.info(list(fileID.variables.keys()))
    # Closing the NetCDF file
    fileID.close()

# PURPOSE: output transport file in ATLAS netCDF format
def output_netcdf_transport(
        FILE: str | pathlib.Path,
        u: np.ndarray,
        v: np.ndarray,
        lon_u: np.ndarray,
        lat_u: np.ndarray,
        lon_v: np.ndarray,
        lat_v: np.ndarray,
        constituent: str
    ):
    """
    Writes transport constituents to netCDF4 files in ATLAS format

    Parameters
    ----------
    FILE: str or pathlib.Path
        output ATLAS transport file name
    u: np.ndarray
        Eulerian form of tidal zonal transport oscillation
    v: np.ndarray
        Eulerian form of tidal meridional transport oscillation
    lon_u: np.ndarray
        longitude coordinates at u-nodes
    lat_u: np.ndarray
        latitude coordinates at u-nodes
    lon_v: np.ndarray
        longitude coordinates at v-nodes
    lat_v: np.ndarray
        latitude coordinates at v-nodes
    constituents: str
        tidal constituent ID
    """
    # tilde-expand output file
    FILE = pathlib.Path(FILE).expanduser()
    # opening NetCDF file for writing
    fileID = netCDF4.Dataset(FILE, 'w', format="NETCDF4")
    # define the NetCDF dimensions
    ny, nx = np.shape(u)
    fileID.createDimension('nx', nx)
    fileID.createDimension('ny', ny)
    fileID.createDimension('nct', 4)
    # defining the NetCDF variables
    nc = {}
    nc['lon_u'] = fileID.createVariable('lon_u', lon_u.dtype, ('nx',))
    nc['lat_u'] = fileID.createVariable('lat_u', lat_u.dtype, ('ny',))
    nc['lon_v'] = fileID.createVariable('lon_v', lon_v.dtype, ('nx',))
    nc['lat_v'] = fileID.createVariable('lat_v', lat_v.dtype, ('ny',))
    nc['uRe'] = fileID.createVariable('uRe', u.real.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    nc['uIm'] = fileID.createVariable('uIm', u.imag.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    nc['vRe'] = fileID.createVariable('vRe', v.real.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    nc['vIm'] = fileID.createVariable('vIm', v.imag.dtype, ('nx','ny',),
        fill_value=0, zlib=True)
    # filling the NetCDF variables
    nc['lon_u'][:] = lon_u[:]
    nc['lat_u'][:] = lat_u[:]
    nc['lon_v'][:] = lon_v[:]
    nc['lat_v'][:] = lat_v[:]
    nc['uRe'][:] = u.real[:].T
    nc['uIm'][:] = u.imag[:].T
    nc['vRe'][:] = v.real[:].T
    nc['vIm'][:] = v.imag[:].T
    # define variable attributes
    direction = dict(u='WE', v='SN')
    complexpart = dict(Re='Real part', Im='Imag part')
    for TYPE in ('u','v'):
        # set variable attributes for coordinates
        nc[f'lon_{TYPE}'].setncattr('units', 'degrees_east')
        long_name = f'longitude of {TYPE.upper()} nodes'
        nc[f'lon_{TYPE}'].setncattr('long_name', long_name)
        nc[f'lat_{TYPE}'].setncattr('units', 'degrees_north')
        long_name = f'latitude of {TYPE.upper()} nodes'
        nc[f'lat_{TYPE}'].setncattr('long_name', long_name)
        # set variable attributes for tidal constituents
        for COMP in ('Re','Im'):
            key = f'{TYPE}{COMP}'
            long_name = (f'Tidal {direction[TYPE]} transport '
                f'complex amplitude, {complexpart[COMP]}')
            field = (f'{COMP}({TYPE}), scalar; '
                f'amp=abs({TYPE}Re+i*{TYPE}Im); '
                f'GMT phase=atan2(-{TYPE}Im,{TYPE}Re)/pi*180;')
            # set variable attributes
            nc[key].setncattr('units', 'centimeter^2/sec')
            nc[key].setncattr('long_name', long_name)
            nc[key].setncattr('field', field)
    # define and fill constituent ID
    nc['con'] = fileID.createVariable('con', 'S1', ('nct',))
    con = [char.encode('utf8') for char in constituent.ljust(4)]
    nc['con'][:] = np.array(con, dtype='S1')
    nc['con'].setncattr('_Encoding', 'utf8')
    nc['con'].setncattr('long_name', "tidal constituent")
    # add global attributes
    fileID.title = "ATLAS tidal SN and WE transports file"
    fileID.type = "OTIS transport file"
    # add attribute for date created
    fileID.date_created = datetime.datetime.now().isoformat()
    # add attributes for software information
    fileID.software_reference = pyTMD.version.project_name
    fileID.software_version = pyTMD.version.full_version
    # Output NetCDF structure information
    logging.info(str(FILE))
    logging.info(list(fileID.variables.keys()))
    # Closing the NetCDF file
    fileID.close()

# PURPOSE: Extend a longitude array
def _extend_array(input_array: np.ndarray, step_size: float):
    """
    Extends a longitude array

    Parameters
    ----------
    input_array: np.ndarray
        array to extend
    step_size: float
        step size between elements of array

    Returns
    -------
    temp: np.ndarray
        extended array
    """
    n = len(input_array)
    temp = np.zeros((n+2), dtype=input_array.dtype)
    # extended array [x-1,x0,...,xN,xN+1]
    temp[0] = input_array[0] - step_size
    temp[1:-1] = input_array[:]
    temp[-1] = input_array[-1] + step_size
    return temp

# PURPOSE: Extend a global matrix
def _extend_matrix(input_matrix: np.ndarray):
    """
    Extends a global matrix

    Parameters
    ----------
    input_matrix: np.ndarray
        matrix to extend

    Returns
    -------
    temp: np.ndarray
        extended matrix
    """
    ny, nx = np.shape(input_matrix)
    # allocate for extended matrix
    if np.ma.isMA(input_matrix):
        temp = np.ma.zeros((ny,nx+2), dtype=input_matrix.dtype)
    else:
        temp = np.zeros((ny,nx+2), dtype=input_matrix.dtype)
    # extend matrix
    temp[:,0] = input_matrix[:,-1]
    temp[:,1:-1] = input_matrix[:,:]
    temp[:,-1] = input_matrix[:,0]
    return temp

# PURPOSE: crop tide model data to bounds
def _crop(
        input_matrix: np.ndarray,
        ilon: np.ndarray,
        ilat: np.ndarray,
        bounds: list | tuple,
        buffer: int | float = 0
    ):
    """
    Crop tide model data to bounds

    Parameters
    ----------
    input_matrix: np.ndarray
        matrix to crop
    ilon: np.ndarray
        longitude of tidal model
    ilat: np.ndarray
        latitude of tidal model
    bounds: list, tuple
        bounding box: ``[xmin, xmax, ymin, ymax]``
    buffer: int or float, default 0
        buffer to add to bounds for cropping

    Returns
    -------
    temp: np.ndarray
        cropped matrix
    lon: np.ndarray
        cropped longitude
    lat: np.ndarray
        cropped latitude
    """
    # adjust longitudinal convention of tide model
    if (np.min(bounds[:2]) < 0.0) & (np.max(ilon) > 180.0):
        input_matrix, ilon = _shift(input_matrix, ilon,
            lon0=180.0, cyclic=360.0, direction='west')
    elif (np.max(bounds[:2]) > 180.0) & (np.min(ilon) < 0.0):
        input_matrix, ilon = _shift(input_matrix, ilon,
            lon0=0.0, cyclic=360.0, direction='east')
    # unpack bounds and buffer
    xmin = bounds[0] - buffer
    xmax = bounds[1] + buffer
    ymin = bounds[2] - buffer
    ymax = bounds[3] + buffer
    # find indices for cropping
    yind = np.flatnonzero((ilat >= ymin) & (ilat <= ymax))
    xind = np.flatnonzero((ilon >= xmin) & (ilon <= xmax))
    # slices for cropping axes
    rows = slice(yind[0], yind[-1]+1)
    cols = slice(xind[0], xind[-1]+1)
    # crop matrix
    temp = input_matrix[rows, cols]
    lon = ilon[cols]
    lat = ilat[rows]
    # return cropped data
    return (temp, lon, lat)

# PURPOSE: shift a grid east or west
def _shift(
        input_matrix: np.ndarray,
        ilon: np.ndarray,
        lon0: int | float = 180,
        cyclic: int | float = 360,
        direction: str = 'west'
    ):
    """
    Shift global grid east or west to a new base longitude

    Parameters
    ----------
    input_matrix: np.ndarray
        input matrix to shift
    ilon: np.ndarray
        longitude of tidal model
    lon0: int or float, default 180
        Starting longitude for shifted grid
    cyclic: int or float, default 360
        width of periodic domain
    direction: str, default 'west'
        Direction to shift grid

            - ``'west'``
            - ``'east'``

    Returns
    -------
    temp: np.ndarray
        shifted matrix
    lon: np.ndarray
        shifted longitude
    """
    # find the starting index if cyclic
    offset = 0 if (np.fabs(ilon[-1]-ilon[0]-cyclic) > 1e-4) else 1
    i0 = np.argmin(np.fabs(ilon - lon0))
    # shift longitudinal values
    lon = np.zeros(ilon.shape, ilon.dtype)
    lon[0:-i0] = ilon[i0:]
    lon[-i0:] = ilon[offset: i0+offset]
    # add or remove the cyclic
    if (direction == 'east'):
        lon[-i0:] += cyclic
    elif (direction == 'west'):
        lon[0:-i0] -= cyclic
    # allocate for shifted data
    if np.ma.isMA(input_matrix):
        temp = np.ma.zeros(input_matrix.shape,input_matrix.dtype)
    else:
        temp = np.zeros(input_matrix.shape, input_matrix.dtype)
    # shift data values
    temp[:,:-i0] = input_matrix[:,i0:]
    temp[:,-i0:] = input_matrix[:,offset: i0+offset]
    # return the shifted values
    return (temp, lon)
