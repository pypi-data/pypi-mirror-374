#!/usr/bin/env python
u"""
predict.py
Written by Tyler Sutterley (09/2025)
Prediction routines for ocean, load, equilibrium and solid earth tides

REFERENCES:
    G. D. Egbert and S. Erofeeva, "Efficient Inverse Modeling of Barotropic
        Ocean Tides", Journal of Atmospheric and Oceanic Technology, (2002).

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
    timescale: Python tools for time and astronomical calculations
        https://pypi.org/project/timescale/

PROGRAM DEPENDENCIES:
    arguments.py: loads nodal corrections for tidal constituents
    astro.py: computes the basic astronomical mean longitudes
    crs.py: Coordinate Reference System (CRS) routines
    spatial.py: utilities for working with geospatial data

UPDATE HISTORY:
    Updated 09/2025: make permanent tide amplitude an input parameter
        can choose different tide potential catalogs for body tides
    Updated 08/2025: add simplified solid earth tide prediction function
        add correction of anelastic effects for long-period body tides
        use sign convention from IERS for complex body tide Love numbers
        include mantle anelastic effects when inferring long-period tides
        allow definition of nominal Love numbers for degree-2 constituents
        added option to include mantle anelastic effects for LPET predict
        switch time decimal in pole tides to nominal years of 365.25 days
        convert angles with numpy radians and degrees functions
        convert arcseconds to radians with asec2rad function in math.py
        return numpy arrays if cannot infer minor constituents
        use a vectorized linear interpolator for inferring from major tides
    Updated 07/2025: revert free-to-mean conversion to April 2023 version
        revert load pole tide to IERS 1996 convention definitions
        mask mean pole values prior to valid epoch of convention
    Updated 05/2025: pass keyword arguments to nodal corrections functions
    Updated 03/2025: changed argument for method calculating mean longitudes
    Updated 02/2025: verify dimensions of harmonic constants
    Updated 11/2024: use Love numbers for long-period tides when inferring
        move body tide Love/Shida numbers to arguments module
    Updated 10/2024: use PREM as the default Earth model for Love numbers
        more descriptive error message if cannot infer minor constituents
        updated calculation of long-period equilibrium tides
        added option to use Munk-Cartwright admittance interpolation for minor
    Updated 09/2024: verify order of minor constituents to infer
        fix to use case insensitive assertions of string argument values
        split infer minor function into short and long period calculations
        add two new functions to infer semi-diurnal and diurnal tides separately
    Updated 08/2024: minor nodal angle corrections in radians to match arguments
        include inference of eps2 and eta2 when predicting from GOT models
        add keyword argument to allow inferring specific minor constituents
    	use nodal arguments for all non-OTIS model type cases
        add load pole tide function that exports in cartesian coordinates
        add ocean pole tide function that exports in cartesian coordinates
    Updated 07/2024: use normalize_angle from pyTMD astro module
        make number of days to convert tide time to MJD a variable
    Updated 02/2024: changed class name for ellipsoid parameters to datum
    Updated 01/2024: moved minor arguments calculation into new function
        moved constituent parameters function from predict to arguments
    Updated 12/2023: phase_angles function renamed to doodson_arguments
    Updated 09/2023: moved constituent parameters function within this module
    Updated 08/2023: changed ESR netCDF4 format to TMD3 format
    Updated 04/2023: using renamed astro mean_longitudes function
        using renamed arguments function for nodal corrections
        adding prediction routine for solid earth tides
        output solid earth tide corrections as combined XYZ components
    Updated 03/2023: add basic variable typing to function inputs
    Updated 12/2022: merged prediction functions into a single module
    Updated 05/2022: added ESR netCDF4 formats to list of model types
    Updated 04/2022: updated docstrings to numpy documentation format
    Updated 02/2021: replaced numpy bool to prevent deprecation warning
    Updated 09/2020: append output mask over each constituent
    Updated 08/2020: change time variable names to not overwrite functions
    Updated 07/2020: added function docstrings
    Updated 11/2019: output as numpy masked arrays instead of nan-filled arrays
    Updated 09/2019: added netcdf option to CORRECTIONS option
    Updated 08/2018: added correction option ATLAS for localized OTIS solutions
    Updated 07/2018: added option to use GSFC GOT nodal corrections
    Updated 09/2017: Rewritten in Python
"""
from __future__ import annotations

import logging
import numpy as np
import pyTMD.arguments
import pyTMD.astro
import pyTMD.math
import pyTMD.interpolate
import pyTMD.spatial
import timescale.eop

__all__ = [
    "map",
    "drift",
    "time_series",
    "infer_minor",
    "_infer_short_period",
    "_infer_semi_diurnal",
    "_infer_diurnal",
    "_infer_long_period",
    "equilibrium_tide",
    "load_pole_tide",
    "ocean_pole_tide",
    "solid_earth_tide",
    "_out_of_phase_diurnal",
    "_out_of_phase_semidiurnal",
    "_latitude_dependence",
    "_frequency_dependence_diurnal",
    "_frequency_dependence_long_period",
    "_free_to_mean",
    "body_tide"
]

# number of days between the Julian day epoch and MJD
_jd_mjd = 2400000.5
# number of days between MJD and the tide epoch (1992-01-01T00:00:00)
_mjd_tide = 48622.0
# number of days between the Julian day epoch and the tide epoch
_jd_tide = _jd_mjd + _mjd_tide

# PURPOSE: Predict tides at single times
def map(t: float | np.ndarray,
        hc: np.ndarray,
        constituents: list | np.ndarray,
        deltat: float | np.ndarray = 0.0,
        corrections: str = 'OTIS',
        **kwargs
    ):
    """
    Predict tides at a single time using harmonic
    constants :cite:p:`Egbert:2002ge`

    Parameters
    ----------
    t: float or np.ndarray
        days relative to 1992-01-01T00:00:00
    hc: np.ndarray
        harmonic constant vector
    constituents: list or np.ndarray
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS/ATLAS or GOT/FES models
    **kwargs: dict
        keyword arguments for nodal corrections functions

    Returns
    -------
    ht: np.ndarray
        tide values reconstructed using the nodal corrections
    """
    # number of points and number of constituents
    npts, nc = np.shape(hc)
    # verify dimensions of harmonic constants
    hc = np.ma.atleast_2d(hc)
    # load the nodal corrections
    # convert time to Modified Julian Days (MJD)
    pu, pf, G = pyTMD.arguments.arguments(t + _mjd_tide,
        constituents,
        deltat=deltat,
        corrections=corrections,
        **kwargs
    )
    # allocate for output tidal elevation
    ht = np.ma.zeros((npts))
    ht.mask = np.zeros((npts), dtype=bool)
    # for each constituent
    for k,c in enumerate(constituents):
        if corrections in ('OTIS', 'ATLAS', 'TMD3', 'netcdf'):
            # load parameters for each constituent
            amp, ph, omega, alpha, species = \
                pyTMD.arguments._constituent_parameters(c)
            # add component for constituent to output tidal elevation
            th = omega*t*86400.0 + ph + pu[0,k]
        else:
            th = np.radians(G[0,k]) + pu[0,k]
        # sum over all tides
        ht.data[:] += pf[0,k]*hc.real[:,k]*np.cos(th) - \
            pf[0,k]*hc.imag[:,k]*np.sin(th)
        ht.mask[:] |= (hc.real.mask[:,k] | hc.imag.mask[:,k])
    # return the tidal elevation after removing singleton dimensions
    return np.squeeze(ht)

# PURPOSE: Predict tides at drift buoys or altimetry points
def drift(t: float | np.ndarray,
        hc: np.ndarray,
        constituents: list | np.ndarray,
        deltat: float | np.ndarray = 0.0,
        corrections: str = 'OTIS',
        **kwargs
    ):
    """
    Predict tides at multiple times and locations using harmonic
    constants :cite:p:`Egbert:2002ge`

    Parameters
    ----------
    t: float or np.ndarray
        days relative to 1992-01-01T00:00:00
    hc: np.ndarray
        harmonic constant vector
    constituents: list or np.ndarray
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS/ATLAS or GOT/FES models
    **kwargs: dict
        keyword arguments for nodal corrections functions

    Returns
    -------
    ht: np.ndarray
        tidal time series reconstructed using the nodal corrections
    """
    # number of points
    nt = len(t)
    # verify dimensions of harmonic constants
    hc = np.ma.atleast_2d(hc)
    # load the nodal corrections
    # convert time to Modified Julian Days (MJD)
    pu, pf, G = pyTMD.arguments.arguments(t + _mjd_tide,
        constituents,
        deltat=deltat,
        corrections=corrections,
        **kwargs
    )
    # allocate for output time series
    ht = np.ma.zeros((nt))
    ht.mask = np.zeros((nt), dtype=bool)
    # for each constituent
    for k,c in enumerate(constituents):
        if corrections in ('OTIS', 'ATLAS', 'TMD3', 'netcdf'):
            # load parameters for each constituent
            amp, ph, omega, alpha, species = \
                pyTMD.arguments._constituent_parameters(c)
            # add component for constituent to output tidal elevation
            th = omega*t*86400.0 + ph + pu[:,k]
        else:
            th = np.radians(G[:,k]) + pu[:,k]
        # sum over all tides
        ht.data[:] += pf[:,k]*hc.real[:,k]*np.cos(th) - \
            pf[:,k]*hc.imag[:,k]*np.sin(th)
        ht.mask[:] |= (hc.real.mask[:,k] | hc.imag.mask[:,k])
    # return tides
    return ht

# PURPOSE: Predict a tidal time series at a location
def time_series(t: float | np.ndarray,
        hc: np.ndarray,
        constituents: list | np.ndarray,
        deltat: float | np.ndarray = 0.0,
        corrections: str = 'OTIS',
        **kwargs
    ):
    """
    Predict tidal time series at a single location using harmonic
    constants :cite:p:`Egbert:2002ge`

    Parameters
    ----------
    t: float or np.ndarray
        days relative to 1992-01-01T00:00:00
    hc: np.ndarray
        harmonic constant vector
    constituents: list or np.ndarray
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS/ATLAS or GOT/FES models
    **kwargs: dict
        keyword arguments for nodal corrections functions

    Returns
    -------
    ht: np.ndarray
        tidal time series reconstructed using the nodal corrections
    """
    # number of time points
    nt = len(t)
    # verify dimensions of harmonic constants
    hc = np.ma.atleast_2d(hc)
    # load the nodal corrections
    # convert time to Modified Julian Days (MJD)
    pu, pf, G = pyTMD.arguments.arguments(t + _mjd_tide,
        constituents,
        deltat=deltat,
        corrections=corrections,
        **kwargs
    )
    # allocate for output time series
    ht = np.ma.zeros((nt))
    ht.mask = np.zeros((nt), dtype=bool)
    # for each constituent
    for k,c in enumerate(constituents):
        if corrections in ('OTIS', 'ATLAS', 'TMD3', 'netcdf'):
            # load parameters for each constituent
            amp, ph, omega, alpha, species = \
                pyTMD.arguments._constituent_parameters(c)
            # add component for constituent to output tidal time series
            th = omega*t*86400.0 + ph + pu[:,k]
        else:
            th = np.radians(G[:,k]) + pu[:,k]
        # sum over all tides at location
        ht.data[:] += pf[:,k]*hc.real[0,k]*np.cos(th) - \
            pf[:,k]*hc.imag[0,k]*np.sin(th)
        ht.mask[:] |= np.any(hc.real.mask[0,k] | hc.imag.mask[0,k])
    # return the tidal time series
    return ht

