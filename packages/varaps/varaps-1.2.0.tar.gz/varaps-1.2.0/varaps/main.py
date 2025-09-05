import sys
import time
import os
import argparse
import numpy as np
from typing import List, Optional

sys.path.append("./")

from varaps.util import mode1, mode2, generate_M, downsampling


def get_input_with_default(prompt: str, default: str) -> str:
    user_input = input(f"{prompt} (default: {default}): ")
    return user_input.strip() if user_input.strip() != "" else default


def humansize(nbytes: int) -> str:
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.0
        i += 1
    f = f"{nbytes:.2f}".rstrip("0").rstrip(".")
    return f"{f} {suffixes[i]}"


def get_files(fpath: str, mode: int) -> Optional[List[str]]:
    file_extension = (".bam", ".cram") if mode in [1, 3, 5] else ".csv"
    prefix = "" if mode in [1, 3, 5] else "Xsparse_"
    files_to_analyse = []

    if os.path.isfile(fpath) and fpath.endswith(file_extension):
        files_to_analyse.append(fpath)
    elif os.path.isdir(fpath):
        files_to_analyse = [os.path.join(fpath, file) for file in os.listdir(fpath) if file.startswith(prefix) and file.endswith(file_extension)]
    else:
        print("The path is invalid.")

    if not files_to_analyse:
        print("No files to analyse")
        return None

    files_to_analyse.sort()
    print("Files to analyse:")
    for file in files_to_analyse:
        print(file)
    return files_to_analyse


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VarAPS: Variant Analysis Pipeline")
    parser.add_argument(
        "-m",
        "--mode",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Mode selection (Choose 1, 2, 3, 4, or 5): \n"
        "1 - Retrieve mutations from each read found in BAM/CRAM files. \n"
        "2 - Get variants proportions from mode 1 output. \n"
        "3 - Get variants proportions directly from BAM/CRAM files.\n"
        "4 - Generate a new M matrix with different lineage choices.\n"
        "5 - Downsample BAM/CRAM files.",
    )
    parser.add_argument("--path", help="Path to the directory containing bam/cram files or to the bam/cram file directly")
    parser.add_argument("--ref", help="Path to the reference sequence file")
    parser.add_argument("-o", "--output", help="Path to the output directory (default: current directory)")
    parser.add_argument("-p", "--filter_per", type=float, help="Percentage of reads that must contain a mutation to be kept as a mutation (default: 0.0)")
    parser.add_argument("-n", "--filter_num", type=int, help="Number of reads that must contain a mutation to be kept as a mutation (default: 0)")
    parser.add_argument(
        "--deconv_method",
        type=int,
        choices=[1, 2, 3],
        help="Deconvolution method: \n" "1 - Co-occurence based methode\n" "2 - Count based method\n" "3 - Frequencies based method\n" "(only applicable in Mode 2 and Mode 3) (default: 1):",
    )
    parser.add_argument("--M", help="Path to the profile mutation variant matrix (only applicable in Mode 2 and Mode 3)")
    parser.add_argument("--NbBootstraps", type=int, help="Number of bootstraps (only applicable in Mode 2 and Mode 3), default: 1")
    parser.add_argument(
        "--max_workers",
        type=int,
        default=4,
        help="Maximum parallel workers for mode 2 (default: 4)",
    )
    parser.add_argument(
        "--optibyAlpha", type=lambda x: x.lower() == "true", help="Optimise by alpha - True/False optimize by Error Rate (alpha) also - " "(only applicable in Mode 2 and Mode 3), default: True"
    )
    parser.add_argument("--alphaInit", type=float, help="Initial value for Error Rate alpha (only applicable in Mode 2 and Mode 3), default: 0.01")
    parser.add_argument(
        "--num_reads",
        type=int,
        help="Number of reads to sample with replacement for deconvolution (modes 2 & 3). Default: all reads",
    )
    parser.add_argument("--full_data", help="Path to the full data file or URL for mode 4")
    parser.add_argument("--tree_file", help="Path to the tree file for mode 4")
    parser.add_argument("--variant_list", help="Path to the variant list file for mode 4")
    parser.add_argument("--output_M", help="Path to store the result M matrix in mode 4 (default: current directory)")
    parser.add_argument("--min_freq_M", type=float, default=0.5, help="Minimum frequency filter for mode 4 (default: 0.5)")
    parser.add_argument("--min_seq_M", type=int, default=5, help="Minimum number of sequences filter for mode 4 (default: 5)")
    parser.add_argument("--target_reads", type=int, help="Target number of reads for downsampling in mode 5 (default: 50000)")
    return parser.parse_args()


