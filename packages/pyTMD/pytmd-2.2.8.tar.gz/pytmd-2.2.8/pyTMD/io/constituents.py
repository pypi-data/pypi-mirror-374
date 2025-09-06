#!/usr/bin/env python
u"""
constituents.py
Written by Tyler Sutterley (08/2025)
Basic tide model constituent class

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html

UPDATE HISTORY:
    Updated 08/2025: use numpy degree to radian conversions
        add functions for converting constituents to an xarray Dataset
        suppress pyproj user warnings about using PROJ4 strings
    Updated 02/2025: add RHO to rho1 to known mappable constituents
        add more known constituents to string parser function
    Updated 11/2024: added property for Extended Doodson numbers
    Updated 10/2024: added property for the shape of constituent fields
    Updated 09/2024: add more known constituents to string parser function
    Updated 08/2024: add GOT prime nomenclature for 3rd degree constituents
    Updated 07/2024: add function to parse tidal constituents from strings
    Updated 05/2024: make subscriptable and allow item assignment
    Updated 01/2024: added properties for Doodson and Cartwright numbers
    Updated 08/2023: added default for printing constituent class
    Updated 07/2023: output constituent from get and pop as copy
    Updated 03/2023: add basic variable typing to function inputs
    Written 12/2022
"""
from __future__ import division, annotations

import re
import copy
import warnings
import numpy as np
import pyTMD.arguments
from pyTMD.utilities import import_dependency
from dataclasses import dataclass
# suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# attempt imports
xr = import_dependency('xarray')
    
__all__ = [
    "coords",
    "constituents"
]

@dataclass
class coords(dict):
    """Class for pyTMD constituent coordinates"""
    x: np.ndarray
    y: np.ndarray
    def __init__(self, *args, **kwargs):
        super(coords, self).__init__(*args, **kwargs)
        self.__dict__ = self