# PURPOSE: infer the minor corrections from the major constituents
def infer_minor(
        t: float | np.ndarray,
        zmajor: np.ndarray,
        constituents: list | np.ndarray,
        **kwargs
    ):
    """
    Infer the tidal values for minor constituents using their
    relation with major constituents
    :cite:p:`Doodson:1941td,Schureman:1958ty,Foreman:1989dt,Egbert:2002ge`

    Parameters
    ----------
    t: float or np.ndarray
        days relative to 1992-01-01T00:00:00
    zmajor: np.ndarray
        Complex HC for given constituents/points
    constituents: list
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS/ATLAS or GOT/FES models
    minor: list or None, default None
        tidal constituent IDs of minor constituents for inference
    infer_long_period, bool, default True
        try to infer long period tides from constituents
    raise_exception: bool, default False
        Raise a ``ValueError`` if major constituents are not found

    Returns
    -------
    dh: np.ndarray
        tidal time series for minor constituents
    """
    # set default keyword arguments
    kwargs.setdefault('deltat', 0.0)
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('infer_long_period', True)
    kwargs.setdefault('raise_exception', False)
    # list of minor constituents
    kwargs.setdefault('minor', None)
    # infer the minor tidal constituents
    dh = 0.0
    # infer short-period tides for minor constituents
    if kwargs['corrections'] in ('GOT',):
        dh += _infer_semi_diurnal(t, zmajor, constituents, **kwargs)
        dh += _infer_diurnal(t, zmajor, constituents, **kwargs)
    else:
        dh += _infer_short_period(t, zmajor, constituents, **kwargs)
    # infer long-period tides for minor constituents
    if kwargs['infer_long_period']:
        dh += _infer_long_period(t, zmajor, constituents, **kwargs)
    # return the inferred values
    return dh

# PURPOSE: infer short-period tides for minor constituents
def _infer_short_period(
        t: float | np.ndarray,
        zmajor: np.ndarray,
        constituents: list | np.ndarray,
        **kwargs
    ):
    """
    Infer the tidal values for short-period minor constituents
    using their relation with major constituents
    :cite:p:`Egbert:2002ge,Ray:1999vm`

    Parameters
    ----------
    t: float or np.ndarray
        days relative to 1992-01-01T00:00:00
    zmajor: np.ndarray
        Complex HC for given constituents/points
    constituents: list
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS/ATLAS or GOT/FES models
    minor: list or None, default None
        tidal constituent IDs of minor constituents for inference
    raise_exception: bool, default False
        Raise a ``ValueError`` if major constituents are not found

    Returns
    -------
    dh: np.ndarray
        tidal time series for minor constituents
    """
    # set default keyword arguments
    kwargs.setdefault('deltat', 0.0)
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('raise_exception', False)
    # list of minor constituents
    kwargs.setdefault('minor', None)
    # number of constituents
    zmajor = np.ma.atleast_2d(zmajor)
    npts, nc = np.shape(zmajor)
    nt = len(np.atleast_1d(t))
    # number of data points to calculate if running time series/drift/map
    n = nt if ((npts == 1) & (nt > 1)) else npts
    # allocate for output elevation correction
    dh = np.ma.zeros((n))
    # major constituents used for inferring minor tides
    cindex = ['q1', 'o1', 'p1', 'k1', 'n2', 'm2', 's2', 'k2', '2n2']
    # re-order major tides to correspond to order of cindex
    z = np.ma.zeros((n,len(cindex)), dtype=np.complex64)
    nz = 0
    for i,c in enumerate(cindex):
        j = [j for j,val in enumerate(constituents) if (val.lower() == c)]
        if j:
            j1, = j
            z[:,i] = zmajor[:,j1]
            nz += 1

    # raise exception or log error
    msg = 'Not enough constituents to infer short-period tides'
    if (nz < 6) and kwargs['raise_exception']:
        raise Exception(msg)
    elif (nz < 6):
        logging.debug(msg)
        return dh

    # complete list of minor constituents
    minor_constituents = ['2q1', 'sigma1', 'rho1', 'm1b', 'm1',
        'chi1', 'pi1', 'phi1', 'theta1', 'j1', 'oo1', '2n2', 'mu2',
        'nu2', 'lambda2', 'l2', 'l2b', 't2', 'eps2', 'eta2']
    # possibly reduced list of minor constituents
    minor = kwargs['minor'] or minor_constituents
    # only add minor constituents that are not on the list of major values
    minor_indices = [i for i,m in enumerate(minor_constituents)
        if (m not in constituents) and (m in minor)]
    # if there are no constituents to infer
    msg = 'No short-period tidal constituents to infer'
    if not np.any(minor_indices):
        logging.debug(msg)
        return dh

    # relationship between major and minor constituent amplitude and phase
    zmin = np.zeros((n, 20), dtype=np.complex64)
    zmin[:,0] = 0.263*z[:,0] - 0.0252*z[:,1]# 2Q1
    zmin[:,1] = 0.297*z[:,0] - 0.0264*z[:,1]# sigma1
    zmin[:,2] = 0.164*z[:,0] + 0.0048*z[:,1]# rho1
    zmin[:,3] = 0.0140*z[:,1] + 0.0101*z[:,3]# M12
    zmin[:,4] = 0.0389*z[:,1] + 0.0282*z[:,3]# M11
    zmin[:,5] = 0.0064*z[:,1] + 0.0060*z[:,3]# chi1
    zmin[:,6] = 0.0030*z[:,1] + 0.0171*z[:,3]# pi1
    zmin[:,7] = -0.0015*z[:,1] + 0.0152*z[:,3]# phi1
    zmin[:,8] = -0.0065*z[:,1] + 0.0155*z[:,3]# theta1
    zmin[:,9] = -0.0389*z[:,1] + 0.0836*z[:,3]# J1
    zmin[:,10] = -0.0431*z[:,1] + 0.0613*z[:,3]# OO1
    zmin[:,11] = 0.264*z[:,4] - 0.0253*z[:,5]# 2N2
    zmin[:,12] = 0.298*z[:,4] - 0.0264*z[:,5]# mu2
    zmin[:,13] = 0.165*z[:,4] + 0.00487*z[:,5]# nu2
    zmin[:,14] = 0.0040*z[:,5] + 0.0074*z[:,6]# lambda2
    zmin[:,15] = 0.0131*z[:,5] + 0.0326*z[:,6]# L2
    zmin[:,16] = 0.0033*z[:,5] + 0.0082*z[:,6]# L2
    zmin[:,17] = 0.0585*z[:,6]# t2
    # additional coefficients for FES and GOT models
    if kwargs['corrections'] in ('FES',):
        # spline coefficients for admittances
        mu2 = [0.069439968323, 0.351535557706, -0.046278307672]
        nu2 = [-0.006104695053, 0.156878802427, 0.006755704028]
        l2 = [0.077137765667, -0.051653455134, 0.027869916824]
        t2 = [0.180480173707, -0.020101177502, 0.008331518844]
        lda2 = [0.016503557465, -0.013307812292, 0.007753383202]
        zmin[:,12] = mu2[0]*z[:,7] + mu2[1]*z[:,4] + mu2[2]*z[:,5]# mu2
        zmin[:,13] = nu2[0]*z[:,7] + nu2[1]*z[:,4] + nu2[2]*z[:,5]# nu2
        zmin[:,14] = lda2[0]*z[:,7] + lda2[1]*z[:,4] + lda2[2]*z[:,5]# lambda2
        zmin[:,16] = l2[0]*z[:,7] + l2[1]*z[:,4] + l2[2]*z[:,5]# L2
        zmin[:,17] = t2[0]*z[:,7] + t2[1]*z[:,4] + t2[2]*z[:,5]# t2
        zmin[:,18] = 0.53285*z[:,8] - 0.03304*z[:,4]# eps2
        zmin[:,19] = -0.0034925*z[:,5] + 0.0831707*z[:,7]# eta2

    # load the nodal corrections for minor constituents
    # convert time to Modified Julian Days (MJD)
    pu, pf, G = pyTMD.arguments.minor_arguments(t + _mjd_tide,
        deltat=kwargs['deltat'],
        corrections=kwargs['corrections']
    )

    # sum over the minor tidal constituents of interest
    for k in minor_indices:
        th = np.radians(G[:,k]) + pu[:,k]
        dh += zmin.real[:,k]*pf[:,k]*np.cos(th) - \
            zmin.imag[:,k]*pf[:,k]*np.sin(th)
    # return the inferred values
    return dh

