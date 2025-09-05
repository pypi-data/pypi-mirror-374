import pysam
import numpy as np
import pandas as pd
import gc
from tqdm import tqdm


def read_bam_file(path_to_file):
    """
    convert a bam/cram file into a dataframe

    INPUT:
    path_to_file: string, path to the bam/cram file to be converted.

    OUTPUT:
    a dataframe containing 4 columns:
    0-based start indices, CIGAR strings, sequence strings and the counts of apperance of a read.
    """
    read_mode = "rb" if path_to_file.endswith(".bam") else "rc" if path_to_file.endswith(".cram") else "r" if path_to_file.endswith(".sam") else None
    pysam.index(path_to_file)

    bam = pysam.AlignmentFile(path_to_file, read_mode)
    contig, nbReads = np.array(bam.get_index_statistics()[0])[[0, -1]]
    nbReads = int(nbReads)
    # nbReads = int(bam.count())
    print("*number of reads: ", nbReads)

    # Build the dataframe **before** closing the BAM handle
    df = read_to_df(bam, contig, nbReads)

    # Explicitly close the AlignmentFile to release underlying C-level resources
    bam.close()

    # Help the garbage collector reclaim memory that may still be referenced in C extensions
    gc.collect()

    return df


def read_to_df(bam, contig, nbReads):
    """
    Convert a BAM/CRAM AlignmentFile into a tidy pandas DataFrame.

    Steps
    -----
    1. Collect (qname, startIdx_0Based, CIGAR, Sequence) for every read.
    2. Vectorised counting with pandas → df['Counts'].
    """
    # Step 1 – harvest the data in a single, tight comprehension.
    records = [
        (
            aln.query_name,
            aln.reference_start,  # already 0-based
            aln.cigarstring,
            aln.query_sequence,
        )
        for aln in tqdm(
            bam.fetch(contig),
            total=nbReads,
            desc="Step 1/3 - reading bam/cram file",
        )
    ]
    # print(f"    ⏱️  Time to harvest records: {time.time() - harvest_start_time:.2f} seconds")

    # Build the DataFrame in one shot (much faster than incremental appends).
    df = pd.DataFrame.from_records(
        records,
        columns=["qname", "startIdx_0Based", "CIGAR", "Sequence"],
    )
    # print(f"    ⏱️  Time to build DataFrame: {time.time() - df_start_time:.2f} seconds")

    # Memory optimization: Use compact dtypes and categorical strings
    df["startIdx_0Based"] = df["startIdx_0Based"].astype(np.int32)
    df["qname"] = df["qname"].astype("category")
    df["CIGAR"] = df["CIGAR"].astype("category")
    df["Sequence"] = df["Sequence"].astype("category")

    # Keep only reads with a well-formed CIGAR (starts with a digit) and drop rows
    # where the CIGAR string is missing (pysam can yield `None`).
    mask_cigar_starts_with_digit = df["CIGAR"].str[0].str.isdigit().fillna(False)
    df = df[mask_cigar_starts_with_digit]
    # print(f"    ⏱️  Time to filter CIGAR: {time.time() - cigar_start_time:.2f} seconds")

    # Step 2 – count identical (startIdx_0Based, Sequence) pairs in C speed.
    df["Counts"] = df.groupby(["startIdx_0Based", "Sequence"])["Sequence"].transform("size").astype(np.int32)
    # print(f"    ⏱️  Time to count sequences: {time.time() - count_start_time:.2f} seconds")

    # Clean up intermediate variables
    del records
    gc.collect()

    return df


def humansize(nbytes):
    """
    Convert a number of bytes to a human-readable string.

    INPUT:
    nbytes: int, number of bytes
    OUTPUT:
    a string containing the number of bytes in a human-readable format.
    """
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.0
        i += 1
    f = ("%.2f" % nbytes).rstrip("0").rstrip(".")
    return "%s %s" % (f, suffixes[i])
