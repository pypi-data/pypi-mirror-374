#!/usr/bin/env python
u"""
model.py
Written by Tyler Sutterley (08/2025)
Retrieves tide model parameters for named tide models and
    from model definition files

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html

UPDATE HISTORY:
    Updated 08/2025: use numpy degree to radian conversions
        update node equilibrium tide estimation
        add functions for converting a model to an xarray DataTree object
    Updated 06/2025: add function for reducing list of model files
        fix extra_databases to not overwrite the default database
        add capability to use a dictionary to expand the model database
    Updated 02/2025: fixed missing grid kwarg for reading from TMD3 models 
    Updated 11/2024: use Love numbers for long-period tides in node equilibrium
    Updated 10/2024: add wrapper functions to read and interpolate constants
        add functions to append node tide equilibrium values to amplitudes
        remove redundant default keyword arguments to readers and interpolators
    Updated 09/2024: use JSON database for known model parameters
        drop support for the ascii definition file format
        add file_format and nodal correction attributes
        export database as a dataclass for easier access
        added variable name and descriptions for long period tides
    Updated 08/2024: added attribute for minor constituents to infer
        allow searching over iterable glob strings in definition files
        added option to try automatic detection of definition file format
        added new TPXO10-atlas-v2 to list of models
    Updated 07/2024: added new FES2022 and FES2022_load to list of models
        added JSON format for model definition files
        use parse function from constituents class to extract names
        renamed format for ATLAS to ATLAS-compact
        renamed format for netcdf to ATLAS-netcdf
        renamed format for FES to FES-netcdf and added FES-ascii
        renamed format for GOT to GOT-ascii and added GOT-netcdf
    Updated 05/2024: make subscriptable and allow item assignment
    Updated 04/2024: append v-components of velocity only to netcdf format
    Updated 11/2023: revert TPXO9-atlas currents changes to separate dicts
    Updated 09/2023: fix scale values for TPXO9-atlas currents
    Updated 08/2023: changed ESR netCDF4 format to TMD3 format
        updated filenames for CATS2008-v2023 to final version
    Updated 06/2023: remap FES2012 e2 constituent to eps2
    Updated 04/2023: added global HAMTIDE11 model
        made ICESat, ICESat-2 and output file attributes properties
        updated model definition read function for currents
        using pathlib to define and expand tide model paths
        add basic file searching with glob strings in definition files
        add long_name and description attributes for current variables
        added exceptions for files missing when using glob patterns
        simplify TPXO9-atlas currents dictionaries to single list
    Updated 03/2023: add basic variable typing to function inputs
    Updated 12/2022: moved to io and added deprecation warning to old
    Updated 11/2022: use f-strings for formatting verbose or ascii output
    Updated 06/2022: added Greenland 1km model (Gr1kmTM) to list of models
        updated citation url for Goddard Ocean Tide (GOT) models
    Updated 05/2022: added ESR CATS2022 to list of models
        added attribute for flexure fields being available for model
    Updated 04/2022: updated docstrings to numpy documentation format
        include utf-8 encoding in reads to be windows compliant
        set default directory to None for documentation
    Updated 03/2022: added static decorators to define model lists
    Updated 02/2022: added Arctic 2km model (Arc2kmTM) to list of models
    Updated 01/2022: added global Empirical Ocean Tide model (EOT20)
    Updated 12/2021: added TPXO9-atlas-v5 to list of available tide models
        added atl10 attributes for tidal elevation files
    Written 09/2021
"""
from __future__ import annotations

import io
import copy
import json
import pathlib
import numpy as np
from pyTMD.utilities import import_dependency, get_data_path
from collections.abc import Iterable
from dataclasses import dataclass

# attempt imports
xr = import_dependency('xarray')

__all__ = [
    'DataBase',
    'load_database',
    'model'
]

@dataclass
class DataBase:
    """Class for pyTMD model database"""
    current: dict
    elevation: dict

    def keys(self):
        """Returns the keys of the model database"""
        return self.__dict__.keys()

    def values(self):
        """Returns the values of the model database"""
        return self.__dict__.values()

    def items(self):
        """Returns the items of the model database"""
        return self.__dict__.items()

    def __getitem__(self, key):
        return getattr(self, key)


# PURPOSE: load the JSON database of model files
def load_database(extra_databases: list = []):
    """
    Load the JSON database of model files

    Parameters
    ----------
    extra_databases: list, default []
        A list of additional databases to load, as either
        JSON file paths or dictionaries

    Returns
    -------
    parameters: dict
        Database of model parameters
    """
    # path to model database
    database = get_data_path(['data','database.json'])
    # extract JSON data
    with database.open(mode='r', encoding='utf-8') as fid:
        parameters = json.load(fid)
    # verify that extra_databases is iterable
    if isinstance(extra_databases, (str, pathlib.Path, dict)):
        extra_databases = [extra_databases]
    # load any additional databases
    for db in extra_databases:
        # use database parameters directly if a dictionary
        if isinstance(db, dict):
            extra_database = copy.copy(db)
        # otherwise load parameters from JSON file path
        else:
            # verify that extra database file exists
            db = pathlib.Path(db).expanduser().absolute()
            if not db.exists():
                raise FileNotFoundError(db)
            # extract JSON data
            with db.open(mode='r', encoding='utf-8') as fid:
                extra_database = json.load(fid)
        # Add additional models to database, accounting
        # for top level elevation and current dict keys
        for key, val in extra_database.items():
            parameters[key].update(val)
    return DataBase(**parameters)