def _infer_semi_diurnal(
        t: float | np.ndarray,
        zmajor: np.ndarray,
        constituents: list | np.ndarray,
        **kwargs
    ):
    """
    Infer the tidal values for semi-diurnal minor constituents
    using their relation with major constituents
    :cite:p:`Munk:1966go,Ray:1999vm,Cartwright:1971iz`

    Parameters
    ----------
    t: float or np.ndarray
        days relative to 1992-01-01T00:00:00
    zmajor: np.ndarray
        Complex HC for given constituents/points
    constituents: list
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    minor: list or None, default None
        tidal constituent IDs of minor constituents for inference
    method: str, default 'linear'
        method for interpolating between major constituents

            * 'linear': linear interpolation
            * 'admittance': Munk-Cartwright admittance interpolation
    raise_exception: bool, default False
        Raise a ``ValueError`` if major constituents are not found

    Returns
    -------
    dh: np.ndarray
        tidal time series for minor constituents
    """
    # set default keyword arguments
    kwargs.setdefault('deltat', 0.0)
    kwargs.setdefault('corrections', 'GOT')
    kwargs.setdefault('method', 'linear')
    kwargs.setdefault('raise_exception', False)
    # list of minor constituents
    kwargs.setdefault('minor', None)
    # validate interpolation method
    assert kwargs['method'].lower() in ('linear', 'admittance')
    # number of constituents
    zmajor = np.ma.atleast_2d(zmajor)
    npts, nc = np.shape(zmajor)
    nt = len(np.atleast_1d(t))
    # number of data points to calculate if running time series/drift/map
    n = nt if ((npts == 1) & (nt > 1)) else npts
    # allocate for output elevation correction
    dh = np.ma.zeros((n))
    # major constituents used for inferring semi-diurnal minor tides
    # pivot waves listed in Table 6.7 of the 2010 IERS Conventions
    cindex = ['n2', 'm2', 's2']
    # angular frequencies for major constituents
    omajor = pyTMD.arguments.frequency(cindex, **kwargs)
    # Cartwright and Edden potential amplitudes for major constituents
    amajor = np.zeros((3))
    amajor[0] = 0.121006# n2
    amajor[1] = 0.631931# m2
    amajor[2] = 0.294019# s2
    # re-order major tides to correspond to order of cindex
    z = np.ma.zeros((n,len(cindex)), dtype=np.complex64)
    nz = 0
    for i,c in enumerate(cindex):
        j = [j for j,val in enumerate(constituents) if (val.lower() == c)]
        if j:
            j1, = j
            # "normalize" tide values
            z[:,i] = zmajor[:,j1]/amajor[i]
            nz += 1

    # raise exception or log error
    msg = 'Not enough constituents to infer semi-diurnal tides'
    if (nz < 3) and kwargs['raise_exception']:
        raise Exception(msg)
    elif (nz < 3):
        logging.debug(msg)
        return dh

    # complete list of minor constituents
    minor_constituents = ['eps2', '2n2', 'mu2', 'nu2', 'gamma2',
        'alpha2', 'beta2', 'delta2', 'lambda2', 'l2', 't2',
        'r2', 'k2', 'eta2']
    # possibly reduced list of minor constituents
    minor = kwargs['minor'] or minor_constituents
    # only add minor constituents that are not on the list of major values
    minor_indices = [i for i,m in enumerate(minor_constituents)
        if (m not in constituents) and (m in minor)]
    # if there are no constituents to infer
    msg = 'No semi-diurnal tidal constituents to infer'
    if not np.any(minor_indices):
        logging.debug(msg)
        return dh

    # coefficients for Munk-Cartwright admittance interpolation
    if (kwargs['method'].lower() == 'admittance'):
        Ainv = np.array([[3.3133, -4.2538, 1.9405],
            [-3.3133, 4.2538, -0.9405],
            [1.5018, -3.2579, 1.7561]])
        coef = np.dot(Ainv, z.T)

    # angular frequencies for inferred constituents
    omega = pyTMD.arguments.frequency(minor_constituents, **kwargs)
    # Cartwright and Edden potential amplitudes for inferred constituents
    amin = np.zeros((14))
    amin[0] = 0.004669# eps2
    amin[1] = 0.016011# 2n2
    amin[2] = 0.019316# mu2
    amin[3] = 0.022983# nu2
    amin[4] = 0.001902# gamma2
    amin[5] = 0.002178# alpha2
    amin[6] = 0.001921# beta2
    amin[7] = 0.000714# delta2
    amin[8] = 0.004662# lambda2
    amin[9] = 0.017862# l2
    amin[10] = 0.017180# t2
    amin[11] = 0.002463# r2
    amin[12] = 0.079924# k2
    amin[13] = 0.004467# eta

    # load the nodal corrections for minor constituents
    # convert time to Modified Julian Days (MJD)
    pu, pf, G = pyTMD.arguments.arguments(t + _mjd_tide,
        minor_constituents,
        deltat=kwargs['deltat'],
        corrections=kwargs['corrections']
    )

    # sum over the minor tidal constituents of interest
    for k in minor_indices:
        # interpolate from major constituents
        if (kwargs['method'].lower() == 'linear'):
            # linearly interpolate between major constituents
            interp = pyTMD.interpolate.interp1d(omega[k], omajor, z)
        elif (kwargs['method'].lower() == 'admittance'):
            # admittance interpolation using Munk-Cartwright approach
            # convert frequency to radians per 48 hours
            # following Munk and Cartwright (1966)
            f = 2.0*omega[k]*86400.0
            # calculate interpolated values for constituent
            interp = coef[0,:] + coef[1,:]*np.cos(f) + coef[2,:]*np.sin(f)
        # rescale tide values
        zmin = amin[k]*interp
        # sum over all tides
        th = np.radians(G[:,k]) + pu[:,k]
        dh += zmin.real*pf[:,k]*np.cos(th) - \
            zmin.imag*pf[:,k]*np.sin(th)
    # return the inferred values
    return dh

def _infer_diurnal(
        t: float | np.ndarray,
        zmajor: np.ndarray,
        constituents: list | np.ndarray,
        **kwargs
    ):
    """
    Infer the tidal values for diurnal minor constituents
    using their relation with major constituents taking into
    account resonance due to free core nutation
    :cite:p:`Munk:1966go,Ray:2017jx,Wahr:1981if,Cartwright:1973em`

    Parameters
    ----------
    t: float or np.ndarray
        days relative to 1992-01-01T00:00:00
    zmajor: np.ndarray
        Complex HC for given constituents/points
    constituents: list
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    minor: list or None, default None
        tidal constituent IDs of minor constituents for inference
    method: str, default 'linear'
        method for interpolating between major constituents

            * 'linear': linear interpolation
            * 'admittance': Munk-Cartwright admittance interpolation
    raise_exception: bool, default False
        Raise a ``ValueError`` if major constituents are not found

    Returns
    -------
    dh: np.ndarray
        tidal time series for minor constituents
    """
    # set default keyword arguments
    kwargs.setdefault('deltat', 0.0)
    kwargs.setdefault('corrections', 'GOT')
    kwargs.setdefault('method', 'linear')
    kwargs.setdefault('raise_exception', False)
    # list of minor constituents
    kwargs.setdefault('minor', None)
    # validate interpolation method
    assert kwargs['method'].lower() in ('linear', 'admittance')
    # number of constituents
    zmajor = np.ma.atleast_2d(zmajor)
    npts, nc = np.shape(zmajor)
    nt = len(np.atleast_1d(t))
    # number of data points to calculate if running time series/drift/map
    n = nt if ((npts == 1) & (nt > 1)) else npts
    # allocate for output elevation correction
    dh = np.ma.zeros((n))
    # major constituents used for inferring diurnal minor tides
    # pivot waves listed in Table 6.7 of the 2010 IERS Conventions
    cindex = ['q1', 'o1', 'k1']
    # angular frequencies for major constituents
    omajor = pyTMD.arguments.frequency(cindex, **kwargs)
    # Cartwright and Edden potential amplitudes for major constituents
    amajor = np.zeros((3))
    amajor[0] = 0.050184# q1
    amajor[1] = 0.262163# o1
    amajor[2] = 0.368731# k1
    # re-order major tides to correspond to order of cindex
    z = np.ma.zeros((n,len(cindex)), dtype=np.complex64)
    nz = 0
    for i,c in enumerate(cindex):
        j = [j for j,val in enumerate(constituents) if (val.lower() == c)]
        if j:
            j1, = j
            # Love numbers of degree 2 for constituent
            h2, k2, l2 = pyTMD.arguments._love_numbers(omajor[i])
            # tilt factor: response with respect to the solid earth
            gamma_2 = (1.0 + k2 - h2)
            # "normalize" tide values
            z[:,i] = zmajor[:,j1]/(amajor[i]*gamma_2)
            nz += 1

    # raise exception or log error
    msg = 'Not enough constituents to infer diurnal tides'
    if (nz < 3) and kwargs['raise_exception']:
        raise Exception(msg)
    elif (nz < 3):
        logging.debug(msg)
        return dh

    # complete list of minor constituents
    minor_constituents = ['2q1', 'sigma1', 'rho1', 'tau1', 'beta1',
        'm1a', 'm1b', 'chi1', 'pi1', 'p1', 'psi1', 'phi1',
        'theta1', 'j1', 'so1', 'oo1', 'ups1']
    # possibly reduced list of minor constituents
    minor = kwargs['minor'] or minor_constituents
    # only add minor constituents that are not on the list of major values
    minor_indices = [i for i,m in enumerate(minor_constituents)
        if (m not in constituents) and (m in minor)]
    # if there are no constituents to infer
    msg = 'No diurnal tidal constituents to infer'
    if not np.any(minor_indices):
        logging.debug(msg)
        return dh

    # coefficients for Munk-Cartwright admittance interpolation
    if (kwargs['method'].lower() == 'admittance'):
        Ainv = np.array([[3.1214, -3.8494, 1.728],
            [-3.1727, 3.9559, -0.7832],
            [1.438, -3.0297, 1.5917]])
        coef = np.dot(Ainv, z.T)

    # angular frequencies for inferred constituents
    omega = pyTMD.arguments.frequency(minor_constituents, **kwargs)
    # Cartwright and Edden potential amplitudes for inferred constituents
    amin = np.zeros((17))
    amin[0] = 0.006638# 2q1
    amin[1] = 0.008023# sigma1
    amin[2] = 0.009540# rho1
    amin[3] = 0.003430# tau1
    amin[4] = 0.001941# beta1
    amin[5] = 0.020604# m1a
    amin[6] = 0.007420# m1b
    amin[7] = 0.003925# chi1
    amin[8] = 0.007125# pi1
    amin[9] = 0.122008# p1
    amin[10] = 0.002929# psi1
    amin[11] = 0.005247# phi1
    amin[12] = 0.003966# theta1
    amin[13] = 0.020618# j1
    amin[14] = 0.003417# so1
    amin[15] = 0.011293# oo1
    amin[16] = 0.002157# ups1

    # load the nodal corrections for minor constituents
    # convert time to Modified Julian Days (MJD)
    pu, pf, G = pyTMD.arguments.arguments(t + _mjd_tide,
        minor_constituents,
        deltat=kwargs['deltat'],
        corrections=kwargs['corrections']
    )

    # sum over the minor tidal constituents of interest
    for k in minor_indices:
        # Love numbers of degree 2 for constituent
        h2, k2, l2 = pyTMD.arguments._love_numbers(omega[k])
        # tilt factor: response with respect to the solid earth
        gamma_2 = (1.0 + k2 - h2)
        # interpolate from major constituents
        if (kwargs['method'].lower() == 'linear'):
            # linearly interpolate between major constituents
            interp = pyTMD.interpolate.interp1d(omega[k], omajor, z)
        elif (kwargs['method'].lower() == 'admittance'):
            # convert frequency to radians per 48 hours
            # following Munk and Cartwright (1966)
            f = 2.0*omega[k]*86400.0
            # calculate interpolated values for constituent
            interp = coef[0,:] + coef[1,:]*np.cos(f) + coef[2,:]*np.sin(f)
        # rescale tide values
        zmin = amin[k]*gamma_2*interp
        # sum over all tides
        th = np.radians(G[:,k]) + pu[:,k]
        dh += zmin.real*pf[:,k]*np.cos(th) - \
            zmin.imag*pf[:,k]*np.sin(th)
    # return the inferred values
    return dh

