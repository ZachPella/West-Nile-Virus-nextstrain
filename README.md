# West Nile Virus Nextstrain Build - Nebraska County and US State Analysis

This repository contains an automated Nextstrain build for analyzing West Nile Virus (WNV) genomic data at both Nebraska county and United States state levels. The pipeline automatically updates with new data on a monthly basis.

## Overview

This Nextstrain build processes WNV genomic sequences and associated metadata to create interactive visualizations for tracking WNV evolution and spread across Nebraska counties and US states.

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
├── results/              # Output directory
└── Snakefile            # Pipeline definition
```

## Prerequisites

- Nextstrain CLI
- Snakemake
- Python 3.x

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ZachPella/West-Nile-Virus-nextstrain.git
cd WNV_build_test_gitversion
```

2. Install required dependencies:
```bash
conda env create -f environment.yml  # If you have an environment file
# or
pip install -r requirements.txt      # If you have a requirements file
```

## Usage

### Running the Pipeline

To execute the complete pipeline:

```bash
snakemake --cores all
```

### Automated Updates

The pipeline is configured to automatically update monthly with new data. The update process includes:
1. Fetching new sequence data
2. Updating metadata
3. Regenerating visualizations

### Output

The pipeline generates:
- Phylogenetic trees
- Geographic visualizations
- Temporal analyses
- Interactive web visualizations (via Auspice)

## Configuration

### Metadata Format

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
- county: County-level information

### Geographic Data

Geographic coordinates are managed in `config/lat_longs_clean.tsv` and automatically integrated into the metadata using `scripts/add_lat_long_to_metadata.py`.

## Scripts

### add_lat_long_to_metadata.py
Adds geographic coordinates to sequence metadata based on location information.

### new_pathoplexus_data.py
Processes and integrates new data from Pathoplexus into the existing dataset.

## Contact

Provide contact zpella@unmc.edu for any questions

## Acknowledgments

- Nextstrain team
- UNMC Dr. Fauver Lab

## Citation

If others should cite this work, provide citation information here.
