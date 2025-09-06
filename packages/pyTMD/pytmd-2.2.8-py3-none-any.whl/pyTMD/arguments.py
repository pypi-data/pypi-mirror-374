#!/usr/bin/env python
u"""
arguments.py
Written by Tyler Sutterley (09/2025)
Calculates the nodal corrections for tidal constituents
Modification of ARGUMENTS fortran subroutine by Richard Ray 03/1999

CALLING SEQUENCE:
    pu, pf, G = arguments(MJD, constituents)

INPUTS:
    MJD: Modified Julian Day of input date
    constituents: tidal constituent IDs

OUTPUTS:
    pu, pf: nodal corrections for the constituents
    G: phase correction in degrees

OPTIONS:
    deltat: time correction for converting to Ephemeris Time (days)
    corrections: use nodal corrections from OTIS, FES or GOT models

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html

PROGRAM DEPENDENCIES:
    astro.py: computes the basic astronomical mean longitudes
    math.py: Special functions of mathematical physics

REFERENCES:
    A. T. Doodson and H. Warburg, "Admiralty Manual of Tides", HMSO, (1941).
    P. Schureman, "Manual of Harmonic Analysis and Prediction of Tides"
        US Coast and Geodetic Survey, Special Publication, 98, (1958).
    M. G. G. Foreman and R. F. Henry, "The harmonic analysis of tidal model
        time series", Advances in Water Resources, 12, (1989).
    G. D. Egbert and S. Erofeeva, "Efficient Inverse Modeling of Barotropic
        Ocean Tides", Journal of Atmospheric and Oceanic Technology, (2002).

UPDATE HISTORY:
    Updated 09/2025: added spherical harmonic degree to tide potential tables
    Updated 08/2025: add Cartwright and Tayler table with radiational tides
        make frequency function a wrapper around one that calculates using
            Doodson coefficients (Cartwright numbers)
        add complex love numbers function for correcting out-of-phase effects
        use Mathews et al. (2002) functions for diurnal complex love numbers
        take the absolute value of the constituent angular frequencies
        convert angles with numpy radians and degrees functions
    Updated 04/2025: convert longitudes p and n to radians within nodal function
        use schureman_arguments function to get nodal variables for FES models
        added Schureman to list of M1 options in nodal arguments
        use numpy power function over using pow for consistency
        added option to modulate tidal groups for e.g. seasonal effects
        renamed nodal to nodal_modulation to parallel group_modulation
    Updated 03/2025: changed argument for method calculating mean longitudes
        add 1066A neutral and stable Earth models to Love number calculation
        use string mapping to remap non-numeric Doodson numbers
    Updated 02/2025: add option to make doodson numbers strings
        add Doodson number convention for converting 11 to E
        add Doodson (1921) table for coefficients missing from Cartwright tables
        add function to convert from Cartwright number to constituent ID
        added option to compute climatologically affected terms without p'
    Updated 12/2024: added function to calculate tidal aliasing periods
    Updated 11/2024: allow variable case for Doodson number formalisms
        fix species in constituent parameters for complex tides
        move body tide Love/Shida numbers from predict module
    Updated 10/2024: can convert Doodson numbers formatted as strings
        update Doodson number conversions to follow Cartwright X=10 convention
        add function to parse Cartwright/Tayler/Edden tables
        add functions to calculate UKHO Extended Doodson numbers for constituents
    Updated 09/2024: add function to calculate tidal angular frequencies
    Updated 08/2024: add support for constituents in PERTH5 tables
        add back nodal arguments from PERTH3 for backwards compatibility
    Updated 01/2024: add function to create arguments coefficients table
        add function to calculate the arguments for minor constituents
        include multiples of 90 degrees as variable following Ray 2017
        add function to calculate the Doodson numbers for constituents
        add option to return None and not raise error for Doodson numbers
        moved constituent parameters function from predict to arguments
        added more constituent parameters for OTIS/ATLAS predictions
    Updated 12/2023: made keyword argument for selecting M1 coefficients
    Updated 08/2023: changed ESR netCDF4 format to TMD3 format
    Updated 04/2023: using renamed astro mean_longitudes function
        function renamed from original load_nodal_corrections
    Updated 03/2023: add basic variable typing to function inputs
    Updated 11/2022: use f-strings for formatting verbose or ascii output
    Updated 05/2022: added ESR netCDF4 formats to list of model types
        changed keyword arguments to camel case
    Updated 04/2022: updated docstrings to numpy documentation format
    Updated 12/2020: fix k1 for FES models
    Updated 08/2020: change time variable names to not overwrite functions
        update nodal corrections for FES models
    Updated 07/2020: added function docstrings.  add shallow water constituents
    Updated 09/2019: added netcdf option to corrections option
    Updated 08/2018: added correction option ATLAS for localized OTIS solutions
    Updated 07/2018: added option to use GSFC GOT nodal corrections
    Updated 09/2017: Rewritten in Python
    Rewritten in Matlab by Lana Erofeeva 01/2003
    Written by Richard Ray 03/1999
"""
from __future__ import annotations

import re
import json
import pathlib
import warnings
import numpy as np
import pyTMD.astro
from pyTMD.utilities import get_data_path

__all__ = [
    "arguments",
    "minor_arguments",
    "coefficients_table",
    "doodson_number",
    "nodal_modulation",
    "group_modulation",
    "frequency",
    "aliasing_period",
    "_arguments_table",
    "_minor_table",
    "_constituent_parameters",
    "_frequency",
    "_love_numbers",
    "_complex_love_numbers",
    "_parse_tide_potential_table",
    "_to_constituent_id",
    "_to_doodson_number",
    "_to_extended_doodson",
    "_from_doodson_number",
    "_from_extended_doodson"
]

def arguments(
        MJD: np.ndarray,
        constituents: list | np.ndarray,
        **kwargs
    ):
    """
    Calculates the nodal corrections for tidal constituents
    :cite:p:`Doodson:1941td,Schureman:1958ty,Foreman:1989dt,Pugh:2014di`

    Parameters
    ----------
    MJD: np.ndarray
        modified Julian day of input date
    constituents: list
        tidal constituent IDs
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS, FES or GOT models
    climate_solar_perigee: bool, default False
        compute climatologically affected terms without p'
    M1: str, default 'perth5'
        coefficients to use for M1 tides

                - ``'Doodson'``
                - ``'Ray'``
                - ``'Schureman'``
                - ``'perth5'``

    Returns
    -------
    pu: np.ndarray
        nodal correction angle (radians)
    pf: np.ndarray
        nodal modulation factor
    G: np.ndarray
        phase correction (degrees)
    """
    # set default keyword arguments
    kwargs.setdefault('deltat', 0.0)
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('climate_solar_perigee', False)
    kwargs.setdefault('M1', 'perth5')

    # set function for astronomical longitudes
    # use ASTRO5 routines if not using an OTIS type model
    if kwargs['corrections'] in ('OTIS','ATLAS','TMD3','netcdf'):
        method = 'Cartwright'
    else:
        method = 'ASTRO5'
    # convert from Modified Julian Dates into Ephemeris Time
    s, h, p, n, pp = pyTMD.astro.mean_longitudes(MJD + kwargs['deltat'],
        method=method)

    # number of temporal values
    nt = len(np.atleast_1d(MJD))
    # initial time conversions
    hour = 24.0*np.mod(MJD, 1)
    # convert from hours solar time into mean lunar time in degrees
    tau = 15.0*hour - s + h
    # variable for multiples of 90 degrees (Ray technical note 2017)
    # full expansion of Equilibrium Tide includes some negative cosine
    # terms and some sine terms (Pugh and Woodworth, 2014)
    k = 90.0 + np.zeros((nt))

    # determine equilibrium arguments
    fargs = np.c_[tau, s, h, p, n, pp, k]
    G = np.dot(fargs, coefficients_table(constituents, **kwargs))

    # determine modulations f and u for each model type
    if (kwargs['corrections'] == 'group'):
        pu, pf = group_modulation(h, n, p, pp, constituents, **kwargs)
    else:
        # set nodal corrections
        pu, pf = nodal_modulation(n, p, constituents, **kwargs)

    # return values as tuple
    return (pu, pf, G)