# PURPOSE: infer long-period tides for minor constituents
def _infer_long_period(
        t: float | np.ndarray,
        zmajor: np.ndarray,
        constituents: list | np.ndarray,
        **kwargs
    ):
    """
    Infer the tidal values for long-period minor constituents
    using their relation with major constituents with option to
    take into account variations due to mantle anelasticity
    :cite:p:`Ray:1999vm,Ray:2014fu,Cartwright:1973em,Mathews:2002cr`

    Parameters
    ----------
    t: float or np.ndarray
        days relative to 1992-01-01T00:00:00
    zmajor: np.ndarray
        Complex HC for given constituents/points
    constituents: list
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    minor: list or None, default None
        tidal constituent IDs of minor constituents for inference
    include_anelasticity: bool, default False
        compute Love numbers taking into account mantle anelasticity
    raise_exception: bool, default False
        Raise a ``ValueError`` if major constituents are not found

    Returns
    -------
    dh: np.ndarray
        tidal time series for minor constituents
    """
    # set default keyword arguments
    kwargs.setdefault('deltat', 0.0)
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('include_anelasticity', False)
    kwargs.setdefault('raise_exception', False)
    # list of minor constituents
    kwargs.setdefault('minor', None)
    # number of constituents
    zmajor = np.ma.atleast_2d(zmajor)
    npts, nc = np.shape(zmajor)
    nt = len(np.atleast_1d(t))
    # number of data points to calculate if running time series/drift/map
    n = nt if ((npts == 1) & (nt > 1)) else npts
    # allocate for output elevation correction
    dh = np.ma.zeros((n))
    # major constituents used for inferring long period minor tides
    # pivot waves listed in Table 6.7 of the 2010 IERS Conventions
    cindex = ['node', 'mm', 'mf']
    # angular frequencies for major constituents
    omajor = pyTMD.arguments.frequency(cindex, **kwargs)
    # Cartwright and Edden potential amplitudes for major constituents
    amajor = np.zeros((3))
    amajor[0] = 0.027929# node
    amajor[1] = 0.035184# mm
    amajor[2] = 0.066607# mf
    # re-order major tides to correspond to order of cindex
    z = np.ma.zeros((n,len(cindex)), dtype=np.complex64)
    nz = 0
    for i,c in enumerate(cindex):
        j = [j for j,val in enumerate(constituents) if (val.lower() == c)]
        if j:
            j1, = j
            # complex Love numbers of degree 2 for long-period band
            if kwargs['include_anelasticity']:
                # include variations largely due to mantle anelasticity
                h2, k2, l2 = pyTMD.arguments._complex_love_numbers(omajor[i])
            else:
                # Love numbers for long-period tides (Wahr, 1981)
                h2, k2, l2 = pyTMD.arguments._love_numbers(omajor[i],
                    astype=np.complex128)
            # tilt factor: response with respect to the solid earth
            # use real components from Mathews et al. (2002)
            gamma_2 = (1.0 + k2.real - h2.real)
            # "normalize" tide values
            z[:,i] = zmajor[:,j1]/(amajor[i]*gamma_2)
            nz += 1

    # raise exception or log error
    msg = 'Not enough constituents to infer long-period tides'
    if (nz < 3) and kwargs['raise_exception']:
        raise Exception(msg)
    elif (nz < 3):
        logging.debug(msg)
        return dh

    # complete list of minor constituents
    minor_constituents = ['sa', 'ssa', 'sta', 'msm', 'msf',
        'mst', 'mt', 'msqm', 'mq']
    # possibly reduced list of minor constituents
    minor = kwargs['minor'] or minor_constituents
    # only add minor constituents that are not on the list of major values
    minor_indices = [i for i,m in enumerate(minor_constituents)
        if (m not in constituents) and (m in minor)]
    # if there are no constituents to infer
    msg = 'No long-period tidal constituents to infer'
    if not np.any(minor_indices):
        logging.debug(msg)
        return dh

    # angular frequencies for inferred constituents
    omega = pyTMD.arguments.frequency(minor_constituents, **kwargs)
    # Cartwright and Edden potential amplitudes for inferred constituents
    amin = np.zeros((9))
    amin[0] = 0.004922# sa
    amin[1] = 0.030988# ssa
    amin[2] = 0.001809# sta
    amin[3] = 0.006728# msm
    amin[4] = 0.005837# msf
    amin[5] = 0.002422# mst
    amin[6] = 0.012753# mt
    amin[7] = 0.002037# msqm
    amin[8] = 0.001687# mq

    # load the nodal corrections for minor constituents
    # convert time to Modified Julian Days (MJD)
    pu, pf, G = pyTMD.arguments.arguments(t + _mjd_tide,
        minor_constituents,
        deltat=kwargs['deltat'],
        corrections=kwargs['corrections']
    )

    # sum over the minor tidal constituents of interest
    for k in minor_indices:
        # complex Love numbers of degree 2 for long-period band
        if kwargs['include_anelasticity']:
            # include variations largely due to mantle anelasticity
            h2, k2, l2 = pyTMD.arguments._complex_love_numbers(omega[k])
        else:
            # Love numbers for long-period tides (Wahr, 1981)
            h2, k2, l2 = pyTMD.arguments._love_numbers(omega[k],
                astype=np.complex128)
        # tilt factor: response with respect to the solid earth
        # use real components from Mathews et al. (2002)
        gamma_2 = (1.0 + k2.real - h2.real)
        # linearly interpolate between major constituents
        interp = pyTMD.interpolate.interp1d(omega[k], omajor, z)
        # rescale tide values
        zmin = amin[k]*gamma_2*interp
        # sum over all tides
        th = np.radians(G[:,k]) + pu[:,k]
        dh += zmin.real*pf[:,k]*np.cos(th) - \
            zmin.imag*pf[:,k]*np.sin(th)
    # return the inferred values
    return dh

# PURPOSE: estimate long-period equilibrium tides
def equilibrium_tide(
        t: np.ndarray,
        lat: np.ndarray,
        **kwargs
    ):
    """
    Compute the long-period equilibrium tides the summation of fifteen
    tidal spectral lines from Cartwright-Tayler-Edden tables
    :cite:p:`Cartwright:1971iz,Cartwright:1973em`

    Parameters
    ----------
    t: np.ndarray
        time (days relative to January 1, 1992)
    lat: np.ndarray
        latitude (degrees north)
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS/ATLAS or GOT/FES models
    include_anelasticity: bool, default False
        compute Love numbers taking into account mantle anelasticity
    constituents: list
        long-period tidal constituent IDs

    Returns
    -------
    lpet: np.ndarray
        long-period equilibrium tide in meters
    """
    # set default keyword arguments
    cindex = ['node', 'sa', 'ssa', 'msm', '065.445', 'mm',
        '065.465', 'msf', '075.355', 'mf', 'mf+', '075.575',
        'mst', 'mt', '085.465']
    kwargs.setdefault('constituents', cindex)
    kwargs.setdefault('deltat', 0.0)
    kwargs.setdefault('include_anelasticity', False)
    kwargs.setdefault('corrections', 'OTIS')

    # number of input points
    nt = len(np.atleast_1d(t))
    nlat = len(np.atleast_1d(lat))
    # number of constituents
    nc = 15

    # set function for astronomical longitudes
    # use ASTRO5 routines if not using an OTIS type model
    if kwargs['corrections'] in ('OTIS','ATLAS','TMD3','netcdf'):
        method = 'Cartwright'
    else:
        method = 'ASTRO5'
    # convert from Modified Julian Dates into Ephemeris Time
    MJD = t + _mjd_tide
    # compute principal mean longitudes
    s, h, p, n, pp = pyTMD.astro.mean_longitudes(MJD + kwargs['deltat'],
        method=method)
    # initial time conversions
    hour = 24.0*np.mod(MJD, 1)
    # convert from hours solar time into mean lunar time in degrees
    tau = 15.0*hour - s + h
    # variable for multiples of 90 degrees (Ray technical note 2017)
    # full expansion of Equilibrium Tide includes some negative cosine
    # terms and some sine terms (Pugh and Woodworth, 2014)
    k = 90.0 + np.zeros((nt))
    # convert to negative mean longitude of the ascending node (N')
    Np = pyTMD.math.normalize_angle(360.0 - n)
    # determine equilibrium arguments
    fargs = np.c_[tau, s, h, p, Np, pp, k]

    # Cartwright and Edden potential amplitudes (centimeters)
    # assemble long-period tide potential from 15 CTE terms greater than 1 mm
    amajor = np.zeros((nc))
    # group 0,0
    # nodal term is included but not the constant term.
    amajor[0] = 2.7929# node
    amajor[1] = -0.4922# sa
    amajor[2] = -3.0988# ssa
    # group 0,1
    amajor[3] = -0.6728# msm
    amajor[4] = 0.231
    amajor[5] = -3.5184# mm
    amajor[6] = 0.228
    # group 0,2
    amajor[7] = -0.5837# msf
    amajor[8] = -0.288
    amajor[9] = -6.6607# mf
    amajor[10] = -2.763# mf+
    amajor[11] = -0.258
    # group 0,3
    amajor[12] = -0.2422# mst
    amajor[13] = -1.2753# mt
    amajor[14] = -0.528

    # set constituents to be iterable and lower case
    if isinstance(kwargs['constituents'], str):
        constituents = [kwargs['constituents'].lower()]
    else:
        constituents = [c.lower() for c in kwargs['constituents']]

    # reduce potential amplitudes to constituents
    CTE = np.zeros((nc))
    for i,c in enumerate(cindex):
        if c in constituents:
            CTE[i] = amajor[i]

    # Doodson coefficients for 15 long-period terms
    coef = np.zeros((7, nc))
    # group 0,0
    coef[:,0] = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]# node
    coef[:,1] = [0.0, 0.0, 1.0, 0.0, 0.0, -1.0, 0.0]# sa
    coef[:,2] = [0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0]# ssa
    # group 0,1
    coef[:,3] = [0.0, 1.0, -2.0, 1.0, 0.0, 0.0, 0.0]# msm
    coef[:,4] = [0.0, 1.0, 0.0, -1.0, -1.0, 0.0, 0.0]
    coef[:,5] = [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0]# mm
    coef[:,6] = [0.0, 1.0, 0.0, -1.0, 1.0, 0.0, 0.0]
    # group 0,2
    coef[:,7] = [0.0, 2.0, -2.0, 0.0, 0.0, 0.0, 0.0]# msf
    coef[:,8] = [0.0, 2.0, 0.0, -2.0, 0.0, 0.0, 0.0]
    coef[:,9] = [0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0]# mf
    coef[:,10] = [0.0, 2.0, 0.0, 0.0, 1.0, 0.0, 0.0]# mf+
    coef[:,11] = [0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0]
    # group 0,3
    coef[:,12] = [0.0, 3.0, -2.0, 1.0, 0.0, 0.0, 0.0]# mst
    coef[:,13] = [0.0, 3.0, 0.0, -1.0, 0.0, 0.0, 0.0]# mt
    coef[:,14] = [0.0, 3.0, 0.0, -1.0, 1.0, 0.0, 0.0]

    # spherical harmonic degree and order
    l = 2
    m = 0
    # colatitude in radians
    theta = np.radians(90.0 - lat)
    # degree dependent normalization (4-pi)
    dfactor = np.sqrt((2.0*l + 1.0)/(4.0*np.pi))
    # 2nd degree Legendre polynomials (normalized)
    P20 = dfactor*pyTMD.math.legendre(l, np.cos(theta), m=m)

    # determine equilibrium arguments
    G = np.dot(fargs, coef)

    # temporal component of long-period equilibrium tides (meters)
    Z = np.zeros((nt))
    # for each constituent
    for i in range(nc):
        # calculate angular frequencies of constituents
        omega = pyTMD.arguments._frequency(coef[:, i])
        # complex Love numbers of degree 2 for long-period band
        if kwargs['include_anelasticity']:
            # include variations largely due to mantle anelasticity
            h2, k2, l2 = pyTMD.arguments._complex_love_numbers(omega)
        else:
            # Love numbers for long-period tides (Wahr, 1981)
            h2, k2, l2 = pyTMD.arguments._love_numbers(omega,
                astype=np.complex128)
        # tilt factor: response with respect to the solid earth
        # use real components from Mathews et al. (2002)
        gamma_2 = (1.0 + k2.real - h2.real)
        # phase of the equilibrium argument (radians)
        phase = np.radians(G[:, i])
        # add constituent to temporal component and convert to meters
        Z += gamma_2*np.cos(phase)*(CTE[i]/100.0)

    # calculate long-period equilibrium tide
    if (nlat != nt):
        lpet = np.outer(P20, Z)
    else:
        lpet = P20*Z
    # return the long-period equilibrium tides
    return lpet

