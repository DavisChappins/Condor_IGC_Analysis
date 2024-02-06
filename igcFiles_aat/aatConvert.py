
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
    {"CN": "HG1", "Plane": "JS3-15", "Time": "1:26:49", "Speed": 139.13, "Distance": 201.33},
    {"CN": "DC1", "Plane": "JS3-15", "Time": "1:20:23", "Speed": 136.24, "Distance": 182.51},
    {"CN": "BG1", "Plane": "JS3-15", "Time": "1:23:07", "Speed": 133.62, "Distance": 185.11},
    {"CN": "C4", "Plane": "JS3-15", "Time": "1:29:15", "Speed": 130.86, "Distance": 194.66},
    {"CN": "RED", "Plane": "JS3-15", "Time": "1:28:17", "Speed": 130.57, "Distance": 192.13},
    {"CN": "BQ", "Plane": "JS3-15", "Time": "1:24:38", "Speed": 129.58, "Distance": 183.92},
    {"CN": "UP5", "Plane": "JS3-15", "Time": "1:23:27", "Speed": 128.69, "Distance": 178.97},
    {"CN": "MWH", "Plane": "JS3-15", "Time": "1:19:12", "Speed": 128.28, "Distance": 172.91},
    {"CN": "GJB", "Plane": "JS3-15", "Time": "1:19:15", "Speed": 128.08, "Distance": 169.17},
    {"CN": "DRS", "Plane": "JS3-15", "Time": "1:20:30", "Speed": 128.06, "Distance": 174.1},
    {"CN": "VS1", "Plane": "JS3-15", "Time": "1:23:02", "Speed": 127.13, "Distance": 180.38},
    {"CN": "HN1", "Plane": "JS3-15", "Time": "1:24:48", "Speed": 127.01, "Distance": 179.51},
    {"CN": "FW1", "Plane": "JS3-15", "Time": "1:45:28", "Speed": 125.74, "Distance": 222.05},
    {"CN": "EMC", "Plane": "JS3-15", "Time": "1:27:14", "Speed": 125.44, "Distance": 182.37},
    {"CN": "1JG", "Plane": "JS3-15", "Time": "1:23:58", "Speed": 124.85, "Distance": 174.73},
    {"CN": "ERJ", "Plane": "JS3-15", "Time": "1:50:04", "Speed": 120.63, "Distance": 238.79},
    {"CN": "K12", "Plane": "JS3-15", "Time": "1:29:23", "Speed": 119.82, "Distance": 184.07},
    {"CN": "KG", "Plane": "JS3-15", "Time": "1:41:47", "Speed": 119.71, "Distance": 203.09},
    {"CN": "DFR", "Plane": "Ventus3-15", "Time": "1:31:20", "Speed": 118.46, "Distance": 181.9},
    {"CN": "J3", "Plane": "JS3-15", "Time": "1:30:27", "Speed": 117.57, "Distance": 185.48},
    {"CN": "L9", "Plane": "JS3-15", "Time": "1:21:41", "Speed": 117.42, "Distance": 169.1},
    {"CN": "SHM", "Plane": "JS3-15", "Time": "1:50:19", "Speed": 115.59, "Distance": 216.45},
    {"CN": "XL", "Plane": "JS3-15", "Time": "1:28:36", "Speed": 115.57, "Distance": 177.44},
    {"CN": "284", "Plane": "JS3-15", "Time": "1:37:12", "Speed": 112.28, "Distance": 184.07},
    {"CN": "NKO", "Plane": "Ventus3-15", "Time": "1:56:56", "Speed": 111.95, "Distance": 223.81},
    {"CN": "RET", "Plane": "DG808C-15", "Time": "1:49:16", "Speed": 111.31, "Distance": 211.81},
    {"CN": "STW", "Plane": "Ventus3-15", "Time": "1:32:38", "Speed": 111, "Distance": 176.4},
    {"CN": "F8", "Plane": "JS3-15", "Time": "1:35:31", "Speed": 104.87, "Distance": 172.21},
    {"CN": "TR", "Plane": "JS3-15", "Time": "1:57:03", "Speed": 98.19, "Distance": 191.56},
    {"CN": "QQQ", "Plane": "JS3-15", "Time": "1:51:06", "Speed": 89.64, "Distance": 168},
    {"CN": "FU2", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 171.76, "Distance": 214.7},
    {"CN": "CD", "Plane": "Diana2", "Time": "0:00:00", "Speed": 171.68, "Distance": 214.6},
    {"CN": "58", "Plane": "Diana2", "Time": "0:00:00", "Speed": 152.96, "Distance": 191.2},
    {"CN": "SP4", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 132.87, "Distance": 171.88},
    {"CN": "BS9", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 130.28, "Distance": 171.67},
    {"CN": "SAS", "Plane": "Diana2", "Time": "0:00:00", "Speed": 131.18, "Distance": 171.66},
    {"CN": "2MC", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 135.57, "Distance": 169.46},
    {"CN": "GUN", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 125.85, "Distance": 157.31},
    {"CN": "WX", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 117.74, "Distance": 147.18},
    {"CN": "QQ", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 113.79, "Distance": 144.04},
    {"CN": "DB2", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 100.14, "Distance": 131.49},
    {"CN": "CW", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 93.13, "Distance": 119.21},
    {"CN": "TNG", "Plane": "JS3-15", "Time": "0:00:00", "Speed": 33.52, "Distance": 41.9},
]






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


# Applying the handicap to the speeds in the data, if club class
for entry in data:
    plane = entry["Plane"]
    if plane in handicap_values:
        entry["Speed"] = handicap_speed(entry["Speed"], handicap_values[plane])
    else:
        pass



# Assuming you have a list of file names with .igc extension
igc_files = [file for file in os.listdir('.') if file.endswith('.igc')]

if igc_files == []:
    print("No igc files found...")


# Loop through each igc file
for igc_file in igc_files:
    with open(igc_file, 'r') as file:
        file_content = file.readlines()
        print(f'Looking through {igc_file}')
        # Loop through each item in the data list
        for item in data:
            cn_match_text = f'HFCIDCOMPETITIONID:{item["CN"]}'

            #print('item',item)
            # Check if the match text is present in any line of the file content
            if any(line.strip() == cn_match_text for line in file_content):
                print(f'Found match in {igc_file}: {cn_match_text}')
                
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
            
                # Rename the file with "_aat" appended to the file name
                os.rename(igc_file, f'{igc_file[:-4]}_aat.igc')
                print(f'Renamed {igc_file} to {igc_file[:-4]}_aat.igc')
                break
