# -*- coding: utf-8 -*-

"""Module defining the Python and command line client.
"""

import argparse
import datetime
import logging
import math
import os
from pathlib import Path
from pprint import pformat
import sys
import textwrap

import requests
import tqdm


from . import __version__

BASE_URL = "http://api.mlso.ucar.edu:5000"
API_VERSION = "v1"
SIGNUP_URL = "https://registration.hao.ucar.edu"


# chunk size for downloading files, 1-10M is probably the most efficient size
# for good speed and reasonable memory usage
CHUNK_SIZE = 1024 * 1024

session = requests.Session()

# setup default logging, users of this library can set this to their own logger
# or modify this one to suit their needs
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


# API


class UserNotFound(Exception):
    """Exception raised when a username is found in the registration database."""

    pass


class ServerError(Exception):
    """Exception raised when there is a problem with the server not returning a
    valid result.
    """

    pass


def about(
    base_url: str = BASE_URL, api_version: str = API_VERSION, verbose: bool = False
):
    """Retrieve the results of the `/about` endpoint."""
    url = f"{base_url}/{api_version}/about"
    if verbose:
        logger.debug(f"URL: {url}")

    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        raise ServerError(f"Connection error reaching {url}")

    if not r.ok:
        j = r.json()
        msg = j["message"]
        raise ServerError(f"Server response: {r.status_code} {r.reason} ({msg})")

    j = r.json()

    if verbose:
        logger.debug(pformat(j))

    return j


def instruments(
    base_url: str = BASE_URL, api_version: str = API_VERSION, verbose: bool = False
):
    """Retrieve list of instruments from the `/instruments/{instrument}`
    endpoint with some of their properties.
    """
    url = f"{base_url}/{api_version}/instruments"
    if verbose:
        logger.debug(f"URL: {url}")

    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        raise ServerError(f"Connection error reaching {url}")

    if not r.ok:
        raise ServerError(f"Server response: {r.status_code} {r.reason}")

    instruments = r.json()
    if verbose:
        logger.debug(pformat(instruments))

    instruments = sorted(instruments)

    results = []

    for instrument in instruments:
        url = f"{base_url}/{api_version}/instruments/{instrument}/"
        if verbose:
            logger.debug(f"URL: {url}")

        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            raise ServerError(f"Connection error reaching {url}")

        j = r.json()

        if verbose:
            logger.debug(pformat(j))

        dates = j["dates"]
        full_name = j["name"]
        start_date = dates["start-date"]
        end_date = dates["end-date"]

        i = {
            "id": instrument,
            "start-date": start_date,
            "end-date": end_date,
            "name": j["name"],
        }
        results.append(i)

    return results


def products(
    instrument,
    base_url: str = BASE_URL,
    api_version: str = API_VERSION,
    verbose: bool = False,
):
    """Handle retrieving the `/instruments/{instrument}/products` endpoint
    results. Can raise ServerError if there is a problem with the web request.
    """
    url = f"{base_url}/{api_version}/instruments/{instrument}/products"
    if verbose:
        logger.debug(f"URL: {url}")

    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        raise ServerError(f"Connection error reaching {url}")

    if not r.ok:
        j = r.json()
        msg = j["message"]
        raise ServerError(f"Server response: {r.status_code} {r.reason} ({msg})")

    j = r.json()

    if verbose:
        logger.debug(pformat(j))

    return j


def authenticate(
    username: str = None,
    base_url: str = BASE_URL,
    api_version: str = API_VERSION,
    verbose: bool = False,
):
    """Authenticate username within the session. This must be called before
    `download_file`.
    """
    if username is None:
        msg = f"username required, sign up at {SIGNUP_URL}"
        raise UserNotFound(msg)
    else:
        url = f"{base_url}/{api_version}/authenticate?username={username}"
        if verbose:
            logger.debug(pformat(f"URL: {url}"))
        try:
            r = session.get(url)
        except requests.exceptions.ConnectionError as e:
            raise ServerError(f"Connection error reaching {url}")

        if not r.ok:
            if r.status_code == 404:
                info = r.json()
                if verbose:
                    logger.debug(pformat(info))
                raise UserNotFound(info["message"])
            else:
                j = r.json()
                msg = j["message"]
                raise ServerError(
                    f"Server response: {r.status_code} {r.reason} ({msg})"
                )


def download_file(file, output_dir):
    """Download a single file to the given output directory. The `file` argument
    is a dict with fields "url" and "filename". `output_dir` is simply the
    directory to put the downloaded file. Can raise ServerError if there is a
    problem with the web request.
    """
    url = file["url"]
    try:
        r = session.get(url, stream=True, cookies=session.cookies.get_dict())
    except requests.exceptions.ConnectionError as e:
        raise ServerError(f"Connection error reaching {url}")

    if not r.ok:
        raise ServerError(f"Server response: {r.status_code} {r.reason}")

    path = Path(output_dir) / file["filename"]

    with open(path, "wb") as handle:
        for data in r.iter_content(chunk_size=CHUNK_SIZE):
            handle.write(data)
    return path