# PURPOSE: estimate load pole tides in Cartesian coordinates
def load_pole_tide(
        t: np.ndarray,
        XYZ: np.ndarray,
        deltat: float = 0.0,
        gamma_0: float = 9.80665,
        omega: float = 7.2921151467e-5,
        h2: float = 0.6207,
        l2: float = 0.0836,
        convention: str = '2018'
    ):
    """
    Estimate load pole tide displacements in Cartesian coordinates
    :cite:p:`Petit:2010tp`

    Parameters
    ----------
    t: np.ndarray
        Time (days relative to January 1, 1992)
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    gamma_0: float, default 9.80665
        Normal gravity (m/s^2)
    omega: float, default 7.2921151467e-5
        Earth's rotation rate (radians/second)
    h2: float, default 0.6207
        Degree-2 Love number of vertical displacement
    l2: float, default 0.0836
        Degree-2 Love (Shida) number of horizontal displacement
    convention: str, default '2018'
        IERS Mean or Secular Pole Convention

            - ``'2003'``
            - ``'2010'``
            - ``'2015'``
            - ``'2018'``

    Returns
    -------
    dxt: np.ndarray
        Load pole tide displacements in meters in Cartesian coordinates
    """
    # convert time to nominal years (Terrestrial Time)
    time_decimal = 1992.0 + np.atleast_1d(t + deltat)/365.25
    # convert time to Modified Julian Days (MJD)
    MJD = t + deltat + _mjd_tide

    # radius of the Earth
    radius = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2 + XYZ[:,2]**2)
    # geocentric latitude (radians)
    latitude = np.arctan(XYZ[:,2] / np.sqrt(XYZ[:,0]**2.0 + XYZ[:,1]**2.0))
    # geocentric colatitude (radians)
    theta = (np.pi/2.0 - latitude)
    # calculate longitude (radians)
    phi = np.arctan2(XYZ[:,1], XYZ[:,0])

    # calculate angular coordinates of mean/secular pole at time
    mpx, mpy, fl = timescale.eop.iers_mean_pole(time_decimal,
        convention=convention)
    # read and interpolate IERS daily polar motion values
    px, py = timescale.eop.iers_polar_motion(MJD, k=3, s=0)
    # calculate differentials from mean/secular pole positions
    # using the latest definition from IERS Conventions (2010)
    # convert angles from arcseconds to radians
    mx = pyTMD.math.asec2rad(px - mpx)
    my = -pyTMD.math.asec2rad(py - mpy)

    # number of points
    n = np.maximum(len(time_decimal), len(theta))
    # conversion factors in latitude, longitude, and radial directions
    dfactor = np.zeros((n, 3))
    dfactor[:,0] = -l2*(omega**2 * radius**2)/(gamma_0)
    dfactor[:,1] = l2*(omega**2 * radius**2)/(gamma_0)
    dfactor[:,2] = -h2*(omega**2 * radius**2)/(2.0*gamma_0)

    # calculate pole tide displacements (meters)
    S = np.zeros((n, 3))
    # pole tide displacements in latitude, longitude, and radial directions
    S[:,0] = dfactor[:,0]*np.cos(2.0*theta)*(mx*np.cos(phi) - my*np.sin(phi))
    S[:,1] = dfactor[:,1]*np.cos(theta)*(mx*np.sin(phi) + my*np.cos(phi))
    S[:,2] = dfactor[:,2]*np.sin(2.0*theta)*(mx*np.cos(phi) - my*np.sin(phi))

    # rotation matrix
    R = np.zeros((3, 3, n))
    R[0,0,:] = np.cos(phi)*np.cos(theta)
    R[0,1,:] = -np.sin(phi)
    R[0,2,:] = np.cos(phi)*np.sin(theta)
    R[1,0,:] = np.sin(phi)*np.cos(theta)
    R[1,1,:] = np.cos(phi)
    R[1,2,:] = np.sin(phi)*np.sin(theta)
    R[2,0,:] = -np.sin(theta)
    R[2,2,:] = np.cos(theta)
    # rotate displacements to ECEF coordinates
    dxt = np.ma.zeros((n, 3))
    dxt[:,:] = np.einsum('ti...,jit...->tj...', S, R)
    # use mask from mean pole estimates
    dxt.mask = np.broadcast_to(np.logical_not(fl[:,None]), (n,3))

    # return the pole tide displacements
    # in Cartesian coordinates
    return dxt

# PURPOSE: estimate ocean pole tides in Cartesian coordinates
def ocean_pole_tide(
        t: np.ndarray,
        XYZ: np.ndarray,
        UXYZ: np.ndarray,
        deltat: float = 0.0,
        gamma_0: float = 9.780325,
        a_axis: float = 6378136.3,
        GM: float = 3.986004418e14,
        omega: float = 7.2921151467e-5,
        rho_w: float = 1025.0,
        g2: complex = 0.6870 + 0.0036j,
        convention: str = '2018'
    ):
    """
    Estimate ocean pole tide displacements in Cartesian coordinates
    :cite:p:`Desai:2002ev,Desai:2015jr,Petit:2010tp`

    Parameters
    ----------
    t: np.ndarray
        Time (days relative to January 1, 1992)
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    UXYZ: np.ndarray
        Ocean pole tide values from Desai (2002)
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    a_axis: float, default 6378136.3
        Semi-major axis of the Earth (meters)
    gamma_0: float, default 9.780325
        Normal gravity (m/s^2)
    GM: float, default 3.986004418e14
        Earth's gravitational constant [m^3/s^2]
    omega: float, default 7.2921151467e-5
        Earth's rotation rate (radians/second)
    rho_w: float, default 1025.0
        Density of sea water [kg/m^3]
    g2: complex, default 0.6870 + 0.0036j
        Degree-2 Love number differential (1 + k2 - h2)
    convention: str, default '2018'
        IERS Mean or Secular Pole Convention

            - ``'2003'``
            - ``'2010'``
            - ``'2015'``
            - ``'2018'``

    Returns
    -------
    dxt: np.ndarray
        Load pole tide displacements in meters in Cartesian coordinates
    """
    # convert time to nominal years (Terrestrial Time)
    time_decimal = 1992.0 + np.atleast_1d(t + deltat)/365.25
    # convert time to Modified Julian Days (MJD)
    MJD = t + deltat + _mjd_tide

    # geocentric latitude (radians)
    latitude = np.arctan(XYZ[:,2] / np.sqrt(XYZ[:,0]**2.0 + XYZ[:,1]**2.0))
    # geocentric colatitude (radians)
    theta = (np.pi/2.0 - latitude)
    # universal gravitational constant [N*m^2/kg^2]
    G = 6.67430e-11

    # calculate angular coordinates of mean/secular pole at time
    mpx, mpy, fl = timescale.eop.iers_mean_pole(time_decimal,
        convention=convention)
    # read and interpolate IERS daily polar motion values
    px, py = timescale.eop.iers_polar_motion(MJD, k=3, s=0)
    # calculate differentials from mean/secular pole positions
    # using the latest definition from IERS Conventions (2010)
    # convert angles from arcseconds to radians
    mx = pyTMD.math.asec2rad(px - mpx)
    my = -pyTMD.math.asec2rad(py - mpy)

    # pole tide displacement factors
    Hp = np.sqrt(8.0*np.pi/15.0)*(omega**2 * a_axis**4)/GM
    K = 4.0*np.pi*G*rho_w*Hp*a_axis/(3.0*gamma_0)

    # number of points
    n = np.maximum(len(time_decimal), len(theta))
    # calculate ocean pole tide displacements (meters)
    dxt = np.ma.zeros((n, 3))
    # use mask from mean pole estimates
    dxt.mask = np.broadcast_to(np.logical_not(fl[:,None]), (n,3))
    for i in range(3):
        dxt[:,i] = K*np.real(
            (mx*g2.real + my*g2.imag)*UXYZ.real[:,i] +
            (my*g2.real - mx*g2.imag)*UXYZ.imag[:,i])

    # return the ocean pole tide displacements
    # in Cartesian coordinates
    return dxt

# get IERS parameters
_iers = pyTMD.spatial.datum(ellipsoid='IERS', units='MKS')

