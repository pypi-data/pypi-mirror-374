#!/usr/bin/env python
u"""
reduce_OTIS_files.py
Written by Tyler Sutterley (07/2025)
Read OTIS-format tidal files and reduce to a regional subset

COMMAND LINE OPTIONS:
    -D X, --directory X: working data directory
    -T X, --tide X: Tide model to use
    -B X, --bounds X: Grid Bounds (xmin,xmax,ymin,ymax)
    --projection X: spatial projection of bounds as EPSG code or PROJ4 string
        4326: latitude and longitude coordinates on WGS84 reference ellipsoid
    -M X, --mode X: permissions mode of the output files

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
    scipy: Scientific Tools for Python
        https://docs.scipy.org/doc/
    pyproj: Python interface to PROJ library
        https://pypi.org/project/pyproj/
    timescale: Python tools for time and astronomical calculations
        https://pypi.org/project/timescale/

PROGRAM DEPENDENCIES:
    io/model.py: retrieves tide model parameters for named tide models
    io/OTIS.py: extract tidal harmonic constants from OTIS tide models
    utilities.py: download and management utilities for syncing files
    crs.py: Coordinate Reference System (CRS) routines

UPDATE HISTORY:
    Updated 07/2025: add a default directory for tide models
    Updated 11/2024: use "stem" instead of "basename"
    Updated 07/2024: renamed format for ATLAS to ATLAS-compact
    Updated 04/2024: add debug mode printing input arguments
        use wrapper to importlib for optional dependencies
    Updated 12/2023: use new crs class for coordinate reprojection
    Updated 04/2023: using pathlib to define and expand paths
    Updated 03/2023: new function name for coordinate reference systems
    Updated 12/2022: refactored OTIS model input and output
    Updated 11/2022: place some imports within try/except statements
        use f-strings for formatting verbose or ascii output
    Updated 05/2022: updated keyword arguments to read tide model programs
    Updated 04/2022: use argparse descriptions within documentation
    Updated 11/2021: add function for attempting to extract projection
    Updated 09/2021: refactor to use model class for files and attributes
    Updated 07/2021: can use prefix files to define command line arguments
    Updated 10/2020: using argparse to set command line parameters
    Updated 09/2020: can use projected coordinates for output model bounds
        compatibility updates for python3
    Updated 07/2020: renamed coordinate conversion program
    Updated 02/2020: changed CATS2008 grid to match version on U.S. Antarctic
        Program Data Center http://www.usap-dc.org/view/dataset/601235
    Updated 11/2019: added AOTIM-5-2018 tide model (2018 update to 2004 model)
    Written 08/2018
"""
from __future__ import print_function

import sys
import os
import logging
import pathlib
import argparse
import traceback
import numpy as np
import pyTMD.crs
import pyTMD.io
import pyTMD.utilities
import timescale.time

# attempt imports
pyproj = pyTMD.utilities.import_dependency('pyproj')

# PURPOSE: keep track of threads
def info(args):
    logging.debug(pathlib.Path(sys.argv[0]).name)
    logging.debug(args)
    logging.debug(f'module name: {__name__}')
    if hasattr(os, 'getppid'):
        logging.debug(f'parent process: {os.getppid():d}')
    logging.debug(f'process id: {os.getpid():d}')

