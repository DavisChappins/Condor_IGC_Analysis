import os
import glob

def delete_csv_files_with_prefix(prefix):
    # Create a pattern to match CSV files starting with the specified prefix
    pattern = f'{prefix}*.csv'

    # Use glob to find all matching files
    files_to_delete = glob.glob(pattern)

    # Delete each matching file
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

# Replace 'sequenceData' with the desired prefix
file_prefix = 'sequenceData'

delete_csv_files_with_prefix(file_prefix)