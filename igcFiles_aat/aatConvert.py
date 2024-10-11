
import os


def handicap_speed(speed, handicap):
    """
    Handicap the speed based on a given handicap value.

    Parameters:
    - speed (float): Original speed value.
    - handicap (float): Handicap value.

    Returns:
    - float: Handicapped speed.
    """
    handicapped_speed = speed * (100.0 / handicap)
    return handicapped_speed


#speeds must be in kmh and distance must be in km!!



data = [
    {"CN": "DC1", "Plane": "JS3-18", "Time": "1:17:39", "Speed": 199.42, "Distance": 258.1},
    {"CN": "RED", "Plane": "JS3-18", "Time": "1:17:09", "Speed": 198.5, "Distance": 255.23},
    {"CN": "1JG", "Plane": "JS3-18", "Time": "1:21:11", "Speed": 187.88, "Distance": 256.67},
    {"CN": "BG1", "Plane": "JS3-18", "Time": "1:16:30", "Speed": 187.87, "Distance": 239.53},
    {"CN": "HG1", "Plane": "JS3-18", "Time": "1:24:42", "Speed": 183.13, "Distance": 258.53},
    {"CN": "330", "Plane": "JS3-18", "Time": "1:15:03", "Speed": 183.04, "Distance": 228.96},
    {"CN": "SHM", "Plane": "JS3-18", "Time": "1:17:07", "Speed": 180.43, "Distance": 231.91},
    {"CN": "112", "Plane": "JS3-18", "Time": "1:24:48", "Speed": 171.56, "Distance": 242.47},
    {"CN": "TT2", "Plane": "JS3-18", "Time": "1:18:42", "Speed": 170.38, "Distance": 223.48},
    {"CN": "HN1", "Plane": "JS3-18", "Time": "1:19:14", "Speed": 166.05, "Distance": 219.28},
    {"CN": "TA3", "Plane": "JS3-18", "Time": "1:19:55", "Speed": 165.16, "Distance": 219.97},
    {"CN": "107", "Plane": "JS3-18", "Time": "1:22:31", "Speed": 159.81, "Distance": 219.8},
    {"CN": "JDD", "Plane": "JS3-18", "Time": "1:25:25", "Speed": 155.4, "Distance": 221.24},
    {"CN": "UP2", "Plane": "JS3-18", "Time": "1:25:04", "Speed": 152.54, "Distance": 216.27},
    {"CN": "CK", "Plane": "JS3-18", "Time": "1:19:51", "Speed": 150.51, "Distance": 200.29},
    {"CN": "2PK", "Plane": "JS3-18", "Time": "1:25:11", "Speed": 147.27, "Distance": 209.9},
    {"CN": "F8", "Plane": "JS3-18", "Time": "1:18:21", "Speed": 137.28, "Distance": 181.3},
    {"CN": "MBW", "Plane": "JS3-18", "Time": "1:30:19", "Speed": 122.93, "Distance": 186.99},
    {"CN": "AZ2", "Plane": "JS3-18", "Time": "1:40:05", "Speed": 128.62, "Distance": 214.56},
    {"CN": "PB5", "Plane": "JS3-18", "Time": "1:58:47", "Speed": 94.29, "Distance": 186.69},
    {"CN": "058", "Plane": "JS3-18", "Time": "0:00:00", "Speed": 186.56, "Distance": 233.2},
    {"CN": "BOK", "Plane": "JS3-18", "Time": "0:00:00", "Speed": 181.92, "Distance": 227.4},
    {"CN": "GUN", "Plane": "JS3-18", "Time": "0:00:00", "Speed": 64.24, "Distance": 80.3},
    {"CN": "BS9", "Plane": "JS3-18", "Time": "0:00:00", "Speed": 45.32, "Distance": 58.27},
    {"CN": "VAP", "Plane": "JS3-18", "Time": "0:00:00", "Speed": 41.52, "Distance": 51.9},
    {"CN": "JD2", "Plane": "JS3-18", "Time": "0:00:00", "Speed": 38.95, "Distance": 49.02},
    {"CN": "K12", "Plane": "JS3-18", "Time": "0:00:00", "Speed": 16.28, "Distance": 20.35},
    {"CN": "KG", "Plane": "JS3-18", "Time": "0:00:00", "Speed": 7.04, "Distance": 8.8}
]