def files(
    instrument: str,
    product: str,
    filters: list[dict[str, str]] | None = None,
    base_url: str = BASE_URL,
    api_version: str = API_VERSION,
    verbose=False,
):
    """Handle retrieving the `/instruments/{instrument}/products/{product}`
    endpoint results. Can raise ServerError if there is a problem with the web
    request. Use `download_file` to download the file(s) returned with routine.
    """
    url = f"{base_url}/{api_version}/instruments/{instrument}/products/{product}"

    if len(filters) > 0:
        url += "?" + "&".join([f"{f}={filters[f]}" for f in filters])

    if verbose:
        logger.debug(f"URL: {url}")

    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        raise ServerError(f"Connection error reaching {url}")

    if not r.ok:
        j = r.json()
        msg = j["message"]
        raise ServerError(f"Server response: {r.status_code} {r.reason} ({msg})")

    j = r.json()
    if verbose:
        logger.debug(pformat(j))

    return j


# Command line interface sub-command handlers


def _about(args):
    """Handle printing the `/about` endpoint results for the command line
    interface.
    """
    try:
        about_response = about(args.base_url, verbose=args.verbose)
        server_version = about_response["version"]
        documentation_url = about_response["documentation"]
        print(
            f"server version: {server_version}, client version: {__version__}"
        )
        print(f"documentation: {documentation_url}")
    except ServerError as e:
        print(e)


def _instruments(args):
    """Handle printing the `/instruments` endpoint results for the command line
    interface.
    """
    try:
        instruments_response = instruments(args.base_url, verbose=args.verbose)
    except ServerError as e:
        print(e)
        return

    print(f"{'ID':8s} {'Instrument name':44s} Dates available")
    print(f"{'-' * 8} {'-' * 44} {'-' * 23}")

    for i in instruments_response:
        instrument = i["id"]
        instrument_name = i["name"]
        start_date = i["start-date"][:10]
        end_date = i["end-date"][:10]

        print(f"{instrument:8s} {instrument_name:44s} {start_date}...{end_date}")


def _products(args):
    """Handle printing the `/instruments/{instrument}/products` endpoint
    results for the command line interface.
    """
    try:
        products_response = products(
            args.instrument, base_url=args.base_url, verbose=args.verbose
        )
    except ServerError as e:
        print(e)
        return

    print(f"{'ID':13s} {'Title':22s} {'Description'}")
    print(f"{'-' * 13} {'-' * 22} {'-' * 55}")
    for p in products_response["products"]:
        title = p["title"]
        product_id = p["id"]
        description = textwrap.wrap(p["description"], width=55)
        if len(description) == 0:
            description = [""]
        for description_line in description:
            print(f"{product_id:13s} {title:22s} {description_line}")
            product_id = ""
            title = ""
            name = ""


def _download_files(
    base_url: str,
    filelist: list,
    output_dir: Path,
    username: str,
    verbose: bool = False,
    quiet: bool = False,
):
    """Download the given files to an output directory. The `files` argument is
    a list of dicts with fields "url" and "filename".
    """
    if not output_dir.is_dir():
        if verbose:
            print(f"creating output path {output_dir}")
        os.makedirs(output_dir)

    try:
        authenticate(username, base_url=base_url, verbose=verbose)
    except UserNotFound as e:
        print(e)
        sys.exit(1)
    except ServerError as e:
        print(e)
        sys.exit(1)

    if quiet:
        iterable_files = filelist
        message = print
    else:
        iterable_files = tqdm.tqdm(filelist)
        message = tqdm.tqdm.write

    n_failed = 0
    for f in iterable_files:
        try:
            filepath = download_file(f, output_dir)
        except ServerError as e:
            message(f"{f['url']} failed")
            n_failed += 1

    if n_failed > 0:
        print(f"{n_failed} failed downloads")


unit_list = list(zip(["B", "KB", "MB", "GB", "TB", "PB"], [0, 0, 1, 2, 2, 2]))


def sizeof_fmt(n_bytes: int) -> str:
    """Human friendly file size"""
    if n_bytes == 0:
        return "0 B"
    if n_bytes >= 1:
        exponent = min(int(math.log(n_bytes, 1024)), len(unit_list) - 1)
        quotient = float(n_bytes) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = "{:.%sf} {}" % (num_decimals)
        return format_string.format(quotient, unit)


