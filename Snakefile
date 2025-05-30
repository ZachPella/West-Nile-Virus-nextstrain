# Wild card constraints
wildcard_constraints:
    dataset = "WNV_NA"

# File paths
files = {
    'sequences': "data/sequences.fasta",
    'metadata': "data/updated_metadata.tsv",  # Updated to use the new metadata file
    'reference': "config/WNV_reference.gb",
    'colors_script': "config/colors_clean.py",
    'lat_longs': "config/lat_longs_clean.tsv",
    'auspice_config': "config/auspice_config.json"
}

rule all:
    input:
        "auspice/WNV_NA_2025.json"  # Updated output file name to include 2025

# Update metadata from Pathoplexus
rule update_metadata:
    input:
        metadata = files['metadata']
    output:
        metadata = files['metadata']
    log:
        "logs/update_metadata.log"

# Add geographical coordinates
rule add_lat_longs:
    input:
        metadata = rules.update_metadata.output.metadata,
        lat_longs = files['lat_longs']
    output:
        metadata = "data/metadata_with_coords_2025.tsv"  # Updated output file name
    log:
        "logs/add_lat_longs.log"

# Sequence alignment
rule align:
    input:
        sequences = files['sequences'],
        reference = files['reference']
    output:
        alignment = "results/aligned_2025.fasta"  # Updated output file name
    log:
        "logs/align.log"
    threads: 14
    shell:
        """
        augur align \
            --sequences {input.sequences} \
            --reference-sequence {input.reference} \
            --output {output.alignment} \
            --fill-gaps \
            --nthreads {threads} 2> {log}
        """

# Build phylogenetic tree
rule tree:
    input:
        alignment = rules.align.output.alignment
    output:
        tree = "results/tree_raw_2025.nwk"  # Updated output file name
    log:
        "logs/tree.log"
    threads: 14
    shell:
        """
	augur tree \
	    --alignment {input.alignment} \
	    --output {output.tree} \
	    --nthreads {threads} 2> {log}
"""

# Refine tree and estimate dates
rule refine:
    input:
        tree = rules.tree.output.tree,
        alignment = rules.align.output.alignment,
        metadata = files['metadata']
    output:
        tree = "results/tree_2025.nwk",  # Updated output file name
        node_data = "results/branch_lengths_2025.json"  # Updated output file name
    params:                           # <-- ADDED THIS SECTION
        coalescent = "opt",
        date_inference = "marginal",
	clock_filter_iqd = 4
    log:
        "logs/refine.log"
    shell:
        """
        augur refine \
            --tree {input.tree} \
            --alignment {input.alignment} \
            --metadata {input.metadata} \
            --output-tree {output.tree} \
            --output-node-data {output.node_data} \
            --timetree \
            --coalescent {params.coalescent} \
            --date-confidence \
            --date-inference {params.date_inference} \
	    --clock-filter-iqd {params.clock_filter_iqd} \
	    2> {log}
        """

# Reconstruct ancestral sequences
rule ancestral:
    input:
        tree = rules.refine.output.tree,
        alignment = rules.align.output.alignment
    output:
        node_data = "results/nt_muts_2025.json"  # Updated output file name
    params:
        inference = "joint"
    log:
        "logs/ancestral.log"
    shell:
        """
        augur ancestral \
            --tree {input.tree} \
            --alignment {input.alignment} \
            --output-node-data {output.node_data} \
            --inference {params.inference} 2> {log}
        """

# Translate sequences
rule translate:
    input:
        tree = rules.refine.output.tree,
        node_data = rules.ancestral.output.node_data,
        reference = files['reference']
    output:
        node_data = "results/aa_muts_2025.json"  # Updated output file name
    log:
        "logs/translate.log"
    shell:
        """
        augur translate \
            --tree {input.tree} \
            --ancestral-sequences {input.node_data} \
            --reference-sequence {input.reference} \
            --output-node-data {output.node_data} 2> {log}
        """

# Infer traits
rule traits:
    input:
        tree = rules.refine.output.tree,
        metadata = files['metadata']
    output:
        node_data = "results/traits_2025.json"  # Updated output file name
    params:
        columns = "state county Region Species"  # Added Region to the columns
    log:
        "logs/traits.log"
    shell:
        """
        augur traits \
            --tree {input.tree} \
            --metadata {input.metadata} \
            --output-node-data {output.node_data} \
            --columns {params.columns} \
            --confidence 2> {log}
        """

# Generate colors using Python script
rule generate_colors:
    input:
        script = files['colors_script'],
        metadata = files['metadata']
    output:
        colors = "results/colors_2025.tsv"  # Updated output file name
    log:
        "logs/generate_colors.log"
    shell:
        """
        python {input.script} {input.metadata} {output.colors} 2> {log}
        """

# Export for visualization
rule export:
    input:
        tree = rules.refine.output.tree,
        metadata = files['metadata'],
        branch_lengths = rules.refine.output.node_data,
        traits = rules.traits.output.node_data,
        nt_muts = rules.ancestral.output.node_data,
        aa_muts = rules.translate.output.node_data,
        colors = rules.generate_colors.output.colors,
        lat_longs = files['lat_longs'],
        auspice_config = files['auspice_config']
    output:
        auspice_json = "auspice/WNV_NA_2025.json"  # Updated output file name
    log:
        "logs/export.log"
    shell:
        """
        augur export v2 \
            --tree {input.tree} \
            --metadata {input.metadata} \
            --node-data {input.branch_lengths} {input.traits} {input.nt_muts} {input.aa_muts} \
	    --colors {input.colors} \
            --lat-longs {input.lat_longs} \
            --auspice-config {input.auspice_config} \
            --include-root-sequence \
	    --output {output} 2> {log}
        """

# Clean up
rule clean:
    shell:
        """
        rm -rf results/ logs/
        """