# data = [
#     {"CN": "JM", "Plane": "JS3-15", "Time": "1:16:42", "Speed": 163.19, "Distance": 208.62},
#     {"CN": "CM2", "Plane": "JS3-15", "Time": "1:18:52", "Speed": 159.96, "Distance": 210.26},
#     {"CN": "DC1", "Plane": "JS3-15", "Time": "1:15:54", "Speed": 156.16, "Distance": 197.53},
#     {"CN": "BZ1", "Plane": "JS3-15", "Time": "1:18:00", "Speed": 154.39, "Distance": 200.7},
#     {"CN": "BQ", "Plane": "JS3-15", "Time": "1:15:04", "Speed": 153.4, "Distance": 191.93},
#     {"CN": "2MC", "Plane": "JS3-15", "Time": "1:15:08", "Speed": 153.22, "Distance": 191.86},
#     {"CN": "JBD", "Plane": "JS3-15", "Time": "1:18:28", "Speed": 150.18, "Distance": 196.53},
#     {"CN": "EMC", "Plane": "JS3-15", "Time": "1:17:08", "Speed": 150.05, "Distance": 192.91},
#     {"CN": "GJB", "Plane": "JS3-15", "Time": "1:17:22", "Speed": 149.17, "Distance": 192.36},
#     {"CN": "BOK", "Plane": "JS3-15", "Time": "1:15:53", "Speed": 147.18, "Distance": 201.91},
#     {"CN": "LH2", "Plane": "JS3-15", "Time": "1:18:43", "Speed": 147.12, "Distance": 193.01},
#     {"CN": "57", "Plane": "JS3-15", "Time": "1:29:52", "Speed": 145.92, "Distance": 218.72},
#     {"CN": "HN1", "Plane": "JS3-15", "Time": "1:15:49", "Speed": 145.84, "Distance": 184.29},
#     {"CN": "SHM", "Plane": "JS3-15", "Time": "1:22:47", "Speed": 141.53, "Distance": 195.27},
#     {"CN": "KG", "Plane": "JS3-15", "Time": "1:20:05", "Speed": 135.58, "Distance": 180.95},
#     {"CN": "42", "Plane": "JS3-15", "Time": "1:21:19", "Speed": 133.32, "Distance": 180.68},
#     {"CN": "KE", "Plane": "Ventus3-15", "Time": "1:22:22", "Speed": 130.47, "Distance": 179.12},
#     {"CN": "UP5", "Plane": "JS3-15", "Time": "1:21:24", "Speed": 126.78, "Distance": 172.01},
#     {"CN": "F8", "Plane": "JS3-15", "Time": "1:19:18", "Speed": 126.32, "Distance": 167.62},
#     {"CN": "58", "Plane": "Diana2", "Time": "1:32:49", "Speed": 124.35, "Distance": 199.59},
#     {"CN": "BWL", "Plane": "JS3-15", "Time": "1:12:44", "Speed": 122.0, "Distance": 152.5},
#     {"CN": "K12", "Plane": "JS3-15", "Time": "1:33:26", "Speed": 118.89, "Distance": 185.13},
#     {"CN": "9K", "Plane": "Ventus3-15", "Time": "1:20:41", "Speed": 116.96, "Distance": 158.12},
#     {"CN": "SKJ", "Plane": "Diana2", "Time": "1:20:22", "Speed": 111.11, "Distance": 148.83},
#     {"CN": "MBW", "Plane": "Diana2", "Time": "1:42:11", "Speed": 82.69, "Distance": 140.82},
#     {"CN": "ET2", "Plane": "Diana2", "Time": "1:55:12", "Speed": 87.64, "Distance": 168.25},
#     {"CN": "107", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 119.06, "Distance": 161.1}
# ]