# PURPOSE: estimate solid Earth tides due to gravitational attraction
def solid_earth_tide(
        t: np.ndarray,
        XYZ: np.ndarray,
        SXYZ: np.ndarray,
        LXYZ: np.ndarray,
        a_axis: float = _iers.a_axis,
        tide_system: str = 'tide_free',
        **kwargs
    ):
    """
    Compute the solid Earth tides due to the gravitational
    attraction of the moon and sun
    :cite:p:`Mathews:1991kv,Mathews:1997js,Ries:1992ip,Wahr:1981ea`

    Parameters
    ----------
    t: np.ndarray
        Time (days relative to January 1, 1992)
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    SXYZ: np.ndarray
        Earth-centered Earth-fixed coordinates of the sun (meters)
    LXYZ: np.ndarray
        Earth-centered Earth-fixed coordinates of the moon (meters)
    a_axis: float, default 6378136.3
        Semi-major axis of the Earth (meters)
    tide_system: str, default 'tide_free'
        Permanent tide system for the output solid Earth tide

            - ``'tide_free'``: no permanent direct and indirect tidal potentials
            - ``'mean_tide'``: permanent tidal potentials (direct and indirect)
    h2: float, default 0.6078
        Degree-2 Love number of vertical displacement
    l2: float, default 0.0847
        Degree-2 Love (Shida) number of horizontal displacement
    h3: float, default 0.292
        Degree-3 Love number of vertical displacement
    l3: float, default 0.015
        Degree-3 Love (Shida) number of horizontal displacement
    mass_ratio_solar: float, default 332946.0482
        Mass ratio between the Earth and the Sun
    mass_ratio_lunar: float, default 0.0123000371
        Mass ratio between the Earth and the Moon

    Returns
    -------
    dxt: np.ndarray
        Solid Earth tide in meters in Cartesian coordinates
    """
    # set default keyword arguments
    # nominal Love and Shida numbers for degrees 2 and 3
    kwargs.setdefault('h2', 0.6078)
    kwargs.setdefault('l2', 0.0847)
    kwargs.setdefault('h3', 0.292)
    kwargs.setdefault('l3', 0.015)
    # mass ratios between earth and sun/moon
    kwargs.setdefault('mass_ratio_solar', 332946.0482)
    kwargs.setdefault('mass_ratio_lunar', 0.0123000371)
    # validate output tide system
    assert tide_system.lower() in ('tide_free', 'mean_tide')
    # number of input coordinates
    nt = len(np.atleast_1d(t))
    # convert time to Modified Julian Days (MJD)
    MJD = t + _mjd_tide
    # scalar product of input coordinates with sun/moon vectors
    radius = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2 + XYZ[:,2]**2)
    solar_radius = np.sqrt(SXYZ[:,0]**2 + SXYZ[:,1]**2 + SXYZ[:,2]**2)
    lunar_radius = np.sqrt(LXYZ[:,0]**2 + LXYZ[:,1]**2 + LXYZ[:,2]**2)
    solar_scalar = (XYZ[:,0]*SXYZ[:,0] + XYZ[:,1]*SXYZ[:,1] +
        XYZ[:,2]*SXYZ[:,2])/(radius*solar_radius)
    lunar_scalar = (XYZ[:,0]*LXYZ[:,0] + XYZ[:,1]*LXYZ[:,1] +
        XYZ[:,2]*LXYZ[:,2])/(radius*lunar_radius)
    # compute new h2 and l2 (Mathews et al., 1997)
    cosphi = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2)/radius
    h2 = kwargs['h2'] - 0.0006*(1.0 - 3.0/2.0*cosphi**2)
    l2 = kwargs['l2'] + 0.0002*(1.0 - 3.0/2.0*cosphi**2)
    # compute P2 terms
    P2_solar = 3.0*(h2/2.0 - l2)*solar_scalar**2 - h2/2.0
    P2_lunar = 3.0*(h2/2.0 - l2)*lunar_scalar**2 - h2/2.0
    # compute P3 terms
    P3_solar = 5.0/2.0*(kwargs['h3'] - 3.0*kwargs['l3'])*solar_scalar**3 + \
        3.0/2.0*(kwargs['l3'] - kwargs['h3'])*solar_scalar
    P3_lunar = 5.0/2.0*(kwargs['h3'] - 3.0*kwargs['l3'])*lunar_scalar**3 + \
        3.0/2.0*(kwargs['l3'] - kwargs['h3'])*lunar_scalar
    # compute terms in direction of sun/moon vectors
    X2_solar = 3.0*l2*solar_scalar
    X2_lunar = 3.0*l2*lunar_scalar
    X3_solar = 3.0*kwargs['l3']/2.0*(5.0*solar_scalar**2 - 1.0)
    X3_lunar = 3.0*kwargs['l3']/2.0*(5.0*lunar_scalar**2 - 1.0)
    # factors for sun and moon using IAU estimates of mass ratios
    F2_solar = kwargs['mass_ratio_solar']*a_axis*(a_axis/solar_radius)**3
    F2_lunar = kwargs['mass_ratio_lunar']*a_axis*(a_axis/lunar_radius)**3
    F3_solar = kwargs['mass_ratio_solar']*a_axis*(a_axis/solar_radius)**4
    F3_lunar = kwargs['mass_ratio_lunar']*a_axis*(a_axis/lunar_radius)**4
    # compute total displacement (Mathews et al. 1997)
    dxt = np.zeros((nt, 3))
    for i in range(3):
        S2 = F2_solar*(X2_solar*SXYZ[:,i]/solar_radius+P2_solar*XYZ[:,i]/radius)
        L2 = F2_lunar*(X2_lunar*LXYZ[:,i]/lunar_radius+P2_lunar*XYZ[:,i]/radius)
        S3 = F3_solar*(X3_solar*SXYZ[:,i]/solar_radius+P3_solar*XYZ[:,i]/radius)
        L3 = F3_lunar*(X3_lunar*LXYZ[:,i]/lunar_radius+P3_lunar*XYZ[:,i]/radius)
        dxt[:,i] = S2 + L2 + S3 + L3
    # corrections for out-of-phase portions of the Love and Shida numbers
    dxt += _out_of_phase_diurnal(XYZ, SXYZ, LXYZ, F2_solar, F2_lunar)
    dxt += _out_of_phase_semidiurnal(XYZ, SXYZ, LXYZ, F2_solar, F2_lunar)
    # corrections for the latitudinal dependence
    dxt += _latitude_dependence(XYZ, SXYZ, LXYZ, F2_solar, F2_lunar)
    # corrections for the frequency dependence
    dxt += _frequency_dependence_diurnal(XYZ, MJD)
    dxt += _frequency_dependence_long_period(XYZ, MJD)
    # convert the permanent tide system if specified
    if (tide_system.lower() == 'mean_tide'):
        dxt += _free_to_mean(XYZ, h2, l2)
    # return the solid earth tide
    return dxt

def _out_of_phase_diurnal(
        XYZ: np.ndarray,
        SXYZ: np.ndarray,
        LXYZ: np.ndarray,
        F2_solar: np.ndarray,
        F2_lunar: np.ndarray
    ):
    """
    Computes the out-of-phase corrections induced by mantle
    anelasticity in the diurnal band :cite:p:`Petit:2010tp`

    Parameters
    ----------
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    SXYZ: np.ndarray
        Earth-centered Earth-fixed coordinates of the sun (meters)
    LXYZ: np.ndarray
        Earth-centered Earth-fixed coordinates of the moon (meters)
    F2_solar: np.ndarray
        Factors for the sun
    F2_lunar: np.ndarray
        Factors for the moon
    """
    # Love and Shida number corrections
    dhi = -0.0025
    dli = -0.0007
    # Compute the normalized position vector of coordinates
    radius = np.sqrt(np.sum(XYZ**2, axis=1))
    sinphi = XYZ[:,2]/radius
    cosphi = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2)/radius
    cos2phi = cosphi**2 - sinphi**2
    sinla = XYZ[:,1]/cosphi/radius
    cosla = XYZ[:,0]/cosphi/radius
    # Compute the normalized position vector of the Sun/Moon
    solar_radius = np.sqrt(np.sum(SXYZ**2, axis=1))
    lunar_radius = np.sqrt(np.sum(LXYZ**2, axis=1))
    # calculate offsets
    dr_solar = -3.0*dhi*sinphi*cosphi*F2_solar*SXYZ[:,2]* \
        (SXYZ[:,0]*sinla-SXYZ[:,1]*cosla)/solar_radius**2
    dr_lunar = -3.0*dhi*sinphi*cosphi*F2_lunar*LXYZ[:,2]* \
        (LXYZ[:,0]*sinla-LXYZ[:,1]*cosla)/lunar_radius**2
    dn_solar = -3.0*dli*cos2phi*F2_solar*SXYZ[:,2]* \
        (SXYZ[:,0]*sinla-SXYZ[:,1]*cosla)/solar_radius**2
    dn_lunar = -3.0*dli*cos2phi*F2_lunar*LXYZ[:,2]* \
        (LXYZ[:,0]*sinla-LXYZ[:,1]*cosla)/lunar_radius**2
    de_solar = -3.0*dli*sinphi*F2_solar*SXYZ[:,2]* \
        (SXYZ[:,0]*cosla+SXYZ[:,1]*sinla)/solar_radius**2
    de_lunar = -3.0*dli*sinphi*F2_lunar*LXYZ[:,2]* \
        (LXYZ[:,0]*cosla+LXYZ[:,1]*sinla)/lunar_radius**2
    # add solar and lunar offsets
    DR = dr_solar + dr_lunar
    DN = dn_solar + dn_lunar
    DE = de_solar + de_lunar
    # compute corrections
    DX = DR*cosla*cosphi - DE*sinla - DN*cosla*sinphi
    DY = DR*sinla*cosphi + DE*cosla - DN*sinla*sinphi
    DZ = DR*sinphi + DN*cosphi
    # return the corrections
    return np.c_[DX, DY, DZ]

def _out_of_phase_semidiurnal(
        XYZ: np.ndarray,
        SXYZ: np.ndarray,
        LXYZ: np.ndarray,
        F2_solar: np.ndarray,
        F2_lunar: np.ndarray
    ):
    """
    Computes the out-of-phase corrections induced by mantle
    anelasticity in the semi-diurnal band :cite:p:`Petit:2010tp`

    Parameters
    ----------
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    SXYZ: np.ndarray
        Earth-centered Earth-fixed coordinates of the sun (meters)
    LXYZ: np.ndarray
        Earth-centered Earth-fixed coordinates of the moon (meters)
    F2_solar: np.ndarray
        Factors for the sun
    F2_lunar: np.ndarray
        Factors for the moon
    """
    # Love and Shida number corrections
    dhi = -0.0022
    dli = -0.0007
    # Compute the normalized position vector of coordinates
    radius = np.sqrt(np.sum(XYZ**2, axis=1))
    sinphi = XYZ[:,2]/radius
    cosphi = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2)/radius
    sinla = XYZ[:,1]/cosphi/radius
    cosla = XYZ[:,0]/cosphi/radius
    cos2la = cosla**2 - sinla**2
    sin2la = 2.0*cosla*sinla
    # Compute the normalized position vector of the Sun/Moon
    solar_radius = np.sqrt(np.sum(SXYZ**2, axis=1))
    lunar_radius = np.sqrt(np.sum(LXYZ**2, axis=1))
    # calculate offsets
    dr_solar = -3.0/4.0*dhi*cosphi**2*F2_solar * \
        ((SXYZ[:,0]**2-SXYZ[:,1]**2)*sin2la-2.0*SXYZ[:,0]*SXYZ[:,1]*cos2la) / \
        solar_radius**2
    dr_lunar = -3.0/4.0*dhi*cosphi**2*F2_lunar * \
        ((LXYZ[:,0]**2-LXYZ[:,1]**2)*sin2la-2.0*LXYZ[:,0]*LXYZ[:,1]*cos2la) / \
        lunar_radius**2
    dn_solar = 3.0/2.0*dli*sinphi*cosphi*F2_solar * \
        ((SXYZ[:,0]**2-SXYZ[:,1]**2)*sin2la-2.0*SXYZ[:,0]*SXYZ[:,1]*cos2la) / \
        solar_radius**2
    dn_lunar = 3.0/2.0*dli*sinphi*cosphi*F2_lunar * \
        ((LXYZ[:,0]**2-LXYZ[:,1]**2)*sin2la-2.0*LXYZ[:,0]*LXYZ[:,1]*cos2la) / \
        lunar_radius**2
    de_solar = -3.0/2.0*dli*cosphi*F2_solar * \
        ((SXYZ[:,0]**2-SXYZ[:,1]**2)*cos2la+2.0*SXYZ[:,0]*SXYZ[:,1]*sin2la) / \
        solar_radius**2
    de_lunar = -3.0/2.0*dli*cosphi*F2_lunar * \
        ((LXYZ[:,0]**2-LXYZ[:,1]**2)*cos2la+2.0*LXYZ[:,0]*LXYZ[:,1]*sin2la) / \
        lunar_radius**2
    # add solar and lunar offsets
    DR = dr_solar + dr_lunar
    DN = dn_solar + dn_lunar
    DE = de_solar + de_lunar
    # compute corrections
    DX = DR*cosla*cosphi - DE*sinla - DN*cosla*sinphi
    DY = DR*sinla*cosphi + DE*cosla - DN*sinla*sinphi
    DZ = DR*sinphi + DN*cosphi
    # return the corrections
    return np.c_[DX, DY, DZ]