def prompt_for_missing_args(args: argparse.Namespace) -> argparse.Namespace:
    if args.mode is None:
        args.mode = int(
            input(
                "Mode selection (Choose 1, 2, 3, 4, or 5): \n"
                "1 - Retrieve mutations from each read found in BAM/CRAM files. \n"
                "2 - Get variants proportions from mode 1 output. \n"
                "3 - Get variants proportions directly from BAM/CRAM files.\n"
                "4 - Generate a new M matrix with different lineage choices.\n"
                "5 - Downsample BAM/CRAM files.\n"
                "Mode selection (Choose 1, 2, 3, 4, or 5): "
            )
        )

    if args.mode in [1, 3, 5]:
        while not args.path or not os.path.exists(args.path):
            args.path = input("Enter path to BAM/CRAM file or directory: ")

    if args.mode in [1, 3]:
        while not args.ref or not os.path.isfile(args.ref):
            args.ref = input("Enter path to the reference sequence file: ")

    if args.mode == 2:
        while not args.path or not os.path.exists(args.path):
            args.path = input("Enter path to X files folder/file: ")

    if args.mode == 4:
        while not args.full_data:
            args.full_data = (
                input("Enter path or URL to the full data file (default: download from https://raw.githubusercontent.com/hacen-ai/Varaps-data/main/Full_data_latest.zip): ")
                or "https://raw.githubusercontent.com/hacen-ai/Varaps-data/main/Full_data_latest.zip"
            )
        while not args.tree_file:
            args.tree_file = (
                input("Enter path to the tree file (default: download from https://raw.githubusercontent.com/hacen-ai/Varaps-data/main/Full_data_latest.zip): ")
                or "https://raw.githubusercontent.com/hacen-ai/Varaps-data/main/Full_data_latest.zip"
            )
        while not args.variant_list:
            args.variant_list = (
                input("Enter path to the variant list file (default: download from https://raw.githubusercontent.com/hacen-ai/Varaps-data/main/Full_data_latest.zip): ")
                or "https://raw.githubusercontent.com/hacen-ai/Varaps-data/main/Full_data_latest.zip"
            )

    if not args.output:
        args.output = input("Enter path to result folder (default: current folder): ") or os.getcwd()
    os.makedirs(args.output, exist_ok=True)

    if args.mode in [1, 3]:
        args.filter_per = args.filter_per if args.filter_per is not None else float(input("Enter percentage filter (default 0.0): ") or 0.0)
        args.filter_num = args.filter_num if args.filter_num is not None else int(input("Enter number filter (default 0): ") or 0)

    if args.mode in [2, 3]:
        if args.deconv_method is None:
            args.deconv_method = int(
                input(
                    "Enter deconvolution method: \n"
                    "1 - Co-occurence based methode\n"
                    "2 - Count based method\n"
                    "3 - Frequencies based method\n"
                    "Deconvolution method (Choose 1, 2 or 3) (default 1): "
                )
                or 1
            )
        while not args.M or not os.path.isfile(args.M):
            args.M = input("Enter path to profile mutation variant matrix: ")
        args.NbBootstraps = args.NbBootstraps or int(input("Enter number of bootstraps (default 1): ") or 1)
        args.optibyAlpha = args.optibyAlpha if args.optibyAlpha is not None else input("Optimize by Error Rate alpha? (True/False, default True): ").lower() == "true"
        args.alphaInit = args.alphaInit or float(input("Enter initial value for Error Rate alpha (default 0.01): ") or 0.01)

    if args.mode == 4:
        args.min_freq_M = args.min_freq_M if args.min_freq_M is not None else float(input("Enter minimum frequency filter (default 0.5): ") or 0.5)
        args.min_seq_M = args.min_seq_M if args.min_seq_M is not None else int(input("Enter minimum number of sequences filter (default 5): ") or 5)
        args.output_M = args.output_M if args.output_M is not None else input("Enter path to store the result M matrix (defaut: current folder): ") or os.getcwd()

    if args.mode == 5:
        args.target_reads = args.target_reads if args.target_reads else int(input("Enter target number of reads for downsampling (default 50000): ") or 50000)

    return args


def main():
    args = parse_arguments()
    args = prompt_for_missing_args(args)

    global_start_time = time.time()

    if args.mode in [1, 2, 3, 5]:
        files_to_analyse = get_files(args.path, args.mode)
        if files_to_analyse is None:
            return

    if args.mode == 1:
        for file_name in files_to_analyse:
            mode1.analyze_file_mode1(file_name, args.ref, args.filter_per, args.filter_num, args.output)
    elif args.mode == 2:
        mode2.analyze_file_mode2(
            args.path,
            args.M,
            args.output,
            args.NbBootstraps,
            args.alphaInit,
            args.optibyAlpha,
            args.deconv_method,
            args.num_reads,
            args.max_workers,
        )
    elif args.mode == 3:
        temp_output_dir = os.path.join(args.output, f"temp_X_Matrix_{np.random.randint(0, 10000000)}")
        os.makedirs(temp_output_dir, exist_ok=True)
        for file_name in files_to_analyse:
            mode1.analyze_file_mode1(file_name, args.ref, args.filter_per, args.filter_num, temp_output_dir)
        mode2.analyze_file_mode2(
            temp_output_dir,
            args.M,
            args.output,
            args.NbBootstraps,
            args.alphaInit,
            args.optibyAlpha,
            args.deconv_method,
            args.num_reads,
            args.max_workers,
        )
    elif args.mode == 4:
        output_file = os.path.join(args.output_M, "new_M_matrix.csv")
        generate_M.generate_M(args.full_data, args.tree_file, args.variant_list, output_file, args.min_freq_M, args.min_seq_M)
        print(f"New M matrix generated and saved to: {output_file}")
    elif args.mode == 5:
        downsampling.downsample_bam(args.path, args.output, args.target_reads)

    # print(f"**** Total time: {time.time() - global_start_time:.2f}s ****")


if __name__ == "__main__":
    main()
