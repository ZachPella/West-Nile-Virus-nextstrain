from __future__ import print_function
import matplotlib as mpl
import numpy as np
import argparse
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, hex2color

def interpolate_hex_colors(color1, color2, n_colors):
    """Interpolate between two hex colors."""
    c1 = np.array(hex2color(color1))
    c2 = np.array(hex2color(color2))
    mix = np.linspace(0, 1, n_colors)
    
    return [mpl.colors.rgb2hex(c1 * (1 - m) + c2 * m) for m in mix]

def create_color_scheme():
    # Regional state groupings
    states = {
        "west": ["AK", "WA", "ID", "MT", "OR", "NV", "WY", "CA", "UT", "CO", "HI"],
        "southwest": ["AZ", "NM", "OK", "TX"],
        "midwest": ["ND", "MN", "IL", "WI", "MI", "SD", "IA", "IN", "OH", "NE", "MO", "KS"],
        "southeast": ["KY", "WV", "VA", "AR", "TN", "NC", "SC", "LA", "MS", "AL", "GA", "FL"],
        "northeast": ["ME", "VT", "NH", "NY", "MA", "RI", "PA", "NJ", "CT", "MD", "DC", "DE"]
    }

    # Color schemes for each region
    states_cols = {
        "west": ["#3B4992", "#4B5CA5", "#5B6FB8", "#6B82CB", "#7B95DE", "#8BA8F1"],
        "southwest": ["#EE0000", "#FF2222", "#FF4444", "#FF6666"],
        "midwest": ["#008B45", "#00A352", "#00BB5F", "#00D36C", "#00EB79", "#00FF86"],
        "southeast": ["#631879", "#802090", "#9D28A7", "#BA30BE", "#D738D5", "#F440EC"],
        "northeast": ["#E69F00", "#FFB61A", "#FFCD33", "#FFE44D", "#FFFB66", "#FFFF80"]
    }

    # Nebraska counties
    ne_counties = [
        "Adams", "Antelope", "Arthur", "Banner", "Blaine", "Boone", "Box Butte", "Boyd",
        "Brown", "Buffalo", "Burt", "Butler", "Cass", "Cedar", "Chase", "Cherry",
        "Cheyenne", "Clay", "Colfax", "Cuming", "Custer", "Dakota", "Dawes", "Dawson",
        "Deuel", "Dixon", "Dodge", "Douglas", "Dundy", "Fillmore", "Franklin", "Frontier",
        "Furnas", "Gage", "Garden", "Garfield", "Gosper", "Grant", "Greeley", "Hall",
        "Hamilton", "Harlan", "Hayes", "Hitchcock", "Holt", "Hooker", "Howard",
        "Jefferson", "Johnson", "Kearney", "Keith", "Keya Paha", "Kimball", "Knox",
        "Lancaster", "Lincoln", "Logan", "Loup", "Madison", "McPherson", "Merrick",
        "Morrill", "Nance", "Nemaha", "Nuckolls", "Otoe", "Pawnee", "Perkins", "Phelps",
        "Pierce", "Platte", "Polk", "Red Willow", "Richardson", "Rock", "Saline",
        "Sarpy", "Saunders", "Scotts Bluff", "Seward", "Sheridan", "Sherman", "Sioux",
        "Stanton", "Thayer", "Thomas", "Thurston", "Valley", "Washington", "Wayne",
        "Webster", "Wheeler", "York"
    ]

    # Generate colors for counties using viridis colormap
    county_colors = [mpl.colors.rgb2hex(mpl.cm.viridis(i)) 
                    for i in np.linspace(0, 1, len(ne_counties))]

    return states, states_cols, ne_counties, county_colors

