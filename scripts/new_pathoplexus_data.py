import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
from typing import Dict, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# State coordinates from provided data
STATE_COORDS = {
    'Alabama': (32.8067, -86.7911),
    'Alaska': (61.3707, -152.4044),
    'Arizona': (33.7298, -111.4312),
    'Arkansas': (34.9697, -92.3731),
    'California': (36.1162, -119.6816),
    'Colorado': (39.0598, -105.3111),
    'Connecticut': (41.5978, -72.7554),
    'Delaware': (39.3185, -75.5071),
    'Florida': (27.7663, -81.6868),
    'Georgia': (33.0406, -83.6431),
    'Hawaii': (21.0943, -157.4983),
    'Idaho': (44.2405, -114.4788),
    'Illinois': (40.3495, -88.9861),
    'Indiana': (39.8494, -86.2583),
    'Iowa': (42.0115, -93.2105),
    'Kansas': (38.5266, -96.7265),
    'Kentucky': (37.6681, -84.6701),
    'Louisiana': (31.1695, -91.8678),
    'Maine': (44.6939, -69.3819),
    'Maryland': (39.0639, -76.8021),
    'Massachusetts': (42.2302, -71.5301),
    'Michigan': (43.3266, -84.5361),
    'Minnesota': (45.6945, -93.9002),
    'Mississippi': (32.7416, -89.6787),
    'Missouri': (38.4561, -92.2884),
    'Montana': (46.9219, -110.4544),
    'Nebraska': (41.1254, -98.2681),
    'Nevada': (38.3135, -117.0554),
    'New Hampshire': (43.4525, -71.5639),
    'New Jersey': (40.2989, -74.5210),
    'New Mexico': (34.8405, -106.2485),
    'New York': (42.1657, -74.9481),
    'North Carolina': (35.6301, -79.8064),
    'North Dakota': (47.5289, -99.7840),
    'Ohio': (40.3888, -82.7649),
    'Oklahoma': (35.5653, -96.9289),
    'Oregon': (44.5720, -122.0709),
    'Pennsylvania': (40.5908, -77.2098),
    'Rhode Island': (41.6809, -71.5118),
    'South Carolina': (33.8569, -80.9450),
    'South Dakota': (44.2998, -99.4388),
    'Tennessee': (35.7478, -86.6923),
    'Texas': (31.0545, -97.5635),
    'Utah': (40.1500, -111.8624),
    'Vermont': (44.0459, -72.7107),
    'Virginia': (37.7693, -78.1690),
    'Washington': (47.4009, -121.4905),
    'West Virginia': (38.4912, -80.9545),
    'Wisconsin': (44.2685, -89.6165),
    'Wyoming': (42.7559, -107.3025),
    'DC': (38.9072, -77.0369)
}

# Mapping from full state names to abbreviations
STATE_ABBREVIATIONS = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 
    'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 
    'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 
    'DC': 'DC'
}

def standardize_date(date_str: str) -> str:
    """
    Standardize various date formats to Nextstrain format (YYYY-MM-DD or YYYY-XX-XX)
    
    Handles:
    - YYYY-MM-DD (already correct) -> keep as-is
    - YYYY-XX-XX (already correct) -> keep as-is  
    - M/D/YYYY or MM/DD/YYYY -> YYYY-MM-DD
    - YYYY (year only) -> YYYY-XX-XX
    - Invalid/empty -> XXXX-XX-XX
    """
    if not date_str or date_str.strip() == '':
        return 'XXXX-XX-XX'
    
    date_str = date_str.strip()
    
    # Already in correct Nextstrain format (YYYY-MM-DD or YYYY-XX-XX)
    if re.match(r'^\d{4}-[\dX]{2}-[\dX]{2}$', date_str):
        return date_str
    
    # Handle year-only format (e.g., "2016", "2017")
    if re.match(r'^\d{4}$', date_str):
        return f"{date_str}-XX-XX"
    
    # Handle US format dates (M/D/YYYY or MM/DD/YYYY)
    us_date_match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
    if us_date_match:
        month, day, year = us_date_match.groups()
        try:
            # Validate the date is real
            datetime(int(year), int(month), int(day))
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except ValueError:
            logger.warning(f"Invalid US date format: {date_str}")
            return 'XXXX-XX-XX'
    
    # Handle partial ISO dates that might be malformed
    iso_partial_match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', date_str)
    if iso_partial_match:
        year, month, day = iso_partial_match.groups()
        try:
            # Validate and reformat with zero-padding
            datetime(int(year), int(month), int(day))
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except ValueError:
            logger.warning(f"Invalid ISO date: {date_str}")
            return f"{year}-XX-XX"  # Keep year if it's valid
    
    # If we can't parse it, log and return unknown
    logger.warning(f"Unable to parse date format: {date_str}")
    return 'XXXX-XX-XX'

