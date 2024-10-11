
import os
from datetime import datetime, timedelta

#data needs to come from https://members.ssa.org/ContestResults.asp?contestId=2548&ContestDetailId=30407&ContestName=2023+US+18%2DMeter+Nationals&ContestDate=8/16/2023&ResultsUpdate=True
#as an example
#need to format in excel first
#looking for: IGC Filename, glider type, Start Time, Time on Course (TOC)
#additional data needed for AAT tasks
##distance flown is KM and task speed is kmh, need to convert from sm/mph

#Task Data
TaskMaxStartAltitude_ft = 10000 #max start altitude from task sheet
LCONFPLTPAltitude1 =TaskMaxStartAltitude_ft * 0.3048  #max start altitude in m


####need to convert start time to UTC time or add an offset
#currently -7 so add 7 to start time
UTC_Offset = 5

GliderOverride = "18-meter"

altitude_string = f'LCONFPLTPAltitude1={LCONFPLTPAltitude1}'


data = [
    {'IGC Filename': '48K_ELF.igc', 'Glider': 'Ventus 3e', 'Start Time': '15:42:13', 'TOC': '3:57:02', 'Speed': 128.12, 'Distance': 506.14},
    {'IGC Filename': '48K_QX.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:45:05', 'TOC': '3:47:23', 'Speed': 128.09, 'Distance': 485.41},
    {'IGC Filename': '48K_2L.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:43:23', 'TOC': '3:47:48', 'Speed': 127.58, 'Distance': 484.39},
    {'IGC Filename': '48K_SF.igc', 'Glider': 'AS 33 Me', 'Start Time': '15:42:08', 'TOC': '3:58:16', 'Speed': 127.50, 'Distance': 506.33},
    {'IGC Filename': '48K_5M.igc', 'Glider': 'JS3', 'Start Time': '15:42:36', 'TOC': '3:44:36', 'Speed': 126.64, 'Distance': 474.91},
    {'IGC Filename': '48K_V.igc', 'Glider': 'AS 33 18m', 'Start Time': '15:43:04', 'TOC': '3:48:36', 'Speed': 126.95, 'Distance': 483.68},
    {'IGC Filename': '48K_A7.igc', 'Glider': 'JS3 RES 18m', 'Start Time': '15:44:55', 'TOC': '3:46:38', 'Speed': 122.75, 'Distance': 463.65},
    {'IGC Filename': '48K_KW.igc', 'Glider': 'JS3 18m', 'Start Time': '15:43:34', 'TOC': '3:57:09', 'Speed': 122.12, 'Distance': 482.66},
    {'IGC Filename': '48K_QT.igc', 'Glider': 'JS3-TJ', 'Start Time': '15:43:04', 'TOC': '3:46:06', 'Speed': 122.04, 'Distance': 459.90},
    {'IGC Filename': '48K_AJ.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:41:23', 'TOC': '3:46:34', 'Speed': 121.77, 'Distance': 459.82},
    {'IGC Filename': '48K_AB.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:53', 'TOC': '3:47:02', 'Speed': 121.61, 'Distance': 460.15},
    {'IGC Filename': '48K_2S.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:34', 'TOC': '3:43:41', 'Speed': 121.55, 'Distance': 455.81},
    {'IGC Filename': '48K_NJ.igc', 'Glider': 'Ventus 3M 18m', 'Start Time': '15:44:42', 'TOC': '3:46:36', 'Speed': 121.48, 'Distance': 458.78},
    {'IGC Filename': '48K_ZE.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:54', 'TOC': '3:48:27', 'Speed': 121.40, 'Distance': 462.22},
    {'IGC Filename': '48K_N1.igc', 'Glider': 'Ventus 3T', 'Start Time': '15:44:44', 'TOC': '3:45:44', 'Speed': 121.25, 'Distance': 456.18},
    {'IGC Filename': '48K_JR.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:42:10', 'TOC': '3:47:09', 'Speed': 121.20, 'Distance': 458.84},
    {'IGC Filename': '48K_ZO.igc', 'Glider': 'AS 33 Es', 'Start Time': '15:43:57', 'TOC': '3:46:50', 'Speed': 121.08, 'Distance': 457.75},
    {'IGC Filename': '48K_GT.igc', 'Glider': 'Ventus 3T', 'Start Time': '15:44:40', 'TOC': '3:46:21', 'Speed': 121.00, 'Distance': 456.46},
    {'IGC Filename': '48K_LB.igc', 'Glider': 'JS3 18m', 'Start Time': '15:43:04', 'TOC': '3:46:15', 'Speed': 120.94, 'Distance': 456.05},
    {'IGC Filename': '48K_WG.igc', 'Glider': 'AS 33 Es', 'Start Time': '15:46:19', 'TOC': '3:46:26', 'Speed': 121.37, 'Distance': 458.02},
    {'IGC Filename': '48K_DZ.igc', 'Glider': 'JS3', 'Start Time': '15:44:32', 'TOC': '3:46:18', 'Speed': 120.61, 'Distance': 454.89},
    {'IGC Filename': '48K_LP.igc', 'Glider': 'JS-3-18m', 'Start Time': '15:45:36', 'TOC': '3:47:48', 'Speed': 119.91, 'Distance': 455.26},
    {'IGC Filename': '48K_XG.igc', 'Glider': 'AS 33 Es', 'Start Time': '15:39:42', 'TOC': '3:51:26', 'Speed': 118.93, 'Distance': 458.74},
    {'IGC Filename': '48K_IMS.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:03', 'TOC': '3:49:13', 'Speed': 117.71, 'Distance': 449.70},
    {'IGC Filename': '48K_MS.igc', 'Glider': 'ASG29', 'Start Time': '15:43:55', 'TOC': '3:48:43', 'Speed': 119.32, 'Distance': 454.86},
    {'IGC Filename': '48K_XC.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:04', 'TOC': '3:56:08', 'Speed': 115.37, 'Distance': 454.04},
    {'IGC Filename': '48K_BK.igc', 'Glider': 'JS-3-15m', 'Start Time': '15:45:27', 'TOC': '3:48:18', 'Speed': 121.43, 'Distance': 462.06},
    {'IGC Filename': '48K_MII.igc', 'Glider': 'JS3 RES 18m', 'Start Time': '15:38:43', 'TOC': '4:06:51', 'Speed': 107.15, 'Distance': 440.84},
    {'IGC Filename': '48K_FS.igc', 'Glider': 'JS3 18m', 'Start Time': '15:45:34', 'TOC': '', 'Speed': None, 'Distance': 463.98},
    {'IGC Filename': '48K_A8.igc', 'Glider': 'JS1 TJ 18m', 'Start Time': '15:42:29', 'TOC': '', 'Speed': None, 'Distance': 456.57},
    {'IGC Filename': '48K_MM.igc', 'Glider': 'JS3 18m', 'Start Time': '15:51:54', 'TOC': '', 'Speed': None, 'Distance': 388.30},
    {'IGC Filename': '48K_ST.igc', 'Glider': 'JS3-RES', 'Start Time': '16:05:33', 'TOC': '', 'Speed': None, 'Distance': 310.13}
]






