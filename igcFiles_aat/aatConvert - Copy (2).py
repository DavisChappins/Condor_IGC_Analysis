
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
    {"CN": "C4", "Plane": "StdCirrus", "Time": "1:24:21", "Speed": 126.99, "Distance": 178.53},
    {"CN": "51", "Plane": "LS4a", "Time": "1:21:01", "Speed": 132.22, "Distance": 178.53},
    {"CN": "SAS", "Plane": "StdCirrus", "Time": "1:26:23", "Speed": 124.01, "Distance": 178.53},
    {"CN": "284", "Plane": "LS4a", "Time": "1:22:33", "Speed": 129.76, "Distance": 178.53},
    {"CN": "1JG", "Plane": "LS4a", "Time": "1:22:40", "Speed": 129.59, "Distance": 178.53},
    {"CN": "RET", "Plane": "LS4a", "Time": "1:23:28", "Speed": 128.32, "Distance": 178.53},
    {"CN": "V99", "Plane": "ASW20", "Time": "1:19:13", "Speed": 135.23, "Distance": 178.53},
    {"CN": "BJN", "Plane": "ASW20", "Time": "1:19:54", "Speed": 134.07, "Distance": 178.53},
    {"CN": "57", "Plane": "ASW20", "Time": "1:20:30", "Speed": 133.05, "Distance": 178.53},
    {"CN": "HN1", "Plane": "LS4a", "Time": "1:25:16", "Speed": 125.62, "Distance": 178.53},
    {"CN": "BQ", "Plane": "LS4a", "Time": "1:25:21", "Speed": 125.51, "Distance": 178.53},
    {"CN": "AC6", "Plane": "LS4a", "Time": "1:26:12", "Speed": 124.27, "Distance": 178.53},
    {"CN": "XCB", "Plane": "ASW20", "Time": "1:22:35", "Speed": 129.7, "Distance": 178.53},
    {"CN": "5YA", "Plane": "LS4a", "Time": "1:27:50", "Speed": 121.95, "Distance": 178.53},
    {"CN": "ISS", "Plane": "LS4a", "Time": "1:28:22", "Speed": 121.22, "Distance": 178.53},
    {"CN": "TNG", "Plane": "LS4a", "Time": "1:28:39", "Speed": 120.83, "Distance": 178.53},
    {"CN": "OCG", "Plane": "LS4a", "Time": "1:29:08", "Speed": 120.19, "Distance": 178.53},
    {"CN": "EX", "Plane": "LS4a", "Time": "1:30:18", "Speed": 118.62, "Distance": 178.53},
    {"CN": "S29", "Plane": "LS4a", "Time": "1:30:54", "Speed": 117.85, "Distance": 178.53},
    {"CN": "XS", "Plane": "ASW20", "Time": "1:26:46", "Speed": 123.47, "Distance": 178.53},
    {"CN": "CM2", "Plane": "ASW20", "Time": "1:26:52", "Speed": 123.3, "Distance": 178.53},
    {"CN": "TL8", "Plane": "ASW20", "Time": "1:40:11", "Speed": 106.93, "Distance": 178.53},
    {"CN": "T1", "Plane": "LS4a", "Time": "2:05:47", "Speed": 85.16, "Distance": 178.53},
    {"CN": "BRM", "Plane": "ASW20", "Time": "0:00:00", "Speed": 0, "Distance": 167.8},
    {"CN": "R1", "Plane": "ASW19", "Time": "0:00:00", "Speed": 0, "Distance": 178.48},
    {"CN": "GR2", "Plane": "StdCirrus", "Time": "0:00:00", "Speed": 0, "Distance": 98},
    {"CN": "JU", "Plane": "LS4a", "Time": "0:00:00", "Speed": 0, "Distance": 84.3},
    {"CN": "HB2", "Plane": "StdCirrus", "Time": "0:00:00", "Speed": 0, "Distance": 34.5}
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
        print(f"Warning: No handicap value found for plane {plane}")



# Assuming you have a list of file names with .igc extension
igc_files = [file for file in os.listdir('.') if file.endswith('.igc')]

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