# PURPOSE: reads OTIS-format tidal files and reduces to a regional subset
def make_regional_OTIS_files(tide_dir, TIDE_MODEL,
        BOUNDS=4*[None],
        PROJECTION='4326',
        MODE=0o775
    ):
    # get parameters for tide model grid
    try:
        model = pyTMD.io.model(directory=tide_dir).elevation(TIDE_MODEL)
    except Exception as exc:
        model = pyTMD.io.model(directory=tide_dir).current(TIDE_MODEL)
    # directionaries with input and output files
    model_file = {}
    new_model_file = {}

    # read the OTIS-format tide grid file
    if (model.format == 'ATLAS-compact'):
        # if reading a global solution with localized solutions
        x0,y0,hz0,mz0,iob,dt,pmask,local = pyTMD.io.OTIS.read_atlas_grid(
            model.grid_file)
        xi,yi,hz = pyTMD.io.OTIS.combine_atlas_model(x0, y0, hz0, pmask,
            local, variable='depth')
        mz = pyTMD.io.OTIS.create_atlas_mask(x0, y0, mz0,
            local, variable='depth')
    else:
        # if reading a pure global solution
        xi,yi,hz,mz,iob,dt = pyTMD.io.OTIS.read_otis_grid(model.grid_file)

    # converting bounds x,y from projection to latitude/longitude
    crs1 = pyTMD.crs().from_input(PROJECTION)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    xbox = np.array([BOUNDS[0],BOUNDS[1],BOUNDS[1],BOUNDS[0],BOUNDS[0]])
    ybox = np.array([BOUNDS[2],BOUNDS[2],BOUNDS[3],BOUNDS[3],BOUNDS[2]])
    lon,lat = transformer.transform(xbox,ybox)

    # convert bounds from latitude/longitude to model coordinates
    x,y = pyTMD.crs().convert(lon,lat,model.projection,'F')

    # find indices to reduce to xmin,xmax,ymin,ymax
    gridx,gridy = np.meshgrid(xi,yi)
    indy,indx = np.nonzero((gridx >= x.min()) & (gridx <= x.max()) &
        (gridy >= y.min()) & (gridy <= y.max()))
    nx = np.count_nonzero((xi >= x.min()) & (xi <= x.max()))
    ny = np.count_nonzero((yi >= y.min()) & (yi <= y.max()))
    # calculate new grid limits and convert back to grid-cell edges
    dx = np.abs(xi[1]-xi[0])
    dy = np.abs(yi[1]-yi[0])
    xlim = np.array([xi[indx[0]]-dx/2.0,xi[indx[-1]]+dx/2.0],dtype='>f4')
    ylim = np.array([yi[indy[0]]-dy/2.0,yi[indy[-1]]+dy/2.0],dtype='>f4')
    # reduce grid and mask to new bounds
    hz1 = np.zeros((ny,nx),dtype='>f4')
    mz1 = np.zeros((ny,nx),dtype='>i4')
    hz1[:,:] = hz[indy,indx].reshape(ny,nx)
    mz1[:,:] = mz[indy,indx].reshape(ny,nx)
    # output reduced grid to file
    new_grid_file = create_unique_filename(model.grid_file)
    pyTMD.io.OTIS.output_otis_grid(new_grid_file,xlim,ylim,hz1,mz1,iob,dt)
    # change the permissions level to MODE
    new_grid_file.chmod(mode=MODE)

    # combine ATLAS sub-grids into single output grid
    # reduce elevation files to bounds
    try:
        # get parameters for tide model
        model = model.elevation(TIDE_MODEL)
    except Exception as exc:
        pass
    else:
        # read each constituent
        constituents,nc = pyTMD.io.OTIS.read_constituents(model_file['z'])
        z1 = np.zeros((ny,nx,nc),dtype=np.complex64)
        for i,c in enumerate(constituents):
            # read constituent from elevation file
            if (model.format == 'ATLAS-compact'):
                z0,zlocal = pyTMD.io.OTIS.read_atlas_elevation(
                    model_file['z'], i, c)
                xi,yi,z=pyTMD.io.OTIS.combine_atlas_model(x0, y0, z0, pmask,
                    zlocal, variable='z')
            else:
                z = pyTMD.io.OTIS.read_otis_elevation(model_file['z'], i)
            # reduce elevation to new bounds
            z1[:,:,i] = z[indy,indx].reshape(ny,nx)
        # output reduced elevation components
        new_model_file['z'] = create_unique_filename(model_file['z'])
        pyTMD.io.OTIS.output_otis_elevation(new_model_file['z'], z1,
            xlim, ylim, constituents)
        # change the permissions level to MODE
        new_model_file['z'].chmod(mode=MODE)

    # combine ATLAS sub-grids into single output grid
    # reduce transport files to bounds
    try:
        # get parameters for tide model
        model = model.current(TIDE_MODEL)
    except Exception as exc:
        pass
    else:
        # read each constituent
        constituents,nc = pyTMD.io.OTIS.read_constituents(model_file['u'])
        u1 = np.zeros((ny,nx,nc),dtype=np.complex64)
        v1 = np.zeros((ny,nx,nc),dtype=np.complex64)
        for i,c in enumerate(constituents):
            # read constituent from transport file
            if (model.format == 'ATLAS-compact'):
                u0,v0,uvlocal = pyTMD.io.OTIS.read_atlas_transport(
                    model_file['u'], i, c)
                xi,yi,u = pyTMD.io.OTIS.combine_atlas_model(x0, y0, u0, pmask,
                    uvlocal, variable='u')
                xi,yi,v = pyTMD.io.OTIS.combine_atlas_model(x0, y0, v0, pmask,
                    uvlocal, variable='v')
            else:
                u,v = pyTMD.io.OTIS.read_otis_transport(model_file['u'],i)
            # reduce transport components to new bounds
            u1[:,:,i] = u[indy,indx].reshape(ny,nx)
            v1[:,:,i] = v[indy,indx].reshape(ny,nx)
        # output reduced transport components
        new_model_file['uv'] = create_unique_filename(model_file['u'])
        pyTMD.io.OTIS.output_otis_transport(new_model_file['u'], u1, v1,
            xlim, ylim, constituents)
        # change the permissions level to MODE
        new_model_file['u'].chmod(mode=MODE)