def _latitude_dependence(
        XYZ: np.ndarray,
        SXYZ: np.ndarray,
        LXYZ: np.ndarray,
        F2_solar: np.ndarray,
        F2_lunar: np.ndarray
    ):
    r"""
    Computes the corrections induced by the latitude of the
    dependence given by L\ :sup:`1` :cite:p:`Petit:2010tp`

    Parameters
    ----------
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    SXYZ: np.ndarray
        Earth-centered Earth-fixed coordinates of the sun (meters)
    LXYZ: np.ndarray
        Earth-centered Earth-fixed coordinates of the moon (meters)
    F2_solar: np.ndarray
        Factors for the sun
    F2_lunar: np.ndarray
        Factors for the moon
    """
    # Love/Shida number corrections (diurnal and semi-diurnal)
    l1d = 0.0012
    l1sd = 0.0024
    # Compute the normalized position vector of coordinates
    radius = np.sqrt(np.sum(XYZ**2, axis=1))
    sinphi = XYZ[:,2]/radius
    cosphi = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2)/radius
    sinla = XYZ[:,1]/cosphi/radius
    cosla = XYZ[:,0]/cosphi/radius
    cos2la = cosla**2 - sinla**2
    sin2la = 2.0*cosla*sinla
    # Compute the normalized position vector of the Sun/Moon
    solar_radius = np.sqrt(np.sum(SXYZ**2, axis=1))
    lunar_radius = np.sqrt(np.sum(LXYZ**2, axis=1))
    # calculate offsets for the diurnal band
    dn_d_solar = -l1d*sinphi**2*F2_solar*SXYZ[:,2] * \
        (SXYZ[:,0]*cosla+SXYZ[:,1]*sinla)/solar_radius**2
    dn_d_lunar = -l1d*sinphi**2*F2_lunar*LXYZ[:,2] * \
        (LXYZ[:,0]*cosla+LXYZ[:,1]*sinla)/lunar_radius**2
    de_d_solar = l1d*sinphi*(cosphi**2-sinphi**2)*F2_solar*SXYZ[:,2] * \
        (SXYZ[:,0]*sinla-SXYZ[:,1]*cosla)/solar_radius**2
    de_d_lunar = l1d*sinphi*(cosphi**2-sinphi**2)*F2_lunar*LXYZ[:,2] * \
        (LXYZ[:,0]*sinla-LXYZ[:,1]*cosla)/lunar_radius**2
    # calculate offsets for the semi-diurnal band
    dn_s_solar = -l1sd/2.0*sinphi*cosphi*F2_solar * \
        ((SXYZ[:,0]**2-SXYZ[:,1]**2)*cos2la+2.0*SXYZ[:,0]*SXYZ[:,1]*sin2la) / \
        solar_radius**2
    dn_s_lunar =-l1sd/2.0*sinphi*cosphi*F2_lunar * \
        ((LXYZ[:,0]**2-LXYZ[:,1]**2)*cos2la+2.0*LXYZ[:,0]*LXYZ[:,1]*sin2la) / \
        lunar_radius**2
    de_s_solar =-l1sd/2.0*sinphi**2*cosphi*F2_solar * \
        ((SXYZ[:,0]**2-SXYZ[:,1]**2)*sin2la-2.0*SXYZ[:,0]*SXYZ[:,1]*cos2la) / \
        solar_radius**2
    de_s_lunar =-l1sd/2.0*sinphi**2*cosphi*F2_lunar * \
        ((LXYZ[:,0]**2-LXYZ[:,1]**2)*sin2la-2.0*LXYZ[:,0]*LXYZ[:,1]*cos2la) / \
        lunar_radius**2
    # add solar and lunar offsets (diurnal and semi-diurnal)
    DN = 3.0*(dn_d_solar + dn_d_lunar + dn_s_solar + dn_s_lunar)
    DE = 3.0*(de_d_solar + de_d_lunar + de_s_solar + de_s_lunar)
    # compute combined diurnal and semi-diurnal corrections
    DX = -DE*sinla - DN*cosla*sinphi
    DY = DE*cosla - DN*sinla*sinphi
    DZ = DN*cosphi
    # return the corrections
    return np.c_[DX, DY, DZ]

def _frequency_dependence_diurnal(
        XYZ: np.ndarray,
        MJD: np.ndarray
    ):
    """
    Computes the in-phase and out-of-phase corrections induced by mantle
    anelasticity in the diurnal band :cite:p:`Petit:2010tp`

    Parameters
    ----------
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    MJD: np.ndarray
        Modified Julian Day (MJD)
    """
    # number of time steps
    nt = len(np.atleast_1d(MJD))
    # Corrections to Diurnal Tides for Frequency Dependence
    # of Love and Shida Number Parameters
    # reduced version of table 7.3a from IERS conventions
    table = np.array([
        [-3.0, 0.0, 2.0, 0.0, 0.0, -0.01, 0.0, 0.0, 0.0],
        [-3.0, 2.0, 0.0, 0.0, 0.0, -0.01, 0.0, 0.0, 0.0],
        [-2.0, 0.0, 1.0, -1.0, 0.0, -0.02, 0.0, 0.0, 0.0],
        [-2.0, 0.0, 1.0, 0.0, 0.0, -0.08, 0.0, -0.01, 0.01],
        [-2.0, 2.0, -1.0, 0.0, 0.0, -0.02, 0.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0,-1.0, 0.0, -0.10, 0.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, -0.51, 0.0, -0.02, 0.03],
        [-1.0, 2.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0],
        [0.0, -2.0, 1.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0, 0.0, 0.02, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.06, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.0, 0.0, 0.01, 0.0, 0.0, 0.0],
        [0.0, 2.0, -1.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0],
        [1.0, -3.0, 0.0, 0.0, 1.0, -0.06, 0.0, 0.0, 0.0],
        [1.0, -2.0, 0.0, -1.0, 0.0, 0.01, 0.0, 0.0, 0.0],
        [1.0, -2.0, 0.0, 0.0, 0.0, -1.23, -0.07, 0.06, 0.01],
        [1.0, -1.0, 0.0, 0.0,-1.0, 0.02, 0.0, 0.0, 0.0],
        [1.0, -1.0, 0.0, 0.0, 1.0, 0.04, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, -1.0, 0.0, -0.22, 0.01, 0.01, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0, 12.00, -0.80, -0.67, -0.03],
        [1.0, 0.0, 0.0, 1.0, 0.0, 1.73, -0.12, -0.10, 0.0],
        [1.0, 0.0, 0.0, 2.0, 0.0, -0.04, 0.0, 0.0, 0.0],
        [1.0, 1.0, 0.0, 0.0, -1.0, -0.50, -0.01, 0.03, 0.0],
        [1.0, 1.0, 0.0, 0.0, 1.0, 0.01, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 1.0, -1.0, -0.01, 0.0, 0.0, 0.0],
        [1.0, 2.0, -2.0, 0.0, 0.0, -0.01, 0.0, 0.0, 0.0],
        [1.0, 2.0, 0.0, 0.0, 0.0, -0.11, 0.01, 0.01, 0.0],
        [2.0, -2.0, 1.0, 0.0, 0.0, -0.01, 0.0, 0.0, 0.0],
        [2.0, 0.0,-1.0, 0.0, 0.0, -0.02, 0.0, 0.0, 0.0],
        [3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [3.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ])
    # get phase angles (Doodson arguments)
    TAU, S, H, P, ZNS, PS = pyTMD.astro.doodson_arguments(MJD)
    # Compute the normalized position vector of coordinates
    radius = np.sqrt(np.sum(XYZ**2, axis=1))
    sinphi = XYZ[:,2]/radius
    cosphi = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2)/radius
    sinla = XYZ[:,1]/cosphi/radius
    cosla = XYZ[:,0]/cosphi/radius
    zla = np.arctan2(XYZ[:,1], XYZ[:,0])
    # compute corrections (Mathews et al. 1997)
    DX = np.zeros((nt))
    DY = np.zeros((nt))
    DZ = np.zeros((nt))
    # iterate over rows in the table
    for i, row in enumerate(table):
        thetaf = TAU + S*row[0] + H*row[1] + P*row[2] + \
            ZNS*row[3] + PS*row[4]
        dr = 2.0*row[5]*sinphi*cosphi*np.sin(thetaf + zla) + \
            2.0*row[6]*sinphi*cosphi*np.cos(thetaf + zla)
        dn = row[7]*(cosphi**2 - sinphi**2)*np.sin(thetaf + zla) + \
            row[8]*(cosphi**2 - sinphi**2)*np.cos(thetaf + zla)
        de = row[7]*sinphi*np.cos(thetaf + zla) - \
            row[8]*sinphi*np.sin(thetaf + zla)
        DX += 1e-3*(dr*cosla*cosphi - de*sinla - dn*cosla*sinphi)
        DY += 1e-3*(dr*sinla*cosphi + de*cosla - dn*sinla*sinphi)
        DZ += 1e-3*(dr*sinphi + dn*cosphi)
    # return the corrections
    return np.c_[DX, DY, DZ]

def _frequency_dependence_long_period(
        XYZ: np.ndarray,
        MJD: np.ndarray
    ):
    """
    Computes the in-phase and out-of-phase corrections induced by mantle
    anelasticity in the long-period band :cite:p:`Petit:2010tp`

    Parameters
    ----------
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    MJD: np.ndarray
        Modified Julian Day (MJD)
    """
    # number of time steps
    nt = len(np.atleast_1d(MJD))
    # Corrections to Long-Period Tides for Frequency Dependence
    # of Love and Shida Number Parameters
    # reduced version of table 7.3b from IERS conventions
    table = np.array([
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.47, 0.23, 0.16, 0.07],
        [0.0, 2.0, 0.0, 0.0, 0.0, -0.20, -0.12, -0.11, -0.05],
        [1.0, 0.0, -1.0, 0.0, 0.0, -0.11, -0.08, -0.09, -0.04],
        [2.0, 0.0, 0.0, 0.0, 0.0, -0.13, -0.11, -0.15, -0.07],
        [2.0, 0.0, 0.0, 1.0, 0.0, -0.05, -0.05, -0.06, -0.03]
    ])
    # get phase angles (Doodson arguments)
    TAU, S, H, P, ZNS, PS = pyTMD.astro.doodson_arguments(MJD)
    # Compute the normalized position vector of coordinates
    radius = np.sqrt(np.sum(XYZ**2, axis=1))
    sinphi = XYZ[:,2]/radius
    cosphi = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2)/radius
    sinla = XYZ[:,1]/cosphi/radius
    cosla = XYZ[:,0]/cosphi/radius
    # compute corrections (Mathews et al. 1997)
    DX = np.zeros((nt))
    DY = np.zeros((nt))
    DZ = np.zeros((nt))
    # iterate over rows in the table
    for i, row in enumerate(table):
        thetaf = S*row[0] + H*row[1] + P*row[2] + ZNS*row[3] + PS*row[4]
        dr = row[5]*(3.0*sinphi**2 - 1.0)*np.cos(thetaf)/2.0 + \
            row[7]*(3.0*sinphi**2 - 1.0)*np.sin(thetaf)/2.0
        dn = row[6]*(2.0*cosphi*sinphi)*np.cos(thetaf) + \
            row[8]*(2.0*cosphi*sinphi)*np.sin(thetaf)
        de = 0.0
        DX += 1e-3*(dr*cosla*cosphi - de*sinla - dn*cosla*sinphi)
        DY += 1e-3*(dr*sinla*cosphi + de*cosla - dn*sinla*sinphi)
        DZ += 1e-3*(dr*sinphi + dn*cosphi)
    # return the corrections
    return np.c_[DX, DY, DZ]