class model:
    """Retrieves tide model parameters for named models or
    from a model definition file for use in the pyTMD tide
    prediction programs

    Attributes
    ----------
    atl03: str
        HDF5 dataset string for output ATL03 tide heights
    atl06: str
        HDF5 dataset string for output ATL06 tide heights
    atl07: str
        HDF5 dataset string for output ATL07 tide heights
    atl10: str
        HDF5 dataset string for output ATL10 tide heights
    atl11: str
        HDF5 dataset string for output ATL11 tide heights
    atl12: str
        HDF5 dataset string for output ATL12 tide heights
    compressed: bool
        Model files are gzip compressed
    constituents: list or None
        Model constituents for ``FES`` models
    description: str
        HDF5 ``description`` attribute string for output tide heights
    directory: str, pathlib.Path or None, default None
        Working data directory for tide models
    extra_databases: list, default []
        Additional databases for model parameters
    file_format: str
        File format for model
    flexure: bool
        Flexure adjustment field for tide heights is available
    format: str
        Model format

            - ``OTIS``
            - ``ATLAS-compact``
            - ``TMD3``
            - ``ATLAS-netcdf``
            - ``GOT-ascii``
            - ``GOT-netcdf``
            - ``FES-ascii``
            - ``FES-netcdf``
    gla12: str
        HDF5 dataset string for output GLA12 tide heights
    grid_file: pathlib.Path
        Model grid file for ``OTIS``, ``ATLAS-compact``, ``ATLAS-netcdf``, and ``TMD3`` models
    gzip: bool
        Suffix if model is compressed
    long_name: str
        HDF5 ``long_name`` attribute string for output tide heights
    minor: list or None
        Minor constituents for inference
    model_file: pathlib.Path or list
        Model constituent file or list of files
    name: str
        Model name
    projection: str
        Model projection for ``OTIS``, ``ATLAS-compact`` and ``TMD3`` models
    scale: float
        Model scaling factor for converting to output units
    type: str
        Model type

            - ``z``
            - ``u``
            - ``v``
    verify: bool
        Verify that all model files exist
    version: str
        Tide model version
    """
    def __init__(self, directory: str | pathlib.Path | None = None, **kwargs):
        # set default keyword arguments
        kwargs.setdefault('compressed', False)
        kwargs.setdefault('verify', True)
        kwargs.setdefault('extra_databases', [])
        # set initial attributes
        self.compressed = copy.copy(kwargs['compressed'])
        self.constituents = None
        self.minor = None
        # set working data directory
        self.directory = None
        if directory is not None:
            self.directory = pathlib.Path(directory).expanduser()
        # set any extra databases
        self.extra_databases = copy.copy(kwargs['extra_databases'])
        self.flexure = False
        self.format = None
        self.grid_file = None
        self.model_file = None
        self.name = None
        self.projection = None
        self.reference = None
        self.scale = None
        self.type = None
        self.variable = None
        self.verify = copy.copy(kwargs['verify'])
        self.version = None

    def elevation(self, m: str):
        """
        Create a model object from known tidal elevation models

        Parameters
        ----------
        m: str
            model name
        """
        # set working data directory if unset
        if self.directory is None:
            self.directory = pathlib.Path().absolute()
        # select between known tide models
        parameters = load_database(extra_databases=self.extra_databases)
        # try to extract parameters for model
        try:
            self.from_dict(parameters['elevation'][m])
        except (ValueError, KeyError) as exc:
            raise ValueError(f"Unlisted tide model {m}")
        # validate paths: grid file for OTIS, ATLAS models
        if hasattr(self, 'grid_file') and getattr(self, 'grid_file'):
            self.grid_file = self.pathfinder(self.grid_file)
        # validate paths: model constituent files
        self.model_file = self.pathfinder(self.model_file)
        # get model constituents from constituent files
        if self.format in ('FES-ascii','FES-netcdf',):
            self.parse_constituents()
        # return the model parameters
        self.validate_format()
        return self

    def current(self, m: str):
        """
        Create a model object from known tidal current models

        Parameters
        ----------
        m: str
            model name
        """
        # set working data directory if unset
        if self.directory is None:
            self.directory = pathlib.Path().absolute()
        # select between tide models
        parameters = load_database(extra_databases=self.extra_databases)
        # try to extract parameters for model
        try:
            self.from_dict(parameters['current'][m])
        except (ValueError, KeyError) as exc:
            raise ValueError(f"Unlisted tide model {m}")
        # validate paths: grid file for OTIS, ATLAS models
        if hasattr(self, 'grid_file') and getattr(self, 'grid_file'):
            self.grid_file = self.pathfinder(self.grid_file)
        # validate paths: model constituent files
        for key, val in self.model_file.items():
            self.model_file[key] = self.pathfinder(val)
        # get model constituents from constituent files
        if self.format in ('FES-ascii','FES-netcdf',):
            self.parse_constituents()
        # return the model parameters
        self.validate_format()
        return self

    @property
    def gzip(self) -> str:
        """Returns suffix for gzip compression
        """
        return '.gz' if self.compressed else ''

    @property
    def corrections(self) -> str:
        """
        Returns the corrections type for the model
        """
        part1, _, part2 = self.format.partition('-')
        if self.format in ('GOT-ascii', ):
            return 'perth3'
        else:
            return part1

    @property
    def file_format(self) -> str:
        """
        Returns the file format for the model
        """
        part1, _, part2 = self.format.partition('-')
        if self.format in ('ATLAS-compact'):
            return part1
        elif ('-' in self.format):
            return part2
        else:
            return self.format

    @property
    def atl03(self) -> str:
        """Returns ICESat-2 ATL03 attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return 'tide_ocean'
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return 'tide_load'
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'tide_equilibrium'
        else:
            return None

    @property
    def atl06(self) -> str:
        """Returns ICESat-2 ATL06 attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return 'tide_ocean'
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return 'tide_load'
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'tide_equilibrium'
        else:
            return None

    @property
    def atl07(self) -> str:
        """Returns ICESat-2 ATL07 attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return 'height_segment_ocean'
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return 'height_segment_load'
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'height_segment_lpe'
        else:
            return None

    @property
    def atl10(self) -> str:
        """Returns ICESat-2 ATL07 attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return 'height_segment_ocean'
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return 'height_segment_load'
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'height_segment_lpe'
        else:
            return None

    @property
    def atl11(self) -> str:
        """Returns ICESat-2 ATL11 attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return 'tide_ocean'
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return 'tide_load'
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'tide_equilibrium'
        else:
            return None

    @property
    def atl12(self) -> str:
        """Returns ICESat-2 ATL12 attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return 'tide_ocean_seg'
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return 'tide_load_seg'
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'tide_equilibrium_seg'
        else:
            return None

    @property
    def gla12(self) -> str:
        """Returns ICESat GLA12 attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return 'd_ocElv'
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return 'd_ldElv'
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'd_eqElv'
        else:
            return None

    @property
    def long_name(self) -> str:
        """Returns ``long_name`` attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return 'ocean_tide_elevation'
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return 'load_tide_elevation'
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'equilibrium_tide_elevation'
        elif (self.type == ['u','v']):
            return dict(u='zonal_tidal_current', v='meridional_tidal_current')
        else:
            return None

    @property
    def description(self) -> str:
        """Returns ``description`` attribute string for a given variable
        """
        if (self.type == 'z') and (self.variable == 'tide_ocean'):
            return "Ocean tidal elevations derived from harmonic constants"
        elif (self.type == 'z') and (self.variable == 'tide_load'):
            return ("Local displacement due to ocean tidal loading "
                "derived from harmonic constants")
        elif (self.type == 'z') and (self.variable == 'tide_lpe'):
            return 'Long-period equilibrium tide elevations'
        elif (self.type == ['u','v']):
            attr = {}
            attr['u'] = ('Depth-averaged tidal zonal current '
                'derived from harmonic constants')
            attr['v'] = ('Depth-averaged tidal meridional current '
                'derived from harmonic constants')
            return attr
        else:
            return None

    @staticmethod
    def formats(**kwargs) -> list:
        """
        Returns list of known model formats
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known formats
        format_list = []
        for variable, models in parameters.items():
            for model, val in models.items():
                format_list.append(val['format'])
        # return unique list of formats
        return sorted(set(format_list))

    @staticmethod
    def ocean_elevation(**kwargs) -> list:
        """
        Returns list of ocean tide elevation models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known ocean tide elevation models
        model_list = []
        for model, val in parameters['elevation'].items():
            if (val['type'] == 'z') and (val['variable'] == 'tide_ocean'):
                model_list.append(model)
            elif (val['type'] == 'z') and (val['variable'] == 'tide_lpe'):
                model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    @staticmethod
    def load_elevation(**kwargs) -> list:
        """
        Returns list of load tide elevation models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known load tide elevation models
        model_list = []
        for model, val in parameters['elevation'].items():
            if (val['type'] == 'z') and (val['variable'] == 'tide_load'):
                model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    @staticmethod
    def ocean_current(**kwargs) -> list:
        """
        Returns list of tidal current models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known ocean tide current models
        model_list = []
        for model, val in parameters['current'].items():
            model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    @staticmethod
    def OTIS(**kwargs) -> list:
        """
        Returns list of OTIS format models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known OTIS models
        model_list = []
        for model, val in parameters['elevation'].items():
            if (val['format'] == 'OTIS'):
                model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    @staticmethod
    def ATLAS_compact(**kwargs) -> list:
        """
        Returns list of ATLAS compact format models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known ATLAS-compact models
        model_list = []
        for model, val in parameters['elevation'].items():
            if (val['format'] == 'ATLAS-compact'):
                model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    @staticmethod
    def TMD3(**kwargs) -> list:
        """
        Returns list of TMD3 format models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known TMD3 models
        model_list = []
        for model, val in parameters['elevation'].items():
            if (val['format'] == 'TMD3'):
                model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    @staticmethod
    def ATLAS(**kwargs) -> list:
        """
        Returns list of ATLAS-netcdf format models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known TMD3 models
        model_list = []
        for model, val in parameters['elevation'].items():
            if (val['format'] == 'ATLAS-netcdf'):
                model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    @staticmethod
    def GOT(**kwargs) -> list:
        """
        Returns list of GOT format models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known GOT-ascii or GOT-netcdf models
        model_list = []
        for model, val in parameters['elevation'].items():
            if (val['format'] == 'GOT-ascii') or (val['format'] == 'GOT-netcdf'):
                model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    @staticmethod
    def FES(**kwargs) -> list:
        """
        Returns list of FES format models
        """
        # load the database of model parameters
        parameters = load_database(**kwargs)
        # extract all known FES-ascii or FES-netcdf models
        model_list = []
        for model, val in parameters['elevation'].items():
            if (val['format'] == 'FES-ascii') or (val['format'] == 'FES-netcdf'):
                model_list.append(model)
        # return unique list of models
        return sorted(set(model_list))

    def pathfinder(self, model_file: str | pathlib.Path | list):
        """
        Completes file paths and appends gzip suffix

        Parameters
        ----------
        model_file: str, pathlib.Path or list
            model file(s) to complete
        """
        # set working data directory if unset
        if self.directory is None:
            self.directory = pathlib.Path().absolute()
        # complete model file paths
        if isinstance(model_file, list):
            output_file = [self.pathfinder(f) for f in model_file]
            valid = all([f.exists() for f in output_file])
        elif isinstance(model_file, str):
            output_file = self.directory.joinpath(
                ''.join([model_file, self.gzip]))
            valid = output_file.exists()
        # check that (all) output files exist
        if self.verify and not valid:
            raise FileNotFoundError(output_file)
        # return the complete output path
        return output_file

    def from_file(self,
            definition_file: str | pathlib.Path | io.IOBase,
            **kwargs,
        ):
        """
        Create a model object from an input definition file

        Parameters
        ----------
        definition_file: str, pathlib.Path or io.IOBase
            model definition file for creating model object
        """
        # set default keyword arguments
        kwargs.setdefault('format', 'json')
        # Opening definition file and assigning file ID number
        if isinstance(definition_file, io.IOBase):
            fid = copy.copy(definition_file)
        else:
            definition_file = pathlib.Path(definition_file).expanduser()
            fid = definition_file.open(mode='r', encoding='utf8')
        # load and parse definition file type
        if (kwargs['format'].lower() == 'ascii'):
            raise ValueError('ascii definition format no longer supported')
        else:
            self._parse_file(fid)
        # close the definition file
        fid.close()
        # return the model object
        return self

    def _parse_file(self, fid: io.IOBase):
        """
        Load and parse a model definition file

        Parameters
        ----------
        fid: io.IOBase
            open definition file object
        """
        # attempt to read and parse a JSON file
        try:
            self._parse_json(fid)
        except json.decoder.JSONDecodeError as exc:
            pass
        else:
            return self
        # raise an exception
        raise IOError('Cannot load model definition file')

    def _parse_json(self, fid: io.IOBase):
        """
        Load and parse JSON definition file

        Parameters
        ----------
        fid: io.IOBase
            open definition file object
        """
        # load JSON file
        parameters = json.load(fid)
        # convert from dictionary to model variable
        temp = self.from_dict(parameters)
        # verify model name, format and type
        assert temp.name
        temp.validate_format()
        assert temp.type
        assert temp.model_file
        # split model file into list if an ATLAS, GOT or FES file
        # model files can be comma, tab or space delimited
        # extract full path to tide model files
        # extract full path to tide grid file
        if temp.format in ('OTIS','ATLAS-compact','TMD3'):
            assert temp.grid_file
            # check if grid file is relative
            if (temp.directory is not None):
                temp.grid_file = temp.directory.joinpath(temp.grid_file).resolve()
            else:
                temp.grid_file = pathlib.Path(temp.grid_file).expanduser()
            # extract model files
            if (temp.type == ['u','v']) and (temp.directory is not None):
                # use glob strings to find files in directory
                for key, glob_string in temp.model_file.items():
                    # search singular glob string or iterable glob strings
                    if isinstance(glob_string, str):
                        # singular glob string
                        temp.model_file[key] = list(temp.directory.glob(glob_string))
                    elif isinstance(glob_string, Iterable):
                        # iterable glob strings
                        temp.model_file[key] = []
                        for p in glob_string:
                            temp.model_file[key].extend(temp.directory.glob(p))
            elif (temp.type == 'z') and (temp.directory is not None):
                # use glob strings to find files in directory
                glob_string = copy.copy(temp.model_file)
                # search singular glob string or iterable glob strings
                if isinstance(glob_string, str):
                    # singular glob string
                    temp.model_file = list(temp.directory.glob(glob_string))
                elif isinstance(glob_string, Iterable):
                    # iterable glob strings
                    temp.model_file = []
                    for p in glob_string:
                        temp.model_file.extend(temp.directory.glob(p))
            elif (temp.type == ['u','v']) and isinstance(temp.model_file, dict):
                # resolve paths to model files for each direction
                for key, model_file in temp.model_file.items():
                    temp.model_file[key] = [pathlib.Path(f).expanduser() for f in
                        model_file]
            elif (temp.type == 'z') and isinstance(temp.model_file, list):
                # resolve paths to model files
                temp.model_file = [pathlib.Path(f).expanduser() for f in
                    temp.model_file]
            else:
                # fully defined single file case
                temp.model_file = pathlib.Path(temp.model_file).expanduser()
        elif temp.format in ('ATLAS-netcdf',):
            assert temp.grid_file
            # check if grid file is relative
            if (temp.directory is not None):
                temp.grid_file = temp.directory.joinpath(temp.grid_file).resolve()
            else:
                temp.grid_file = pathlib.Path(temp.grid_file).expanduser()
            # extract model files
            if (temp.type == ['u','v']) and (temp.directory is not None):
                # use glob strings to find files in directory
                for key, glob_string in temp.model_file.items():
                    # search singular glob string or iterable glob strings
                    if isinstance(glob_string, str):
                        # singular glob string
                        temp.model_file[key] = list(temp.directory.glob(glob_string))
                    elif isinstance(glob_string, Iterable):
                        # iterable glob strings
                        temp.model_file[key] = []
                        for p in glob_string:
                            temp.model_file[key].extend(temp.directory.glob(p))
            elif (temp.type == 'z') and (temp.directory is not None):
                # use glob strings to find files in directory
                glob_string = copy.copy(temp.model_file)
                # search singular glob string or iterable glob strings
                if isinstance(glob_string, str):
                    # singular glob string
                    temp.model_file = list(temp.directory.glob(glob_string))
                elif isinstance(glob_string, Iterable):
                    # iterable glob strings
                    temp.model_file = []
                    for p in glob_string:
                        temp.model_file.extend(temp.directory.glob(p))
                #     raise FileNotFoundError(message) from exc
            elif (temp.type == ['u','v']):
                # resolve paths to model files for each direction
                for key, model_file in temp.model_file.items():
                    temp.model_file[key] = [pathlib.Path(f).expanduser() for f in
                        model_file]
            elif (temp.type == 'z'):
                # resolve paths to model files
                temp.model_file = [pathlib.Path(f).expanduser() for f in
                    temp.model_file]
        elif temp.format in ('FES-ascii','FES-netcdf','GOT-ascii','GOT-netcdf'):
            # extract model files
            if (temp.type == ['u','v']) and (temp.directory is not None):
                # use glob strings to find files in directory
                for key, glob_string in temp.model_file.items():
                    # search singular glob string or iterable glob strings
                    if isinstance(glob_string, str):
                        # singular glob string
                        temp.model_file[key] = list(temp.directory.glob(glob_string))
                    elif isinstance(glob_string, Iterable):
                        # iterable glob strings
                        temp.model_file[key] = []
                        for p in glob_string:
                            temp.model_file[key].extend(temp.directory.glob(p))
            elif (temp.type == 'z') and (temp.directory is not None):
                # use glob strings to find files in directory
                glob_string = copy.copy(temp.model_file)
                # search singular glob string or iterable glob strings
                if isinstance(glob_string, str):
                    # singular glob string
                    temp.model_file = list(temp.directory.glob(glob_string))
                elif isinstance(glob_string, Iterable):
                    # iterable glob strings
                    temp.model_file = []
                    for p in glob_string:
                        temp.model_file.extend(temp.directory.glob(p))
            elif (temp.type == ['u','v']):
                # resolve paths to model files for each direction
                for key, model_file in temp.model_file.items():
                    temp.model_file[key] = [pathlib.Path(f).expanduser() for f in
                        model_file]
            elif (temp.type == 'z'):
                # resolve paths to model files
                temp.model_file = [pathlib.Path(f).expanduser() for f in
                    temp.model_file]
        # verify that projection attribute exists for projected models
        if temp.format in ('OTIS','ATLAS-compact','TMD3'):
            assert temp.projection
        # convert scale from string to float
        if temp.format in ('ATLAS-netcdf','GOT-ascii','GOT-netcdf','FES-ascii','FES-netcdf'):
            assert temp.scale
        # assert that FES model has a version
        # get model constituents from constituent files
        if temp.format in ('FES-ascii','FES-netcdf',):
            assert temp.version
            if (temp.constituents is None):
                temp.parse_constituents()
        # return the model parameters
        return temp

    def validate_format(self):
        """Asserts that the model format is a known type"""
        # known remapped cases
        mapping = [('ATLAS','ATLAS-compact'), ('netcdf','ATLAS-netcdf'),
            ('FES','FES-netcdf'), ('GOT','GOT-ascii')]
        # iterate over known remapped cases
        for m in mapping:
            # check if tide model is a remapped case
            if (self.format == m[0]):
                self.format = m[1]
        # assert that tide model is a known format
        assert self.format in self.formats()

    def to_datatree(self, m, **kwargs):
        """
        Create an xarray DataTree from a model object

        Parameters
        ----------
        m: str
            model name
        """
        # output dictionary of xarray Datasets
        ds = {}
        # try to read model elevations
        try:
            model = self.elevation(m)
        except (ValueError, KeyError):
            pass
        else:
            # read model constituents
            model.read_constants(**kwargs)
            # scale factor to convert to output units
            scale = model.scale or 1.0
            # convert to xarray Dataset and scale
            ds[model.type] = scale*model._constituents.to_dataset()
        # try to read model currents
        try:
            model = self.current(m)
        except (ValueError, KeyError):
            pass
        else:
            for TYPE in model.type:
                # read model constituents
                model.read_constants(type=TYPE, **kwargs)
                # scale factor to convert to output units
                scale = model.scale or 1.0
                # convert to xarray Dataset and scale
                ds[TYPE] = scale*model._constituents.to_dataset()
        # create xarray DataTree from dictionary
        dtree = xr.DataTree.from_dict(ds)
        # return the model xarray DataTree
        return dtree

    def from_dict(self, d: dict):
        """
        Create a model object from a python dictionary

        Parameters
        ----------
        d: dict
            Python dictionary for creating model object
        """
        for key, val in d.items():
            setattr(self, key, copy.copy(val))
        # return the model parameters
        return self

    def to_dict(self, **kwargs):
        """
        Create a python dictionary from a model object

        Parameters
        ----------
        fields: list, default all
            List of model attributes to output
        serialize: bool, default False
            Serialize dictionary for JSON output
        """
        # default fields
        keys = ['name', 'format', 'type', 'grid_file', 'model_file', 'projection',
            'variable', 'scale', 'constituents', 'version', 'reference']
        # set default keyword arguments
        kwargs.setdefault('fields', keys)
        kwargs.setdefault('serialize', False)
        # output dictionary
        d = {}
        # for each field
        for key in kwargs['fields']:
            if hasattr(self, key) and getattr(self, key) is not None:
                d[key] = getattr(self, key)
        # serialize dictionary for JSON output
        if kwargs['serialize']:
            d = self.serialize(d)
        # return the model dictionary
        return d

    def serialize(self, d: dict):
        """
        Encodes dictionary to be JSON serializable

        Parameters
        ----------
        d: dict
            Python dictionary to serialize
        """
        # iterate over keys
        for key, val in d.items():
            val = copy.copy(d[key])
            if isinstance(val, pathlib.Path):
                d[key] = str(val)
            elif isinstance(val, (list, tuple)) and isinstance(val[0], pathlib.Path):
                d[key] = [str(v) for v in val]
            elif isinstance(val, dict):
                d[key] = self.serialize(val)
        # return the model dictionary
        return d

    def parse_constituents(self, **kwargs) -> list:
        """
        Parses tide model files for a list of model constituents
        """
        if isinstance(self.model_file, (str, pathlib.Path)):
            # single file elevation case
            self.constituents = [
                self.parse_file(self.model_file, **kwargs)
            ]
        elif isinstance(self.model_file, list):
            # multiple file elevation case
            self.constituents = [
                self.parse_file(f, **kwargs) for f in self.model_file
            ]
        elif isinstance(self.model_file, dict) and \
            isinstance(self.model_file['u'], (str, pathlib.Path)):
            # single file currents case
            self.constituents = [
                self.parse_file(self.model_file['u'], **kwargs)
            ]
        elif isinstance(self.model_file, dict) and \
            isinstance(self.model_file['u'], list):
            # multiple file currents case
            self.constituents = [
                self.parse_file(f, **kwargs) for f in self.model_file['u']
            ]
        # return the model parameters
        return self

    @staticmethod
    def parse_file(
            model_file: str | pathlib.Path,
            raise_error: bool = False
        ):
        """
        Parses a model file for a tidal constituent name

        Parameters
        ----------
        model_file: str or pathlib.Path
            Tide model file to parse
        raise_error: bool, default False
            Raise exception if constituent is not found in file name

        Returns
        -------
        constituent: str or list
            constituent name
        """
        # import constituents class
        from pyTMD.io import constituents
        # convert to pathlib.Path
        model_file = pathlib.Path(model_file)
        # try to parse the constituent name from the file name
        try:
            return constituents.parse(model_file.name)
        except ValueError:
            pass
        # if no constituent name is found
        if raise_error:
            raise ValueError(f'Constituent not found in file {model_file}')
        else:
            return None

    def reduce_constituents(self, constituents: str | list):
        """
        Reduce model files to a subset of constituents

        Parameters
        ----------
        constituents: str or list
            List of constituents names
        """
        # if no constituents are specified, return self
        if constituents is None:
            return None
        # verify that constituents is a list
        if isinstance(constituents, str):
            constituents = [constituents]
        # parse constituents from model files
        try:
            self.parse_constituents(raise_error=True)
        except ValueError as exc:
            return None   
        # only run for multiple files
        if isinstance(self.model_file, list):
            # multiple file elevation case
            # filter model files to constituents
            self.model_file = [self.model_file[self.constituents.index(c)]
                for c in constituents if (c in self.constituents)
            ]
        elif isinstance(self.model_file, dict) and \
            isinstance(self.model_file['u'], list):
            # multiple file currents case
            for key, val in self.model_file.items():
                # reduce list of model files to constituents
                # filter model files to constituents
                self.model_file[key] = [val[self.constituents.index(c)]
                    for c in constituents if (c in self.constituents)
                ]
        # update list of constituents
        self.parse_constituents()
        # return self
        return self

    def extract_constants(self,
            lon: np.ndarray,
            lat: np.ndarray,
            **kwargs
        ):
        """
        Interpolate constants from tide models to input coordinates

        Parameters
        ----------
        lon: np.ndarray
            Longitude point in degrees
        lat: np.ndarray
            Latitude point in degrees
        append_node: bool, default False
            Append equilibrium amplitudes for node tides
        **kwargs: dict
            Keyword arguments for extracting constants

        Returns
        -------
        amp: np.ndarray
            Tidal amplitude
        ph: np.ndarray
            Tidal phase in degrees
        c: list
            Constituent list
        """
        # import tide model functions
        from pyTMD.io import OTIS, ATLAS, GOT, FES
        # set default keyword arguments
        kwargs.setdefault('type', self.type)
        kwargs.setdefault('append_node', False)
        kwargs.setdefault('scale', self.scale)
        kwargs.setdefault('constituents', None)
        # reduce constituents if specified
        self.reduce_constituents(kwargs['constituents'])
        # read tidal constants and interpolate to grid points
        if self.format in ('OTIS', 'ATLAS-compact', 'TMD3'):
            # extract model file in case of currents
            if isinstance(self.model_file, dict):
                model_file = self.model_file['u']
            else:
                model_file = self.model_file
            # extract tidal constants for model type
            amp,ph,D,c = OTIS.extract_constants(lon, lat,
                self.grid_file, model_file, self.projection,
                grid=self.file_format, **kwargs)
        elif self.format in ('ATLAS-netcdf',):
            # extract model file in case of currents
            if isinstance(self.model_file, dict):
                TYPE = kwargs['type'].lower()
                model_file = self.model_file[TYPE]
            else:
                model_file = self.model_file
            # extract tidal constants for model type
            amp,ph,D,c = ATLAS.extract_constants(lon, lat,
                self.grid_file, model_file,
                compressed=self.compressed, **kwargs)
        elif self.format in ('GOT-ascii', 'GOT-netcdf'):
            # extract tidal constants for model type
            amp,ph,c = GOT.extract_constants(lon, lat,
                self.model_file, grid=self.file_format,
                compressed=self.compressed, **kwargs)
        elif self.format in ('FES-ascii', 'FES-netcdf'):
            # extract model file in case of currents
            if isinstance(self.model_file, dict):
                TYPE = kwargs['type'].lower()
                model_file = self.model_file[TYPE]
            else:
                model_file = self.model_file
            # extract tidal constants for model type
            amp,ph = FES.extract_constants(lon, lat,
                model_file, version=self.version,
                compressed=self.compressed, **kwargs)
            # available model constituents
            c = self.constituents
        # append node equilibrium tide if not in constituents list
        if kwargs['append_node'] and ('node' not in c):
            # calculate node equilibrium tide
            anode, pnode = self.node_equilibrium(lat)
            # concatenate to output
            amp = np.ma.concatenate((amp, anode[:,None]), axis=1)
            ph = np.ma.concatenate((ph, pnode[:,None]), axis=1)
            # convert to complex amplitude and append
            c.append('node')
        # return the amplitude, phase, and constituents
        return (amp, ph, c)

    def read_constants(self, **kwargs):
        """
        Read constants from tide models

        Parameters
        ----------
        append_node: bool, default False
            Append equilibrium amplitudes for node tides
        **kwargs: dict
            Keyword arguments for reading constants
        """
        # import tide model functions
        from pyTMD.io import OTIS, ATLAS, GOT, FES
        # set default keyword arguments
        kwargs.setdefault('type', self.type)
        kwargs.setdefault('append_node', False)
        kwargs.setdefault('constituents', None)
        # reduce constituents if specified
        self.reduce_constituents(kwargs['constituents'])
        # read tidal constants
        if self.format in ('OTIS','ATLAS-compact','TMD3'):
            # extract model file in case of currents
            if isinstance(self.model_file, dict):
                model_file = self.model_file['u']
            else:
                model_file = self.model_file
            # read tidal constants for model type
            c = OTIS.read_constants(self.grid_file,
                model_file, self.projection,
                grid=self.file_format, **kwargs)
        elif self.format in ('ATLAS-netcdf',):
            # extract model file in case of currents
            if isinstance(self.model_file, dict):
                TYPE = kwargs['type'].lower()
                model_file = self.model_file[TYPE]
            else:
                model_file = self.model_file
            # read tidal constants for model type
            c = ATLAS.read_constants(self.grid_file,
                model_file, compressed=self.compressed, **kwargs)
        elif self.format in ('GOT-ascii','GOT-netcdf'):
            # read tidal constants for model type
            c = GOT.read_constants(self.model_file,
                compressed=self.compressed, grid=self.file_format,
                **kwargs)
        elif self.format in ('FES-ascii','FES-netcdf'):
            # extract model file in case of currents
            if isinstance(self.model_file, dict):
                TYPE = kwargs['type'].lower()
                model_file = self.model_file[TYPE]
            else:
                model_file = self.model_file
            # read tidal constants for model type
            c = FES.read_constants(model_file,
                version=self.version, compressed=self.compressed,
                **kwargs)
        # append node equilibrium tide if not in constituents list
        if kwargs['append_node'] and ('node' not in c.fields):
            # calculate node equilibrium tide
            amp, ph = self.node_equilibrium(c.latitude)
            # broadcast to shape of constituents
            if (np.shape(c.latitude) != c.shape):
                amp = np.broadcast_to(amp[:,None], c.shape, subok=True)
                ph = np.broadcast_to(ph[:,None], c.shape, subok=True)
                amp.mask = np.zeros_like(amp.data, dtype=bool)
                ph.mask = np.zeros_like(ph.data, dtype=bool)
            # calculate complex phase in radians for Euler's
            cph = -1j*ph*np.pi/180.0
            hc = amp*np.exp(cph)
            # append constituent
            c.append('node', hc)
        # return the tidal constituents
        self._constituents = c
        return c

    def interpolate_constants(self,
            lon: np.ndarray,
            lat: np.ndarray,
            **kwargs
        ):
        """
        Interpolate tidal constants to input coordinates

        Parameters
        ----------
        lon: np.ndarray
            Longitude point in degrees
        lat: np.ndarray
            Latitude point in degrees
        **kwargs: dict
            Keyword arguments for interpolating constants

        Returns
        -------
        amp: np.ndarray
            Tidal amplitude in meters
        ph: np.ndarray
            Tidal phase in degrees
        """
        # import tide model functions
        from pyTMD.io import OTIS, ATLAS, GOT, FES
        # set default keyword arguments
        kwargs.setdefault('type', self.type)
        kwargs.setdefault('scale', self.scale)
        # verify constituents have been read
        if not hasattr(self, '_constituents'):
            self.read_constants(**kwargs)
        # interpolate tidal constants to grid points
        if self.format in ('OTIS','ATLAS-compact','TMD3'):
            amp,ph,D = OTIS.interpolate_constants(lon, lat,
                self._constituents, **kwargs)
        elif self.format in ('ATLAS-netcdf',):
            amp,ph,D = ATLAS.interpolate_constants(lon, lat,
                self._constituents, **kwargs)
        elif self.format in ('GOT-ascii','GOT-netcdf'):
            amp,ph = GOT.interpolate_constants(lon, lat,
                self._constituents, **kwargs)
        elif self.format in ('FES-ascii','FES-netcdf'):
            amp,ph = FES.interpolate_constants(lon, lat,
                self._constituents, **kwargs)
        # return the amplitude and phase
        return (amp, ph)

    @staticmethod
    def node_equilibrium(lat: np.ndarray):
        """
        Compute the equilibrium amplitude and phase of the 18.6 year
        node tide :cite:p:`Cartwright:1971iz,Cartwright:1973em`

        Parameters
        ----------
        lat: np.ndarray
            latitude (degrees north)

        Returns
        -------
        amp: np.ndarray
            Tidal amplitude in meters
        phase: np.ndarray
            Tidal phase in degrees
        """
        # Cartwright and Edden potential amplitude
        amajor = 0.027929# node
        # Love numbers for long-period tides (Wahr, 1981)
        k2 = 0.299
        h2 = 0.606
        # tilt factor: response with respect to the solid earth
        gamma_2 = (1.0 + k2 - h2)
        # colatitude in radians
        th = np.radians(90.0 - lat)
        # 2nd degree Legendre polynomials
        P20 = 0.5*(3.0*np.cos(th)**2 - 1.0)
        # normalization for spherical harmonics
        dfactor = np.sqrt((4.0 + 1.0)/(4.0*np.pi))
        # calculate equilibrium node constants
        amp = np.ma.zeros_like(lat, dtype=np.float64)
        amp.data[:] = dfactor*P20*gamma_2*amajor
        amp.mask = np.zeros_like(lat, dtype=bool)
        phase = np.ma.zeros_like(amp)
        phase.data[:] = 180.0
        return (amp, phase)

    def __str__(self):
        """String representation of the ``io.model`` object
        """
        properties = ['pyTMD.io.model']
        properties.append(f"    name: {self.name}")
        return '\n'.join(properties)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

def extract_constants(lon: np.ndarray, lat: np.ndarray, m, **kwargs):
    """
    Interpolate constants from tide models to input coordinates

    Parameters
    ----------
    lon: np.ndarray
        Longitude point in degrees
    lat: np.ndarray
        Latitude point in degrees
    m: obj
        ``model`` class object
    **kwargs: dict
        Keyword arguments for extracting constants

    Returns
    -------
    amp: np.ndarray
        Tidal amplitude in meters
    ph: np.ndarray
        Tidal phase in degrees
    c: list
        Constituent list
    """
    # verify that constituents are valid class instance
    assert isinstance(m, model)
    # set default keyword arguments
    kwargs.setdefault('type', m.type)
    # extract tidal constants
    amp, ph, c = m.extract_constants(lon, lat, **kwargs)
    # return the amplitude, phase, and constituents
    return (amp, ph, c)

def read_constants(m, **kwargs):
    """
    Read constants from tide models

    Parameters
    ----------
    m: obj
        ``model`` class object
    **kwargs: dict
        Keyword arguments for reading constants

    Returns
    -------
    c: obj
        ``constituents`` class object
    """
    # verify that constituents are valid class instance
    assert isinstance(m, model)
    # set default keyword arguments
    kwargs.setdefault('type', m.type)
    # read tidal constants
    m.read_constants(**kwargs)
    # return the tidal constituents
    return m._constituents

def interpolate_constants(lon: np.ndarray, lat: np.ndarray, m, **kwargs):
    """
    Interpolate tidal constants to input coordinates

    Parameters
    ----------
    lon: np.ndarray
        Longitude point in degrees
    lat: np.ndarray
        Latitude point in degrees
    m: obj
        ``model`` class object
    **kwargs: dict
        Keyword arguments for extracting constants

    Returns
    -------
    amp: np.ndarray
        Tidal amplitude in meters
    ph: np.ndarray
        Tidal phase in degrees
    """
    # extract tidal constants
    amp, ph = m.interpolate_constants(lon, lat, **kwargs)
    # return the amplitude and phase
    return (amp, ph)
