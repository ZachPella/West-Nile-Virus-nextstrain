import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationDataUpdater:
    def __init__(self, lat_long_file: str, metadata_file: str):
        self.lat_long_file = Path(lat_long_file)
        self.metadata_file = Path(metadata_file)
        self.state_coords = {}
        self.county_coords = {}

    def load_lat_longs(self):
        """Loads latitude and longitude data from the file, separating state and county data."""
        try:
            df = pd.read_csv(self.lat_long_file, sep='\t')
            
            # This check is good:
            if not all(col in df.columns for col in ['type', 'name', 'latitude', 'longitude']):
                raise ValueError("lat_long_file must contain 'type', 'name', 'latitude', 'longitude' columns in its header.")

            # Populate state_coords
            state_df = df[df['type'] == 'state']
            for _, row in state_df.iterrows():
                # Use row['name'] as the key, and the correct latitude/longitude columns
                self.state_coords[str(row['name'])] = (str(row['latitude']), str(row['longitude']))
            
            # Populate county_coords ONLY for Nebraska counties
            # Filter for type 'county' AND (optionally) for name starts with 'NE/' or if it's just the county name
            # Assuming Nebraska counties are just their names in the 'name' column in lat_longs_clean.tsv
            county_df = df[df['type'] == 'county']
            for _, row in county_df.iterrows():
                # Store county names as they appear in the TSV (e.g., 'Lancaster')
                # Ensure we're only loading for Nebraska counties. If your lat_longs_clean.tsv only has NE counties for 'county' type, this is fine.
                # If it has other counties, you'd need an additional filter here or in the data.
                self.county_coords[str(row['name'])] = (str(row['latitude']), str(row['longitude']))

            logger.info(f"Loaded {len(self.state_coords)} states and {len(self.county_coords)} counties.")
            
        except Exception as e:
            logger.error(f"Error loading lat/long data from {self.lat_long_file}: {e}")
            raise

    def get_coordinates(self, state_abbr: str, division_full: str) -> Tuple[str, str, str]:
        """
        Gets coordinates and county name based on state abbreviation and full division string.
        Prioritizes NE county coordinates; otherwise, uses state-level coordinates for US states.
        """
        county_name_found = '' # This will only be set for NE counties
        lat = ''
        lon = ''

        # --- Logic for Nebraska counties ---
        # Assuming NE division format is 'NE/CountyName'
        if state_abbr == 'NE' and division_full.startswith('NE/'):
            # Extract county name (e.g., "NE/Lancaster" -> "Lancaster")
            county_part = division_full.split('/', 1)[1].strip()
            
            # Special case for Lincoln -> Lancaster, as per your existing logic
            if county_part.lower() == 'lincoln':
                county_part = 'Lancaster'
            
            # Clean up (e.g., 'Keya-Paha' -> 'Keya Paha' if that's how it's in your county_coords)
            county_key_for_lookup = county_part.replace('-', ' ').strip()

            if county_key_for_lookup in self.county_coords:
                county_name_found = county_key_for_lookup
                lat, lon = self.county_coords[county_name_found]
                return county_name_found, lat, lon
            else:
                # If specific NE county not found, fall through to try state-level NE coordinates
                logger.warning(f"No specific county coordinates found for NE county: '{county_key_for_lookup}' from '{division_full}'. Trying state-level NE coordinates.")

        # --- Logic for all US states (including NE if county not found, and DC) ---
        # This block now handles ALL state-level lookups for US states
        if state_abbr in self.state_coords:
            lat, lon = self.state_coords[state_abbr]
            # No county_name_found if it's a state-level coordinate assignment
            return county_name_found, lat, lon # Return empty county_name_found here

        # --- Logic for non-US or unmapped entries ---
        # If we reach here, it means no US state or NE county was found
        # This will return empty strings for lat, lon, and county_name_found
        logger.debug(f"No coordinates found for state: '{state_abbr}' or division: '{division_full}'. Skipping.")
        return county_name_found, lat, lon

    def update_metadata(self):
        """Updates the metadata file with coordinates and county information."""
        try:
            # Load coordinate data
            self.load_lat_longs()
            print(f"DEBUG: Loaded state_coords: {self.state_coords.keys()}")
            print(f"DEBUG: Loaded county_coords: {self.county_coords.keys()}")
            # Add a break point here if you know how to use a debugger
            # import pdb; pdb.set_trace()
            # Read metadata file
            metadata_df = pd.read_csv(self.metadata_file, sep='\t')
            
            # Add county column if it doesn't exist
            if 'county' not in metadata_df.columns:
                metadata_df['county'] = ''
            
            # Process each row
            for idx, row in metadata_df.iterrows():
                county, lat, lon = self.get_coordinates(row['state'], row['division'])
                
                if county:
                    metadata_df.at[idx, 'county'] = county
                if lat and lon:
                    # Check if we need to handle a combined latitudelongitude column
                    if 'latitudelongitude' in metadata_df.columns:
                        metadata_df.at[idx, 'latitudelongitude'] = f"{lat}\t{lon}"
                    else:
                        # Handle separate latitude/longitude columns
                        if 'latitude' not in metadata_df.columns:
                            metadata_df['latitude'] = ''
                        if 'longitude' not in metadata_df.columns:
                            metadata_df['longitude'] = ''
                        metadata_df.at[idx, 'latitude'] = lat
                        metadata_df.at[idx, 'longitude'] = lon
            
            # Save updated metadata back to updated_metadata.tsv
            output_file = self.metadata_file.parent / 'updated_metadata.tsv'
            metadata_df.to_csv(output_file, sep='\t', index=False)
            logger.info(f"Metadata successfully updated with coordinates and county information. Saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            raise

def main():
    """Main function to run the script."""
    try:
        updater = LocationDataUpdater(
            # Updated path to the lat_longs file in the new directory
            '/home/fauverlab/nextstrain/WNV_build_update_May25/config/lat_longs_clean.tsv',
            # Updated path to your metadata file in the new directory
            '/home/fauverlab/nextstrain/WNV_build_update_May25/data/updated_metadata.tsv'
        )
        updater.update_metadata()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()