def _free_to_mean(
        XYZ: np.ndarray,
        h2: float | np.ndarray,
        l2: float | np.ndarray,
        H0: float = -0.31460
    ):
    """
    Calculate offsets for converting the permanent tide from
    a tide-free to a mean-tide state :cite:p:`Mathews:1997js`

    Parameters
    ----------
    XYZ: np.ndarray
        Cartesian coordinates of the prediction points (meters)
    h2: float or np.ndarray
        Degree-2 Love number of vertical displacement
    l2: float or np.ndarray
        Degree-2 Love (Shida) number of horizontal displacement
    H0: float, default -0.31460
        Mean amplitude of the permanent tide (meters)
    """
    # Compute the normalized position vector of coordinates
    radius = np.sqrt(np.sum(XYZ**2, axis=1))
    sinphi = XYZ[:,2]/radius
    cosphi = np.sqrt(XYZ[:,0]**2 + XYZ[:,1]**2)/radius
    sinla = XYZ[:,1]/cosphi/radius
    cosla = XYZ[:,0]/cosphi/radius
    # in Mathews et al. (1997): dR0=-0.1196 m with h2=0.6026
    dR0 = np.sqrt(5.0/(4.0*np.pi))*h2*H0
    # in Mathews et al. (1997): dN0=-0.0247 m with l2=0.0831
    dN0 = np.sqrt(45.0/(16.0*np.pi))*l2*H0
    # use double angle formula for sin(2*phi)
    dr = dR0*(3.0/2.0*sinphi**2 - 1.0/2.0)
    dn = 2.0*dN0*cosphi*sinphi
    # compute as an additive correction (Mathews et al. 1997)
    DX = -dr*cosla*cosphi + dn*cosla*sinphi
    DY = -dr*sinla*cosphi + dn*sinla*sinphi
    DZ = -dr*sinphi - dn*cosphi
    # return the corrections
    return np.c_[DX, DY, DZ]

# tide potential tables
_tide_potential_table = {}
# Cartwright and Tayler (1971) table with 3rd-degree values
# Cartwright and Edden (1973) table with updated values
_tide_potential_table['CTE1973'] = pyTMD.arguments._cte1973_table
# Hartmann and Wenzel (1995) tidal potential catalog
_tide_potential_table['HW1995'] = pyTMD.arguments._hw1995_table
# Tamura (1987) tidal potential catalog
_tide_potential_table['T1987'] = pyTMD.arguments._t1987_table
# Woodworth (1990) tables with updated and 3rd-degree values
_tide_potential_table['W1990'] = pyTMD.arguments._w1990_table

# PURPOSE: estimate solid Earth tides due to gravitational attraction
# using a simplified approach based on Cartwright and Tayler (1971)
def body_tide(
        t: np.ndarray,
        lon: np.ndarray,
        lat: np.ndarray,
        deltat: float | np.ndarray = 0.0,
        method: str = 'ASTRO5',
        tide_system: str = 'tide_free',
        catalog: str = 'CTE1973',
        **kwargs
    ):
    """
    Compute the solid Earth tides due to the gravitational
    attraction of the moon and sun using the approach of
    :cite:t:`Cartwright:1971iz` adjusting the degree-2 Love numbers
    for a near-diurnal frequency dependence :cite:p:`Mathews:1995go`
    
    Parameters
    ----------
    t: np.ndarray
        Time (days relative to January 1, 1992)
    lon: np.ndarray
        longitude (degrees east)
    lat: np.ndarray
        latitude (degrees north)
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    method: str, default 'ASTRO5'
        Method for computing the mean longitudes

            - ``'Cartwright'``
            - ``'Meeus'``
            - ``'ASTRO5'`` 
            - ``'IERS'``
    tide_system: str, default 'tide_free'
        Permanent tide system for the output solid Earth tide

            - ``'tide_free'``: no permanent direct and indirect tidal potentials
            - ``'mean_tide'``: permanent tidal potentials (direct and indirect)
    catalog: str, default 'CTE1973'
        Name of the tide potential catalog

            - ``'CTE1973'``: :cite:t:`Cartwright:1973em`
            - ``'HW1995'``: :cite:t:`Hartmann:1995jp`
            - ``'T1987'``: :cite:t:`Tamura:1987tp`
            - ``'W1990'``: Woodworth updates to ``'CTE1973'``
    include_planets: bool, default False
        Include tide potentials from planetary bodies
    h2: float or None, default None
        Degree-2 Love number of vertical displacement
    l2: float or None, default None
        Degree-2 Love (Shida) number of horizontal displacement
    h3: float, default 0.291
        Degree-3 Love number of vertical displacement
    l3: float, default 0.015
        Degree-3 Love (Shida) number of horizontal displacement
    h4: float, default 0.18
        Degree-4 Love number of vertical displacement
    l4: float, default 0.01
        Degree-4 Love (Shida) number of horizontal displacement

    Returns
    -------
    zeta: np.ndarray
        Solid Earth tide in meters
    """
    # set default keyword arguments
    kwargs.setdefault('include_planets', False)
    # nominal Love and Shida numbers for degrees 2, 3, and 4
    kwargs.setdefault('h2', None)
    kwargs.setdefault('l2', None)
    kwargs.setdefault('h3', 0.291)
    kwargs.setdefault('l3', 0.015)
    kwargs.setdefault('h4', 0.18)
    kwargs.setdefault('l4', 0.01)
    # validate method and output tide system
    assert method.lower() in ('cartwright', 'meeus', 'astro5', 'iers')
    assert tide_system.lower() in ('tide_free', 'mean_tide')
    assert catalog in _tide_potential_table.keys()

    # convert dates to Modified Julian Days
    MJD = t + _mjd_tide
    # number of temporal values
    nt = len(np.atleast_1d(MJD))

    # compute principal mean longitudes
    # convert dates into Ephemeris Time
    s, h, p, n, pp = pyTMD.astro.mean_longitudes(MJD + deltat,
        method=method)
    # initial time conversions
    hour = 24.0*np.mod(MJD, 1)
    # convert from hours solar time into mean lunar time in degrees
    tau = 15.0*hour - s + h
    # variable for multiples of 90 degrees (Ray technical note 2017)
    # full expansion of Equilibrium Tide includes some negative cosine
    # terms and some sine terms (Pugh and Woodworth, 2014)
    k = 90.0 + np.zeros((nt))

    # astronomical and planetary mean longitudes
    if kwargs['include_planets']:
        # calculate planetary mean longitudes
        # me: Mercury, ve: Venus, ma: Mars, ju: Jupiter, sa: Saturn
        me, ve, ma, ju, sa = pyTMD.astro.planetary_longitudes(MJD)
        fargs = np.c_[tau, s, h, p, n, pp, k, me, ve, ma, ju, sa]
    else:
        fargs = np.c_[tau, s, h, p, n, pp, k]

    # longitudes and colatitudes in radians
    phi = np.radians(lon)
    th = np.radians(90.0 - lat)

    # allocate for output body tide estimates (meters)
    # latitudinal, longitudinal and radial components
    zeta = np.zeros((nt, 3))

    # check if tide catalog includes planetary contributions
    if catalog in ('HW1995','T1987',):
        include_planets = True
    else:
        include_planets = False
    # parse tide potential table for constituents
    table = _tide_potential_table[catalog]
    CTE = pyTMD.arguments._parse_tide_potential_table(table,
        skiprows=1, columns=1, include_degree=True,
        include_planets=include_planets)
    # for each line in the table
    for i, line in enumerate(CTE):
        # spherical harmonic degree
        l = line['l']
        # currently only calculating for low-degree harmonics
        if (l > 4):
            continue
        # spherical harmonic dependence (order)
        TAU = line['tau']
        # Doodson coefficients for constituent
        S = line['s']
        H = line['h']
        P = line['p']
        # convert N for ascending lunar node (from N')
        N = -1.0*line['n']
        PP = line['pp']
        # use cosines for (l + tau) even
        # and sines for (l + tau) odd
        K = -1.0*np.mod(l + TAU, 2)
        # Doodson coefficients
        coef = np.array([TAU, S, H, P, N, PP, K], dtype=np.float64)
        # create array of equilibrium arguments
        if kwargs['include_planets']:
            # planetary mean longitudes
            LMe = line['lme']
            LVe = line['lve']
            LMa = line['lma']
            LJu = line['lju']
            LSa = line['lsa']
            # coefficients including planetary terms
            coef = np.hstack([*coef, LMe, LVe, LMa, LJu, LSa])
        # calculate angular frequency of constituent
        omega = pyTMD.arguments._frequency(coef, method=method,
            include_planets=kwargs['include_planets'])
        # skip the permanent tide if using a mean-tide system
        if (omega == 0) and (tide_system.lower() == 'mean_tide'):
            continue
        # determine constituent phase using equilibrium arguments
        G = pyTMD.math.normalize_angle(np.dot(fargs, coef))
        # convert phase angles to radians
        phase = np.radians(G)
        # calculate spherical harmonics (and derivatives)
        S = pyTMD.math.sph_harm(l, th, phi, m=TAU, phase=phase)
        dS = pyTMD.math.sph_harm(l, th, phi, m=TAU, phase=phase, deriv=True)
        # add components for degree and order to output body tides
        if (l == 2):
            # determine love numbers for constituent
            if (kwargs['h2'] is not None) and (kwargs['l2'] is not None):
                # user-defined Love numbers for all constituents
                h2 = np.complex128(kwargs['h2'])
                l2 = np.complex128(kwargs['l2'])
            elif (method == 'IERS'):
                # IERS: including both in-phase and out-of-phase components
                # 1) using resonance formula for tides in the diurnal band
                # 2) adjusting some long-period tides for anelastic effects
                h2, k2, l2 = pyTMD.arguments._complex_love_numbers(omega,
                    method=method)
                # 3) including complex latitudinal dependence
                h2 -= (0.615e-3 + 0.122e-4j)*(1.0 - 1.5*np.sin(th)**2)
                l2 += (0.19334e-3 - 0.3819e-5j)*(1.0 - 1.5*np.sin(th)**2)
            else:
                # use resonance formula for tides in the diurnal band
                h2, k2, l2 = pyTMD.arguments._love_numbers(omega,
                    method=method, astype=np.complex128)
                # include latitudinal dependence
                h2 -= 0.0006*(1.0 - 1.5*np.sin(th)**2)
                l2 += 0.0002*(1.0 - 1.5*np.sin(th)**2)
            # convert potentials for constituent and add to the total
            # (latitudinal, longitudinal and radial components)
            zeta[:,0] += line['Hs1']*(l2.real*dS.real - l2.imag*dS.imag)
            zeta[:,1] -= line['Hs1']*TAU*(l2.real*S.imag - l2.imag*S.real)
            zeta[:,2] += line['Hs1']*(h2.real*S.real - h2.imag*S.imag)
        elif (l == 3):
            # convert potentials for degree-3 constituents
            zeta[:,0] += line['Hs1']*kwargs['l3']*dS.real
            zeta[:,1] -= line['Hs1']*TAU*kwargs['l3']*S.imag
            zeta[:,2] += line['Hs1']*kwargs['h3']*S.real
        elif (l == 4):
            # convert potentials for degree-4 constituents
            zeta[:,0] += line['Hs1']*kwargs['l4']*dS.real
            zeta[:,1] -= line['Hs1']*TAU*kwargs['l4']*S.imag
            zeta[:,2] += line['Hs1']*kwargs['h4']*S.real

    # return the body tides
    return zeta
