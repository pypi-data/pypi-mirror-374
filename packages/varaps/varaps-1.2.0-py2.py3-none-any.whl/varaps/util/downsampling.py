import os
import sys
import pysam
from tqdm import tqdm
import random


def downsample_bam(input_path, output_dir, target_reads):
    print("output_dir: ", output_dir)

    # Check if input directory /file exists
    if input_path.endswith(".bam"):
        if os.path.exists(input_path):
            bam_files = [input_path]
        else:
            print(f"Error: Input file '{input_path}' does not exist.")
            sys.exit(1)
    elif os.path.isdir(input_path):
        # Get all BAM files in the input directory
        bam_files = [f for f in os.listdir(input_path) if f.endswith(".bam")]
    else:
        print(f"Error: Input directory '{input_path}' does not exist.")
        sys.exit(1)

    if not bam_files:
        print(f"Error: No BAM files found in '{input_path}'.")
        sys.exit(1)

    total_files = len(bam_files)

    print(f"Starting downsampling process for {total_files} BAM files from '{input_path}'...")
    print(f"Target number of reads: {target_reads}")

    # Process each BAM file
    # Process each BAM file
    for filename in tqdm(bam_files, desc="Processing BAM files"):
        if os.path.isdir(input_path):
            full_input_path = os.path.join(input_path, filename)
        else:
            full_input_path = input_path  # If input_path is already a file

        output_path = os.path.join(output_dir, filename.replace(".bam", ".downsampled.bam"))

        # Calculate the fraction for downsampling
        total_reads = pysam.view("-c", full_input_path)
        total_reads = int(total_reads.strip())
        fraction = min(target_reads / total_reads, 0.999)

        if fraction >= 1:
            print(f"Skipping {filename}: has fewer reads than target")
            continue

        # print(f"Downsampling {filename} with fraction {fraction:.4f}")

        seed = random.randint(0, 1000000)
        fraction = str(fraction).split(".")[1]
        # Perform downsampling using samtools view
        pysam.view("-bs", str(seed) + "." + str(fraction), full_input_path, "-o", output_path, catch_stdout=False)

        # print(f"Downsampled {filename} saved as {os.path.basename(output_path)}")
