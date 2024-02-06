import os
import glob
from analyzeIGC import *
from addTimeDeltas import *
from helperFile import *

'''

------ Place igc files to be analyzed in the folder /igcFiles

'''

##################    VARIABLES     ####################

AAT = 0 # set to 1 if AAT, set to 0 if racing task
#To run an AAT analysis in Condor you must first add in condor.club results data using aatConvert.py

##################    VARIABLES     ####################


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


delete_csv_files_with_prefix('sequenceData')
print('sequence files deleted')

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Relative path to the folder
folder_path = os.path.join(script_dir, "igcFiles")

# Find all files in the folder with the .igc extension
igc_files = glob.glob(os.path.join(folder_path, "*.igc"))

# Print the number of .igc files found
print(f"Number of .igc files in {folder_path}: {len(igc_files)}")

detailed_summary_list = []
header_row = ['pilot_id',
                'Rule1_glide_avg_gs_kts', 'Rule1_glide_avg_ias_kts', 'Rule1_glide_ratio', 'Rule1_glide_ratio_better_actual_MC','Rule1_ideal_ias_given_avg_climb_kts',
                'Rule1_glide_avg_dist_nmi', 'Rule2_avg_climb_rate_kts', 'Rule2_ideal_MC_given_avg_ias_kts', 'Rule3_total_glide_distance_nmi',
                'Rule3_total_glide_more_percent', 'Rule4_avg_altitude_ft', 'start_speed_gs_kts', 'start_altitude_ft',
                'total_energy_start_MJ', 'finish_speed_gs_kts', 'finish_altitude_ft', 'total_energy_finish_MJ',
                'task_speed_kmh','task_speed_kmh', 'task_time_hmmss', 'task_distance_km', 'total_glide_time_mmss', 'total_thermal_time_mmss']


detailed_summary_list.append(header_row)

# Loop through each file and analyze it
for igc_file in igc_files:
    detailed_summary = add_igc_to_summary(igc_file)
    print(f'Processed {igc_file}')
    if detailed_summary is not None:
        detailed_summary_list.append(detailed_summary)
    #print(detailed_summary_list)
print('')
print(f'Analyzed {len(igc_files)} total .igc files and generated {file_path}')

#print(detailed_summary_list)






#add rank and reorder by rank
reorder_csv_by_speed(file_path)

#find time behind leader
if AAT == 1:
    AAT_Task_time_behind_rank1(file_path)  #### AAT ONLY ###
elif AAT == 0:
    Task_time_behind_rank1(file_path)

#add time behidn rank 1 for gliding performance
Rule1_add_time_delta(file_path)

#add time delta from best climb
Rule2_add_time_delta(file_path)

#task_distance_km = detailed_summary_list[1][20]

#do time lost analysis, rule 3
Rule3_add_time_delta(file_path)



#max_start_height_ft = detailed_summary[15]
#mass_kg = 600 #18m is 600, 15m is 500, club is 250 