def extract_state_improved(text: str) -> tuple:
    """Enhanced state extraction returning (state_abbr, standardized_division)"""
    if not text:
        return None, text
        
    # Clean quotes and strip
    clean_text = text.replace('"', '').strip()
    
    # Handle specific problematic cases first (including truncated text)
    problematic_cases = {
        'San Gabriel Val…': ('CA', 'CA/San Gabriel Valley'),
        'Lexington,MA': ('MA', 'MA/Lexington'), 
        'Black Hawk, Iowa': ('IA', 'IA/Black Hawk'),
        'Black Hawk, Iow…': ('IA', 'IA/Black Hawk'),  # Handle truncated version
        'Polk, Iowa': ('IA', 'IA/Polk'),
        'DesMoines, Iowa': ('IA', 'IA/Des Moines'),
        "O'Brien, Iowa": ('IA', "IA/O'Brien"),
        'Washington DC': ('DC', 'DC/Washington'),
        'Miami Florida': ('FL', 'FL/Miami'),
        'Brandford,CT': ('CT', 'CT/Bradford'),
    }
    
    # Check problematic cases first - these return (state_abbr, division)
    for pattern, (state_abbr, standardized_division) in problematic_cases.items():
        if pattern in text:
            return state_abbr, standardized_division
    
    # Handle other truncated Iowa cases (ending with "Iow…")
    if ', Iow…' in clean_text:
        county_part = clean_text.split(',')[0].strip()
        return 'IA', f'IA/{county_part}'
    
    # Extract from "County, State" format
    if ',' in clean_text:
        parts = [p.strip() for p in clean_text.split(',')]
        if len(parts) >= 2:
            county_part = parts[0]
            state_part = parts[-1]
            
            # Check if it's a state abbreviation
            if state_part.upper() in STATE_ABBREVIATIONS.values():
                return state_part.upper(), f"{state_part.upper()}/{county_part}"
            
            # Check if it's a full state name
            if state_part in STATE_ABBREVIATIONS:
                state_abbr = STATE_ABBREVIATIONS[state_part]
                return state_abbr, f"{state_abbr}/{county_part}"
    
    # Handle state-only entries like "Connecticut"
    if clean_text in STATE_ABBREVIATIONS:
        state_abbr = STATE_ABBREVIATIONS[clean_text]
        return state_abbr, f"{state_abbr}/{clean_text}"
    
    # Check for full state names anywhere in text
    for full_name, abbr in STATE_ABBREVIATIONS.items():
        if full_name in clean_text:
            return abbr, f"{abbr}/{clean_text}"
            
    return None, clean_text