# data = [
#     {'IGC Filename': '48K_ELF.igc', 'Glider': 'Ventus 3e', 'Start Time': '15:42:13', 'TOC': '3:57:02', 'Speed': 128.12, 'Distance': 506.14},
#     {'IGC Filename': '48K_QX.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:45:05', 'TOC': '3:47:23', 'Speed': 128.09, 'Distance': 485.41},
#     {'IGC Filename': '48K_2L.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:43:23', 'TOC': '3:47:48', 'Speed': 127.58, 'Distance': 484.39},
#     {'IGC Filename': '48K_SF.igc', 'Glider': 'AS 33 Me', 'Start Time': '15:42:08', 'TOC': '3:58:16', 'Speed': 127.50, 'Distance': 506.33},
#     {'IGC Filename': '48K_5M.igc', 'Glider': 'JS3', 'Start Time': '15:42:36', 'TOC': '3:44:36', 'Speed': 126.64, 'Distance': 474.91},
#     {'IGC Filename': '48K_V.igc', 'Glider': 'AS 33 18m', 'Start Time': '15:43:04', 'TOC': '3:48:36', 'Speed': 126.95, 'Distance': 483.68},
#     {'IGC Filename': '48K_A7.igc', 'Glider': 'JS3 RES 18m', 'Start Time': '15:44:55', 'TOC': '3:46:38', 'Speed': 122.75, 'Distance': 463.65},
#     {'IGC Filename': '48K_KW.igc', 'Glider': 'JS3 18m', 'Start Time': '15:43:34', 'TOC': '3:57:09', 'Speed': 122.12, 'Distance': 482.66},
#     {'IGC Filename': '48K_QT.igc', 'Glider': 'JS3-TJ', 'Start Time': '15:43:04', 'TOC': '3:46:06', 'Speed': 122.04, 'Distance': 459.90},
#     {'IGC Filename': '48K_AJ.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:41:23', 'TOC': '3:46:34', 'Speed': 121.77, 'Distance': 459.82},
#     {'IGC Filename': '48K_AB.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:53', 'TOC': '3:47:02', 'Speed': 121.61, 'Distance': 460.15},
#     {'IGC Filename': '48K_2S.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:34', 'TOC': '3:43:41', 'Speed': 121.55, 'Distance': 455.81},
#     {'IGC Filename': '48K_NJ.igc', 'Glider': 'Ventus 3M 18m', 'Start Time': '15:44:42', 'TOC': '3:46:36', 'Speed': 121.48, 'Distance': 458.78},
#     {'IGC Filename': '48K_ZE.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:54', 'TOC': '3:48:27', 'Speed': 121.40, 'Distance': 462.22},
#     {'IGC Filename': '48K_N1.igc', 'Glider': 'Ventus 3T', 'Start Time': '15:44:44', 'TOC': '3:45:44', 'Speed': 121.25, 'Distance': 456.18},
#     {'IGC Filename': '48K_JR.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:42:10', 'TOC': '3:47:09', 'Speed': 121.20, 'Distance': 458.84},
#     {'IGC Filename': '48K_ZO.igc', 'Glider': 'AS 33 Es', 'Start Time': '15:43:57', 'TOC': '3:46:50', 'Speed': 121.08, 'Distance': 457.75},
#     {'IGC Filename': '48K_GT.igc', 'Glider': 'Ventus 3T', 'Start Time': '15:44:40', 'TOC': '3:46:21', 'Speed': 121.00, 'Distance': 456.46},
#     {'IGC Filename': '48K_LB.igc', 'Glider': 'JS3 18m', 'Start Time': '15:43:04', 'TOC': '3:46:15', 'Speed': 120.94, 'Distance': 456.05},
#     {'IGC Filename': '48K_WG.igc', 'Glider': 'AS 33 Es', 'Start Time': '15:46:19', 'TOC': '3:46:26', 'Speed': 121.37, 'Distance': 458.02},
#     {'IGC Filename': '48K_DZ.igc', 'Glider': 'JS3', 'Start Time': '15:44:32', 'TOC': '3:46:18', 'Speed': 120.61, 'Distance': 454.89},
#     {'IGC Filename': '48K_LP.igc', 'Glider': 'JS-3-18m', 'Start Time': '15:45:36', 'TOC': '3:47:48', 'Speed': 119.91, 'Distance': 455.26},
#     {'IGC Filename': '48K_XG.igc', 'Glider': 'AS 33 Es', 'Start Time': '15:39:42', 'TOC': '3:51:26', 'Speed': 118.93, 'Distance': 458.74},
#     {'IGC Filename': '48K_IMS.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:03', 'TOC': '3:49:13', 'Speed': 117.71, 'Distance': 449.70},
#     {'IGC Filename': '48K_MS.igc', 'Glider': 'ASG29', 'Start Time': '15:43:55', 'TOC': '3:48:43', 'Speed': 119.32, 'Distance': 454.86},
#     {'IGC Filename': '48K_XC.igc', 'Glider': 'JS3 TJ 18m', 'Start Time': '15:44:04', 'TOC': '3:56:08', 'Speed': 115.37, 'Distance': 454.04},
#     {'IGC Filename': '48K_BK.igc', 'Glider': 'JS-3-15m', 'Start Time': '15:45:27', 'TOC': '3:48:18', 'Speed': 121.43, 'Distance': 462.06},
#     {'IGC Filename': '48K_MII.igc', 'Glider': 'JS3 RES 18m', 'Start Time': '15:38:43', 'TOC': '4:06:51', 'Speed': 107.15, 'Distance': 440.84},
#     {'IGC Filename': '48K_FS.igc', 'Glider': 'JS3 18m', 'Start Time': '15:45:34', 'TOC': '', 'Speed': None, 'Distance': 463.98},
#     {'IGC Filename': '48K_A8.igc', 'Glider': 'JS1 TJ 18m', 'Start Time': '15:42:29', 'TOC': '', 'Speed': None, 'Distance': 456.57},
#     {'IGC Filename': '48K_MM.igc', 'Glider': 'JS3 18m', 'Start Time': '15:51:54', 'TOC': '', 'Speed': None, 'Distance': 388.30},
#     {'IGC Filename': '48K_ST.igc', 'Glider': 'JS3-RES', 'Start Time': '16:05:33', 'TOC': '', 'Speed': None, 'Distance': 310.13}
# ]

