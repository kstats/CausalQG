import argparse

import numpy as np
import pandas as pd


def sample_ce(in_filename, out_filename, num_samples, patterns_path):
    """
    Given a CSV of cause/effects and the PatternID that was used to extract them, randomly sample
    rows stratified by typology of the patterns.

    Inputs:
        - in_filename: path to input file csv contain rows for PatternID, Text, Cause, Effect
        - out_filename: path to output file which will contain samples
        - num_samples: number of samples to return
        - patterns_path: path to csv containing table of patterns to match PatternID to typology
    Outputs:
        - CSV at out_filename containing samples
    """
    patterns = pd.read_csv(patterns_path)

    ce = pd.read_csv(in_filename)
    ce = ce[["PatternID", "Text", "Cause", "Effect"]]
    ce = pd.merge(ce, patterns, left_on="PatternID", right_on="pid")
    ce.groupby(["table", "line", "col"]).size()

    # ensure there is min(size(category), 2) sample from each category
    small_sample_init = ce.groupby(["table", "line", "col"]).apply(
        lambda x: x.sample(min(len(x), 2))
    )

    ce_rest = pd.concat([ce, small_sample_init, small_sample_init]).drop_duplicates(
        keep=False
    )

    small_sample = (
        ce_rest.groupby(["table", "line", "col"])
        .apply(
            lambda x: x.sample(
                int(
                    np.rint(
                        (num_samples - len(small_sample_init)) * len(x) / len(ce_rest)
                    )
                )
            )
        )
        .sample(frac=1)
    )

    small_sample = small_sample.append(small_sample_init, ignore_index=False)

    small_sample = small_sample.sample(frac=1)[["Text", "Cause", "Effect"]]
    small_sample = small_sample.reset_index(level="line", drop=True)
    small_sample = small_sample.reset_index(level="col", drop=True)
    small_sample = small_sample.reset_index(level="table")

    small_sample.to_csv(out_filename, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to generate n stratified samples based on typology"
    )
    parser.add_argument("--infile", type=str, help="path to ce input file")
    parser.add_argument("--outfile", type=str, help="path to ce output file")
    parser.add_argument(
        "--patterns_path",
        type=str,
        default="CSVs/patterns_typology.csv",
        help="path to file of patterns",
    )
    parser.add_argument("--num_samples", type=int, help="number of samples")
    args = parser.parse_args()
    if args.infile and args.outfile and args.num_samples:
        sample_ce(args.infile, args.outfile, args.num_samples, args.patterns_path)