# Override glider type for all entries
for entry in data:
    entry['Glider'] = GliderOverride

# Function to add UTC offset to time
def add_hours_to_time(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    time_obj_adjusted = time_obj + timedelta(hours=UTC_Offset)
    return time_obj_adjusted.strftime('%H:%M:%S')

# Update 'Start Time' in each dictionary in the data list
for item in data:
    if 'Start Time' in item:
        item['Start Time'] = add_hours_to_time(item['Start Time'])

# Debugging print to verify data after time adjustment
print("Updated data with UTC offset applied to Start Time:")
for entry in data:
    print(entry)

# Find IGC files in the current directory
igc_files = [file for file in os.listdir('.') if (file.lower().endswith('.igc'))]

if not igc_files:
    print("No IGC files found...")

hfcid_changes = []  # List to track changes made to HFCIDCOMPETITIONID

# Loop through each IGC file
for igc_file in igc_files:
    with open(igc_file, 'r') as file:
        file_content = file.readlines()
        print(f'Processing {igc_file}...')

    # Extract CN from the filename (ignore the prefix)
    cn_from_filename = igc_file.split('_')[1].split('.')[0]
    correct_hfcid_line = f'HFCIDCOMPETITIONID:{cn_from_filename}'
    hfcid_index = next((i for i, line in enumerate(file_content) if 'HFCIDCOMPETITIONID:' in line), None)

    # Check and correct HFCIDCOMPETITIONID if necessary
    if hfcid_index is None:
        # If HFCIDCOMPETITIONID is missing, add the correct line
        file_content.insert(2, correct_hfcid_line + '\n')
        print(f'Inserted HFCIDCOMPETITIONID for {igc_file}: {correct_hfcid_line}')
        hfcid_changes.append(f'Inserted HFCIDCOMPETITIONID:{cn_from_filename} in {igc_file}')
    else:
        # Check if the existing HFCIDCOMPETITIONID is correct
        existing_hfcid_line = file_content[hfcid_index].strip()
        if existing_hfcid_line != correct_hfcid_line:
            # Correct the HFCIDCOMPETITIONID line if it's wrong
            file_content[hfcid_index] = correct_hfcid_line + '\n'
            print(f'Corrected HFCIDCOMPETITIONID in {igc_file}: {existing_hfcid_line} to {correct_hfcid_line}')
            hfcid_changes.append(f'Corrected {existing_hfcid_line} to HFCIDCOMPETITIONID:{cn_from_filename} in {igc_file}')
        else:
            print(f'HFCIDCOMPETITIONID in {igc_file} is correct: {existing_hfcid_line}')

    # Check for and insert LCONFlightInfoPlayerStatus=FINISHED
    if any('LCONFlightInfoPlayerStatus=FINISHED' in line for line in file_content):
        print(f'Found "LCONFlightInfoPlayerStatus=FINISHED" in {igc_file}. Doing nothing.')
    else:
        file_content.insert(2, 'LCONFlightInfoPlayerStatus=FINISHED\n')
        print(f'Inserted "LCONFlightInfoPlayerStatus=FINISHED" into {igc_file}')

    # Check for and insert altitude string
    if any(altitude_string in line for line in file_content):
        print(f'Found {altitude_string} in {igc_file}. Doing nothing.')
    else:
        file_content.insert(2, f'{altitude_string}\n')
        print(f'Inserted {altitude_string} into {igc_file}')

    # Find matching data for current IGC file
    matching_data = next((item for item in data if item['IGC Filename'] == igc_file), None)

    if matching_data:
        # Create strings to match or insert into file content
        type_match_text = f'LCONFPLName={matching_data["Glider"]}'
        filename_match_text = f'KIGCFILENAME={matching_data["IGC Filename"]}'
        starttime_match_text = f'LCONFlightInfoTaskStart={matching_data["Start Time"]}'
        timeoncourse_match_text = f'LCONFlightInfoTaskTime={matching_data["TOC"]}'
        taskspeed_match_text = f'LCONFlightInfoAverageSpeed={matching_data["Speed"]}'
        distance_flown_match_text = f'LCONFlightInfoDistanceFlown={matching_data["Distance"]}'

        # Function to check and insert lines if not found
        def check_and_insert(match_text, insert_index):
            if match_text in ''.join(file_content):
                print(f'Found match in {igc_file}: {match_text}')
            else:
                file_content.insert(insert_index, f'{match_text}\n')
                print(f'{match_text} inserted into {igc_file}')

        # Check and insert each relevant line
        check_and_insert(type_match_text, 3)
        check_and_insert(filename_match_text, 4)
        check_and_insert(starttime_match_text, 5)
        check_and_insert(timeoncourse_match_text, 6)
        check_and_insert(taskspeed_match_text, 7)
        check_and_insert(distance_flown_match_text, 8)

    else:
        print(f'No matching data found for {igc_file}')

    # Write the modified content back to the file
    with open(igc_file, 'w') as updated_file:
        updated_file.writelines(file_content)

# Print summary of changes to HFCIDCOMPETITIONID
print("\nSummary of HFCIDCOMPETITIONID changes:")
if hfcid_changes:
    for change in hfcid_changes:
        print(change)
else:
    print("No changes were made to HFCIDCOMPETITIONID.")