# PURPOSE: create a unique filename adding a numerical instance if existing
def create_unique_filename(filename):
    # split filename into parts
    filename = pathlib.Path(filename)
    stem = filename.stem
    suffix = '' if (filename.suffix in ('.out','.oce')) else filename.suffix
    # replace extension with reduced flag
    filename = filename.with_name(f'{stem}{suffix}.reduced')
    # create counter to add to the end of the filename if existing
    counter = 1
    while counter:
        try:
            # open file descriptor only if the file doesn't exist
            fd = filename.open(mode='xb')
        except OSError:
            pass
        else:
            # close the file descriptor and return the filename
            fd.close()
            return filename
        # new filename adds counter before the file extension
        filename = filename.with_name(f'{stem}{suffix}.reduced_{counter:d}')
        counter += 1

# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Read OTIS-format tidal files and reduce to a regional
            subset
            """,
        fromfile_prefix_chars="@"
    )
    parser.convert_arg_line_to_args = pyTMD.utilities.convert_arg_line_to_args
    # command line options
    # set data directory containing the tidal data
    default_path = pyTMD.utilities.get_data_path('data')
    parser.add_argument('--directory','-D',
        type=pathlib.Path, default=default_path,
        help='Working data directory')
    # tide model to use
    model_choices = ('CATS0201','CATS2008','CATS2008_load','TPXO9-atlas',
        'TPXO9.1','TPXO8-atlas','TPXO7.2','TPXO7.2_load','AODTM-5','AOTIM-5',
        'AOTIM-5-2018')
    parser.add_argument('--tide','-T',
        metavar='TIDE', type=str, default='TPXO9.1',
        choices=model_choices,
        help='Tide model to use')
    # spatial projection (EPSG code or PROJ4 string)
    parser.add_argument('--projection','-P',
        type=str, default='4326',
        help='Spatial projection as EPSG code or PROJ4 string')
    # bounds for reducing model (xmin,xmax,ymin,ymax)
    parser.add_argument('--bounds','-B',
        metavar=('xmin','xmax','ymin','ymax'), type=float, nargs=4,
        help='Grid bounds for reducing model')
    # verbose output of processing run
    # print information about processing run
    parser.add_argument('--verbose','-V',
        action='count', default=0,
        help='Verbose output of processing run')
    # permissions mode of output reduced files (number in octal)
    parser.add_argument('--mode','-M',
        type=lambda x: int(x,base=8), default=0o775,
        help='Permission mode of the output files')
    # return the parser
    return parser

# This is the main part of the program that calls the individual functions
def main():
    # Read the system arguments listed after the program
    parser = arguments()
    args,_ = parser.parse_known_args()

    # create logger
    loglevels = [logging.CRITICAL, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=loglevels[args.verbose])

    # try to run regional program
    try:
        info(args)
        make_regional_OTIS_files(args.directory, args.tide,
            BOUNDS=args.bounds,
            PROJECTION=args.projection,
            MODE=args.mode)
    except Exception as exc:
        # if there has been an error exception
        # print the type, value, and stack trace of the
        # current exception being handled
        logging.critical(f'process id {os.getpid():d} failed')
        logging.error(traceback.format_exc())

# run main program
if __name__ == '__main__':
    main()