class constituents:
    """
    Class for tide model constituents

    Attributes
    ----------
    fields: list
        list of tide model constituents
    """
    def __init__(self, **kwargs):
        # set initial attributes
        self.fields = []
        self.__index__ = 0
        # set optional fields
        for key, val in kwargs.items():
            setattr(self, key, val)

    def append(self, field: str, constituent: np.ndarray):
        """
        Append a tide model constituent

        Parameters
        ----------
        field: str
            Tide model constituent name
        constituent: np.ndarray
            Tide model constituent (complex form)
        """
        # append field
        self.fields.append(field)
        setattr(self, field, constituent)
        return self

    def get(self, field: str):
        """
        Get a tide model constituent

        Parameters
        ----------
        field: str
            Tide model constituent name

        Returns
        -------
        constituent: np.ndarray
            Tide model constituent (complex form)
        """
        constituent = getattr(self, field)
        return copy.copy(constituent)

    def pop(self, field: str):
        """
        Retrieve a tide model constituent and remove from list

        Parameters
        ----------
        field: str
            Tide model constituent name

        Returns
        -------
        constituent: np.ndarray
            Tide model constituent (complex form)
        """
        self.fields.remove(field)
        constituent = getattr(self, field)
        delattr(self, field)
        return copy.copy(constituent)

    def update(self, field: str, constituent: np.ndarray):
        """
        Update a tide model constituent

        Parameters
        ----------
        field: str
            Tide model constituent name
        constituent: np.ndarray
            Tide model constituent (complex form)
        """
        # raise exception if field not in list
        if not hasattr(self, field):
            raise KeyError(f'Constituent {field}')
        # update the constituent
        setattr(self, field, constituent)
        return self

    def amplitude(self, field: str):
        """
        Calculate the amplitude of a tide model constituent

        Parameters
        ----------
        field: str
            Tide model constituent name

        Returns
        -------
        amp: np.ndarray
            Tide model constituent amplitude
        """
        constituent = getattr(self, field)
        # calculate constituent amplitude
        amp = np.sqrt(constituent.real**2 + constituent.imag**2)
        # update mask and fill values
        amp.mask = np.copy(constituent.mask)
        amp.data[amp.mask] = amp.fill_value
        return amp

    def phase(self, field: str):
        """
        Calculate the phase of a tide model constituent

        Parameters
        ----------
        field: str
            Tide model constituent name

        Returns
        -------
        ph: float
            Tide model constituent phase (degrees)
        """
        constituent = getattr(self, field)
        # calculate constituent phase and convert to degrees
        ph = np.degrees(np.arctan2(-constituent.imag, constituent.real))
        ph.data[ph.data < 0] += 360.0
        # update mask and fill values
        ph.mask = np.copy(constituent.mask)
        ph.data[ph.mask] = ph.fill_value
        return ph

    def to_dataset(self, **kwargs):
        """
        Convert constituents to an xarray Dataset

        Parameters
        ----------
        attrs: dict, default {}
            Attributes to assign to the xarray Dataset
        variables: list, default ["bathymetry"]
            Auxiliary variables to include in the xarray Dataset

        Returns
        -------
        ds: xarray.Dataset
            Dataset of tide model constituents
        """
        kwargs.setdefault('attrs', {})
        kwargs.setdefault('variables', ["bathymetry"])
        # create a dictionary of constituent data
        data = {}
        # data coordinates (standardize to x and y)
        data["coords"] = {}
        data["coords"]["x"] = dict(dims="x", data=self.coords.x)
        data["coords"]["y"] = dict(dims="y", data=self.coords.y)
        # data dimensions
        data["dims"] = ("y", "x")
        # data variables
        data["data_vars"] = {}
        for field in self.fields:
            data["data_vars"][field] = {}
            data["data_vars"][field]["dims"] = ("y", "x")
            data["data_vars"][field]["data"] = getattr(self, field)
        # append auxiliary variables if present
        for var in kwargs['variables']:
            if hasattr(self, var):
                data["data_vars"][var] = {}
                data["data_vars"][var]["dims"] = ("y", "x")
                data["data_vars"][var]["data"] = getattr(self, var)
        # data attributes
        data["attrs"] = kwargs.get("attrs", {})
        # include coordinate reference system if present
        if hasattr(self, "crs"):
            data["attrs"]["crs"] = self.crs.to_dict()
        # convert to xarray Dataset from the data dictionary
        ds = xr.Dataset.from_dict(data)
        return ds

    @property
    def coords(self):
        """Coordinates of constituent fields
        """
        return coords(x=self._x, y=self._y)

    @property
    def _x(self):
        """x-dimension coordinates
        """
        if hasattr(self, "x"):
            return self.x
        elif hasattr(self, "longitude"):
            return self.longitude
        else:
            return None

    @property
    def _y(self):
        """y-dimension coordinates
        """
        if hasattr(self, "y"):
            return self.y
        elif hasattr(self, "latitude"):
            return self.latitude
        else:
            return None

    @property
    def doodson_number(self):
        """Doodson number for constituents
        """
        doodson_numbers = []
        # for each constituent ID
        for f in self.fields:
            try:
                # try to get the Doodson number
                n = pyTMD.arguments.doodson_number(f)
            except (AssertionError, ValueError) as exc:
                n = None
            # add Doodson number to the combined list
            doodson_numbers.append(n)
        # return the list of Doodson numbers
        return doodson_numbers

    @property
    def cartwright_number(self):
        """Cartwright numbers for constituents
        """
        cartwright_numbers = []
        # for each constituent ID
        for f in self.fields:
            try:
                # try to get the Cartwright numbers
                n = pyTMD.arguments.doodson_number(f, formalism='Cartwright')
            except (AssertionError, ValueError) as exc:
                n = None
            # add Cartwright numbers to the combined list
            cartwright_numbers.append(n)
        # return the list of Cartwright numbers
        return cartwright_numbers

    @property
    def extended_doodson(self):
        """Extended Doodson numbers for constituents
        """
        extended_numbers = []
        # for each constituent ID
        for f in self.fields:
            try:
                # try to get the Extended Doodson number
                XDO = pyTMD.arguments.doodson_number(f, formalism='Extended')
            except (AssertionError, ValueError) as exc:
                XDO = None
            # add Extended Doodson number to the combined list
            extended_numbers.append(XDO)
        # return the list of Extended Doodson numbers
        return extended_numbers

    @property
    def shape(self):
        """Shape of constituent fields
        """
        try:
            field = self.fields[0]
            return getattr(self, field).shape
        except:
            return None

    @staticmethod
    def parse(constituent: str) -> str:
        """
        Parses for tidal constituents using regular expressions and
        remapping of known cases

        Parameters
        ----------
        constituent: str
            Unparsed tidal constituent name
        """
        # list of tidal constituents (not all are included in tidal program)
        # include negative look-behind and look-ahead for complex cases
        cindex = ['z0','node','sa','ssa','sta','msqm','mtm',
            r'mf(?![a|b|n])',r'mm(?![un])',r'msf(?![a|b])',r'mt(?![m|ide])',
            '2q1','alpha1','beta1','chi1','j1','psi1','phi1','pi1','sigma1',
            'rho1','tau1','theta1','oo1','so1','ups1','q1','s1',
            r'(?<!rh)o1(?!n)',r'm1(?![a|b])',r'(?<![al|oo|])p1',r'k1(?!n)',
            '2sm2','alpha2','beta2','delta2','eps2','gamma2','k2','lambda2',
            'm2a','m2b','mks2','mns2','mu2','r2',
            r'(?<![ms])2n2',r'(?<![b|z])eta2',r'(?<!de)l2(?![a|b])',
            r'(?<![ga|la])m2(?![a|b|n])',r'(?<![mmu|ms])n2',r'(?<![ms])nu2',
            r'(?<![mn|mk|mnu|ep])s2(?![0|r|m])',r'(?<![be])t2',
            'm3','mk3','mk4','mn4','ms4','s3','m4','n4','s4',
            's5','m6','s6','s7','s8','m8',
        ]
        # compile regular expression
        # adding GOT prime nomenclature for 3rd degree constituents
        rx = re.compile(
            r'(?<![\d|j|k|l|m|n|o|p|q|r|s|t|u])(?<![|\(|\)])(' + 
            r'|'.join(cindex) + r')(?![|\(|\)])(?![\d])(?![+|-])(\')?',
            re.IGNORECASE
        )
        # check if tide model is a simple regex case
        if rx.search(constituent):
            return "".join(rx.findall(constituent)[0]).lower()
        # regular expression pattern for finding constituent names
        # include negative look-behind and look-ahead for complex cases
        patterns = (r'node|alpha|beta|chi|delta|eps|eta|gamma|lambda|muo|mu|'
            r'nu|pi|psi|phi|rho\d|sigma|tau|theta|ups|zeta|e3|f\d|jk|jo|jp|'
            r'jq|j|kb|kjq|kj|kmsn|km|kn|ko|kpq|kp|kq|kso|ks|k\d|lb|'
            r'(?<!de)l\d|ma|mb|mfa|mfb|mfn|mf|mkj|mkl|mknu|mkn|mkp|mks|mk|'
            r'mlns|mls|ml|mmun|mm|mnks|mnk|mnls|mnm|mno|mnp|mns|mnus|mnu|mn|'
            r'mop|moq|mo|mpq|mp|mq|mr|msfa|msfb|msf|mskn|msko|msk|msl|msm|'
            r'msnk|msnu|msn|mso|msp|msqm|mst|ms(?!q)|mtm|mt(?![m|ide])|'
            r'(?<![2s|l|la|ga])m[1-9]|na|nb|nkms|nkm|nkp|nks|nk|'
            r'nmks|nmk|nmls|nm|no|np|nq|nsk|nso|ns|(?<!m)n\d|(?<!l)oa|ob|ok|'
            r'ojm|oj|omg|om(?![0|ega])|ook|oop|oo\d|opk|opq|op|oq|os|'
            r'(?<![rh|o|s|tpx])o\d|pjrho|pk|pmn|pm|po|pqo|(?<![al|e])p\d|qj|'
            r'qk|qms|qm|qp|qs|q\d|rp|r\d|(?<!s)sa|sf|skm|skn|sk|sl(?!ev)|smk|'
            r'smn|sm|snk|snmk|snm|snu|sn|so|sp|(?<!m)sq|ssa|sta|st(?!a)|'
            r'(?<![ep|fe|m|mn|mk])s\d|ta|tk|(?<![curren|be])t\d|z\d')
        # full regular expression pattern for extracting complex and compound
        # constituents with GOT prime nomenclature for 3rd degree terms
        cases = re.compile(r'(\d+)?(\(\w+\))?(\+|\-|\')?(node|alpha|beta|chi|'
            r'delta|eps|eta|gamma|lambda|muo|mu|nu|pi|psi|phi|rho|sigma|tau|'
            r'theta|ups|zeta|e|f|jk|jo|jp|jq|j|kb|kjq|kj|kmsn|km|kn|ko|kpq|'
            r'kp|kq|kso|ks|k|lb|l|ma|mb|mfa|mfb|mfn|mf|mkj|mkl|mknu|mkn|mkp|'
            r'mks|mk|mlns|mls|ml|mmun|mm|mnks|mnk|mnls|mnm|mno|mnp|mns|mnus|'
            r'mnu|mn|mop|moq|mo|mpq|mp|mq|mr|msfa|msfb|msf|mskn|msko|msk|msl|'
            r'msm|msnk|msnu|msn|mso|msp|msqm|mst|ms|mtm|mt|m|na|nb|nkms|nkm|'
            r'nkp|nks|nk|nmks|nmk|nmls|nm|no|np|nq|nsk|nso|ns|n|oa|ob|ok|ojm|'
            r'oj|omg|om|ook|oop|oo|opk|opq|op|oq|os|o|pjrho|pk|pmn|pm|po|pqo|p|'
            r'qj|qk|qms|qm|qp|qs|q|rp|r|sa|sf|skm|skn|sk|sl|smk|smn|sm|snk|'
            r'snmk|snm|snu|sn|so|sp|sq|ssa|sta|st|s|ta|tk|t|z)?(\d+)?(\(\w+\))?'
            r'(\d+)?(\+\+|\+|\-\-|\-|a|b|k|m|nk|ns|n|r|s)?(\d+)?(\')?',
            re.IGNORECASE)
        # check if tide model is a regex case for compound tides
        if re.search(patterns, constituent, re.IGNORECASE):
            return "".join(cases.findall(constituent)[0]).lower()
        # known remapped cases
        mapping = [('2n','2n2'), ('alp1', 'alpha1'), ('alp2', 'alpha2'),
            ('bet1', 'beta1'), ('bet2', 'beta2'), ('del2', 'delta2'),
            ('e2','eps2'), ('ep2','eps2'), ('gam2', 'gamma2'),
            ('la2','lambda2'), ('lam2','lambda2'), ('lm2','lambda2'),
            ('msq', 'msqm'), ('omega0', 'node'), ('om0', 'node'),
            ('rho', 'rho1'), ('sig1','sigma1'),
            ('the', 'theta1'), ('the1', 'theta1')]
        # iterate over known remapped cases
        for m in mapping:
            # check if tide model is a remapped case
            if m[0] in constituent.lower():
                return m[1]
        # raise a value error if not found
        raise ValueError(f'Constituent not found in {constituent}')

    def __str__(self):
        """String representation of the ``constituents`` object
        """
        properties = ['pyTMD.constituents']
        fields = ', '.join(self.fields)
        properties.append(f"    constituents: {fields}")
        return '\n'.join(properties)

    def __len__(self):
        """Number of constituents
        """
        return len(self.fields)

    def __iter__(self):
        """Iterate over constituents
        """
        self.__index__ = 0
        return self

    def __next__(self):
        """Get the next constituent
        """
        try:
            field = self.fields[self.__index__]
        except IndexError as exc:
            raise StopIteration from exc
        # get the model constituent
        constituent = getattr(self, field)
        self.__index__ += 1
        return (field, constituent)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
