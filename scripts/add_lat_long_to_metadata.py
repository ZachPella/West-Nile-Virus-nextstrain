import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocationDataUpdater:
    """
    A class to update metadata with latitude and longitude coordinates for states and counties.

    This class reads latitude and longitude data from a file, processes it, and updates
    a metadata file with the corresponding coordinates.

    Attributes
    ----------
    lat_long_file : Path
        The file path to the latitude and longitude data.
    metadata_file : Path
        The file path to the metadata that needs to be updated.
    state_coords : Dict[str, Tuple[str, str]]
        A dictionary to store state coordinates (key: state, value: (latitude, longitude)).
    county_coords : Dict[str, Tuple[str, str]]
        A dictionary to store county coordinates (key: county name, value: (latitude, longitude)).
    """

    def __init__(self, lat_long_file: str, metadata_file: str):
        """
        Initialize the LocationDataUpdater with file paths.

        Parameters
        ----------
        lat_long_file : str
            The path to the file containing latitude and longitude data.
        metadata_file : str
            The path to the metadata file that needs to be updated.
        """
        self.lat_long_file = Path(lat_long_file)
        self.metadata_file = Path(metadata_file)
        self.state_coords = {}
        self.county_coords = {}

    def load_lat_longs(self):
        """
        Load latitude and longitude data from the file.

        This method reads the latitude and longitude data from the file and separates
        it into state and county coordinates. The data is stored in `state_coords` and
        `county_coords` dictionaries.

        Raises
        ------
        Exception
            If there is an error loading the data, an exception is raised and logged.
        """
        try:
            df = pd.read_csv(self.lat_long_file, sep='\t')

            # Split into state and county coordinates
            for _, row in df.iterrows():
                if row['state'] == 'state':  # State entries
                    self.state_coords[row['DC']] = (row['38.9072'], row['-77.0369'])
                elif row['state'] == 'county':  # County entries
                    county_name = row['DC']
                    # Handle special case where county name has a hyphen
                    county_name = county_name.replace('-', ' ')
                    self.county_coords[county_name] = (row['38.9072'], row['-77.0369'])

            logger.info(f"Loaded {len(self.state_coords)} states and {len(self.county_coords)} counties")

        except Exception as e:
            logger.error(f"Error loading lat/long data: {e}")
            raise

    def get_coordinates(self, state: str, division: str) -> Tuple[str, str, str]:
        """
        Get coordinates and county name based on the state and division.

        Parameters
        ----------
        state : str
            The state abbreviation (e.g., 'NE' for Nebraska).
        division : str
            The division information, which may include county details.

        Returns
        -------
        Tuple[str, str, str]
            A tuple containing:
            - county (str): The name of the county (if applicable).
            - lat (str): The latitude coordinate.
            - lon (str): The longitude coordinate.
        """
        county = ''
        lat = ''
        lon = ''

        if state == 'NE' and division and division.startswith('NE/'):
            # Extract county name for Nebraska entries
            county = division.split('/', 1)[1].strip()

            # Special case for Lincoln -> Lancaster
            if county.lower() == 'lincoln':
                county = 'Lancaster'

            # Look up county coordinates
            county = county.replace('-', ' ')  # Handle hyphenated county names
            if county in self.county_coords:
                lat, lon = self.county_coords[county]
            else:
                logger.warning(f"No coordinates found for Nebraska county: {county}")

        elif state in self.state_coords:
            # Use state coordinates for non-Nebraska entries
            lat, lon = self.state_coords[state]

        return county, lat, lon

    def update_metadata(self):
        """
        Update the metadata file with coordinates and county information.

        This method reads the metadata file, adds or updates latitude, longitude,
        and county information, and saves the updated metadata to a new file.

        Raises
        ------
        Exception
            If there is an error updating the metadata, an exception is raised and logged.
        """
        try:
            # Load coordinate data
            self.load_lat_longs()

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
                    metadata_df.at[idx, 'latitude'] = lat
                    metadata_df.at[idx, 'longitude'] = lon

            # Save updated metadata
            output_file = self.metadata_file.parent / 'metadata.tsv'
            metadata_df.to_csv(output_file, sep='\t', index=False)
            logger.info("Metadata successfully updated with coordinates and county information")

        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            raise


def main():
    """
    Main function to run the script.

    This function initializes the LocationDataUpdater and calls the `update_metadata` method
    to process and update the metadata file.

    Raises
    ------
    Exception
        If the script fails, an exception is raised and logged.
    """
    try:
        updater = LocationDataUpdater(
            '/config/lat_longs_clean.tsv',
            '/data/metadata.tsv'
        )
        updater.update_metadata()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise


if __name__ == "__main__":
    main()
