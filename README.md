# West Nile Virus Nextstrain Build - Nebraska County and US State Analysis

This repository contains an automated Nextstrain build for analyzing West Nile Virus (WNV) genomic data at both Nebraska county and United States state levels. Based on the WestNile 4K Project template, this build is customized for Nebraska county-level analysis with automated monthly updates.

## Overview

This Nextstrain build processes WNV genomic sequences and associated metadata to create interactive visualizations for tracking WNV evolution and spread across Nebraska counties and US states.

## Prerequisites

1. Install conda
2. Install augur and its dependencies:
```bash
git clone git@github.com:nextstrain/augur.git
cd augur
conda env create -f environment.yml
export NCBI_EMAIL=<YOUR_EMAIL_HERE>
```

3. Enable the conda environment:
```bash
conda activate augur
```

4. Install auspice:
```bash
conda install -c conda-forge nodejs
npm install --global auspice
```

5. Verify installations:
```bash
augur -h
auspice -h
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ZachPella/West-Nile-Virus-nextstrain.git
cd WNV_build_test_gitversion
```

## Directory Structure

```
WNV_build_test_gitversion/
├── config/                  # Configuration files
│   ├── WNV_reference.gb    # WNV reference genome
│   ├── auspice_config.json # Visualization configuration
│   ├── colors_clean.py     # Color scheme definitions
│   └── lat_longs_clean.tsv # Geographic coordinates
├── data/                   # Input data directory
│   ├── metadata.tsv       # Sequence metadata
│   └── sequences.fasta    # Genomic sequences
├── scripts/               # Analysis scripts
│   ├── add_lat_long_to_metadata.py
│   └── new_pathoplexus_data.py
├── results/              # Build output files
└── Snakefile            # Pipeline definition
```

## Running the Build

### Basic Usage

1. Clean previous build files:
```bash
snakemake clean
```

2. Run the complete build:
```bash
snakemake --cores all
```

The build process takes approximately 40 minutes to complete.

### Individual Steps

You can run specific steps separately:

1. Parse metadata and add authors:
```bash
snakemake --printshellcmds --force parse
snakemake --printshellcmds --force add_authors
```

2. Generate colors:
```bash
snakemake --printshellcmds --force create_colors
```

3. Generate lat-longs:
```bash
snakemake --printshellcmds --force create_lat_longs
```

4. Export final files:
```bash
snakemake --printshellcmds --force export
```

### Automated Updates

This build is configured to automatically update monthly with new data. The automation process:
1. Fetches new sequence data
2. Updates metadata
3. Runs the complete build pipeline
4. Regenerates visualizations

## Visualization

To view the results locally:
```bash
auspice view --datasetDir ./auspice
```
Then open the link that is immeditaely provided to you in your browser. The link should be something like http://localhost:4000 

## Data Format

### Metadata Structure

The `metadata.tsv` file contains the following columns:
- strain: Unique identifier for each sequence
- virus: Virus name
- accession: Sequence accession number
- date: Collection date
- region: Geographic region
- country: Country of collection
- state: US state
- division: Geographic division
- city: City of collection
- db: Database source
- segment: Viral segment information
- authors: Study authors
- url: Related URL
- title: Study title
- journal: Journal of publication
- paper_url: URL to publication
- latitude: Geographic latitude
- longitude: Geographic longitude
- county: County-level information (specific to Nebraska sequences)

## Scripts

### add_lat_long_to_metadata.py
Adds geographic coordinates to sequence metadata based on location information, with special handling for Nebraska counties.

### new_pathoplexus_data.py
Processes and integrates new data from Pathoplexus into the existing dataset.

## Acknowledgments

- Based on the WestNile 4K Project template
- Nextstrain team
- UNMC Dr. Fauver Lab

