# %%
from cigar import Cigar
from tqdm import tqdm
import gc
from array import array

# import pandas as pd
import numpy as np
import pandas as pd


def get_mutations(startPos, cigarStr, seq, ref):
    """
    returns a list of mutations detected in the given read.

    INPUTS:
    startPos: positive integer; 0-based starting position in the reference sequence of the read.
    cigarStr: CIGAR string of the read's alignment.
    seq: string; the read sequence.
    ref: string; the refernce to which the read is compared to find mutations (substitutions, deletions and insertions)

    OUTPUTS:
    mutations: a set of strings containing all mutations found. Notation examples:
    A100T: in 1-based indexation, the 100th letter of the reference sequence is A but the given read is substituted by T;
    AC100A: in 1-based indexation, the 100th and the 101st letters of the reference sequence are AC but the given read has a deletion at the 101st position;
    A100AC: in 1-based indexation, the 100th letter of the reference sequence is A but the given read has an insertion at the 101st position, the letter inserted is C;

    an integer indicating the last 0-based position of the reference sequence covered by the given read.
    """

    # to be returned
    mutations = set()

    shift = 0  # lag between the starting point of the read in the REF seq and the real valid starting point
    qryPos = 0  # index that goes through the QUERY seq
    cigars = list(Cigar(cigarStr).items())

    for cigar in cigars:
        # flag situations and update qryPos and/or shift

        ## D := deletion, N := skipped [consumes Q: no; consumes Ref: yes]
        ## => only the shift moves forward, qry index stays put
        if cigar[1] in ["D", "N"]:
            # in case of deletion
            if cigar[1] == "D":
                mutations.add(ref[startPos + shift - 1 : startPos + shift + cigar[0]] + str(startPos + shift) + ref[startPos + shift - 1])
            qryPos += 0
            shift += cigar[0]

        ## H := hard clipping, P := padding [consumes Q: no; consumes Ref: no]
        ## => do nothing and go to the next cigar WITHOUT moving any positions
        elif cigar[1] in ["H", "P"]:
            continue

        ## I := insertion, S:= soft clip [consumes Q: yes; consumes Ref: no]
        ## => only the qry index moves forward, shift stays put
        elif cigar[1] in ["I", "S"]:
            # in case of insertion
            if cigar[1] == "I":
                mutations.add(ref[startPos + shift - 1] + str(startPos + shift) + ref[startPos + shift - 1] + seq[qryPos : qryPos + cigar[0]])
            qryPos += cigar[0]
            shift += 0

        else:
            if cigar[1] in ["M", "X"]:
                mutations = mutations.union(
                    {
                        ref[min(startPos + shift + i, len(ref) - 1)] + str(startPos + shift + i + 1) + seq[min(qryPos + i, len(seq) - 1)]
                        for i in range(cigar[0])
                        if ref[min(startPos + shift + i, len(ref) - 1)] != seq[min(qryPos + i, len(seq) - 1)]
                    }
                )
            qryPos += cigar[0]
            shift += cigar[0]

    return mutations, startPos + shift


def get_mutations_fast(start_pos_0based: int, cigar_str: str, seq: str, ref: str):
    """
    Faster mutation extractor that avoids string/set allocations.
    Returns:
      - mutations_keys: list of compact mutation keys
          Substitution: ('S', pos0, alt_char)
          Insertion:    ('I', pos0, inserted_str)
          Deletion:     ('D', pos0, del_len)
      - end_idx_0based: int, last 0-based position of the reference covered by the read
    Note: Keys are chosen so we can lazily build the canonical mutation string later.
    """
    mutations_keys = []

    shift = 0  # position on ref (0-based) relative to start_pos_0based
    qry_pos = 0  # position on query sequence

    # Inline CIGAR parser: read number then op
    n = 0
    length = 0
    ref_len = len(ref)
    seq_len = len(seq)
    for ch in cigar_str:
        if ch.isdigit():
            length = length * 10 + (ord(ch) - 48)
            continue
        # ch is an op, length is the number parsed before it
        op_len = length
        length = 0

        if ch in ("D", "N"):
            if ch == "D" and op_len > 0:
                # Deletion at current ref position
                pos0 = start_pos_0based + shift
                mutations_keys.append(("D", pos0, op_len))
            shift += op_len
            # qry_pos unchanged

        elif ch in ("H", "P"):
            # no movement on either
            continue

        elif ch in ("I", "S"):
            if ch == "I" and op_len > 0:
                # Insertion occurs after pos0; inserted string from query
                # Clamp boundaries defensively
                q_end = qry_pos + op_len
                if q_end > seq_len:
                    q_end = seq_len
                inserted = seq[qry_pos:q_end]
                pos0 = start_pos_0based + shift
                mutations_keys.append(("I", pos0, inserted))
            qry_pos += op_len
            # shift unchanged

        else:
            # 'M', 'X', '=' treated as alignment that consumes both
            # We emit substitutions only where bases differ
            op = ch
            if op_len > 0:
                r_start = start_pos_0based + shift
                q_start = qry_pos
                # iterate and compare
                # Clamp to avoid OOB; mimic original using min(..., len-1)
                for i in range(op_len):
                    r_idx = r_start + i
                    q_idx = q_start + i
                    if r_idx >= ref_len:
                        r_idx = ref_len - 1
                    if q_idx >= seq_len:
                        q_idx = seq_len - 1
                    if ref[r_idx] != seq[q_idx]:
                        mutations_keys.append(("S", r_idx, seq[q_idx]))
                qry_pos += op_len
                shift += op_len

    end_idx = start_pos_0based + shift
    return mutations_keys, end_idx


