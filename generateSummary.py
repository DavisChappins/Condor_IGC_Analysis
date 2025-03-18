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

AAT = None  # Can be manually set to 1 for AAT, 0 for racing task, or None for auto-detection
# To run an AAT analysis in Condor you must first add in condor.club results data using aatConvert.py

tp_adjustment_km = None  # Will be auto-calculated from FPL file. Can be manually set if needed.

# Set up logging to both file and console
import sys
class TeeStream:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.logfile = open(filename, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.logfile.write(message)
        self.logfile.flush()

    def flush(self):
        self.terminal.flush()
        self.logfile.flush()

def setup_logging():
    log_file = "task_analysis.log"
    sys.stdout = TeeStream(log_file)
    print(f"Logging output to: {os.path.abspath(log_file)}\n")

setup_logging()

def calculate_tp_adjustment(fpl_lines):
    """Calculate total TP adjustment (negative of total bonus distance) from FPL file content"""
    import math
    
    def bearing(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        angle = math.degrees(math.atan2(dx, dy))
        if angle < 0:
            angle += 360
        return angle

    # Parse turnpoints from FPL
    turnpoints = []
    tp_count = 0
    
    # First get number of turnpoints
    for line in fpl_lines:
        if line.startswith("Count="):
            try:
                tp_count = int(line.split("=")[1].strip())
                break
            except ValueError:
                return 0
    
    # Then parse each turnpoint
    current_tp = {}
    for line in fpl_lines:
        for i in range(tp_count):
            if line.startswith(f"TPName{i}="):
                current_tp = {'index': i, 'name': line.split("=")[1].strip()}
            elif line.startswith(f"TPPosX{i}="):
                current_tp['x'] = float(line.split("=")[1].strip())
            elif line.startswith(f"TPPosY{i}="):
                current_tp['y'] = float(line.split("=")[1].strip())
            elif line.startswith(f"TPRadius{i}="):
                current_tp['radius'] = float(line.split("=")[1].strip())
            elif line.startswith(f"TPAngle{i}="):
                current_tp['angle'] = float(line.split("=")[1].strip())
                if len(current_tp) == 6:  # Have all required fields including name
                    turnpoints.append(current_tp)
                    current_tp = {}
    
    print("\nCalculating TP adjustments:")
    print("-" * 50)
    
    # Calculate bonus distances for each turnpoint
    total_bonus = 0
    for i in range(1, len(turnpoints)-1):  # Skip first (start) and handle last separately
        tp = turnpoints[i]
        tp_bonus = 0
        if abs(tp['angle'] - 360) <= 1e-2:  # Only if it's a full cylinder
            if i == 1:  # Start line
                tp_bonus = tp['radius'] / 1000.0
                print(f"Start ({tp['name']}): {tp_bonus:.2f} km bonus (radius = {tp['radius']/1000:.2f} km)")
            else:
                # Calculate effective angle for regular turnpoint
                inc = bearing(turnpoints[i-1]['x'], turnpoints[i-1]['y'], tp['x'], tp['y'])
                out = bearing(tp['x'], tp['y'], turnpoints[i+1]['x'], turnpoints[i+1]['y'])
                raw_diff = abs(out - inc)
                eff_angle = raw_diff if raw_diff <= 180 else 360 - raw_diff
                tp_bonus = 2 * (tp['radius'] / 1000.0) * math.sin(math.radians(eff_angle / 2))
                print(f"TP {i} ({tp['name']}): {tp_bonus:.2f} km bonus (radius = {tp['radius']/1000:.2f} km, angle = {eff_angle:.1f}°)")
            total_bonus += tp_bonus
    
    # Handle finish (last turnpoint)
    if len(turnpoints) > 0:
        last_tp = turnpoints[-1]
        if abs(last_tp['angle'] - 360) <= 1e-2:
            tp_bonus = last_tp['radius'] / 1000.0
            print(f"Finish ({last_tp['name']}): {tp_bonus:.2f} km bonus (radius = {last_tp['radius']/1000:.2f} km)")
            total_bonus += tp_bonus
    
    print("-" * 50)
    print(f"Total bonus distance: {total_bonus:.2f} km")
    print(f"Final TP adjustment: {-total_bonus:.2f} km")
    print("")
    
    return -total_bonus  # Return negative of total bonus

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
aat_detected = None

fpl_files = glob.glob(os.path.join(script_dir, "*.fpl"))
if fpl_files:
    fpl_file = fpl_files[0]
    with open(fpl_file, "r") as f:
        # Read all lines so we can process both TPHeight1, TPWidth* and AAT status
        lines = f.readlines()

    # --- Check if task is AAT ---
    for line in lines:
        if line.strip() == "AAT=1":
            aat_detected = 1
            print("Task type detected: AAT (Assigned Area Task)")
            break
        elif line.strip() == "AAT=0":
            aat_detected = 0
            print("Task type detected: Racing Task")
            break

    # If AAT is not manually set, use the detected value
    if AAT is None:
        AAT = aat_detected if aat_detected is not None else 0
        if aat_detected is None:
            print("Warning: Could not detect task type in FPL file. Defaulting to Racing Task.")

    # Calculate TP adjustment if not manually set
    if tp_adjustment_km is None:
        if AAT == 1:
            tp_adjustment_km = 0  # No adjustment for AAT tasks
            print("AAT task detected - no TP adjustment applied")
        else:
            tp_adjustment_km = calculate_tp_adjustment(lines)
            print(f"TP adjustment calculated from FPL: {tp_adjustment_km:.2f} km")

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
