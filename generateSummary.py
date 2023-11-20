import os
import glob
from analyzeIGC import *


'''

------ Place igc files to be analyzed in the folder /igcFiles

'''

#remove old summary.csv file

file_path = "summary.csv"

# Check if the file exists
if os.path.exists(file_path):
    # If it exists, delete the file
    os.remove(file_path)
    print(f'The old "{file_path}" has been removed')
    print('')
else:
    pass
    



# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Relative path to the folder
folder_path = os.path.join(script_dir, "igcFiles")

# Find all files in the folder with the .igc extension
igc_files = glob.glob(os.path.join(folder_path, "*.igc"))

# Print the number of .igc files found
print(f"Number of .igc files in {folder_path}: {len(igc_files)}")

# Loop through each file and analyze it
for igc_file in igc_files:
    add_igc_to_summary(igc_file)
    print(f'Processed {igc_file}')
print('')
print(f'Analyzed {len(igc_files)} total .igc files')

#add rank and reorder by rank
reorder_csv_by_speed(file_path)

