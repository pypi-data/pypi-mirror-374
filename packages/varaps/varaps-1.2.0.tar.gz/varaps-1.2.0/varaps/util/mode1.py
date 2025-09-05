# %%
import sys
import time
import os

sys.path.append("./")
from varaps.util.read_bam_file import read_bam_file
from varaps.util.get_mutations import get_all_mutations
from varaps.util.refseq import get_reference

import numpy as np
import pandas as pd


def analyze_file_mode1(file_name, ref_path, filter_per, filter_num, output_dir):
    """
    Analyze a single file for mutations and save the results.

    Args:
        file_name (str): The name of the BAM/Cram file to analyze.
        REFSEQ (str): The reference sequence.
        filter_per (float): The percentage of reads that must contain a mutation to be kept.
        filter_num (int): The number of reads that must contain a mutation to be kept.
        output_dir (str): The directory to save the output files.
    """
    print("Output directory: ", output_dir)
    print("Analyzing: ", file_name)
    print("Starting...")
    REFSEQ = get_reference(ref_path)
    readInfoDf = read_bam_file(file_name)

    # print("readInfoDf.shape: ", readInfoDf.shape)
    # print("*-* time for read_bam_file: ", time.time() - startTime)
    # get mutations
    (
        results_relative_mutation_index,
        results_ablolute_positions,
        mutations_kept,
    ) = get_all_mutations(readInfoDf, REFSEQ, filter_per, filter_num)
    # print("*-* time for get_all_mutations: ", time.time() - startTime)
    # remove invalid mutations (mutations containing 'N' or '=')
    # need to be coded more flexibly if in the future more unexpected errors occur.
    startTime = time.time()
    rand_id = np.random.randint(0, 10000000)

    df_mutations_kept = pd.DataFrame(mutations_kept, columns=["Mutations"])

    # export results

    results_ablolute_positions[["startIdx_0Based", "endIdx_0Based", "muts"]].to_csv(
        os.path.join(
            output_dir,
            f"Xsparse_{file_name.split('/')[-1]}_filter_{filter_per}_{filter_num}_{rand_id}.csv",
        ),
        index=False,
    )
    results_ablolute_positions["Counts"].to_csv(
        os.path.join(
            output_dir,
            f"Wsparse_{file_name.split('/')[-1]}_filter_{filter_per}_{filter_num}_{rand_id}.csv",
        ),
        index=False,
    )
    df_mutations_kept.to_csv(
        os.path.join(
            output_dir,
            f"mutations_index_{file_name.split('/')[-1]}_filter_{filter_per}_{filter_num}_{rand_id}.csv",
        ),
        index=False,
    )


# %%
