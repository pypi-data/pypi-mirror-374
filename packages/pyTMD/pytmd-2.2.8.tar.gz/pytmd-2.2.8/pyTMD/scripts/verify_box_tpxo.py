#!/usr/bin/env python
u"""
verify_box_tpxo.py
Written by Tyler Sutterley (07/2025)
Verifies downloaded TPXO9-atlas global tide models from the box file
    sharing service

CALLING SEQUENCE:
    python verify_box_tpxo.py --token <token> --tide TPXO9-atlas-v5
    where <username> is your box api access token

COMMAND LINE OPTIONS:
    --help: list the command line options
    --directory X: working data directory
    -t X, --token X: user access token for box API
    -F X, --folder X: box folder id for model
    --tide X: TPXO9-atlas model to verify
    --currents: verify tide model current outputs
    -M X, --mode X: Local permissions mode of the files downloaded

PYTHON DEPENDENCIES:
    future: Compatibility layer between Python 2 and Python 3
        https://python-future.org/

REFERENCE:
    https://developer.box.com/guides/

UPDATE HISTORY:
    Updated 07/2025: add a default directory for tide models
    Updated 01/2025: scrubbed use of pathlib.os to just use os directly
    Updated 09/2024: use model class to define output directory
    Updated 04/2023: using pathlib to define and expand paths
    Updated 01/2023: use default context from utilities module
    Updated 11/2022: use f-strings for formatting verbose or ascii output
    Updated 04/2022: use argparse descriptions within documentation
    Updated 12/2021: added TPXO9-atlas-v5 to list of available tide models
    Updated 10/2021: using python logging for handling verbose output
    Updated 07/2021: can use prefix files to define command line arguments
    Written 03/2021
"""
from __future__ import print_function

import os
import re
import json
import logging
import pathlib
import argparse
import posixpath
import pyTMD.utilities

# PURPOSE: create an opener for box with a supplied user access token
def build_opener(token, context=pyTMD.utilities._default_ssl_context,
    redirect=True):
    """
    Build ``urllib`` opener for box with supplied user access token

    Arguments
    ---------
    token: box user access token

    Keyword arguments
    -----------------
    context: SSL context for opener object
    redirect: create redirect handler object
    """
    # https://docs.python.org/3/howto/urllib2.html#id5
    handler = []
    # create cookie jar for storing cookies for session
    cookie_jar = pyTMD.utilities.CookieJar()
    handler.append(pyTMD.utilities.urllib2.HTTPCookieProcessor(cookie_jar))
    handler.append(pyTMD.utilities.urllib2.HTTPSHandler(context=context))
    # redirect handler
    if redirect:
        handler.append(pyTMD.utilities.urllib2.HTTPRedirectHandler())
    # create "opener" (OpenerDirector instance)
    opener = pyTMD.utilities.urllib2.build_opener(*handler)
    # add Authorization header to opener
    opener.addheaders = [("Authorization", f"Bearer {token}")]
    # Now all calls to urllib2.urlopen use our opener.
    pyTMD.utilities.urllib2.install_opener(opener)
    return opener

# PURPOSE: verify downloaded TPXO9-atlas files with box server
def verify_box_tpxo(tide_dir, folder_id, TIDE_MODEL=None,
    CURRENTS=False, MODE=None):

    # create logger for verbosity level
    logger = pyTMD.utilities.build_logger(__name__, level=logging.INFO)

    # check if local directory exists and recursively create if not
    m = pyTMD.io.model(directory=tide_dir).elevation(TIDE_MODEL)
    localpath = m.model_file[0].parent
    # create output directory if non-existent
    localpath.mkdir(MODE, parents=True, exist_ok=True)

    # regular expression pattern for files of interest
    regex_patterns = []
    regex_patterns.append('grid')
    regex_patterns.append('h')
    if CURRENTS:
        regex_patterns.append('u')
    rx = re.compile(r'^({0})'.format(r'|'.join(regex_patterns)), re.VERBOSE)

    # box api url
    HOST = posixpath.join('https://api.box.com','2.0')
    # get folder contents
    folder_url = posixpath.join(HOST,'folders',folder_id,'items')
    request = pyTMD.utilities.urllib2.Request(folder_url)
    response = pyTMD.utilities.urllib2.urlopen(request)
    folder_contents = json.loads(response.read())
    # find files of interest
    file_entries = [entry for entry in folder_contents['entries'] if
        (entry['type'] == 'file') and rx.match(entry['name'])]
    # for each file in the folder
    for entry in file_entries:
        # have insufficient permissions for downloading content
        file_url = posixpath.join(HOST,'files',entry['id'])
        # print remote path
        logger.info(f'{file_url} -->')
        # get last modified time for file
        request = pyTMD.utilities.urllib2.Request(file_url)
        response = pyTMD.utilities.urllib2.urlopen(request)
        file_contents = json.loads(response.read())
        modified_at = file_contents['modified_at']
        remote_mtime = pyTMD.utilities.get_unix_time(modified_at,
            format='%Y-%m-%dT%H:%M:%S%z')
        # print file information
        local = localpath.joinpath(entry['name'])
        logger.info(f'\t{str(local)}')
        # compare checksums to validate download
        sha1 = pyTMD.utilities.get_hash(local, algorithm='sha1')
        if sha1 != entry['sha1']:
            logger.critical(f'Remote checksum: {entry["sha1"]}')
            logger.critical(f'Local checksum: {sha1}')
            raise Exception('Checksum verification failed')
        # keep remote modification time of file and local access time
        os.utime(local, (local.stat().st_atime, remote_mtime))
        # change the permissions mode of the local file
        local.chmod(mode=MODE)

# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Verifies downloaded TPXO9-atlas global
            tide models from the box file sharing service
            """,
        fromfile_prefix_chars="@"
    )
    parser.convert_arg_line_to_args = pyTMD.utilities.convert_arg_line_to_args
    # command line parameters
    # working data directory
    default_path = pyTMD.utilities.get_data_path('data')
    parser.add_argument('--directory','-D',
        type=pathlib.Path, default=default_path,
        help='Working data directory')
    # box user access token
    parser.add_argument('--token','-t',
        type=str, default='',
        help='User access token for box API')
    # box folder id
    parser.add_argument('--folder','-F',
        type=str, default='',
        help='box folder id for model')
    # TPXO9-atlas tide models
    parser.add_argument('--tide','-T',
        type=str, default='TPXO9-atlas-v5',
        help='TPXO9-atlas tide model to verify')
    # download tidal currents
    parser.add_argument('--currents',
        default=False, action='store_true',
        help='Verify tide model current outputs')
    # permissions mode of the local directories and files (number in octal)
    parser.add_argument('--mode','-M',
        type=lambda x: int(x,base=8), default=0o775,
        help='Permission mode of directories and files downloaded')
    # return the parser
    return parser

# This is the main part of the program that calls the individual functions
def main():
    # Read the system arguments listed after the program
    parser = arguments()
    args,_ = parser.parse_known_args()

    # build an opener for accessing box folders
    opener = build_opener(args.token)
    # check internet connection before attempting to run program
    if pyTMD.utilities.check_connection('https://app.box.com/'):
        verify_box_tpxo(args.directory, args.folder, TIDE_MODEL=args.tide,
            CURRENTS=args.currents, MODE=args.mode)

# run main program
if __name__ == '__main__':
    main()
