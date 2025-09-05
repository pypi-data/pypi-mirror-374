import pysam


def get_reference(seq_path):
    REFSEQ = ""
    with pysam.FastxFile(seq_path) as fh:
        for entry in fh:
            REFSEQ = str(entry.sequence)
    return REFSEQ
