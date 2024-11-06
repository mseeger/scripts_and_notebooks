# Script can be used to query address from location (longitude, latitude) en
# bulk from the `Nominatim` geolocation service.
#
# Note: The term of use strongly discourage bulk querying, so running this is
# probably not OK.
#
# https://www.geoapify.com/reverse-geocoding-api
# This allows for 3000 queries per day free of charge.
#
# Still, this code is useful for chunking up work and processing in parallel
# more generally.
from typing import Optional, Tuple
from pathlib import Path
from argparse import ArgumentParser
from filelock import SoftFileLock
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm

import pandas as pd
import numpy as np


def query_address_from_location(
    chunk_df: pd.DataFrame, user_agent: str, use_tqdm: bool
) -> pd.DataFrame:
    """
    For all rows of `chunk_df`, with columns "unique_key" and "location", query
    the address. We use a rate limiter, which delays for 1 sec between requests.

    :param chunk_df: Input dataframe
    :param user_agent: Name for querying `Nominatim`
    :param use_tqdm: Use `tqdm` for progress?
    :return: Copy of `chunk_df` with additional column "address", as queried
    """
    geolocator = Nominatim(user_agent=user_agent)
    # Argument `loc` is a string of form "(<latitude>, <longitude>)", we just
    # strip off the parentheses.
    def query_func_int(loc):
        result = geolocator.reverse(loc.strip()[1:-1])
        return result.address if result is not None else np.nan

    # We use a rate limiter (as recommended in the GeoPy docs).
    query_func = RateLimiter(query_func_int, min_delay_seconds=1)
    # The result dataframe contains the unique key, location, and queried address
    result_df = chunk_df.copy()
    if use_tqdm:
        tqdm.pandas()  # Show progress
        result_df["address"] = chunk_df["location"].progress_apply(query_func)
    else:
        result_df["address"] = chunk_df["location"].apply(query_func)
    return result_df


def determine_next_chunk(chunk_fname: Path, num_chunks: int) -> Optional[int]:
    """
    We glob filenames of the form `chunk_fname + "*.started"` and find the
    smallest integer in `range(num_chunks)` which does not appear as "*".

    :param chunk_fname: Prefix of chunk filenames
    :param num_chunks: Total number of chunks
    :return: Number for next chunk to process, or `None` (no more chunks)
    """
    chunk_names = [
        path.stem
        for path in chunk_fname.parent.glob(chunk_fname.name + "*.started")
    ]
    if len(chunk_names) >= num_chunks:
        return None
    prefix_len = len(chunk_fname.name)
    chunk_nums = set(int(fname[prefix_len:]) for fname in chunk_names)
    free_chunks = set(range(num_chunks)).difference(chunk_nums)
    if free_chunks:
        return min(free_chunks)
    else:
        return None


def number_of_chunks(chunk_fname: Path) -> int:
    return len(list(chunk_fname.parent.glob(chunk_fname.name + "*.csv")))


def next_chunk_iterator(
    chunk_fname: Path, num_chunks: int
) -> Tuple[pd.DataFrame, int]:
    """
    Generator function. Reads the next chunk to be processed.
    If a chunk has filename "XXX.csv", we use an additional file "XXX.started",
    which is written here, before returning the chunk dataframe.
    The next chunk is identified by a glob for all "XXX.started" files, then
    using the smallest number not already featuring in these names.

    :param chunk_fname: Prefix of chunk filenames
    :param num_chunks: Total number of chunks
    :return: Dataframe for next chunk, or `None` if no chunk left
    """
    while True:
        # Acquire a lock on the path (kept until the ".started" file is written)
        lock = SoftFileLock(str(chunk_fname.parent / "lock"))
        with lock.acquire(timeout=120, poll_interval=1):
            # While we have the lock, we determine the next chunk and claim it
            # by writing the "XXX.started" file. Once this is done, the lock
            # can be released.
            next_chunk_num = determine_next_chunk(chunk_fname, num_chunks)
            if next_chunk_num is None:
                break  # Leave iterator loop
            fname = str(chunk_fname) + f"{next_chunk_num}.started"
            with open(fname, "w") as fp:
                fp.write(f"{next_chunk_num}\n")
        # Read and return chunk dataframe
        fname = str(chunk_fname) + f"{next_chunk_num}.csv"
        print(f"Next chunk to process: {fname}")
        chunk_df = pd.read_csv(fname)
        yield chunk_df, next_chunk_num


if __name__ == "__main__":
    parser = ArgumentParser()
    default_path = Path.home() / "datasets" / "tabular_practice"
    parser.add_argument("--user_agent", type=str, required=True)
    parser.add_argument("--use_tqdm", action="store_true")
    parser.add_argument(
        "--chunk_fname",
        type=str,
        default=str(default_path / "chunks" / "nypd_mvc_2018_location_chunk"),
    )
    parser.add_argument(
        "--result_fname",
        type=str,
        default=str(default_path / "chunks" / "nypd_mvc_2018_location_address_chunk"),
    )
    args = parser.parse_args()

    chunk_fname = Path(args.chunk_fname)
    num_chunks = number_of_chunks(chunk_fname)
    print(f"Total number of chunks: {num_chunks}")
    # Iterate over chunks until no more are available
    for chunk_df, next_chunk_num in next_chunk_iterator(chunk_fname, num_chunks):
        result_df = query_address_from_location(
            chunk_df, user_agent=args.user_agent, use_tqdm=args.use_tqdm,
        )
        fname = args.result_fname + f"{next_chunk_num}.csv"
        result_df.to_csv(fname, index=False)

    print("No more chunks available. Terminating.")
