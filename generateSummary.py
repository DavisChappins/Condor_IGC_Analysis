import os
import glob
from analyzeIGC import *
from addTimeDeltas import *
from helperFile import *
from plotThermals import *
from plotGlideSpeeds import *
from generateAdditionalSummary import *
from formatExcel import *

'''
------ Place igc files to be analyzed in the folder /igcFiles
'''

##################    VARIABLES     ####################

AAT = 0  # set to 1 if AAT, set to 0 if racing task
# To run an AAT analysis in Condor you must first add in condor.club results data using aatConvert.py

tp_adjustment_km = -11
# calculate turnpoint radius (if 360 circle) * num of TPs
# example: triangle task with start line/finish line and 2 circular TPs of radius 3000m = 2*3km = -6km adjustment
# (6 km less distance flown than to center of circle

##################    VARIABLES     ####################

# remove old summary.csv file
file_path = "summary.csv"

if os.path.exists(file_path):
    os.remove(file_path)
    print(f'The old "{file_path}" has been removed')
    print('')
else:
    pass

delete_csv_files_with_prefix('sequenceData')
print('sequence files deleted')

delete_csv_files_with_prefix('freq_gs_kts_')
print('sequence files deleted')

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Optional Section: Read the .fpl file to get TPHeight1 value FPL must be in local folder---
task_start_height_ft = None
task_finish_height_ft = None

fpl_files = glob.glob(os.path.join(script_dir, "*.fpl"))
if fpl_files:
    fpl_file = fpl_files[0]
    with open(fpl_file, "r") as f:
        # Read all lines so we can process both TPHeight1 and TPWidth*
        lines = f.readlines()

    # --- Get TPHeight1 for start height ---
    for line in lines:
        if line.startswith("TPHeight1="):
            try:
                task_start_height_meters = float(line.split("=")[1].strip())
                task_start_height_ft = task_start_height_meters * 3.28084
                print(f"TPHeight1 found: {task_start_height_meters} m -> {task_start_height_ft:.2f} ft")
            except ValueError:
                print("Error parsing TPHeight1 value. Using default start height (None).")
            break

    # --- Get finish height from the highest TPWidth value ---
    max_index = -1
    finish_height_meters = None
    for line in lines:
        # Use regex to capture TPWidth followed by a number and then its value
        match = re.match(r"TPWidth(\d+)\s*=\s*(\S+)", line)
        if match:
            index = int(match.group(1))
            try:
                value = float(match.group(2))
            except ValueError:
                print(f"Error parsing TPWidth{index} value. Skipping.")
                continue
            if index > max_index:
                max_index = index
                finish_height_meters = value

    if max_index != -1 and finish_height_meters is not None:
        task_finish_height_ft = finish_height_meters * 3.28084
        print(f"TPWidth{max_index} found: {finish_height_meters} m -> {task_finish_height_ft:.2f} ft")
    else:
        print("No valid TPWidth entry found. Proceeding without finish height.")
else:
    print("No .fpl file found. Proceeding without start height.")
    
    

# Relative path to the folder
folder_path = os.path.join(script_dir, "igcFiles")

# Find all files in the folder with the .igc extension
igc_files = glob.glob(os.path.join(folder_path, "*.igc"))
print(f"Number of .igc files in {folder_path}: {len(igc_files)}")

detailed_summary_list = []
header_row = ['pilot_id',
              'Rule1_glide_avg_gs_kts', 'Rule1_glide_avg_ias_kts', 'Rule1_glide_ratio', 'Rule1_glide_ratio_better_actual_MC',
              'Rule1_ideal_ias_given_avg_climb_kts', 'Rule1_glide_avg_dist_nmi', 'Rule2_avg_climb_rate_kts',
              'Rule2_ideal_MC_given_avg_ias_kts', 'Rule3_total_glide_distance_nmi', 'Rule3_total_glide_more_percent',
              'Rule4_avg_altitude_ft', 'start_speed_gs_kts', 'start_altitude_ft', 'start_efficiency_score', 'height_loss_due_to_start_energy_ft',
              'total_energy_start_MJ', 'finish_speed_gs_kts', 'finish_altitude_ft', 'finish_efficiency_score', 'height_loss_due_to_finish_energy_ft','total_energy_finish_MJ',
              'task_speed_kmh','task_speed_kmh', 'task_time_hmmss', 'task_distance_km', 'total_glide_time_mmss', 'total_thermal_time_mmss']

detailed_summary_list.append(header_row)

# Loop through each file and analyze it.
# Pass in both tp_adjustment_km and the optional task start_height_ft (which may be None).
for igc_file in igc_files:
    detailed_summary = add_igc_to_summary(igc_file, tp_adjustment_km, task_start_height_ft, task_finish_height_ft)
    print(f'Processed {igc_file}')
    if detailed_summary is not None:
        detailed_summary_list.append(detailed_summary)
print('')
print(f'Analyzed {len(igc_files)} total .igc files and generated {file_path}')

# add rank and reorder by rank
reorder_csv_by_speed(file_path)

# find time behind leader
if AAT == 1:
    AAT_Task_time_behind_rank1(file_path)  # AAT ONLY
elif AAT == 0:
    Task_time_behind_rank1(file_path)

# add time behind rank 1 for gliding performance
Rule1_add_time_delta(file_path)

# add time delta from best climb
Rule2_add_time_delta(file_path)

# do time lost analysis, rule 3
Rule3_add_time_delta(file_path)


Start_energy_add_time_delta(file_path)
Finish_energy_add_time_delta(file_path)

# Generate thermal plot vs time
print("Plotting thermals")
plotThermalsInteractive()

print("Plotting glide speeds")
plot_freq_vs_groundspeed()

# must have generateAdditionalSummary.py
generate_slim_summary(AAT)
generate_slim_rules_summary()
generate_slim_timing_summary()
generate_slim_gap_analysis_summary()

# format summary
format_excel_from_csv("summary.csv","summary.xlsx")
