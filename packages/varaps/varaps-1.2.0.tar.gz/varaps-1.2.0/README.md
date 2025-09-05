# VaRaPS: Variants Ratios from Pooled Sequencing

## Introduction
VaRaPS (Variants Ratios from Pooled Sequencing) is a Python package orignaly designed for calculating the proportions of SARS-CoV-2 variants from sequencing data. It supports BAM and CRAM file formats and re-implements methods like Freyja[[1]](#1), LCS[[2]](#2), and VirPool[[3]](#3). VaRaPS is equipped with three modes of operation to cater to various analysis needs.

## Table of Contents
1. [Installation](#installation)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Usage](#usage)
   - [General Command Structure](#general-command-structure)
   - [Mode 1: Retrieve Mutations (Variant calling)](#mode-1-retrieve-mutations)
   - [Mode 2: Calculate Variant Proportions](#mode-2-calculate-variant-proportions)
   - [Mode 3: Direct Calculation from Files(Combination of mode 1 and 2)](#mode-3-direct-calculation-from-files)
   - [Mode 4: Generate New M Matrix](#mode-4-generate-M)
   - [Mode 5: Downsample BAM/CRAM Files](#downsampling)
5. [Understanding the Output of mode 1](#understanding-the-output)
<!-- 6. [Dependencies](#dependencies) -->
6. [Troubleshooting](#troubleshooting)
7. [Contributors](#contributors)
8. [License](#license)
9. [Contact](#contact)
10. [Citation](#citation)

<a id="installation"></a>
## Installation
Ensure   that   Python   3.8 or later version   is   installed   on   your   system   before   installing   varaps.
```
pip install VaRaPS
```
<a id="features"></a>
## Features

* Implements multiple methods for variant proportion calculations from sequencing data.
* Offers three deconvolution methods [Co-occurence based methode, Count based method and Frequencies based method] for flexible analysis requirements.
* Interactive mode prompts users through the analysis process.
* Supports both BAM and CRAM file formats.

<a id="quick-start"></a>
## Quick Start

For a quick start, you can run VaRaPS in an interactive mode which will guide you through the process:

```shell
varaps
```

Follow the on-screen prompts to input your data and choose the analysis parameters.

<a id="usage"></a>
## Usage

VaRaPS is designed to be flexible and user-friendly, offering several modes and parameters to fit your analysis needs. Below are detailed explanations of how to use each mode and what each parameter means.

<a id="general-command-structure"></a>
##### General Command Structure

All commands in VaRaPS follow a basic structure:

```bash
varaps --mode <mode_number> [options]
```

Replace `<mode_number>` with the mode you wish to use (1, 2, or 3), and `[options]` with the various options available for that mode, detailed below.

<a id="mode-1-retrieve-mutations"></a>
#### Mode 1: Retrieve Mutations (Variant calling)

This mode extracts mutations from reads in BAM/CRAM files, by Doing a variant calling for each read.

```bash
varaps --mode 1 --path <path_to_bam_cram_files> --ref <path_to_reference_fasta> [--output <output_directory>] [--percentage <filter_percentage>] [--number <filter_number>]
```

* `--path <path_to_bam_cram_files>`: Specify the directory containing your BAM/CRAM files.
* `--ref <path_to_reference_fasta>`: Indicate the path to your reference genome file in FASTA format.
* `--output <output_directory>`: (Optional) Designate where you want the results to be saved. By default, results are saved in the current directory.
* `--percentage <filter_percentage>`: (Optional) Set the minimum percentage of reads that must contain a mutation for it to be considered significant. The default is 0.0, which means no filtering is applied based on percentage.
* `--number <filter_number>`: (Optional) Define the minimum number of reads that must contain a mutation for it to be recognized. The default is 0, which means no filtering is applied based on read count.

<a id="mode-2-calculate-variant-proportions"></a>
#### Mode 2: Calculate Variant Proportions

In this mode, VaRaPS calculates the proportion of each variant using the output from Mode 1.

```bash
varaps --mode 2 --deconv_method <method_number> --NbBootstraps <number_of_bootstraps> --optibyAlpha <optimize_by_alpha> --alphaInit <initial_alpha_value> --path <path_to_data> [--output <output_directory>] [--num_reads <num_reads>] --M <path_to_variant_matrix>
```

* `--deconv_method <method_number>`: Choose the deconvolution method to use. The number corresponds to the specific implementation:
   * 1 - Co-occurence based methode [[3]](#3)
   * 2 - Count based method [[2]](#2)
   * 3 - Frequencies based method [[1]](#1)
* `--path <path_to_data>`: Specify the path to the input data, which can be the output directory from Mode 1.
* `--M <path_to_variant_matrix>`: Provide the path to the variant/mutation profile matrix, which is a CSV file with rows representing variants and columns representing mutations [[Exemple file for the variant/mutation profile matrix]](https://github.com/hacen-ai/Varaps-data/blob/main/Variant-mutation%20profile%20matrix.csv).
* `--output <output_directory>`: (Optional) Indicate the output directory for the results.

* `--NbBootstraps <number_of_bootstraps>`: (Optional) Set the number of bootstrap iterations for estimating uncertainty.
* `--optibyAlpha <optimize_by_alpha>`: (Optional) Boolean value (`True` or `False`) to determine if the algorithm should optimize by the sequencing error rate.
* `--alphaInit <initial_alpha_value>`: (Optional) Provide the initial value for the error rate parameter.
* `--num_reads <num_reads>`: (Optional) Number of reads to sample with replacement for deconvolution; defaults to using all reads. Useful to speed up runs on very large datasets (also available in Mode 3).

**Subsampling semantics (vs. file downsampling):** When `--num_reads` is set, VaRaPS uniformly subsamples reads with replacement from the observed read distribution. This is the same resampling mechanism as in bootstrapping, but with a user-chosen target sample size that can be smaller than the original dataset. In expectation, relative abundances are preserved, though variance increases at smaller sample sizes. This subsampling is performed in memory only and does not modify or create BAM/CRAM files. To generate physically smaller BAM/CRAM files on disk, use Mode 5 (file-level downsampling).

<a id="mode-3-direct-calculation-from-files"></a>
#### Mode 3: Direct Calculation from Files

Mode 3 combines the functionality of Modes 1 and 2 for a direct calculation of variant proportions from BAM/CRAM files without the intermediate step.

```bash
varaps --mode 3 --path <path_to_bam_cram_files> --ref <path_to_reference_fasta> --deconv_method <method_number> [--num_reads <num_reads>] [--other_options]
```

* The parameters for Mode 3 are a combination of those from Modes 1 and 2.
* Use the same `--path`, `--ref`, `--output`, and `--deconv_method` parameters as described above.
* Include any other optional parameters as needed to refine your analysis.

- `--num_reads <num_reads>` (optional): Uniform in-memory subsampling with replacement, identical in mechanism to bootstrapping but with a user-specified smaller target size. It preserves relative abundances in expectation, increases variance at smaller sizes, and never alters or creates BAM/CRAM files. Use Mode 5 for file-level downsampling when you need smaller on-disk files.


<a id="nderstanding-the-output"></a>
## Understanding the Output

VaRaPS generates detailed output files that encapsulate the results of the mutation and variant analysis. Below are the explanations of the files along with examples to help you understand their structure and content.
#### mutations_index File

- **Filename**: `mutations_index_<input_file_name>_<options>.csv`
- **Contents**: Lists all mutations, that passed the filter, found in the input files, serving as an index for the mutations referenced in the Xsparse file.
- **Example**:
```
Mutations
T6TC
C9A
A11G
A11T
AAA14A
A16G
A16AG
...
...
```
 - **Interpretation**:
    - Each line represents a unique mutation, identified by a combination of the reference base, the position in the reference sequence, and the alternate base.
    - This file acts as a legend for the mutation indices used in the Xsparse file[e.i The mutation at index 4 is `AAA14A`.]

#### Mutation Encoding

- **Format**: `[reference base][position][alternate base]`
- **Example**:
- `T6TC` indicates a substitution at position 6 where 'T' has been replaced by 'C'.
- `AAA14A` suggests a deletion at position 14 where 'AAA' has been shortened to 'A'.
- `A16AG` describes an insertion at position 16 where 'G' has been added after 'A'.

#### Xsparse File

- **Filename**: `Xsparse_<input_file_name>_<options>.csv`
- **Contents**: The Xsparse file contains a list of unique reads and the mutations they contain, represented in a sparse matrix format.The `Xsparse` file is the most important file as it contains the actual data.PS: The number of occurences of each read in BAM/CRAM is stored in the Wsparse file (see below).
- **Example**:
```

startIdx_position,endIdx_position,muts
0,4,
0,44,"0, 2"
0,22,"3,"
1,150,"1, 4"
2,275,"2, 5, 6"
...
...
```

**Interpretation**:
- The columns `startIdx_position` and `endIdx_position` define the range of positions covered by a read.
- The `muts` column lists the indices of the mutations present in the read within the defined range.
- For instance:
    - In read 0, it covers the region from position 0  inclusive to position 4 exclusive. It has no mutations.
    - In read 4, it covers the region from position 2 inclusive to position 75 exclusive. The mutations 2, 5, and 6 are found in this read.

#### Wsparse File

- **Filename**: `Wsparse_<input_file_name>_<options>.csv`
- **Contents**: This file associates each read with its frequency in the dataset to optimize data storage.
- **Example**:
```
Counts
2
1
1
1
5
...
...
```


**Interpretation**:
- Each line corresponds to the reads as they are listed in the Xsparse file.
- The `Counts` column indicates how many times each respective read appears in the dataset [e.i - Read 4 occurs 5 times in the data.]



<a id="mode-4-generate-M"></a>
#### Mode 4: Generate New M Matrix

This mode allows you to generate a new M matrix with different lineage choices, using data from GISAID and integrating it with phylogenetic information.

```bash
varaps --mode 4 --full_data [PATH_OR_URL] --tree_file [PATH] --variant_list [PATH] --output_M [PATH] [--min_freq_M FLOAT] [--min_seq_M INT]
```

- `--full_data`: Path or URL to the Full_data_latest.csv file. Default: "https://raw.githubusercontent.com/hacen-ai/Varaps-data/main/Full_data_latest.zip". If left empty, it will automatically download from the default URL.
- `--tree_file`: Path to the tree.json file. Default: Downloaded from the same URL as full_data if not specified.
- `--variant_list`: Path to the variant_list.txt file. Default: Downloaded from the same URL as full_data if not specified.
- `--output_M`: (Optional) Path to save the new M matrix. Default: Current directory.
- `--min_freq_M`: (Optional) Minimum frequency filter for including mutations in the matrix. Default: 0.5.
- `--min_seq_M`: (Optional) Minimum number of sequences a lineage must have to be included. Default: 5.

##### Important Files:

1. **variant_list.txt**:

   - This is the most crucial file for customizing your analysis.
   - Structure: Each line contains a single SARS-CoV-2 lineage designation.
   - Example contents:
     ```
     BA.2
     BA.5
     XBB.1.5
     ```
   - Users can modify this file to include any valid lineages they want to analyze. These lineages will form the rows of the resulting M matrix.

2. **tree.json**:

   - Contains the SARS-CoV-2 phylogenetic tree structure.
   - Used to maintain relationships between lineages, especially for those not explicitly listed in variant_list.txt.

3. **Full_data_latest.csv**:
   - Contains comprehensive SARS-CoV-2 sequence data processed with Nextclade.
   - Includes information on lineages, mutations, and other relevant metadata.

##### Process:

1. Data Loading:

   - If paths are not specified, the script automatically downloads the necessary files from the default URL.
   - Users can provide local file paths if they have the files on their system.

2. Lineage Selection:

   - The script processes the lineages listed in variant_list.txt.
   - It also considers child lineages not explicitly listed, using the tree.json file to maintain phylogenetic relationships.

3. Matrix Construction:

   - Builds the M matrix where rows represent lineages and columns represent mutations.
   - For each lineage-mutation pair, calculates the frequency of the mutation within that lineage.

4. Filtering:

   - Applies `min_freq_M` filter to keep only mutations that appear frequently enough in at least one lineage.
   - Uses `min_seq_M` to ensure each included lineage has sufficient representation in the dataset.

5. Output:
   - Generates a CSV file containing the new M matrix, saved to the specified output path or the current directory by default.

This mode is particularly useful for researchers who want to focus on specific lineages or update their analysis with the latest available data. By modifying the variant_list.txt file, users can tailor the M matrix to include emerging variants or focus on lineages of particular interest in their study.






<a id="downsampling"></a>

#### Mode 5: Downsample BAM/CRAM Files

This mode allows you to downsample BAM/CRAM files to a specified number of reads, which can be useful for reducing file size or normalizing read counts across samples.

```bash
varaps --mode 5 --path <INPUT_PATH> --output <OUTPUT_DIR> [--target_reads <TARGET_READS>]
```

* `--path <INPUT_PATH>`: Specify the path to a single BAM/CRAM file or a directory containing multiple BAM/CRAM files.
* `--output <OUTPUT_DIR>`: Indicate the directory where downsampled files will be saved.
* `--target_reads <TARGET_READS>`: (Optional) Set the desired number of reads in the downsampled output. Default is 50,000.

**Important distinction:** Mode 5 performs file-level downsampling and writes new, physically smaller BAM/CRAM files on disk (useful to reduce file sizes and I/O). In contrast, Modes 2 and 3 perform in-memory resampling/subsampling for analysis (bootstrap via `--NbBootstraps`, subsampling via `--num_reads`) to reduce computational burden without touching source files.

**Process:**

1. The script identifies all BAM/CRAM files in the specified input path.
2. For each file:
   - It calculates the total number of reads.
   - Determines the fraction of reads to keep based on the target number.
   - If the file has fewer reads than the target, it's skipped.
   - Uses samtools (via pysam) to perform the downsampling.
3. Downsampled files are saved in the output directory with ".downsampled.bam" appended to the original filename.

**Example:**

```bash
varaps --mode 5 --path /path/to/bam/files --output /path/to/output --target_reads 100000
```

This command will downsample all BAM files in `/path/to/bam/files` to approximately 100,000 reads each, saving the results in `/path/to/output`.

**Note:** The actual number of reads in the output may slightly vary from the target due to the probabilistic nature of downsampling.



<a id="troubleshooting"></a>
## Troubleshooting
If you encounter any issues while using VaRaPS, please contact us at djaout [at] lpsm.paris

<a id="contributors"></a>
## Contributing

Contributions to VaRaPS are welcome. If you have suggestions or improvements, feel free to mail me at djaout[at]lpsm.paris

<a id="license"></a>
## License

GNU General Public License v3 or later (GPLv3+)

<a id="contact"></a>
## Contact

For any questions or feedback regarding VaRaPS, feel free to reach out through by mail at djaout[at]lpsm.paris

<a id="citation"></a>
## Citation

To cite the PyPI package 'VaRaPS' in publications, use:

Djaout, E.H. (2024). VaRaPS: Variants Ratios from Pooled Sequencing. PyPI package.

A BibTeX entry for LaTeX users is:
```bibtex
@Manual{djaout2024varaps,
title = {VaRaPS: Variants Ratios from Pooled Sequencing},
author = {El Hacene Djaout},
year = {2024},
note = {PyPI package},
}
```

<a id="reference"></a>
## References
<a id="1">[1]</a> S. Karthikeyan et al. “Wastewater sequencing reveals early cryptic SARS-CoV-2 variant transmission”. In:
Nature 609.7925 (2022), pp. 101–108.

<a id="2">[2]</a> R. Valieris et al. “A mixture model for determining SARS-CoV-2 variant composition in pooled samples”. In: Bioinformatics 38.7 (2022), pp. 1809–1815.

<a id="3">[3]</a> A. Gafurov et al. “VirPool: Model-based estimation of SARS-CoV-2 variant proportions in wastewater samples”. In: medRxiv (2022).






