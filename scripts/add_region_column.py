import pandas as pd

def add_region_column(metadata_file):
   # Define the region mappings
   east_counties = ['Cuming', 'Dodge', 'Douglas', 'Lancaster', 'Platte', 
                    'Richardson', 'Saline', 'Wayne', 'Dakota', 'Sarpy', 'Thurston']
   
   central_counties = ['Adams', 'Dawson', 'Hall', 'Holt', 'Lincoln', 
                      'Red Willow', 'Garfield', 'York', 'Madison', 'Cherry', 'Seward', 'Phelps']
   
   west_counties = ['Box Butte', 'Scotts Bluff', 'Chase', 'Dawes', 'Garden',]
   
   # Read the metadata file
   df = pd.read_csv(metadata_file, sep='\t')
   
   # Initialize 'Region' column with empty values
   df['Region'] = ''
   
   # Set region based on county (Nebraska counties)
   for idx, row in df.iterrows():
       county = row.get('county', '')
       if county in east_counties:
           df.at[idx, 'Region'] = 'NE_East'
       elif county in central_counties:
           df.at[idx, 'Region'] = 'NE_Central'
       elif county in west_counties:
           df.at[idx, 'Region'] = 'NE_West'

   # Define US-wide regions for non-Nebraska states
   us_regions = {
       'Northeast': ['ME', 'VT', 'NH', 'NY', 'MA', 'RI', 'PA', 'NJ', 'CT', 'MD', 'DC', 'DE'],
       'South': ['KY', 'WV', 'VA', 'AR', 'TN', 'NC', 'SC', 'LA', 'MS', 'AL', 'GA', 'FL', 'OK', 'TX'],
       'Midwest': ['ND', 'MN', 'IL', 'WI', 'MI', 'SD', 'IA', 'IN', 'OH', 'MO', 'KS', 'NE'],
       'West': ['AK', 'WA', 'ID', 'MT', 'OR', 'NV', 'WY', 'CA', 'UT', 'CO', 'HI', 'AZ', 'NM']
   }

   # Assign US regions for non-Nebraska states
   for idx, row in df.iterrows():
       state = row.get('state', '')
       # Only assign if Region is still empty (i.e., not a Nebraska county)
       if df.at[idx, 'Region'] == '' and state:
           for region_name, states_list in us_regions.items():
               if state in states_list:
                   df.at[idx, 'Region'] = region_name
                   break
   
   # Count counties without region assigned
   missing_region = df[(df['state'] == 'NE') & (df['Region'] == '') & (df['county'] != '')]
   if not missing_region.empty:
       print(f"Warning: {len(missing_region)} Nebraska counties don't have a region assigned:")
       for county in missing_region['county'].unique():
           print(f"  - {county}")
   
   # Save the updated metadata
   df.to_csv(metadata_file, sep='\t', index=False)
   print(f"Added Region column to {metadata_file}")
   print(f"NE_East counties: {len(df[df['Region'] == 'NE_East'])}")
   print(f"NE_Central counties: {len(df[df['Region'] == 'NE_Central'])}")
   print(f"NE_West counties: {len(df[df['Region'] == 'NE_West'])}")
   print(f"Northeast states: {len(df[df['Region'] == 'Northeast'])}")
   print(f"South states: {len(df[df['Region'] == 'South'])}")
   print(f"Midwest states: {len(df[df['Region'] == 'Midwest'])}")
   print(f"West states: {len(df[df['Region'] == 'West'])}")

if __name__ == "__main__":
   metadata_file = '/home/fauverlab/nextstrain/WNV_build_update_May25/data/updated_metadata.tsv'
   add_region_column(metadata_file)