def extract_positions(mut_str):
    """
    returns the position (extract digits from a string) in a mutation string
    """
    return int("".join([i for i in mut_str if i.isdigit()]))


def check_if_in_interval(num, interval):
    """
    returns True if position is in the interval, False otherwise
    """
    return num >= interval[0] and num <= interval[1]


def weighted_concatenate(lists, weight):
    """
    returns a numpy array of mutations found in lists repeated weight time (needed to calculate excat number of occurence of each mutation).
    CAREFUL: weight here is not the count of each read but the count of "counts of each read"
    """
    if weight > 1:
        return np.repeat(np.concatenate(lists), weight)
    if len(lists) == 1:
        return np.array(lists[0])
    return np.concatenate(lists)


def coverage_profile(readInfoDF, nbPositions):
    """
    returns a dict with the number of reads covering each position.
    OUTPUT:
    a dict with keys = positions and values = number of reads covering that position
    """
    readInfoDF["Counts_intervals"] = readInfoDF.groupby(["startIdx_0Based", "endIdx_0Based"])["Counts"].transform("sum")
    temp = readInfoDF.drop_duplicates(subset=["startIdx_0Based", "endIdx_0Based", "Counts_intervals"])
    coverage = {pos: 0 for pos in range(nbPositions + 1)}
    for _, row in tqdm(temp.iterrows(), total=temp.shape[0], desc="Step 3/3 - Creat coverage profile"):
        for pos in range(row["startIdx_0Based"], row["endIdx_0Based"]):
            coverage[pos] += row["Counts_intervals"]
    return coverage


def humansize(nbytes):
    """
    returns a human-readable string representation of a number of bytes.

    INPUTS:
    nbytes: integer; number of bytes
    OUTPUTS:
    a string with the number of bytes in a human-readable format
    """
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.0
        i += 1
    f = ("%.2f" % nbytes).rstrip("0").rstrip(".")
    return "%s %s" % (f, suffixes[i])