def fetch_url_data(url: str, timeout: int = 30) -> Dict:
    """Fetch data from URL with proper error handling"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        if not table:
            raise ValueError("No table found in the response")
            
        data = {}
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        
        columns = {
            'accession': next(i for i, h in enumerate(headers) if 'Accession' in h),
            'collection_date': next(i for i, h in enumerate(headers) if 'Collection date' in h),
            'subdivision': next(i for i, h in enumerate(headers) if 'subdivision level 1' in h.lower()),
            'authors': next(i for i, h in enumerate(headers) if 'Authors' in h)
        }
        
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            acc = cells[columns['accession']].get_text(strip=True).split('.')[0]
            
            # CLEAN QUOTES HERE - this prevents the quote issue
            data[acc] = {
                'collection_date': cells[columns['collection_date']].get_text(strip=True).replace('"', ''),
                'subdivision': cells[columns['subdivision']].get_text(strip=True).replace('"', ''),
                'authors': cells[columns['authors']].get_text(strip=True).replace('"', '')
            }
            
        return data
        
    except Exception as e:
        logger.error(f"Error fetching URL data: {str(e)}")
        raise

def process_new_accession(acc: str, url_data: Dict, original_columns: list) -> Dict:
    """Process single accession data with built-in standardization"""
    raw_subdivision = url_data[acc]['subdivision']
    raw_date = url_data[acc]['collection_date']
    
    # Extract state and get standardized division format
    state_abbr, standardized_division = extract_state_improved(raw_subdivision)
    
    # Standardize the date format
    standardized_date = standardize_date(raw_date)
    
    # Get coordinates using full state name
    state_full = next((k for k, v in STATE_ABBREVIATIONS.items() if v == state_abbr), None)
    coords = STATE_COORDS.get(state_full, (None, None)) if state_full else (None, None)
    
    return {
        'strain': acc,
        'virus': 'wnv',
        'accession': acc,
        'date': standardized_date,  # Now properly standardized
        'region': 'North America',
        'country': 'USA',
        'state': state_abbr or '',  # This ensures state is properly set
        'division': standardized_division,  # Now in STATE/COUNTY format
        'segment': 'genome',
        'authors': url_data[acc]['authors'],  # Already cleaned of quotes in fetch_url_data
        'latitude': str(coords[0]) if coords[0] else '',
        'longitude': str(coords[1]) if coords[1] else '',
        'Species': '',
        **{col: '' for col in original_columns if col not in ['strain', 'virus', 'accession', 'date', 'region', 'country', 'state', 'division', 'segment', 'authors', 'latitude', 'longitude', 'Species']}
    }

def update_metadata(metadata_file: str, url: str) -> int:
    """Main function to update metadata"""
    try:
        metadata_df = pd.read_csv(metadata_file, sep="\t")
        existing_accessions = set(metadata_df['accession'])
        
        url_data = fetch_url_data(url)
        new_accessions = set(url_data.keys()) - existing_accessions
        
        if not new_accessions:
            logger.info("No new accessions found")
            return 0
            
        logger.info(f"Processing {len(new_accessions)} new accessions")
        
        with ThreadPoolExecutor() as executor:
            new_rows = list(executor.map(
                lambda acc: process_new_accession(acc, url_data, metadata_df.columns),
                new_accessions
            ))
        
        new_df = pd.DataFrame(new_rows)
        metadata_df = pd.concat([metadata_df, new_df], ignore_index=True)
        metadata_df = metadata_df.fillna('')
        
        metadata_df.to_csv(metadata_file, sep='\t', index=False)
        return len(new_accessions)
        
    except Exception as e:
        logger.error(f"Error updating metadata: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # CORRECT PATH - pointing to your actual working directory
        metadata_file = '/home/fauverlab/nextstrain/WNV_build_update_May25/data/updated_metadata.tsv'
        url = "https://pathoplexus.org/west-nile/search?geoLocCountry=USA&visibility_geoLocLatitude=true&visibility_geoLocLongitude=true&visibility_lineage=false&visibility_authors=true&visibility_geoLocAdmin1=false&visibility_geoLocCity=true&column_geoLocLatitude=true&column_geoLocLongitude=true&column_geoLocAdmin1=true&column_geoLocCity=false&column_geoLocAdmin2=false&column_hostNameCommon=false&column_hostNameScientific=true"
        
        new_count = update_metadata(metadata_file, url)
        logger.info(f"Successfully added {new_count} new accessions")
        
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)