def write_colors_file(output_path, states, states_cols, ne_counties, county_colors, metadata_path):
    """Write the color scheme to a TSV file based on states and counties in metadata."""
    try:
        metadata = pd.read_csv(metadata_path, sep='\t')
        if 'state' not in metadata.columns:
            raise ValueError("Metadata file must contain a 'state' column")
        
        unique_states = metadata['state'].dropna().unique()
        
        # Get unique counties only for Nebraska
        unique_counties = metadata[metadata['state'] == 'NE']['county'].dropna().unique()
        
        # Get unique species values
        unique_species = []
        if 'Species' in metadata.columns:
            unique_species = metadata['Species'].dropna().unique()
            unique_species = [s for s in unique_species if s != '']  # Remove empty strings
        
    except Exception as e:
        print(f"Error reading metadata file: {e}")
        raise

    with open(output_path, "w") as fh:
        # Write header
        fh.write("trait\tvalue\tcolor\n")
        
        # Write states
        for region, states_list in states.items():
            colors = states_cols[region]
            if len(states_list) > len(colors):
                colors = interpolate_hex_colors(colors[0], colors[-1], len(states_list))
            
            for state, color in zip(states_list, colors):
                if state in unique_states:
                    fh.write(f"state\t{state}\t{color}\n")
        # Add international locations
        international_colors = {
            "ARG/B": "#8B4513",        # Brown for Argentina
            "MEX/CHH": "#FF6347",      # Tomato for Mexico
            "CAN/QC": "#4169E1",       # Royal Blue for Canada
            "MEX/SON": "#FF4500",      # Orange Red for Mexico
            "MEX/BCN": "#FF8C00",      # Dark Orange for Mexico
            "MEX/TAM": "#FFA500",      # Orange for Mexico
            "BRA/Bahia": "#228B22",    # Forest Green for Brazil
            "VGB": "#9370DB",          # Medium Purple for Virgin Islands
            "US-VI": "#BA55D3",        # Medium Orchid for US Virgin Islands
            "MEX/TAB": "#FFD700",      # Gold for Mexico
            "COL/ANT": "#32CD32",      # Lime Green for Colombia
            "ISR/D": "#00CED1"         # Dark Turquoise for Israel
        }        

        for state, color in international_colors.items():
            if state in unique_states:
                fh.write(f"state\t{state}\t{color}\n")

        # Write counties (only for Nebraska)
        for county, color in zip(ne_counties, county_colors):
            if county in unique_counties:
                fh.write(f"county\t{county}\t{color}\n")
        
        # Add ALL Region colors - both US regions AND Nebraska sub-regions
        region_colors = {
            # US regions - new additions
            "Northeast": "#1f77b4",    # Blue
            "South": "#e31a1c",        # Red  
            "Midwest": "#f781bf",      # Pink
            "West": "#ffff33",         # yellow
            
            # Nebraska sub-regions - matching your metadata
            "NE_East": "#1b9e77",      # Your original color
            "NE_Central": "#d95f02",   # Your original color
            "NE_West": "#7570b3"       # Your original color
        }
        
        # Write ALL regions found in metadata
        if 'Region' in metadata.columns:
            unique_regions = metadata['Region'].dropna().unique()
            for region in unique_regions:
                if region in region_colors:
                    fh.write(f"Region\t{region}\t{region_colors[region]}\n")
        
        # Add Species colors - keeping your original two
        species_colors = {
            "Culex pipiens": "#1f77b4",
            "Culex tarsalis": "#ff7f0e"
        }
        for species in unique_species:
            if species in species_colors:
                fh.write(f"Species\t{species}\t{species_colors[species]}\n")

def main():
    parser = argparse.ArgumentParser(description='Generate color scheme for WNV visualization')
    parser.add_argument('metadata', help='Path to input metadata file')
    parser.add_argument('output', help='Path to output colors TSV file')
    
    args = parser.parse_args()
    
    try:
        states, states_cols, ne_counties, county_colors = create_color_scheme()
        write_colors_file(args.output, states, states_cols, ne_counties, county_colors, args.metadata)
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
