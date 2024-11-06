# Used together with `locserv_process_chunks.py` in order to  query address
# from location (longitude, latitude) en bulk from the `Nominatim` geolocation
# service.
#
# Note: The term of use strongly discourage bulk querying, so running this is
# probably not OK.
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd
import numpy as np


def create_chunks(full_df: pd.DataFrame, chunk_size: int):
    bool_location = full_df["location"].notnull()
    bool_borough = full_df["borough"].isnull()
    bool_off = full_df["off_street"].isnull()
    row_ind = bool_location & (bool_borough | bool_off)
    selected_df = full_df.loc[row_ind, ["unique_key", "location"]]
    num_rows = selected_df.shape[0]
    print(f"Writing {int(np.ceil(num_rows / chunk_size))} chunks...")
    chunks = []
    for start in range(0, num_rows, chunk_size):
        end = min(start + chunk_size, num_rows)
        chunks.append(selected_df.iloc[start:end])
    return chunks


if __name__ == "__main__":
    parser = ArgumentParser()
    default_path = Path.home() / "datasets" / "tabular_practice"
    parser.add_argument(
        "--input_fname",
        type=str,
        default=str(default_path / "nypd_mvc_2018.csv"),
    )
    parser.add_argument(
        "--chunk_fname",
        type=str,
        default=str(default_path / "chunks" / "nypd_mvc_2018_location_chunk"),
    )
    parser.add_argument("--chunk_size", type=int, default=600)
    args = parser.parse_args()

    full_df = pd.read_csv(args.input_fname)
    chunks = create_chunks(full_df, chunk_size=args.chunk_size)

    Path(args.chunk_fname).parent.mkdir(exist_ok=True)
    for id, chunk in enumerate(chunks):
        fname = args.chunk_fname + f"{id}.csv"
        chunk.to_csv(fname, index=False)