def _files(args):
    """Handle printing the `/instruments/{instrument}/products/{product}`
    endpoint results, optionally downloading the files.
    """
    filters = {}

    if args.wave_region is not None:
        filters["wave-region"] = args.wave_region

    if args.obs_plan is not None:
        filters["obs-plan"] = args.obs_plan

    if args.start_date is not None:
        filters["start-date"] = args.start_date

    if args.end_date is not None:
        filters["end-date"] = args.end_date

    if args.carrington_rotation is not None:
        filters["cr"] = args.carrington_rotation

    if args.every is not None:
        filters["every"] = args.every

    try:
        files_response = files(
            args.instrument,
            args.product,
            filters,
            base_url=args.base_url,
            verbose=args.verbose,
        )
    except ServerError as e:
        print(e)
        return

    if args.verbose:
        instrument = files_response["instrument"]
        product = files_response["product"]
        start_date = files_response["start-date"]
        end_date = files_response["end-date"]
        filesize = sizeof_fmt(files_response["total_filesize"])
        print(f"Instrument : {instrument}")
        print(f"Product    : {product}")
        print(f"Start date : {start_date}")
        print(f"End date   : {end_date}")
        print(f"Filesize   : {filesize}")

    filelist = files_response["files"]
    if args.download:
        _download_files(
            args.base_url,
            filelist,
            Path(args.output_dir),
            args.username,
            verbose=args.verbose,
            quiet=args.quiet,
        )
    else:
        if len(filelist) > 0:
            if args.verbose:
                print()
            max_filename_len = max([len(f["filename"]) for f in filelist])
            print(
                f"{'Date/time':20s} {'Instrument':10s} {'Product':13s} {'Filesize':10s} {'Filename'}"
            )
            print(
                f"{'-' * 20} {'-' * 10} {'-' * 13} {'-' * 10} {'-' * max_filename_len}"
            )
            total_filesize = 0
        for f in filelist:
            total_filesize += f["filesize"]
            print(
                f"{f['date-obs']:20s} {f['instrument']:10s} {f['product']:13s} {sizeof_fmt(f['filesize']):>10s} {f['filename']}"
            )
        if len(filelist) > 1:
            print(
                f"{'-' * 20} {'-' * 10} {'-' * 13} {'-' * 10} {'-' * max_filename_len}"
            )
            n_files = f"{len(filelist)} files"
            print(f"{n_files:45s} {sizeof_fmt(total_filesize):>10s} {''}")


def _print_help(args):
    """Print the usage help for the command-line utility."""
    args.parser.print_help()


def main():
    """Entry point for MLSO API command-line utility."""
    name = f"MLSO API command line interface (mlso-api-client {__version__})"
    parser = argparse.ArgumentParser(description=name)

    parser.add_argument("-v", "--version", action="version", version=name)

    # show help if no sub-command given
    parser.set_defaults(func=_print_help, parser=parser)

    parser.add_argument(
        "-u", "--base-url", help="base URL for MLSO API", default=BASE_URL
    )
    parser.add_argument("--verbose", help="output warnings", action="store_true")
    parser.add_argument(
        "-q", "--quiet", help="surpress informational messages", action="store_true"
    )

    subparsers = parser.add_subparsers(help="sub-command help")

    instruments_parser = subparsers.add_parser("instruments", help="MLSO instruments")
    instruments_parser.set_defaults(func=_instruments, parser=instruments_parser)

    products_parser = subparsers.add_parser("products", help="MLSO instruments")
    products_parser.add_argument("-i", "--instrument", help="instrument", default=None)
    products_parser.set_defaults(func=_products, parser=products_parser)

    files_parser = subparsers.add_parser("files", help="MLSO data files")
    files_parser.add_argument("-i", "--instrument", help="instrument", default=None)
    files_parser.add_argument("-p", "--product", help="product", default=None)
    files_parser.add_argument(
        "--wave-region", help="wave region, e.g., 1074, 1079, etc.", default=None
    )
    files_parser.add_argument(
        "--obs-plan", help="observing plan: synoptic or waves", default=None
    )
    files_parser.add_argument("-s", "--start-date", help="start date", default=None)
    files_parser.add_argument("-e", "--end-date", help="end date", default=None)
    files_parser.add_argument(
        "-c", "--carrington-rotation", help="Carrington Rotation number", default=None
    )
    files_parser.add_argument(
        "--every", help="time to choose 1 file from", default=None
    )
    files_parser.add_argument(
        "-d", "--download", help="download the displayed files", action="store_true"
    )
    files_parser.add_argument(
        "-u", "--username", help="email already registered at HAO website", default=None
    )
    files_parser.add_argument(
        "-o", "--output-dir", help="output directory for downloaded files", default="."
    )
    files_parser.set_defaults(func=_files, parser=files_parser)

    # parse args and call appropriate sub-command
    args = parser.parse_args()

    if args.verbose:
        _about(args)
        print()

    if parser.get_default("func"):
        try:
            args.func(args)
        except KeyboardInterrupt:
            print()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