# Handicap values
handicap_values = {
    "ASW15": 97.0,
    "ASW19": 100.0,
    "ASW20": 110.0,
    "DG101G": 100.0,
    "Libelle": 98.0,
    "LS3a": 107.0,
    "LS4a": 104.0,
    "Pegase": 102.0,
    "StdCirrus": 99.0,
}

# Convert data format if needed
if 'IGC Filename' in data[0]:
    converted_data = []
    for entry in data:
        CN = entry['IGC Filename'].split('_')[1].split('.')[0]
        Plane = entry['Glider']
        Speed = entry['Speed']
        Distance = entry['Distance']
        converted_data.append({"CN": CN, "Plane": Plane, "Time": entry['TOC'], "Speed": Speed, "Distance": Distance})
    data = converted_data

# Apply handicap to speeds if applicable
for entry in data:
    plane = entry["Plane"]
    if plane in handicap_values:
        entry["Speed"] = handicap_speed(entry["Speed"], handicap_values[plane])

# Find IGC files in the current directory
igc_files = [file for file in os.listdir('.') if file.endswith('.igc')]

if not igc_files:
    print("No IGC files found...")

no_matches = []  # List to store unmatched items

# Loop through each IGC file
for igc_file in igc_files:
    with open(igc_file, 'r') as file:
        file_content = file.readlines()
        print(f'Looking through {igc_file}')
        match_found = False

        # Loop through each item in the data list
        for item in data:
            cn_match_text = f'HFCIDCOMPETITIONID:{item["CN"]}'
            
            # Allow for extra spaces when matching
            if any(cn_match_text in line.replace(" ", "") for line in file_content):
                print(f'Found match in {igc_file}: {cn_match_text}')
                match_found = True

                # Find the line with "LCONFlightInfoDistanceFlown="
                for i, line in enumerate(file_content):
                    if "LCONFlightInfoDistanceFlown=" in line:
                        # Replace the value with data[i]["Distance"] in kilometers
                        new_line = f'LCONFlightInfoDistanceFlown={item["Distance"]:.2f} km\n'
                        file_content[i] = new_line

                    if "LCONFlightInfoAverageSpeed=" in line:
                        # Replace the value with data[i]["Speed"] in km/h
                        new_line = f'LCONFlightInfoAverageSpeed={item["Speed"]:.2f} km/h\n'
                        file_content[i] = new_line

                # Write the modified content back to the file
                with open(f'{igc_file[:-4]}_aat.igc', 'w') as modified_file:
                    modified_file.writelines(file_content)

                print(f'Replaced distance in {igc_file} with {item["Distance"]:.2f} km')
                print(f'Replaced speed in {igc_file} with {item["Speed"]:.2f} km/h')
                break

        if not match_found:
            print(f'*** No match for {igc_file} ***')
            no_matches.append(igc_file)

# Print list of files with no matches
if no_matches:
    print("\nNo matches found for the following files:")
    for file in no_matches:
        print(f'- {file}')