def minor_arguments(
        MJD: np.ndarray,
        **kwargs
    ):
    """
    Calculates the nodal corrections for minor tidal constituents
    in order to infer their values
    :cite:p:`Doodson:1941td,Schureman:1958ty,Foreman:1989dt,Egbert:2002ge`


    Parameters
    ----------
    MJD: np.ndarray
        modified Julian day of input date
    deltat: float or np.ndarray, default 0.0
        time correction for converting to Ephemeris Time (days)
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS, FES or GOT models

    Returns
    -------
    pu: np.ndarray
        nodal correction angle (radians)
    pf: np.ndarray
        nodal modulation factor
    G: np.ndarray
        phase correction (degrees)
    """
    # set default keyword arguments
    kwargs.setdefault('deltat', 0.0)
    kwargs.setdefault('corrections', 'OTIS')

    # set function for astronomical longitudes
    # use ASTRO5 routines if not using an OTIS type model
    if kwargs['corrections'] in ('OTIS','ATLAS','TMD3','netcdf'):
        method = 'Cartwright'
    else:
        method = 'ASTRO5'
    # convert from Modified Julian Dates into Ephemeris Time
    s, h, p, n, pp = pyTMD.astro.mean_longitudes(MJD + kwargs['deltat'],
        method=method)

    # number of temporal values
    nt = len(np.atleast_1d(MJD))
    # initial time conversions
    hour = 24.0*np.mod(MJD, 1)
    # convert from hours solar time into mean lunar time in degrees
    tau = 15.0*hour - s + h
    # variable for multiples of 90 degrees (Ray technical note 2017)
    k = 90.0 + np.zeros((nt))

    # determine equilibrium arguments
    fargs = np.c_[tau, s, h, p, n, pp, k]
    arg = np.dot(fargs, _minor_table())

    # convert mean longitudes to radians
    P = np.radians(p)
    N = np.radians(n)
    # determine nodal corrections f and u
    sinn = np.sin(N)
    cosn = np.cos(N)
    sin2n = np.sin(2.0*N)
    cos2n = np.cos(2.0*N)

    # nodal factor corrections for minor constituents
    f = np.ones((nt, 20))
    f[:,0] = np.sqrt((1.0 + 0.189*cosn - 0.0058*cos2n)**2 +
        (0.189*sinn - 0.0058*sin2n)**2)# 2Q1
    f[:,1] = f[:,0]# sigma1
    f[:,2] = f[:,0]# rho1
    f[:,3] = np.sqrt((1.0 + 0.185*cosn)**2 + (0.185*sinn)**2)# M12
    f[:,4] = np.sqrt((1.0 + 0.201*cosn)**2 + (0.201*sinn)**2)# M11
    f[:,5] = np.sqrt((1.0 + 0.221*cosn)**2 + (0.221*sinn)**2)# chi1
    f[:,9] = np.sqrt((1.0 + 0.198*cosn)**2 + (0.198*sinn)**2)# J1
    f[:,10] = np.sqrt((1.0 + 0.640*cosn + 0.134*cos2n)**2 +
        (0.640*sinn + 0.134*sin2n)**2)# OO1
    f[:,11] = np.sqrt((1.0 - 0.0373*cosn)**2 + (0.0373*sinn)**2)# 2N2
    f[:,12] = f[:,11]# mu2
    f[:,13] = f[:,11]# nu2
    f[:,15] = f[:,11]# L2
    f[:,16] = np.sqrt((1.0 + 0.441*cosn)**2 + (0.441*sinn)**2)# L2

    # nodal angle corrections for minor constituents
    u = np.zeros((nt, 20))
    u[:,0] = np.arctan2(0.189*sinn - 0.0058*sin2n,
        1.0 + 0.189*cosn - 0.0058*sin2n)# 2Q1
    u[:,1] = u[:,0]# sigma1
    u[:,2] = u[:,0]# rho1
    u[:,3] = np.arctan2( 0.185*sinn, 1.0 + 0.185*cosn)# M12
    u[:,4] = np.arctan2(-0.201*sinn, 1.0 + 0.201*cosn)# M11
    u[:,5] = np.arctan2(-0.221*sinn, 1.0 + 0.221*cosn)# chi1
    u[:,9] = np.arctan2(-0.198*sinn, 1.0 + 0.198*cosn)# J1
    u[:,10] = np.arctan2(-0.640*sinn - 0.134*sin2n,
        1.0 + 0.640*cosn + 0.134*cos2n)# OO1
    u[:,11] = np.arctan2(-0.0373*sinn, 1.0 - 0.0373*cosn)# 2N2
    u[:,12] = u[:,11]# mu2
    u[:,13] = u[:,11]# nu2
    u[:,15] = u[:,11]# L2
    u[:,16] = np.arctan2(-0.441*sinn, 1.0 + 0.441*cosn)# L2

    if kwargs['corrections'] in ('FES',):
        # additional astronomical terms for FES models
        II, xi, nu, Qa, Qu, Ra, Ru, nu_prime, nu_sec = \
            pyTMD.astro.schureman_arguments(P, N)
        # nodal factor corrections for minor constituents
        f[:,0] = np.sin(II)*(np.cos(II/2.0)**2)/0.38 # 2Q1
        f[:,1] = f[:,0] # sigma1
        f[:,2] = f[:,0] # rho1
        f[:,3] = f[:,0] # M12
        f[:,4] = np.sin(2.0*II)/0.7214 # M11
        f[:,5] = f[:,4] # chi1
        f[:,9] = f[:,4] # J1
        f[:,10] = np.sin(II)*np.power(np.sin(II/2.0),2.0)/0.01640 # OO1
        f[:,11] = np.power(np.cos(II/2.0),4.0)/0.9154 # 2N2
        f[:,12] = f[:,11] # mu2
        f[:,13] = f[:,11] # nu2
        f[:,14] = f[:,11] # lambda2
        f[:,15] = f[:,11]/Ra # L2
        f[:,18] = f[:,11] # eps2
        f[:,19] = np.power(np.sin(II),2.0)/0.1565 # eta2

        # nodal angle corrections for minor constituents
        u[:,0] = (2.0*xi - nu) # 2Q1
        u[:,1] = u[:,0] # sigma1
        u[:,2] = u[:,0] # rho1
        u[:,3] = u[:,0] # M12
        u[:,4] = -nu # M11
        u[:,5] = u[:,4] # chi1
        u[:,9] = u[:,4] # J1
        u[:,10] = (-2.0*xi - nu) # OO1
        u[:,11] = (2.0*xi - 2.0*nu) # 2N2
        u[:,12] = u[:,11] # mu2
        u[:,13] = u[:,11] # nu2
        u[:,14] = (2.0*xi - 2.0*nu) # lambda2
        u[:,15] = (2.0*xi - 2.0*nu - Ru)# L2
        u[:,18] = u[:,12] # eps2
        u[:,19] = -2.0*nu # eta2
    elif kwargs['corrections'] in ('GOT',):
        f[:,18] = f[:,11] # eps2
        f[:,19] = np.sqrt((1.0 + 0.436*cosn)**2 + (0.436*sinn)**2) # eta2
        u[:,18] = u[:,11] # eps2
        u[:,19] = np.arctan(-0.436*sinn/(1.0 + 0.436*cosn)) # eta2

    # return values as tuple
    return (u, f, arg)

# JSON file of Doodson coefficients
_coefficients_table = get_data_path(['data','doodson.json'])

def coefficients_table(
        constituents: list | tuple | np.ndarray | str,
        **kwargs
    ):
    """
    Doodson table coefficients for tidal constituents
    :cite:p:`Doodson:1921kt,Doodson:1941td,Pugh:2014di`

    Parameters
    ----------
    constituents: list, tuple, np.ndarray or str
        tidal constituent IDs
    corrections: str, default 'OTIS'
        use coefficients from OTIS, FES or GOT models
    climate_solar_perigee: bool, default False
        compute climatologically affected terms without p'
    file: str or pathlib.Path, default `coefficients.json`
        JSON file of Doodson coefficients

    Returns
    -------
    coef: np.ndarray
        Doodson coefficients (Cartwright numbers) for each constituent
    """
    # set default keyword arguments
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('climate_solar_perigee', False)
    kwargs.setdefault('file', _coefficients_table)

    # verify coefficients table path
    table = pathlib.Path(kwargs['file']).expanduser().absolute()
    # modified Doodson coefficients for constituents
    # using 7 index variables: tau, s, h, p, n, pp, k
    # tau: mean lunar time
    # s: mean longitude of moon
    # h: mean longitude of sun
    # p: mean longitude of lunar perigee
    # n: mean longitude of ascending lunar node
    # pp: mean longitude of solar perigee
    # k: 90-degree phase
    with table.open(mode='r', encoding='utf8') as fid:
        coefficients = json.load(fid)

    # compute climatologically affected terms without p'
    # following Pugh and Woodworth (2014)
    if kwargs['climate_solar_perigee']:
        coefficients['sa'] = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        coefficients['sta'] = [0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0]
    # set s1 coefficients
    if kwargs['corrections'] in ('OTIS','ATLAS','TMD3','netcdf'):
        coefficients['s1'] = [1.0, 1.0, -1.0, 0.0, 0.0, 0.0, 1.0]

    # set constituents to be iterable
    if isinstance(constituents, str):
        constituents = [constituents]
    # allocate for output coefficients
    nc = len(constituents)
    coef = np.zeros((7, nc))
    # for each constituent of interest
    for i, c in enumerate(constituents):
        try:
            coef[:,i] = coefficients[c]
        except KeyError:
            raise ValueError(f'Unsupported constituent: {c}')

    # return Doodson coefficients for constituents
    return coef

def doodson_number(
        constituents: str | list | np.ndarray,
        **kwargs
    ):
    """
    Calculates the Doodson or Cartwright number for
    tidal constituents :cite:p:`Doodson:1921kt`

    Parameters
    ----------
    constituents: str, list or np.ndarray
        tidal constituent ID(s)
    corrections: str, default 'OTIS'
        use arguments from OTIS, FES or GOT models
    formalism: str, default 'Doodson'
        constituent identifier formalism

            - ``'Cartwright'``
            - ``'Doodson'``
            - ``'Extended'``
    raise_error: bool, default True
        Raise exception if constituent is unsupported

    Returns
    -------
    numbers: float, np.ndarray or dict
        Doodson or Cartwright number for each constituent
    """
    # set default keyword arguments
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('formalism', 'Doodson')
    kwargs.setdefault('raise_error', True)
    # validate inputs
    formalisms = ('Cartwright', 'Doodson','Extended')
    assert kwargs['formalism'].title() in formalisms, \
        f'Unknown formalism {kwargs["formalism"]}'
    # get the coefficients of coefficients
    if isinstance(constituents, str):
        # try to get the Doodson coefficients for constituent
        try:
            coefficients = coefficients_table(constituents.lower(), **kwargs)
        except ValueError as exc:
            if kwargs['raise_error']:
                raise ValueError(f'Unsupported constituent {constituents}')
            else:
                return None
        # extract identifier in formalism
        if (kwargs['formalism'].title() == 'Cartwright'):
            # extract Cartwright number
            numbers = np.array(coefficients[:6,0])
        elif (kwargs['formalism'].title() == 'Doodson'):
            # convert from coefficients to Doodson number
            numbers = _to_doodson_number(coefficients[:,0], **kwargs)
        elif (kwargs['formalism'].title() == 'Extended'):
            # convert to extended Doodson number in UKHO format
            numbers = _to_extended_doodson(coefficients[:,0], **kwargs)
    else:
        # output dictionary with Doodson numbers
        numbers = {}
        # for each input constituent
        for i,c in enumerate(constituents):
            # try to get the Doodson coefficients for constituent
            try:
                coefficients = coefficients_table(c.lower(), **kwargs)
            except ValueError as exc:
                if kwargs['raise_error']:
                    raise ValueError(f'Unsupported constituent {c}')
                else:
                    numbers[c] = None
                    continue
            # convert from coefficients to Doodson number
            if (kwargs['formalism'].title() == 'Cartwright'):
                # extract Cartwright number
                numbers[c] = np.array(coefficients[:6,0])
            elif (kwargs['formalism'].title() == 'Doodson'):
                # convert from coefficients to Doodson number
                numbers[c] = _to_doodson_number(coefficients[:,0], **kwargs)
            elif (kwargs['formalism'].title() == 'Extended'):
                # convert to extended Doodson number in UKHO format
                numbers[c] = _to_extended_doodson(coefficients[:,0], **kwargs)
    # return the Doodson or Cartwright number
    return numbers

def nodal(*args, **kwargs):
    warnings.warn("Deprecated. Please use pyTMD.arguments.nodal_modulation instead",
        DeprecationWarning)
    return nodal_modulation(*args, **kwargs)