def get_all_mutations(readInfoDf, refseq, filter_per=0.01, filter_num=5):
    """
    Get mutations for each read and concatenate them together.

    INPUTS:
    readInfoDf: pandas dataframe; contains information about each read
    refseq: string; reference sequence
    filter_per: float; <Filter par>percentage of reads that must contain a mutation to be kept as a mutation
    filter_num: integer; <Filter par> number of reads that must contain a mutation to be kept as a mutation

    OUTPUTS:
    1. results_relative_mutation_index:a pandas dataframe with the following columns:
        - "startIdx_mutations_Based": integer; first mutaions indice[in mutations_kept] in the read
        - "endIdx_mutations_Based": integer; last mutaions indice[in mutations_kept] in the read
        - "muts": string; mutations found in the read separated by a comma
        - "Counts": integer; number of times the read was found in the bam file
    2. results_ablolute_positions: a pandas dataframe with the following columns:
        - "startIdx_0Based": integer; start position of the read in the reference sequence
        - "endIdx_0Based": integer; end position of the read in the reference sequence
        - "muts": string; mutations found in the read separated by a comma
        - "Counts": integer; number of times the read was found in the bam file

    3. mutations_kept: a list of mutations that were kept after filtering, ordered by position in the reference sequence
    """

    # Step 2/3 - get mutations for each read (memory optimized)

    # Initialize compact structures
    # Map mutation string to a compact integer ID
    mut_str_to_id = {}
    id_to_mut_str = []  # index -> mutation string
    id_to_pos = []  # index -> position (int)
    counts_by_id = []  # index -> total count across reads

    # Per-read mutations stored compactly
    flat_mut_ids = array("I")  # all mutation IDs concatenated
    read_offsets = array("Q")  # offset per read into flat_mut_ids
    read_offsets.append(0)

    end_indices = []
    cc = 0
    # Process reads directly with iterator to avoid storing all mutations in memory
    for row in tqdm(readInfoDf.itertuples(index=False, name=None), total=len(readInfoDf), desc="Step 2/3 - get_all_mutations for each read"):
        cc += 1
        qname, start_idx, cigar, sequence, counts = row

        # Get mutations for this read
        mut_keys, end_idx = get_mutations_fast(start_idx, cigar, sequence, refseq)

        # Store end index
        end_indices.append(end_idx)

        # Map mutation strings to compact IDs, count immediately, and append IDs for this read
        per_read_ids = []
        for key in mut_keys:
            mut_id = mut_str_to_id.get(key)
            if mut_id is None:
                mut_id = len(id_to_mut_str)
                mut_str_to_id[key] = mut_id
                # Build canonical mutation string lazily based on key
                kind = key[0]
                if kind == "S":
                    _, pos0, alt = key
                    mut_str = refseq[min(pos0, len(refseq) - 1)] + str(pos0 + 1) + alt
                    pos_for_filter = pos0 + 1
                elif kind == "I":
                    _, pos0, inserted = key
                    base_prev = refseq[pos0 - 1] if pos0 - 1 >= 0 else refseq[-1]
                    mut_str = base_prev + str(pos0) + base_prev + inserted
                    pos_for_filter = pos0
                else:  # 'D'
                    _, pos0, del_len = key
                    start = pos0 - 1
                    if start < 0:
                        start = -1  # mimic original negative index behavior
                    end = pos0 + del_len
                    end = min(end, len(refseq))
                    mut_str = refseq[start:end] + str(pos0) + refseq[start]
                    pos_for_filter = pos0
                id_to_mut_str.append(mut_str)
                id_to_pos.append(pos_for_filter)
                counts_by_id.append(0)
            counts_by_id[mut_id] += counts
            per_read_ids.append(mut_id)

        # per_read_ids are unique already (mutations is a set). Append to flat storage
        flat_mut_ids.extend(per_read_ids)
        read_offsets.append(len(flat_mut_ids))

    # Update the dataframe with end indices
    readInfoDf["endIdx_0Based"] = end_indices

    # Step 3/3 - Create coverage profile
    coverage = coverage_profile(readInfoDf, len(refseq))
    # print(f"Nb of all mutation detected in the bam file: {len(all_count)}")
    # print("Filter mutations...")

    # Filter mutations based on coverage and thresholds (operate on IDs)
    kept_ids = []
    for mut_id, cnt in enumerate(counts_by_id):
        pos = id_to_pos[mut_id]
        if cnt >= max(coverage.get(pos, 0) * filter_per, filter_num):
            kept_ids.append(mut_id)
    # Clean mutations (remove N and =)
    kept_ids = [mid for mid in kept_ids if ("N" not in id_to_mut_str[mid]) and ("=" not in id_to_mut_str[mid])]
    # Sort kept mutations by genomic position and build mapping oldID -> newIndex
    sorted_kept_ids = sorted(kept_ids, key=lambda mid: id_to_pos[mid])
    kept_id_to_new_index = np.full(len(id_to_mut_str), -1, dtype=np.int32)
    for new_idx, mid in enumerate(sorted_kept_ids):
        kept_id_to_new_index[mid] = new_idx
    mutations_kept = [id_to_mut_str[mid] for mid in sorted_kept_ids]

    # Build results dataframe
    results = pd.DataFrame(
        {
            "startIdx_0Based": readInfoDf["startIdx_0Based"].values,
        }
    )
    results["endIdx_0Based"] = readInfoDf["endIdx_0Based"].values
    results["Counts"] = readInfoDf["Counts"].values
    # results["qname"] = readInfoDf["qname"].values
    # Optimize groupby on qname by using categorical dtype
    # results["qname"] = results["qname"].astype("category")

    # Drop bulky columns early to save memory
    readInfoDf.drop(columns=["Sequence", "CIGAR"], inplace=True)

    # Build per-read filtered mutation indices using compact buffers
    filtred_mut_kept = []
    num_reads = len(read_offsets) - 1
    for i in range(num_reads):
        start = read_offsets[i]
        end = read_offsets[i + 1]
        # Map IDs to kept indices; discard non-kept (-1)
        idxs = [kept_id_to_new_index[mid] for mid in flat_mut_ids[start:end] if kept_id_to_new_index[mid] != -1]
        if idxs:
            idxs.sort()
            filtred_mut_kept.append(tuple(idxs))
        else:
            filtred_mut_kept.append(tuple())

    # print(f"Memory usage of results DataFrame: {asizeof.asizeof(results) / (1024 ** 2):.6f} MB")
    # print(f"Memory usage of id_to_mut_str: {asizeof.asizeof(id_to_mut_str) / (1024 ** 2):.6f} MB")
    # print(f"Memory usage of id_to_pos: {asizeof.asizeof(id_to_pos) / (1024 ** 2):.6f} MB")
    # print(f"Memory usage of counts_by_id: {asizeof.asizeof(counts_by_id) / (1024 ** 2):.6f} MB")
    # print(f"Memory usage of kept_id_to_new_index: {asizeof.asizeof(kept_id_to_new_index) / (1024 ** 2):.6f} MB")
    # print(f"Memory usage of mutations_kept: {asizeof.asizeof(mutations_kept) / (1024 ** 2):.6f} MB")
    # print(f"22 Memory usage of readInfoDf: {asizeof.asizeof(readInfoDf) / (1024 ** 2):.6f} MB")
    # print(f'Memory usage of readInfoDf["startIdx_0Based"].values: {asizeof.asizeof(readInfoDf["startIdx_0Based"].values) / (1024 ** 2):.6f} MB')
    # print(f'Memory usage of readInfoDf["endIdx_0Based"].values: {asizeof.asizeof(readInfoDf["endIdx_0Based"].values) / (1024 ** 2):.6f} MB')
    # print(f'Memory usage of readInfoDf["Counts"].values: {asizeof.asizeof(readInfoDf["Counts"].values) / (1024 ** 2):.6f} MB')
    # print(f'Memory usage of readInfoDf["qname"].values: {asizeof.asizeof(readInfoDf["qname"].values) / (1024 ** 2):.6f} MB')
    results["muts"] = filtred_mut_kept
    # print(f"22 Memory usage of results DataFrame: {asizeof.asizeof(results) / (1024 ** 2):.6f} MB")

    # Clean up large temporary structures to free memory
    del flat_mut_ids, read_offsets, kept_id_to_new_index
    gc.collect()

    # Pair end read merge
    # Aggregate only necessary columns and disable sorting for performance
    cols_to_agg = ["startIdx_0Based", "endIdx_0Based", "muts"]
    # grouped_results = results.groupby("qname", sort=False, observed=True, as_index=False)[cols_to_agg].agg(tuple)
    # remove duplicates based on start and end mutatios's position in the reference sequence
    grouped_results = results
    grouped_results["Counts"] = 1

    # Free the original results DataFrame
    gc.collect()
    results_ablolute_positions = (
        grouped_results.groupby(["startIdx_0Based", "endIdx_0Based", "muts"]).agg({"Counts": "sum"})
        # .agg({"Counts": "sum", "qname": lambda x: tuple(x)})
        .reset_index()
    )
    # Free grouped_results and other temporary variables
    del grouped_results
    del results
    gc.collect()

    # Update start and end index to be relative to mutations, not absulute to the reference
    # results_relative_mutation_index = results_ablolute_positions.copy()
    # all_positions = [v[0] for v in sorted_mutation_position_dict.values()]
    # results_relative_mutation_index[
    #     "startIdx_mutations_Based"
    # ] = results_relative_mutation_index["startIdx_0Based"].apply(
    #     lambda x: min(len(mutations_kept) - 1, bisect.bisect_left(all_positions, x + 1))
    # )
    # results_relative_mutation_index[
    #     "endIdx_mutations_Based"
    # ] = results_relative_mutation_index["endIdx_0Based"].apply(
    #     lambda x: bisect.bisect_right(all_positions, x + 1)
    # )
    # # remove duplicates based on start and end mutatio index
    # # print("time to create dataframe:", time.time() - startTime)
    # startTime = time.time()
    # results_relative_mutation_index = (
    #     results_relative_mutation_index.groupby(
    #         ["startIdx_mutations_Based", "endIdx_mutations_Based", "muts"]
    #     )
    #     .agg({"Counts": "sum"})
    #     .reset_index()
    # )
    # # print("time to groupby:", time.time() - startTime)
    # results_relative_mutation_index["muts"] = (
    #     results_relative_mutation_index["muts"].astype(str).str.strip("(|)")
    # )
    # results_ablolute_positions["muts"] = (
    #     results_ablolute_positions["muts"].astype(str).str.strip("(|)")
    # )

    # results_ablolute_positions["qname"] = results_ablolute_positions["qname"].astype(str).str.strip("(|)")

    # Memory optimization: Use categorical encoding for muts column to save memory
    # Since there are typically many fewer unique mutation patterns than total reads
    # results_ablolute_positions["muts"] = results_ablolute_positions["muts"].astype("category")
    # Final cleanup of large temporary variables
    del mut_str_to_id, id_to_pos, counts_by_id
    del end_indices, filtred_mut_kept
    gc.collect()

    results_ablolute_positions["muts"] = results_ablolute_positions["muts"].apply(
        lambda x: f"{x[0]}," if isinstance(x, tuple) and len(x) == 1 else ", ".join(map(str, x)) if isinstance(x, tuple) else str(x)
    )
    return None, results_ablolute_positions, mutations_kept


# %%