# PURPOSE: compute the nodal corrections
def nodal_modulation(
        n: np.ndarray,
        p: np.ndarray,
        constituents: list | tuple | np.ndarray | str,
        **kwargs
    ):
    """
    Calculates the nodal corrections for tidal constituents
    :cite:p:`Doodson:1941td,Schureman:1958ty,Foreman:1989dt,Ray:1999vm`

    Calculates factors for compound tides using recursion

    Parameters
    ----------
    n: np.ndarray
        mean longitude of ascending lunar node (degrees)
    p: np.ndarray
        mean longitude of lunar perigee (degrees)
    constituents: list, tuple, np.ndarray or str
        tidal constituent IDs
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS, FES or GOT models
    M1: str, default 'perth5'
        coefficients to use for M1 tides

                - ``'Doodson'``
                - ``'Ray'``
                - ``'Schureman'``
                - ``'perth5'``

    Returns
    -------
    u: np.ndarray
        nodal correction angle (radians)
    f: np.ndarray
        nodal modulation factor
    """
    # set default keyword arguments
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('M1', 'perth5')
    # set correction type
    OTIS_TYPE = kwargs['corrections'] in ('OTIS','ATLAS','TMD3','netcdf')
    FES_TYPE = kwargs['corrections'] in ('FES',)
    PERTH3_TYPE = kwargs['corrections'] in ('perth3',)

    # convert longitudes to radians
    N = np.radians(n)
    P = np.radians(p)
    # trigonometric factors for nodal corrections
    sinn = np.sin(N)
    cosn = np.cos(N)
    sin2n = np.sin(2.0*N)
    cos2n = np.cos(2.0*N)
    sin3n = np.sin(3.0*N)
    sinp  = np.sin(P)
    cosp  = np.cos(P)
    sin2p = np.sin(2.0*P)
    cos2p = np.cos(2.0*P)
    # compute additional angles for FES models
    if FES_TYPE:
        # additional astronomical terms for FES models
        II, xi, nu, Qa, Qu, Ra, Ru, nu_prime, nu_sec = \
            pyTMD.astro.schureman_arguments(P, N)

    # set constituents to be iterable
    if isinstance(constituents, str):
        constituents = [constituents]

    # set nodal corrections
    nt = len(np.atleast_1d(n))
    nc = len(constituents)
    # nodal factor correction
    f = np.zeros((nt, nc))
    # nodal angle correction
    u = np.zeros((nt, nc))

    # compute standard nodal corrections f and u
    for i, c in enumerate(constituents):
        if not bool(kwargs['corrections']):
            # no corrections to apply
            f[:,i] = 1.0
            u[:,i] = 0.0
            continue
        elif c in ('msf','tau1','p1','theta1','lambda2','s2') and OTIS_TYPE:
            term1 = 0.0
            term2 = 1.0
        elif c in ('p1','s2') and (FES_TYPE or PERTH3_TYPE):
            # Schureman: Table 2, Page 165
            # Schureman: Table 2, Page 166
            term1 = 0.0
            term2 = 1.0
        elif c in ('mm','msm') and OTIS_TYPE:
            term1 = 0.0
            term2 = 1.0 - 0.130*cosn
        elif c in ('mm','msm') and FES_TYPE:
            # Schureman: Page 164, Table 2
            # Schureman: Page 25, Equation 73
            term1 = 0.0
            term2 = (2.0/3.0 - np.power(np.sin(II),2.0))/0.5021
        elif c in ('mm','msm'):
            term1 = -0.0534*sin2p - 0.0219*np.sin(2.0*P - N)
            term2 = 1.0 - 0.1308*cosn - 0.0534*cos2p - 0.0219*np.cos(2.0*P - N)
        elif c in ('mf','msqm','msp','mq','mtm') and OTIS_TYPE:
            f[:,i] = 1.043 + 0.414*cosn
            u[:,i] = np.radians(-23.7*sinn + 2.7*sin2n - 0.4*sin3n)
            continue
        elif c in ('mf','msqm','msp','mq','mt','mtm') and FES_TYPE:
            # Schureman: Table 2, Page 164
            # Schureman: Page 25, Equation 74
            f[:,i] = np.power(np.sin(II),2.0)/0.1578
            u[:,i] = -2.0*xi
            continue
        elif c in ('mf','msqm','msp','mq'):
            term1 = -0.04324*sin2p - 0.41465*sinn - 0.03873*sin2n
            term2 = 1.0 + 0.04324*cos2p + 0.41465*cosn + 0.03873*cos2n
        elif c in ('mt',) and OTIS_TYPE:
            term1 = -0.203*sinn - 0.040*sin2n
            term2 = 1.0 + 0.203*cosn + 0.040*cos2n
        elif c in ('mt','mtm',):
            term1 = -0.018*sin2p - 0.4145*sinn - 0.040*sin2n
            term2 = 1.0 + 0.018*cos2p + 0.4145*cosn + 0.040*cos2n
        elif c in ('msf',) and FES_TYPE:
            # Schureman: Table 2, Page 165
            # Schureman: Page 25, Equation 78
            # from table 14: use f factor from m2
            f[:,i] = np.power(np.cos(II/2.0),4.0)/0.9154
            # from table 11: take negative of u factor from m2
            u[:,i] = -(2.0*xi - 2.0*nu)
            continue
        elif c in ('msf',):
            # linear tide and not compound
            term1 = 0.137*sinn
            term2 = 1.0
        elif c in ('mst',):
            term1 = -0.380*sin2p - 0.413*sinn - 0.037*sin2n
            term2 = 1.0 + 0.380*cos2p + 0.413*cosn + 0.037*cos2n
        elif c in ('o1','so3','op2') and OTIS_TYPE:
            term1 = 0.189*sinn - 0.0058*sin2n
            term2 = 1.0 + 0.189*cosn - 0.0058*cos2n
            f[:,i] = np.sqrt(term1**2 + term2**2) # O1
            u[:,i] = np.radians(10.8*sinn - 1.3*sin2n + 0.2*sin3n)
            continue
        elif c in ('o1','so3','op2','2q1','q1','rho1','sigma1') and FES_TYPE:
            # Schureman: Table 2, Page 164
            # Schureman: Page 25, Equation 75
            f[:,i] = np.sin(II)*np.power(np.cos(II/2.0),2)/0.38
            u[:,i] = (2.0*xi - nu)
            continue
        elif c in ('q1','o1') and PERTH3_TYPE:
            f[:,i] = 1.009 + 0.187*cosn - 0.015*cos2n
            u[:,i] = np.radians(10.8*sinn - 1.3*sin2n)
            continue
        elif c in ('o1','so3','op2'):
            term1 = 0.1886*sinn - 0.0058*sin2n - 0.0065*sin2p
            term2 = 1.0 + 0.1886*cosn - 0.0058*cos2n - 0.0065*cos2p
        elif c in ('2q1','q1','rho1','sigma1') and OTIS_TYPE:
            f[:,i] = np.sqrt((1.0 + 0.188*cosn)**2 + (0.188*sinn)**2)
            u[:,i] = np.arctan(0.189*sinn/(1.0 + 0.189*cosn))
            continue
        elif c in ('2q1','q1','rho1','sigma1'):
            term1 = 0.1886*sinn
            term2 = 1.0 + 0.1886*cosn
        elif c in ('tau1',):
            term1 = 0.219*sinn
            term2 = 1.0 - 0.219*cosn
        elif c in ('beta1',):
            term1 = 0.226*sinn
            term2 = 1.0 + 0.226*cosn
        elif c in ('m1',) and (kwargs['M1'] == 'Doodson'):
            # A. T. Doodson's coefficients for M1 tides
            term1 = sinp + 0.2*np.sin(P - N)
            term2 = 2.0*cosp + 0.4*np.cos(P - N)
        elif c in ('m1',) and (kwargs['M1'] == 'Ray'):
            # R. Ray's coefficients for M1 tides (perth3)
            term1 = 0.64*sinp + 0.135*np.sin(P - N)
            term2 = 1.36*cosp + 0.267*np.cos(P - N)
        elif c in ('m1',) and (kwargs['M1'] == 'Schureman'):
            # Schureman: Table 2, Page 165
            # Schureman: Page 43, Equation 206
            f[:,i] = np.sin(II)*np.power(np.cos(II/2.0),2)/(0.38*Qa)
            u[:,i] = -nu - Qu
            continue
        elif c in ('m1',) and (kwargs['M1'] == 'perth5'):
            # assumes M1 argument includes p
            term1 = -0.2294*sinn - 0.3594*sin2p - 0.0664*np.sin(2.0*P - N)
            term2 = 1.0 + 0.1722*cosn + 0.3594*cos2p + 0.0664*np.cos(2.0*P - N)
        elif c in ('chi1',) and OTIS_TYPE:
            term1 = -0.221*sinn
            term2 = 1.0 + 0.221*cosn
        elif c in ('chi1','theta1','j1') and FES_TYPE:
            # Schureman: Table 2, Page 164
            # Schureman: Page 25, Equation 76
            f[:,i] = np.sin(2.0*II)/0.7214
            u[:,i] = -nu
            continue
        elif c in ('chi1',):
            term1 = -0.250*sinn
            term2 = 1.0 + 0.193*cosn
        elif c in ('p1',):
            term1 = -0.0112*sinn
            term2 = 1.0 - 0.0112*cosn
        elif c in ('k1','sk3','2sk5') and OTIS_TYPE:
            term1 = -0.1554*sinn + 0.0029*sin2n
            term2 = 1.0 + 0.1158*cosn - 0.0029*cos2n
        elif c in ('k1','sk3','2sk5') and FES_TYPE:
            # Schureman: Table 2, Page 165
            # Schureman: Page 45, Equation 227
            temp1 = 0.8965*np.power(np.sin(2.0*II),2.0)
            temp2 = 0.6001*np.sin(2.0*II)*np.cos(nu)
            f[:,i] = np.sqrt(temp1 + temp2 + 0.1006)
            u[:,i] = -nu_prime
            continue
        elif c in ('k1',) and PERTH3_TYPE:
            f[:,i] = 1.006 + 0.115*cosn - 0.009*cos2n
            u[:,i] = np.radians(-8.9*sinn + 0.7*sin2n)
            continue
        elif c in ('k1','sk3','2sk5'):
            term1 = -0.1554*sinn + 0.0031*sin2n
            term2 = 1.0 + 0.1158*cosn - 0.0028*cos2n
        elif c in ('j1','theta1'):
            term1 = -0.227*sinn
            term2 = 1.0 + 0.169*cosn
        elif c in ('oo1','ups1') and OTIS_TYPE:
            term1 = -0.640*sinn - 0.134*sin2n
            term2 = 1.0 + 0.640*cosn + 0.134*cos2n
        elif c in ('oo1','ups1') and FES_TYPE:
            # Schureman: Table 2, Page 164
            # Schureman: Page 25, Equation 77
            f[:,i] = np.sin(II)*np.power(np.sin(II/2.0),2.0)/0.01640
            u[:,i] = -2.0*xi - nu
            continue
        elif c in ('oo1','ups1'):
            term1 = -0.640*sinn - 0.134*sin2n - 0.150*sin2p
            term2 = 1.0 + 0.640*cosn + 0.134*cos2n + 0.150*cos2p
        elif c in ('m2','2n2','mu2','n2','nu2','lambda2','ms4','eps2','2sm6',
                '2sn6','mp1','mp3','sn4') and FES_TYPE:
            # Schureman: Table 2, Page 165
            # Schureman: Page 25, Equation 78
            f[:,i] = np.power(np.cos(II/2.0),4.0)/0.9154
            u[:,i] = 2.0*xi - 2.0*nu
            continue
        elif c in ('m2','n2') and PERTH3_TYPE:
            f[:,i] = 1.000 - 0.037*cosn
            u[:,i] = np.radians(-2.1*sinn)
            continue
        elif c in ('m2','2n2','mu2','n2','nu2','lambda2','ms4','eps2','2sm6',
                '2sn6','mp1','mp3','sn4'):
            term1 = -0.03731*sinn + 0.00052*sin2n
            term2 = 1.0 - 0.03731*cosn + 0.00052*cos2n
        elif c in ('l2','sl4') and OTIS_TYPE:
            term1 = -0.25*sin2p - 0.11*np.sin(2.0*P - N) - 0.04*sinn
            term2 = 1.0 - 0.25*cos2p - 0.11*np.cos(2.0*P - N) - 0.04*cosn
        elif c in ('l2','sl4') and FES_TYPE:
            # Schureman: Table 2, Page 165
            # Schureman: Page 44, Equation 215
            f[:,i] = np.power(np.cos(II/2.0),4.0)/(0.9154*Ra)
            u[:,i] = 2.0*xi - 2.0*nu - Ru
            continue
        elif c in ('l2','sl4'):
            term1 = -0.25*sin2p - 0.11*np.sin(2.0*P - N) - 0.037*sinn
            term2 = 1.0 - 0.25*cos2p - 0.11*np.cos(2.0*P - N) - 0.037*cosn
        elif c in ('l2b',):
            # for when l2 is split into two constituents
            term1 = 0.441*sinn
            term2 = 1.0 + 0.441*cosn
        elif c in ('k2','sk4','2sk6','kp1') and OTIS_TYPE:
            term1 = -0.3108*sinn - 0.0324*sin2n
            term2 = 1.0 + 0.2852*cosn + 0.0324*cos2n
        elif c in ('k2','sk4','2sk6','kp1') and FES_TYPE:
            # Schureman: Table 2, Page 166
            # Schureman: Page 46, Equation 235
            term1 = 19.0444 * np.power(np.sin(II),4.0)
            term2 = 2.7702 * np.power(np.sin(II),2.0) * np.cos(2.0*nu)
            f[:,i] = np.sqrt(term1 + term2 + 0.0981)
            u[:,i] = -2.0*nu_sec
            continue
        elif c in ('k2',) and PERTH3_TYPE:
            f[:,i] = 1.024 + 0.286*cosn + 0.008*cos2n
            u[:,i] = np.radians(-17.7*sinn + 0.7*sin2n)
            continue
        elif c in ('k2','sk4','2sk6','kp1'):
            term1 = -0.3108*sinn - 0.0324*sin2n
            term2 = 1.0 + 0.2853*cosn + 0.0324*cos2n
        elif c in ('gamma2',):
            term1 = 0.147*np.sin(2.0*(N - P))
            term2 = 1.0 + 0.147*np.cos(2.0*(N - P))
        elif c in ('delta2',):
            term1 = 0.505*sin2p + 0.505*sinn - 0.165*sin2n
            term2 = 1.0 - 0.505*cos2p - 0.505*cosn + 0.165*cos2n
        elif c in ('eta2','zeta2') and FES_TYPE:
            # Schureman: Table 2, Page 165
            # Schureman: Page 25, Equation 79
            f[:,i] = np.power(np.sin(II),2.0)/0.1565
            u[:,i] = -2.0*nu
            continue
        elif c in ('eta2','zeta2'):
            term1 = -0.436*sinn
            term2 = 1.0 + 0.436*cosn
        elif c in ('s2',):
            term1 = 0.00225*sinn
            term2 = 1.0 + 0.00225*cosn
        elif c in ("m1'",):
            # Linear 3rd degree terms
            term1 = -0.01815*sinn
            term2 = 1.0 - 0.27837*cosn
        elif c in ("q1'",):
            # Linear 3rd degree terms
            term1 = 0.3915*sinn + 0.033*sin2n + 0.061*sin2p
            term2 = 1.0 + 0.3915*cosn + 0.033*cos2n + 0.06*cos2p
        elif c in ("j1'",):
            # Linear 3rd degree terms
            term1 = -0.438*sinn - 0.033*sin2n
            term2 = 1.0 + 0.372*cosn + 0.033*cos2n
        elif c in ("2n2'",):
            # Linear 3rd degree terms
            term1 = 0.166*sinn
            term2 = 1.0 + 0.166*cosn
        elif c in ("n2'",):
            # Linear 3rd degree terms
            term1 = 0.1705*sinn - 0.0035*sin2n - 0.0176*sin2p
            term2 = 1.0 + 0.1705*cosn - 0.0035*cos2n - 0.0176*cos2p
        elif c in ("l2'"):
            # Linear 3rd degree terms
            term1 = -0.2495*sinn
            term2 = 1.0 + 0.1315*cosn
        elif c in ('m3',) and FES_TYPE:
            # Schureman: Table 2, Page 166
            # Schureman: Page 36, Equation 149
            f[:,i] = np.power(np.cos(II/2.0), 6.0)/0.8758
            u[:,i] = (3.0*xi - 3.0*nu)
            continue
        elif c in ('m3','e3'):
            # Linear 3rd degree terms
            term1 = -0.05644*sinn
            term2 = 1.0 - 0.05644*cosn
        elif c in ('j3','f3'):
            term1 = -0.464*sinn - 0.052*sin2n
            term2 = 1.0 + 0.387*cosn + 0.052*cos2n
        elif c in ('l3',):
            term1 = -0.373*sin2p - 0.164*np.sin(2.0*P - N)
            term2 = 1.0 - 0.373*cos2p - 0.164*np.cos(2.0*P - N)
        elif c in ('mfdw',):
            # special test of Doodson-Warburg formula
            f[:,i] = 1.043 + 0.414*cosn
            u[:,i] = np.radians(-23.7*sinn + 2.7*sin2n - 0.4*sin3n)
            continue
        elif c in ('so1','2so3','2po1'):
            # compound tides calculated using recursion
            parents = ['o1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]
            u[:,i] = -utmp[:,0]
            continue
        elif c in ('o3',):
            # compound tides calculated using recursion
            parents = ['o1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**3
            u[:,i] = 3.0*utmp[:,0]
            continue
        elif c in ('2k2'):
            # compound tides calculated using recursion
            parents = ['k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2
            u[:,i] = 2.0*utmp[:,0]
            continue
        elif c in ('tk1'):
            # compound tides calculated using recursion
            parents = ['k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]
            u[:,i] = -utmp[:,0]
            continue
        elif c in ('2oop1'):
            # compound tides calculated using recursion
            parents = ['oo1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2
            u[:,i] = 2.0*utmp[:,0]
            continue
        elif c in ('oq2'):
            # compound tides calculated using recursion
            parents = ['o1','q1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in ('2oq1'):
            # compound tides calculated using recursion
            parents = ['o1','q1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] - utmp[:,1]
            continue
        elif c in ('ko2'):
            # compound tides calculated using recursion
            parents = ['o1','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in ('opk1',):
            # compound tides calculated using recursion
            parents = ['o1','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] - utmp[:,1]
            continue
        elif c in ('2ook1',):
            # compound tides calculated using recursion
            parents = ['oo1','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] - utmp[:,1]
            continue
        elif c in ('kj2',):
            # compound tides calculated using recursion
            parents = ['k1','j1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in ('kjq1'):
            # compound tides calculated using recursion
            parents = ['k1','j1','q1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1] * ftmp[:,2]
            u[:,i] = utmp[:,0] + utmp[:,1] - utmp[:,2]
            continue
        elif c in ('k3',):
            # compound tides calculated using recursion
            parents = ['k1','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in('m4','mn4','mns2','2ms2','mnus2','mmus2','2ns2','n4','mnu4',
                'mmu4','2mt6','2ms6','msn6','mns6','2mr6','msmu6','2mp3','2ms3',
                '2mp5','2msp7','2(ms)8','2ms8'):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2
            u[:,i] = 2.0*utmp[:,0]
            continue
        elif c in ('msn2','snm2','nsm2'):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2
            u[:,i] = 0.0
            continue
        elif c in ('mmun2','2mn2'):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**3
            u[:,i] = utmp[:,0]
            continue
        elif c in ('2sm2',):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]
            u[:,i] = -utmp[:,0]
            continue
        elif c in ('m6','2mn6','2mnu6','2mmu6','2nm6','mnnu6','mnmu6','3ms8',
                '3mp7','2msn8','3ms5','3mp5','3ms4','3m2s2','3m2s10','2mn2s2'):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**3
            u[:,i] = 3.0*utmp[:,0]
            continue
        elif c in ('m8','ma8','3mn8','3mnu8','3mmu8','2mn8','2(mn):8','3msn10',
                '4ms10','2(mn)S10','4m2s12'):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**4
            u[:,i] = 4.0*utmp[:,0]
            continue
        elif c in ('m10','4mn10','5ms12','4msn12','4mns12'):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**5
            u[:,i] = 5.0*utmp[:,0]
            continue
        elif c in ('m12','5mn12','6ms14','5msn14'):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**6
            u[:,i] = 6.0*utmp[:,0]
            continue
        elif c in ('m14',):
            # compound tides calculated using recursion
            parents = ['m2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**7
            u[:,i] = 7.0*utmp[:,0]
            continue
        elif c in ('mo3','no3','mso5'):
            # compound tides calculated using recursion
            parents = ['m2','o1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in ('no1','nso3'):
            # compound tides calculated using recursion
            parents = ['m2','o1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] - utmp[:,1]
            continue
        elif c in ('mq3','nq3'):
            # compound tides calculated using recursion
            parents = ['m2','q1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in ('2mq3',):
            # compound tides calculated using recursion
            parents = ['m2','q1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] - utmp[:,1]
            continue
        elif c in ('2no3',):
            # compound tides calculated using recursion
            parents = ['m2','o1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] - utmp[:,1]
            continue
        elif c in ('2mo5','2no5','mno5','2mso7','2(ms):o9'):
            # compound tides calculated using recursion
            parents = ['m2','o1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('2mno7','3mo7'):
            # compound tides calculated using recursion
            parents = ['m2','o1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**3 * ftmp[:,1]
            u[:,i] = 3.0*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('mk3','nk3','msk5','nsk5'):
            # compound tides calculated using recursion
            parents = ['m2','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in ('mnk5','2mk5','2nk5','2msk7'):
            # compound tides calculated using recursion
            parents = ['m2','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('2mk3',):
            # compound tides calculated using recursion
            parents = ['m2','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] - utmp[:,1]
            continue
        elif c in ('3mk7','2mnk7','2nmk7','3nk7','3msk9'):
            # compound tides calculated using recursion
            parents = ['m2','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**3 * ftmp[:,1]
            u[:,i] = 3.0*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('3msk7',):
            # compound tides calculated using recursion
            parents = ['m2','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**3 * ftmp[:,1]
            u[:,i] = 3.0*utmp[:,0] - utmp[:,1]
            continue
        elif c in ('4mk9','3mnk9','2m2nk9','2(mn):k9','3nmk9','4msk11'):
            # compound tides calculated using recursion
            parents = ['m2','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**4 * ftmp[:,1]
            u[:,i] = 4.0*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('3km5',):
            # compound tides calculated using recursion
            parents = ['m2','k1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]**3
            u[:,i] = utmp[:,0] + 3.0*utmp[:,1]
            continue
        elif c in ('mk4','nk4','mks2'):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in ('msk2','2smk4','msk6','snk6'):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] - utmp[:,1]
            continue
        elif c in ('mnk6','2mk6','2msk8','msnk8'):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('mnk2','2mk2'):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] - utmp[:,1]
            continue
        elif c in ('mkn2','nkm2'):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = utmp[:,1]
            continue
        elif c in ('skm2',):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = -utmp[:,0] + utmp[:,1]
            continue
        elif c in ('3mk8','2mnk8'):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**3 * ftmp[:,1]
            u[:,i] = 3.0*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('m2(ks)2',):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]**2
            u[:,i] = utmp[:,0] + 2.0*utmp[:,1]
            continue
        elif c in ('2ms2k2',):
            # compound tides calculated using recursion
            parents = ['m2','k2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]**2
            u[:,i] = 2.0*utmp[:,0] - 2.0*utmp[:,1]
            continue
        elif c in ('mko5','msko7'):
            # compound tides calculated using recursion
            parents = ['m2','k2','o1']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1] * ftmp[:,2]
            u[:,i] = utmp[:,0] + utmp[:,1] + utmp[:,2]
            continue
        elif c in ('ml4','msl6'):
            # compound tides calculated using recursion
            parents = ['m2','l2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0] * ftmp[:,1]
            u[:,i] = utmp[:,0] + utmp[:,1]
            continue
        elif c in ('2ml2',):
            # compound tides calculated using recursion
            parents = ['m2','l2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] - utmp[:,1]
            continue
        elif c in ('2ml6','2ml2s2','2mls4','2msl8'):
            # compound tides calculated using recursion
            parents = ['m2','l2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**2 * ftmp[:,1]
            u[:,i] = 2.0*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('2nmls6','3mls6','2mnls6','3ml8','2mnl8','3msl10'):
            # compound tides calculated using recursion
            parents = ['m2','l2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**3 * ftmp[:,1]
            u[:,i] = 3.0*utmp[:,0] + utmp[:,1]
            continue
        elif c in ('4msl12',):
            # compound tides calculated using recursion
            parents = ['m2','l2']
            utmp, ftmp = nodal_modulation(n, p, parents, **kwargs)
            f[:,i] = ftmp[:,0]**4 * ftmp[:,1]
            u[:,i] = 4.0*utmp[:,0] + utmp[:,1]
            continue
        else:
            # default for linear tides
            term1 = 0.0
            term2 = 1.0

        # calculate factors for linear tides
        # and parent waves in compound tides
        f[:,i] = np.sqrt(term1**2 + term2**2)
        u[:,i] = np.arctan2(term1, term2)

    # return corrections for constituents
    return (u, f)

# PURPOSE: compute the tidal group modulations
def group_modulation(
        h: np.ndarray,
        n: np.ndarray,
        p: np.ndarray,
        ps: np.ndarray,
        constituents: list | tuple | np.ndarray | str,
        **kwargs
    ):
    """
    Calculates the generalized modulations for tidal groups
    :cite:p:`Ray:1999vm,Ray:2022hx`

    Uses the default nodal modulations for unsupported tidal groups

    Parameters
    ----------
    h: np.ndarray
        mean longitude of sun (degrees)
    n: np.ndarray
        mean longitude of ascending lunar node (degrees)
    p: np.ndarray
        mean longitude of lunar perigee (degrees)
    ps: np.ndarray
        mean longitude of solar perigee (degrees)
    constituents: list, tuple, np.ndarray or str
        tidal constituent IDs

    Returns
    -------
    f: np.ndarray
        modulation factor
    u: np.ndarray
        angle correction (radians)
    """

    # convert longitudes to radians
    H = np.radians(h)
    Np = -np.radians(n)
    P = np.radians(p)
    Ps = np.radians(ps)
    # mean anomaly of the sun
    lp = H - Ps

    # set constituents to be iterable
    if isinstance(constituents, str):
        constituents = [constituents]

    # set group modulations
    nt = len(np.atleast_1d(h))
    nc = len(constituents)
    # group factor correction
    f = np.zeros((nt, nc))
    # group angle correction
    u = np.zeros((nt, nc))

    # compute group modulations f and u
    for i, c in enumerate(constituents):
        if c in ('mm',):
            term1 = -0.0137*np.sin(-2.0*H+2.0*P-Np) + \
                0.1912*np.sin(-2.0*H + 2.0*P) - \
                0.0125*np.sin(-2.0*H + 2.0*P + Np) - \
                0.0657*np.sin(-Np) - \
                0.0653*np.sin(Np) - \
                0.0534*np.sin(2.0*P) - \
                0.0219*np.sin(2.0*P + Np) - \
                0.0139*np.sin(2.0*H)
            term2 = 1.0 + 0.0137*np.cos(2.0*H - 2.0*P - Np) + \
                0.1912*np.cos(-2.0*H + 2.0*P) - \
                0.0125*np.cos(-2.0*H + 2.0*P + Np) - \
                0.1309*np.cos(Np) - \
                0.0534*np.cos(2.0*P) - \
                0.0219*np.cos(2.0*P + Np) - \
                0.0139*np.cos(2.0*H)
        elif c in ('mf',):
            term1 = 0.0875*np.sin(-2.0*H) + \
                0.0432*np.sin(-2.0*P) + \
                0.4145*np.sin(Np) + \
                0.0387*np.sin(2.0*Np)
            term2 = 1.0 + 0.0875*np.cos(2.0*H) + \
                0.0432*np.cos(2.0*P) + \
                0.4145*np.cos(Np) + \
                0.0387*np.cos(2.0*Np)
        elif c in ('mt',):
            term1 = 0.0721*np.sin(-2.0*H) + \
                0.1897*np.sin(-2.0*H + 2.0*P) + \
                0.0784*np.sin(-2.0*H + 2.0*P + Np) + \
                0.4146*np.sin(Np)
            term2 = 1.0 + 0.0721*np.cos(2.0*H) + \
                0.1897*np.cos(-2.0*H + 2.0*P) + \
                0.0784*np.cos(-2.0*H + 2.0*P + Np) + \
                0.4146*np.cos(Np)
        elif c in ('mq',):
            term1 = 1.207*np.sin(-2.0*H + 2.0*P) + \
                0.497*np.sin(-2.0*H + 2.0*P + Np) + \
                0.414*np.sin(Np)
            term2 = 1.0 + 1.207*np.cos(-2.0*H + 2.0*P) + \
                0.497*np.cos(-2.0*H + 2.0*P + Np) + \
                0.414*np.cos(Np)
        elif c in ('2q1',):
            term1 = 0.1886*np.sin(-Np) + \
                0.2274*np.sin(2.0*H - 2.0*P - Np) + \
                1.2086*np.sin(2.0*H - 2.0*P)
            term2 = 1.0 + 0.1886*np.cos(Np) + \
                0.2274*np.cos(2.0*H - 2.0*P - Np) + \
                1.2086*np.cos(2.0*H - 2.0*P)
        elif c in ('sigma1',):
            term1 = 0.1561*np.sin(-2.0*H + 2.0*P - Np) - \
                0.1882*np.sin(Np) + \
                0.7979*np.sin(-2.0*H + 2.0*P) + \
                0.0815*np.sin(lp)
            term2 = 1.0 + 0.1561*np.cos(-2.0*H + 2.0*P - Np) + \
                0.1882*np.cos(Np) + \
                0.8569*np.cos(-2.0*H + 2.0*P) + \
                0.0538*np.cos(lp) 
        elif c in ('q1',):
            term1 = 0.1886*np.sin(-Np) + \
                0.0359*np.sin(2.0*H - 2.0*P - Np) + \
                0.1901*np.sin(2.0*H - 2.0*P)
            term2 = 1.0 + 0.1886*np.cos(Np) + \
                0.0359*np.cos(2.0*H - 2.0*P - Np) + \
                0.1901*np.cos(2.0*H - 2.0*P)
        elif c in ('o1',):
            term1 = -0.0058*np.sin(-2*Np) + \
                0.1886*np.sin(-Np) - \
                0.0065*np.sin(2.0*P) - \
                0.0131*np.sin(2.0*H)
            term2 = 1.0 - 0.0058*np.cos(2*Np) + \
                0.1886*np.cos(Np) - \
                0.0065*np.cos(2*P) - \
                0.0131*np.cos(2.0*H)
        elif c in ('m1',):
            term1 = 0.0941*np.sin(-2.0*H) + \
                0.0664*np.sin(-2.0*P - Np) + \
                0.3594*np.sin(-2.0*P) + \
                0.2008*np.sin(Np) + \
                0.1910*np.sin(2.0*H - 2.0*P) + \
                0.0422*np.sin(2.0*H - 2.0*P + Np)
            term2 = 1.0 + 0.0941*np.cos(2.0*H) + \
                0.0664*np.cos(2.0*P + Np) + \
                0.3594*np.cos(2.0*P) + \
                0.2008*np.cos(Np) + \
                0.1910*np.cos(2.0*H - 2.0*P) + \
                0.0422*np.cos(2.0*H-2.0*P+Np)
        elif c in ('k1',):
            term1 = -0.0184*np.sin(-3.0*H + Ps) + \
                0.0036*np.sin(-2.0*H - Np) + \
                0.3166*np.sin(2.0*H) - \
                0.0026*np.sin(H + Ps) + \
                0.0075*np.sin(-lp) + \
                0.1558*np.sin(Np) - \
                0.0030*np.sin(2.0*Np) + \
                0.0049*np.sin(lp) + \
                0.0128*np.sin(2.0*H)
            term2 = 1.0 - 0.0184*np.cos(-3.0*H + Ps) + \
                0.0036*np.cos(2.0*H + Np) - \
                0.3166*np.cos(2.0*H) + \
                0.0026*np.cos(H + Ps) + \
                0.0075*np.cos(lp) + \
                0.1164*np.cos(Np) - \
                0.0030*np.cos(2.0*Np) + \
                0.0049*np.cos(lp) + \
                0.0128*np.cos(2.0*H)
        elif c in ('j1',):
            term1 = 0.1922*np.sin(-2.0*H + 2.0*P) + \
                0.0378*np.sin(-2.0*H + 2.0*P + Np) + \
                0.2268*np.sin(Np) - \
                0.0155*np.sin(2.0*P)
            term2 = 1.0 + 0.1922*np.cos(-2.0*H + 2.0*P) + \
                0.0378*np.cos(-2.0*H + 2.0*P + Np) + \
                0.1701*np.cos(Np) - \
                0.0155*np.cos(2.0*P)
        elif c in ('oo1',):
            term1 = 0.3029*np.sin(-2.0*H) + \
                0.0593*np.sin(-2.0*H + Np) + \
                0.1497*np.sin(-2.0*P) + \
                0.6404*np.sin(Np) + \
                0.1337*np.sin(2.0*Np)
            term2 = 1.0 + 0.3029*np.cos(-2.0*H) + \
                0.0593*np.cos(-2.0*H + Np) + \
                0.1497*np.cos(-2.0*P) + \
                0.6404*np.cos(Np) + \
                0.1337*np.cos(2.0*Np)
        elif c in ('eps2',):
            term1 = 0.385*np.sin(-2.0*H + 2.0*P)
            term2 = 1.0 + 0.385*np.cos(-2.0*H + 2.0*P)
        elif c in ('2n2',):
            term1 = 0.0374*np.sin(Np) + \
                1.2064*np.sin(2.0*H - 2.0*P) - \
                0.0139*np.sin(-lp) - \
                0.0170*np.sin(H - 2.0*P + Ps) - \
                0.0104*np.sin(H - P) + \
                0.0156*np.sin(lp) - \
                0.0448*np.sin(2.0*H - 2.0*P - Np) + \
                0.0808*np.sin(3.0*H - 2.0*P - 4.939) + \
                0.0369*np.sin(4.0*H - 4.0*P)
            term2 = 1.0 - 0.0374*np.cos(Np) + \
                1.2064*np.cos(2.0*H - 2.0*P) - \
                0.0139*np.cos(-lp) - \
                0.0170*np.cos(H - 2.0*P + Ps) - \
                0.0104*np.cos(H - P) + \
                0.0156*np.cos(lp) - \
                0.0448*np.cos(2.0*H - 2.0*P - Np) + \
                0.0808*np.cos(3.0*H - 2.0*P - 4.939) + \
                0.0369*np.cos(4.0*H - 4.0*P)
        elif c in ('mu2',):
            term1 = -0.0115*np.sin(-3.0*H + 2.0*P + Ps) - \
                0.0310*np.sin(-2.0*H + 2.0*P - Np) + \
                0.8289*np.sin(-2.0*H + 2.0*P) - \
                0.0140*np.sin(-lp) - \
                0.0086*np.sin(-H + P) + \
                0.0130*np.sin(-H + 2.0*P - Ps) + \
                0.0371*np.sin(Np) + \
                0.0670*np.sin(lp) + \
                0.0306*np.sin(2.0*H - 2.0*P) 
            term2 = 1.0 - 0.0115*np.cos(-3.0*H + 2.0*P + Ps) - \
                0.0310*np.cos(-2.0*H + 2.0*P - Np) + \
                0.8289*np.cos(-2.0*H + 2.0*P) - \
                0.0140*np.cos(-lp) - \
                0.0086*np.cos(-H + P) + \
                0.0130*np.cos(-H + 2.0*P - Ps) - \
                0.0371*np.cos(Np) + \
                0.0670*np.cos(lp) + \
                0.0306*np.cos(2.0*H - 2.0*P)
        elif c in ('n2',):
            term1 = -0.0084*np.sin(-lp) - \
                0.0373*np.sin(-Np) + \
                0.0093*np.sin(lp) + \
                0.1899*np.sin(2.0*H - 2.0*P) - \
                0.0071*np.sin(2.0*H - 2.0*P - Np)
            term2 = 1.0 - 0.0084*np.cos(-lp) - \
                0.0373*np.cos(Np) + \
                0.0093*np.cos(lp) + \
                0.1899*np.cos(2.0*H - 2.0*P) - \
                0.0071*np.cos(2.0*H - 2.0*P - Np)
        elif c in ('m2',):
            term1 = -0.0030*np.sin(-2.0*H + 2.0*P) - \
                0.0373*np.sin(-Np) + \
                0.0065*np.sin(lp) + \
                0.0011*np.sin(2*H)
            term2 = 1.0 - 0.0030*np.cos(-2.0*H + 2.0*P) - \
                0.0373*np.cos(Np) - \
                0.0004*np.cos(lp) + \
                0.0011*np.cos(2*H)
        elif c in ('l2',):
            term1 = 0.2609*np.sin(-2.0*H + 2.0*P) - \
                0.0370*np.sin(-Np) - \
                0.2503*np.sin(2.0*P) - \
                0.1103*np.sin(2.0*P + Np) - \
                0.0491*np.sin(2.0*H) - \
                0.0230*np.sin(2.0*H + Np)
            term2 = 1.0 + 0.2609*np.cos(-2.0*H + 2.0*P) - \
                0.0370*np.cos(Np) - \
                0.2503*np.cos(2.0*P) - \
                0.1103*np.cos(2.0*P + Np) - \
                0.0491*np.cos(2.0*H) - \
                0.0230*np.cos(2.0*H + Np)
        elif c in ('s2',):
            term1 = 0.0585*np.sin(-lp) - \
                0.0084*np.sin(lp) + \
                0.2720*np.sin(2.0*H) + \
                0.0811*np.sin(2.0*H + Np) + \
                0.0088*np.sin(2.0*H + 2.0*Np)
            term2 = 1.0 + 0.0585*np.cos(-lp) - \
                0.0084*np.cos(lp) + \
                0.2720*np.cos(2.0*H) + \
                0.0811*np.cos(2.0*H + Np) + \
                0.0088*np.cos(2.0*H + 2.0*Np)
        else:
            # unsupported tidal group
            # calculate default nodal modulation
            utmp, ftmp = nodal_modulation(n, p, c, **kwargs)
            f[:,i] = ftmp[:,0]
            u[:,i] = utmp[:,0]
            continue

        # calculate factors for group
        f[:,i] = np.sqrt(term1**2 + term2**2)
        u[:,i] = np.arctan2(term1, term2)
        
    # return corrections for groups
    return (u, f)

def frequency(
        constituents: list | np.ndarray,
        **kwargs
    ):
    """
    Wrapper function for calculating the angular frequency
    for tidal constituents :cite:p:`Ray:1999vm`

    Parameters
    ----------
    constituents: list
        tidal constituent IDs
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS, FES or GOT models
    M1: str, default 'perth5'
        coefficients to use for M1 tides

                - ``'Doodson'``
                - ``'Ray'``
                - ``'Schureman'``
                - ``'perth5'``

    Returns
    -------
    omega: np.ndarray
        angular frequency in radians per second
    """
    # set default keyword arguments
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('M1', 'perth5')
    # set function for astronomical longitudes
    # use ASTRO5 routines if not using an OTIS type model
    if kwargs['corrections'] in ('OTIS','ATLAS','TMD3','netcdf'):
        kwargs.setdefault('method', 'Cartwright')
    else:
        kwargs.setdefault('method', 'ASTRO5')
    # get Doodson coefficients
    coef = coefficients_table(constituents, **kwargs)
    # calculate the angular frequency
    omega = _frequency(coef, **kwargs)
    return omega

def aliasing_period(
        constituents: list | np.ndarray,
        sampling: float | np.ndarray,
        **kwargs
    ):
    """
    Calculates the tidal aliasing for a repeat period

    Parameters
    ----------
    constituents: list
        tidal constituent IDs
    sampling: float
        sampling repeat period in seconds
    corrections: str, default 'OTIS'
        use nodal corrections from OTIS, FES or GOT models
    M1: str, default 'perth5'
        coefficients to use for M1 tides

                - ``'Doodson'``
                - ``'Ray'``
                - ``'Schureman'``
                - ``'perth5'``

    Returns
    -------
    period: np.ndarray
        tidal aliasing period in seconds
    """
    # get the angular frequency for tidal constituents
    omega = frequency(constituents, **kwargs)
    # convert to cycles per second
    f = omega/(2.0*np.pi)
    # calculate the sampling frequency
    fs = 1.0/sampling
    # calculate the aliasing period
    period = 1.0/pyTMD.math.aliasing(f, fs)
    # return the aliasing period
    return period

def _arguments_table(**kwargs):
    """
    Arguments table for tidal constituents
    :cite:p:`Doodson:1921kt,Doodson:1941td`

    Parameters
    ----------
    corrections: str, default 'OTIS'
        use arguments from OTIS, FES or GOT models
    climate_solar_perigee: bool, default False
        compute climatologically affected terms without p'

    Returns
    -------
    coef: np.ndarray
        Doodson coefficients (Cartwright numbers) for each constituent
    """
    # set default keyword arguments
    kwargs.setdefault('corrections', 'OTIS')
    kwargs.setdefault('climate_solar_perigee', False)

    # constituents array (not all are included in tidal program)
    cindex = ['sa', 'ssa', 'mm', 'msf', 'mf', 'mt', 'alpha1', '2q1', 'sigma1',
        'q1', 'rho1', 'o1', 'tau1', 'm1', 'chi1', 'pi1', 'p1', 's1', 'k1',
        'psi1', 'phi1', 'theta1', 'j1', 'oo1', '2n2', 'mu2', 'n2', 'nu2', 'm2a',
        'm2', 'm2b', 'lambda2', 'l2', 't2', 's2', 'r2', 'k2', 'eta2', 'mns2',
        '2sm2', 'm3', 'mk3', 's3', 'mn4', 'm4', 'ms4', 'mk4', 's4', 's5', 'm6',
        's6', 's7', 's8', 'm8', 'mks2', 'msqm', 'mtm', 'n4', 'eps2', 'z0']
    # modified Doodson coefficients for constituents
    # using 7 index variables: tau, s, h, p, n, pp, k
    # tau: mean lunar time
    # s: mean longitude of moon
    # h: mean longitude of sun
    # p: mean longitude of lunar perigee
    # n: mean longitude of ascending lunar node
    # pp: mean longitude of solar perigee
    # k: 90-degree phase
    coef = coefficients_table(cindex, **kwargs)
    # return the coefficient table
    return coef

def _minor_table(**kwargs):
    """
    Arguments table for minor tidal constituents
    :cite:p:`Doodson:1921kt,Doodson:1941td`

    Returns
    -------
    coef: np.ndarray
        Doodson coefficients (Cartwright numbers) for each constituent
    """
    # modified Doodson coefficients for constituents
    # using 7 index variables: tau, s, h, p, n, pp, k
    # tau: mean lunar time
    # s: mean longitude of moon
    # h: mean longitude of sun
    # p: mean longitude of lunar perigee
    # n: mean longitude of ascending lunar node
    # pp: mean longitude of solar perigee
    # k: 90-degree phase
    minor = ['2q1', 'sigma1', 'rho1', 'm1b', 'm1a', 'chi1', 'pi1',
        'phi1', 'theta1', 'j1', 'oo1', '2n2', 'mu2', 'nu2', 'lambda2',
        'l2a', 'l2b', 't2', 'eps2', 'eta2']
    coef = coefficients_table(minor, **kwargs)
    # return the coefficient table
    return coef

def _constituent_parameters(c: str, **kwargs):
    """
    Loads parameters for a given tidal constituent :cite:p:`Egbert:2002ge`

    Parameters
    ----------
    c: str
        tidal constituent ID
    raise_error: bool, default False
        Raise exception if constituent is unsupported

    Returns
    -------
    amplitude: float
        amplitude of equilibrium tide for tidal constituent (meters)
    phase: float
        phase of tidal constituent (radians)
    omega: float
        angular frequency of constituent (radians)
    alpha: float
        load love number of tidal constituent
    species: float
        spherical harmonic dependence of quadrupole potential
    """
    # default keyword arguments
    kwargs.setdefault('raise_error', False)
    # constituents array that are included in tidal program
    cindex = ['m2', 's2', 'k1', 'o1', 'n2', 'p1', 'k2', 'q1', '2n2', 'mu2',
        'nu2', 'l2', 't2', 'j1', 'm1', 'oo1', 'rho1', 'mf', 'mm', 'ssa',
        'm4', 'ms4', 'mn4', 'm6', 'm8', 'mk3', 's6', '2sm2', '2mk3',
        'msf', 'sa', 'mt', '2q1']
    # species type (spherical harmonic dependence of quadrupole potential)
    _species = np.array([2, 2, 1, 1, 2, 1, 2, 1, 2, 2, 2, 2, 2, 1, 1,
        1, 1, 0, 0, 0, 4, 4, 4, 6, 8, 3, 6, 2, 3, 0, 0, 0, 1])
    # Load Love numbers
    # alpha = correction factor for first order load tides
    _alpha = np.array([0.693, 0.693, 0.736, 0.695, 0.693, 0.706, 0.693,
        0.695, 0.693, 0.693, 0.693, 0.693, 0.693, 0.695, 0.695, 0.695, 0.695,
        0.693, 0.693, 0.693, 0.693, 0.693, 0.693, 0.693, 0.693, 0.693, 0.693,
        0.693, 0.693, 0.693, 0.693, 0.693, 0.693])
    # omega: angular frequency of constituent, in radians
    _omega = np.array([1.405189e-04, 1.454441e-04, 7.292117e-05, 6.759774e-05,
        1.378797e-04, 7.252295e-05, 1.458423e-04, 6.495854e-05, 1.352405e-04,
        1.355937e-04, 1.382329e-04, 1.431581e-04, 1.452450e-04, 7.556036e-05,
        7.025945e-05, 7.824458e-05, 6.531174e-05, 0.053234e-04, 0.026392e-04,
        0.003982e-04, 2.810377e-04, 2.859630e-04, 2.783984e-04, 4.215566e-04,
        5.620755e-04, 2.134402e-04, 4.363323e-04, 1.503693e-04, 2.081166e-04,
        4.925200e-06, 1.990970e-07, 7.962619e-06, 6.231934e-05])
    # Astronomical arguments (relative to t0 = 1 Jan 0:00 1992)
    # phases for each constituent are referred to the time when the phase of
    # the forcing for that constituent is zero on the Greenwich meridian
    _phase = np.array([1.731557546, 0.000000000, 0.173003674, 1.558553872,
        6.050721243, 6.110181633, 3.487600001, 5.877717569, 4.086699633,
        3.463115091, 5.427136701, 0.553986502, 0.050398470, 2.137025284,
        2.436575000, 1.929046130, 5.254133027, 1.756042456, 1.964021610,
        3.487600001, 3.463115091, 1.731557546, 1.499093481, 5.194672637,
        6.926230184, 1.904561220, 0.000000000, 4.551627762, 3.290111417,
        4.551627762, 6.232786837, 3.720064066, 3.91369596])
    # amplitudes of equilibrium tide in meters
    # _amplitude = np.array([0.242334,0.112743,0.141565,0.100661,0.046397,
    _amplitude = np.array([0.2441, 0.112743, 0.141565, 0.100661, 0.046397,
        0.046848, 0.030684, 0.019273, 0.006141, 0.007408, 0.008811, 0.006931,
        0.006608, 0.007915, 0.007915, 0.004338, 0.003661, 0.042041, 0.022191,
        0.019567, 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.003681, 0.003104,
        0.008044, 0.002565])

    # map between input constituent and cindex
    j = [j for j,val in enumerate(cindex) if (val == c.lower())]
    # set the values for the constituent
    if j:
        amplitude, = _amplitude[j]
        phase, = _phase[j]
        omega, = _omega[j]
        alpha, = _alpha[j]
        species, = _species[j]
    elif kwargs['raise_error']:
        raise ValueError(f'Unsupported constituent {c}')
    else:
        amplitude = 0.0
        phase = 0.0
        omega = 0.0
        alpha = 0.0
        species = 0
    # return the values for the constituent
    return (amplitude, phase, omega, alpha, species)

def _frequency(
        coef: np.ndarray,
        **kwargs
    ):
    """
    Calculates the angular frequency for Doodson coefficients
    (Cartwright numbers) :cite:p:`Ray:1999vm`

    Parameters
    ----------
    coef: list or np.ndarray
        Doodson coefficients (Cartwright numbers) for constituents
    method: str, default 'Cartwright'
        Method for computing the mean longitudes

            - ``'Cartwright'``
            - ``'Meeus'``
            - ``'ASTRO5'`` 
            - ``'IERS'``
    include_planets: bool, default False
        Include planetary terms in the frequency calculation

    Returns
    -------
    omega: np.ndarray
        angular frequency in radians per second
    """
    # set default keyword arguments
    kwargs.setdefault('method', 'Cartwright')
    kwargs.setdefault('include_planets', False)
    # Modified Julian Dates at J2000
    MJD = np.array([51544.5, 51544.55])
    # time interval in seconds
    deltat = 86400.0*(MJD[1] - MJD[0])
    # calculate the mean longitudes of the sun and moon
    s, h, p, n, pp = pyTMD.astro.mean_longitudes(MJD,
        method=kwargs['method'])

    # number of temporal values
    nt = len(np.atleast_1d(MJD))
    # initial time conversions
    hour = 24.0*np.mod(MJD, 1)
    # convert from hours solar time into mean lunar time in degrees
    tau = 15.0*hour - s + h
    # variable for multiples of 90 degrees (Ray technical note 2017)
    k = 90.0 + np.zeros((nt))

    # determine equilibrium arguments
    if kwargs['include_planets']:
        lm, lv, la, lj, ls = pyTMD.astro.planetary_longitudes(MJD)
        fargs = np.c_[tau, s, h, p, n, pp, k, lm, lv, la, lj, ls]
    else:
        fargs = np.c_[tau, s, h, p, n, pp, k]

    # calculate the rates of change of the fundamental arguments
    rates = (fargs[1,:] - fargs[0,:])/deltat
    fd = np.dot(rates, coef)
    # convert to radians per second
    omega = 2.0*np.pi*fd/360.0
    return np.abs(omega)

def _love_numbers(
        omega: np.ndarray,
        model: str = 'PREM',
        **kwargs
    ):
    """
    Compute the body tide Love/Shida numbers for a given frequency
    :cite:p:`Wahr:1979vx,Wahr:1981ea,Wahr:1981if,Mathews:1995go`

    Parameters
    ----------
    omega: np.ndarray
        angular frequency (radians per second)
    model: str, default 'PREM'
        Earth model to use for Love numbers

            - '1066A'
            - '1066A-N' (neutral)
            - '1066A-S' (stable)
            - 'PEM-C'
            - 'C2'
            - 'PREM'
    astype: np.dtype, default np.float64
        data type for the output Love numbers

    Returns
    -------
    h2: float
        Degree-2 Love number of vertical displacement
    k2: float
        Degree-2 Love number of gravitational potential
    l2: float
        Degree-2 Love (Shida) number of horizontal displacement
    """
    # set default keyword arguments
    kwargs.setdefault('astype', np.float64)
    # free core nutation frequencies (cycles per sidereal day) and
    # Love number parameters from Wahr (1981) table 6
    # and Mathews et al. (1995) table 3
    if (model == '1066A'):
        lambda_fcn = 1.0021714
        h0, h1 = np.array([6.03e-1, -2.46e-3])
        k0, k1 = np.array([2.98e-1, -1.23e-3])
        l0, l1 = np.array([8.42e-2, 7.81e-5])
    elif (model == '1066A-N'):
        lambda_fcn = 1.0021716
        h0, h1 = np.array([6.03e-1, -2.46e-3])
        k0, k1 = np.array([2.98e-1, -1.24e-3])
        l0, l1 = np.array([8.42e-2, 7.82e-5])
    elif (model == '1066A-S'):
        lambda_fcn = 1.0021708
        h0, h1 = np.array([6.03e-1, -2.46e-3])
        k0, k1 = np.array([2.98e-1, -1.24e-3])
        l0, l1 = np.array([8.42e-2, 7.83e-5])
    elif (model == 'PEM-C'):
        lambda_fcn = 1.0021771
        h0, h1 = np.array([6.02e-1, -2.46e-3])
        k0, k1 = np.array([2.98e-1, -1.24e-3])
        l0, l1 = np.array([8.39e-2, 7.69e-5])
    elif (model == 'C2'):
        lambda_fcn = 1.0021844
        h0, h1 = np.array([6.02e-1, -2.45e-3])
        k0, k1 = np.array([2.98e-1, -1.23e-3])
        l0, l1 = np.array([8.46e-2, 7.58e-5])
    elif (model == 'PREM'):
        lambda_fcn = 1.0023214
        h0, h1 = np.array([5.994e-1, -2.532e-3])
        k0, k1 = np.array([2.962e-1, -1.271e-3])
        l0, l1 = np.array([8.378e-2, 7.932e-5])
    else:
        raise ValueError(f'Unknown Earth model: {model}')
    # Love numbers for different frequency bands
    if (omega > 1e-4):
        # tides in the semi-diurnal band
        h2 = 0.609
        k2 = 0.302
        l2 = 0.0852
    elif (omega < 2e-5):
        # tides in the long period band
        h2 = 0.606
        k2 = 0.299
        l2 = 0.0840
    else:
        # calculate love numbers following J. Wahr (1979)
        # use resonance formula for tides in the diurnal band
        # frequency of the o1 tides (radians/second)
        omega_o1, = frequency('o1', **kwargs)
        # convert frequency from cycles per sidereal day
        # frequency of free core nutation (radians/second)
        omega_fcn = lambda_fcn*7292115e-11
        # Love numbers for frequency using equation 4.18 of Wahr (1981)
        # (simplification to use only the free core nutation term)
        ratio = (omega - omega_o1)/(omega_fcn - omega)
        h2 = h0 + h1*ratio
        k2 = k0 + k1*ratio
        l2 = l0 + l1*ratio
    # return the Love numbers for frequency
    return np.array([h2, k2, l2], dtype=kwargs['astype'])

def _complex_love_numbers(
        omega: np.ndarray,
        **kwargs
    ):
    """
    Compute the complex body tide Love/Shida numbers with in-phase
    and out-of-phase components for a given frequency
    :cite:p:`Mathews:1997js,Mathews:2002cr,Petit:2010tp`

    Parameters
    ----------
    omega: np.ndarray
        angular frequency (radians per second)
    kwargs: dict
        additional keyword arguments for love number calculation

    Returns
    -------
    h2: complex
        Degree-2 Love number of vertical displacement
    k2: complex
        Degree-2 Love number of gravitational potential
    l2: complex
        Degree-2 Love (Shida) number of horizontal displacement
    """
    # (number of sidereal days per solar day)
    sidereal_ratio = 1.002737909
    # number of seconds in a sidereal day (approx 86164.1)
    sidereal_day = 86400.0/sidereal_ratio
    # frequency in cycles per sidereal day
    f = omega*sidereal_day/(2.0*np.pi)
    # Love numbers for different frequency bands
    if (omega == 0.0):
        # use real-valued body tide love numbers for permanent tide
        h2, k2, l2 = _love_numbers(omega, **kwargs)
    elif (omega > 1e-4):
        # in-phase and out-of-phase components for the semi-diurnal band
        h2 = 0.6078 - 0.0022j
        k2 = 0.30102 - 0.0013j
        l2 = 0.0847 - 0.0007j
    elif (omega < 2e-5):
        # compute in-phase and out-of-phase components for the long period band
        # variation largely due to mantle anelasticity
        alpha = 0.15
        # frequency equivalent to 200s
        fm = sidereal_day/200.0
        factor = np.tan(alpha*np.pi/2.0)**(-1)
        anelasticity_model = factor*(1.0 - (fm/f)**alpha) + 1j*(fm/f)**alpha
        # model for the variation of love numbers across the zonal tide band
        h2 = 0.5998 - 9.96e-4*anelasticity_model
        k2 = 0.29525 - 5.796e-4*anelasticity_model
        l2 = 0.0831 - 3.01e-4*anelasticity_model
    else:
        # in-phase and out-of-phase components for the diurnal band
        # following IERS conventions and Mathews et al. (2002)
        # values from equation 6.10 of IERS conventions 2010
        # and from Mathews et al. (2002)
        sigma = np.zeros((4), dtype=np.complex128)
        # factor for calculating L0
        sigma[0] = f - 1.0
        # Chandler wobble
        sigma[1] = -0.0026010 - 0.0001361j
        # retrograde free core nutation
        sigma[2] = 1.0023181 + 0.000025j
        # prograde free core nutation
        sigma[3] = 0.999026 + 0.000780j
        # frequency dependence of Love number h2
        H2 = np.zeros((4), dtype=np.complex128)
        H2[0] = 0.60671 - 0.242e-2j
        H2[1] = -0.15777e-2 - 0.7630e-4j
        H2[2] = 0.18053e-3 - 0.6292e-5j
        H2[3] = -0.18616e-5 + 0.1379e-6j
        # frequency dependence of Love number k2
        K2 = np.zeros((4), dtype=np.complex128)
        K2[0] = 0.29954 - 0.1412e-2j
        K2[1] = -0.77896e-3 - 0.3711e-4j
        K2[2] = 0.90963e-4 - 0.2963e-5j
        K2[3] = -0.11416e-5 + 0.5325e-7j
        # frequency dependence of Love number l2
        L2 = np.zeros((4), dtype=np.complex128)
        L2[0] = 0.84963e-1 - 0.7395e-3j
        L2[1] = -0.22107e-3 - 0.9646e-5j
        L2[2] = -0.54710e-5 - 0.2990e-6j
        L2[3] = -0.29904e-7 - 0.7717e-8j
        # estimate the complex Love number fors diurnal tides
        # equation 6.9 of IERS conventions 2010
        h2 = np.sum(H2/(f - sigma))
        k2 = np.sum(K2/(f - sigma))
        l2 = np.sum(L2/(f - sigma))

    # return the Love numbers as a complex number
    return np.array([h2, k2, l2], dtype=np.complex128)

# Doodson (1921) table with values missing from Cartwright tables
# Hs1: amplitude for epoch span 1 (1900 epoch)
_d1921_table = get_data_path(['data','d1921_tab.txt'])
# Cartwright and Tayler (1971) table with 3rd-degree values
# Cartwright and Edden (1973) table with updated values
_cte1973_table = get_data_path(['data','cte1973_tab.txt'])
# Cartwright and Tayler (1971) table with radiational tides
_ct1971_table_6 = get_data_path(['data','ct1971_tab6.txt'])
# Hartmann and Wenzel (1995) tidal potential catalog
_hw1995_table = get_data_path(['data','hw1995_tab.txt'])
# Tamura (1987) tidal potential catalog
_t1987_table = get_data_path(['data','t1987_tab.txt'])
# Woodworth (1990) tables with updated and 3rd-degree values
_w1990_table = get_data_path(['data','w1990_tab.txt'])

def _parse_tide_potential_table(
        table: str | pathlib.Path,
        skiprows: int = 1,
        columns: int = 1,
        include_degree: bool = True,
        include_planets: bool = False
    ):
    """Parse tables of tide-generating potential

    Parameters
    ----------
    table: str or pathlib.Path
        table of tide-generating potentials
    skiprows: int, default 1
        number of header rows to skip in the table
    columns: int, default 1
        number of amplitude columns in the table
    include_degree: bool, default True
        table includes spherical harmonic degree
    include_planets: bool, default False
        table includes coefficients for mean longitudes of planets

    Returns
    -------
    CTE: np.ndarray
        Cartwright-Tayler-Edden table values
    """
    # verify table path
    table = pathlib.Path(table).expanduser().absolute()
    with table.open(mode='r', encoding='utf8') as f:
        file_contents = f.readlines()
    # number of lines in the file
    file_lines = len(file_contents) - int(skiprows)
    # names: names of the columns in the table
    # formats: data types for each column in the table
    names = []
    formats = []
    # l: spherical harmonic degree
    if include_degree:
        names.append('l')
        formats.append('i')
    # tau: spherical harmonic dependence (order)
    # s: coefficient for mean longitude of moon
    # h: coefficient for mean longitude of sun
    # p: coefficient for mean longitude of lunar perigee
    # n: coefficient for mean longitude of ascending lunar node
    # pp: coefficient for mean longitude of solar perigee
    names.extend(['tau','s','h','p','n','pp'])
    formats.extend(['i','i','i','i','i','i'])
    # lme: coefficient for mean longitude of Mercury
    # lve: coefficient for mean longitude of Venus
    # lma: coefficient for mean longitude of Mars
    # lju: coefficient for mean longitude of Jupiter
    # lsa: coefficient for mean longitude of Saturn
    if include_planets:
        names.extend(['lme','lve','lma','lju','lsa'])
        formats.extend(['i','i','i','i','i'])
    # tide potential amplitudes (Cartwright and Tayler norm)
    for c in range(columns):
        # add amplitude columns to names and formats
        names.append(f'Hs{c+1}')
        formats.append('f8')
    # add Doodson number
    names.append('DO')
    formats.append('U7')
    # create a structured numpy dtype for the table
    dtype = np.dtype({'names':names, 'formats':formats})
    CTE = np.zeros((file_lines), dtype=dtype)
    # total number of output columns
    total_columns = len(names)
    # iterate over each line in the file
    for i,line in enumerate(file_contents[skiprows:]):
        # drop last column(s) with values from Doodson (1921)
        CTE[i] = np.array(tuple(line.split()[:total_columns]), dtype=dtype)
    # return the table values
    return CTE

def _to_constituent_id(coef: list | np.ndarray, **kwargs):
    """
    Converts Cartwright numbers into a tidal constituent ID

    Parameters
    ----------
    coef: list or np.ndarray
        Doodson coefficients (Cartwright numbers) for constituent
    corrections: str, default 'GOT'
        use coefficients from OTIS, FES or GOT models
    climate_solar_perigee: bool, default False
        use climatologically affected terms without p'
    arguments: int, default 7
        Number of astronomical arguments to use
    file: str or pathlib.Path, default `coefficients.json`
        JSON file of Doodson coefficients
    raise_error: bool, default True
        Raise exception if constituent is unsupported

    Returns
    -------
    c: str
        tidal constituent ID
    """
    # set default keyword arguments
    kwargs.setdefault('corrections', 'GOT')
    kwargs.setdefault('climate_solar_perigee', False)
    kwargs.setdefault('arguments', 7)
    kwargs.setdefault('file', _coefficients_table)
    kwargs.setdefault('raise_error', True)

    # verify list of coefficients
    N = int(kwargs['arguments'])
    assert (N == 6) or (N == 7)
    # assert length and verify list
    coef = np.copy(coef[:N]).tolist()

    # verify coefficients table path
    table = pathlib.Path(kwargs['file']).expanduser().absolute()
    # modified Doodson coefficients for constituents
    # using 7 index variables: tau, s, h, p, n, pp, k
    # tau: mean lunar time
    # s: mean longitude of moon
    # h: mean longitude of sun
    # p: mean longitude of lunar perigee
    # n: mean longitude of ascending lunar node
    # pp: mean longitude of solar perigee
    # k: 90-degree phase
    with table.open(mode='r', encoding='utf8') as fid:
        coefficients = json.load(fid)

    # use climatologically affected terms without p'
    # following Pugh and Woodworth (2014)
    if kwargs['climate_solar_perigee']:
        coefficients['sa'] = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        coefficients['sta'] = [0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0]
    # set s1 coefficients
    if kwargs['corrections'] in ('OTIS','ATLAS','TMD3','netcdf'):
        coefficients['s1'] = [1.0, 1.0, -1.0, 0.0, 0.0, 0.0, 1.0]
    # separate dictionary into keys and values
    coefficients_keys = list(coefficients.keys()) 
    # truncate coefficient values to number of arguments
    coefficients_values = np.array(list(coefficients.values()))
    coefficients_values = coefficients_values[:,:N].tolist()
    # get constituent ID from Doodson coefficients
    try:
        i = coefficients_values.index(coef)
    except ValueError:
        if kwargs['raise_error']:
            raise ValueError('Unsupported constituent')
    else:
        # return constituent id
        return coefficients_keys[i]

def _to_doodson_number(coef: list | np.ndarray, **kwargs):
    """
    Converts Cartwright numbers into a Doodson number

    Parameters
    ----------
    coef: list or np.ndarray
        Doodson coefficients (Cartwright numbers) for constituent
    astype: type, default float
        Output data type for default case
    raise_error: bool, default True
        Raise exception if constituent is unsupported

    Returns
    -------
    DO: float or string
        Doodson number for constituent
    """
    # default keyword arguments
    kwargs.setdefault('raise_error', True)
    astype = kwargs.get('astype', float)
    # assert length and verify array
    coef = np.array(coef[:6]).astype(int)
    # add 5 to values following Doodson convention (prevent negatives)
    coef[1:] += 5
    # check for unsupported constituents
    if (np.any(coef < 0) or np.any(coef > 12)) and kwargs['raise_error']:
        raise ValueError('Unsupported constituent')
    elif (np.any(coef < 0) or np.any(coef > 12)):
        return None
    elif np.any(coef >= 10) and np.all(coef <= 12):
        # replace 10 to 12 with Doodson convention values
        # X: 10, E: 11, T: 12
        digits = '0123456789XET'
        DO = [digits[v] for v in coef]
        # convert to Doodson number
        return np.str_('{0}{1}{2}.{3}{4}{5}'.format(*DO))
    else:
        # convert to single number and round off floating point errors
        DO = np.sum([v*10**(2-o) for o,v in enumerate(coef)])
        return np.round(DO, decimals=3).astype(astype)

def _to_extended_doodson(coef: list | np.ndarray, **kwargs):
    """
    Converts Cartwright numbers into an UKHO Extended Doodson number

    Parameters
    ----------
    coef: list or np.ndarray
        Doodson coefficients (Cartwright numbers) for constituent

    Returns
    -------
    XDO: string
        Extended Doodson number for constituent
    """
    # assert length and verify array
    coef = np.array(coef).astype(int)
    # digits for UKHO Extended Doodson number
    # Z = 0
    # A - P = 1 to 15
    # R - Y = -8 to -1
    digits = 'RSTUVWXYZABCDEFGHIJKLMNOP'
    XDO = ''.join([digits[v+8] for v in coef])
    return np.str_(XDO)

def _from_doodson_number(DO: str | float | np.ndarray, **kwargs):
    """
    Converts Doodson numbers into Cartwright numbers

    Parameters
    ----------
    DO: str, float or np.ndarray
        Doodson number for constituent

    Returns
    -------
    coef: np.ndarray
        Doodson coefficients (Cartwright numbers) for constituent
    """
    # convert from Doodson number to Cartwright numbers
    # convert to string and verify length
    DO = str(DO).zfill(7)
    # replace 10 to 12 with Doodson convention values
    # X: 10, E: 11, T: 12
    digits = '0123456789XET'
    # find alphanumeric characters in Doodson number
    coef = np.array([digits.index(c) for c in re.findall(r'\w', DO)], dtype=int)
    # remove 5 from values following Doodson convention
    coef[1:] -= 5
    return coef

def _from_extended_doodson(XDO: str | np.str_, **kwargs):
    """
    Converts UKHO Extended Doodson number into Cartwright numbers

    Parameters
    ----------
    XDO: string
        Extended Doodson number for constituent

    Returns
    -------
    coef: np.ndarray
        Doodson coefficients (Cartwright numbers) for constituent
    """
    # digits for UKHO Extended Doodson number
    # Z = 0
    # A - P = 1 to 15
    # R - Y = -8 to -1
    digits = 'RSTUVWXYZABCDEFGHIJKLMNOP'
    # convert from extended Doodson number to Cartwright numbers
    coef = np.array([(digits.index(c)-8) for c in str(XDO)], dtype=int)
    return coef
