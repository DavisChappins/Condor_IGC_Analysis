# helperFile.py
from math import radians, sin, cos, sqrt, atan2, degrees
import math
from collections import deque, Counter
from datetime import datetime, timedelta
import csv
import pandas as pd
import os
import glob





def convert_seconds_to_mmss(overall_time_s):
    minutes = overall_time_s // 60
    seconds = overall_time_s % 60
    overall_time_mmss = f"{int(minutes):02d}:{int(seconds):02d}"
    return overall_time_mmss


#Input igc file data, returns list of lists contiaining only flight data
def process_igc_data(igc_data):
    # Create a new list containing only rows starting with 'B'
    flight_data = [line for line in igc_data if line.startswith('B')]

    # Add column names at index 0
    column_names = ["record",
                    "timeutc",
                    "latitude",
                    "longitude",
                    "validity",
                    "pressAlt",
                    "gnssAlt",
                    "heading",
                    "distance",
                    "groundspeed",
                    "headingChange",
                    "glideOrThermal",
                    "task",
                    "indicatedairspeed",
                    "height_change_ft",
                    "sinkrate_kt",
                    "LD",
                    "IAS_kt",
                    "MC_LD_at_IAS_kt",
                    "MC_sinkrate_at_IAS_kt",
                    "netto_kt",
                    "bool_netto_positive",
                    "bool_sinkrate_positive",
                    "PE_J",
                    "KE_J",
                    "TE_J",
                    "TE_diff_from_last_J"
                    ]
    flight_data.insert(0, column_names)

    # Split each row into specified columns
    for index in range(1, len(flight_data)):
        row = flight_data[index]
        record = row[0:1]
        timeutc = row[1:7] #HHMMSS
        latitude = row[7:15] #DDMMmmm N/S
        longitude = row[15:24] #DDDMMmmmE/W
        validity = row[24:25] #A or V - Use A for a 3D fix and V for a 2D fix (no GPS altitude) or for no GPS data
        pressAlt = row[25:30] #PPPPP
        gnssAlt = row[30:35] #GGGGG

        # Add placeholder values for the new columns
        heading = "" #will be in degrees
        distance = "" #will be in meters
        groundspeed = "" #will be in meters per second m/s
        headingChange = "" #in degrees
        glide_or_thermal = ""  # You can replace this with the actual values
        task = ""  # You can replace this with the actual values
        indicatedairspeed = ""
        height_change_ft = ""
        sinkrate_kt = ""
        IAS_kt = ""
        LD = ""
        MC_LD_at_IAS_kt = ""
        MC_sinkrate_at_IAS_kt = ""
        netto_kt = ""
        bool_netto_positive = 0
        bool_sinkrate_positive = 0
        PE_J = ""
        KE_J = ""
        TE_J = ""
        TE_diff_from_last_J = ""
        

        flight_data[index] = [record,
                              timeutc,
                              latitude,
                              longitude,
                              validity,
                              pressAlt,
                              gnssAlt,
                              heading,
                              distance,
                              groundspeed,
                              headingChange,
                              glide_or_thermal,
                              task,
                              indicatedairspeed,
                              height_change_ft,
                              sinkrate_kt,
                              LD,
                              IAS_kt,
                              MC_LD_at_IAS_kt,
                              MC_sinkrate_at_IAS_kt,
                              netto_kt,
                              bool_netto_positive,
                              bool_sinkrate_positive,
                              PE_J,
                              KE_J,
                              TE_J,
                              TE_diff_from_last_J
                              ]

    return flight_data


def haversine(lat1, lon1, lat2, lon2):
    # Calculate the Haversine distance between two sets of latitude and longitude
    R = 6371  # Earth radius in kilometers

    # Convert latitude and longitude from DDMMmmmN/S, DDDMMmmmE/W format to decimal degrees
    lat1, lon1 = convert_to_decimal(lat1, lon1)
    lat2, lon2 = convert_to_decimal(lat2, lon2)

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # Distance in kilometers

    return distance


def convert_to_decimal(lat_str, lon_str):
    # Convert latitude and longitude from DDMMmmmN/S, DDDMMmmmE/W format to decimal degrees
    lat_deg = float(lat_str[:2])
    lat_min = float(lat_str[2:4] + "." + lat_str[4:7])
    lon_deg = float(lon_str[:3])
    lon_min = float(lon_str[3:5] + "." + lon_str[5:8])

    # Determine hemisphere (N/S, E/W) and adjust sign accordingly
    lat_hemisphere = 1 if lat_str[7] == 'N' else -1
    lon_hemisphere = 1 if lon_str[8] == 'E' else -1

    return lat_hemisphere * (lat_deg + lat_min / 60.0), lon_hemisphere * (lon_deg + lon_min / 60.0)

def calculate_distance_between_fixes(flight_data):
    # Calculate distance between fixes and store the results in flight_data
    for i in range(1, len(flight_data) - 1):
        lat1, lon1 = flight_data[i][2], flight_data[i][3]
        lat2, lon2 = flight_data[i + 1][2], flight_data[i + 1][3]

        distance = haversine(lat1, lon1, lat2, lon2) * 1000  # Convert distance to meters

        # Store the distance in flight_data[i][8] rounded to 3 decimals
        flight_data[i][8] = round(distance, 3)

    return flight_data


def calculate_heading_between_fixes(flight_data):
    # Calculate heading between fixes and store the results in flight_data
    for i in range(1, len(flight_data) - 1):
        lat1, lon1 = flight_data[i][2], flight_data[i][3]
        lat2, lon2 = flight_data[i + 1][2], flight_data[i + 1][3]

        heading = calculate_heading(lat1, lon1, lat2, lon2)

        # Store the heading in flight_data[i][7] rounded to 3 decimals
        flight_data[i][7] = round(heading, 3)

    return flight_data


def calculate_heading(lat1, lon1, lat2, lon2):
    # Calculate the heading between two sets of latitude and longitude
    # Returns the heading in degrees

    # Convert latitude and longitude from DDMMmmmN/S, DDDMMmmmE/W format to decimal degrees
    lat1, lon1 = convert_to_decimal(lat1, lon1)
    lat2, lon2 = convert_to_decimal(lat2, lon2)

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate the heading in radians using the atan2 function
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(dlon))

    heading_radians = atan2(x, y)

    # Convert heading from radians to degrees
    heading_degrees = degrees(heading_radians)

    # Ensure the heading is in the range [0, 360)
    heading_degrees = round((heading_degrees + 360) % 360,0)
    heading_degrees = int(heading_degrees)

    return heading_degrees

def calculate_groundspeed(flight_data):
    # Calculate groundspeed and store the results in flight_data
    for i in range(1, len(flight_data) - 1):
        # Convert distance from meters to kilometers
        distance_km = flight_data[i][8] / 1000

        # Groundspeed in kilometers per hour
        groundspeed_kmh = distance_km * 3600  # Assuming a fixed time step of 1 second

        # Store the groundspeed in flight_data[i][9] rounded to 3 decimals
        flight_data[i][9] = int(round(groundspeed_kmh, 0))

    return flight_data

def add_calculated_ias(flight_data):
    #calculate indicated airspeed and put in flight_data
    for i in range(1,len(flight_data)):
        #calculate ias (estimated) in kmh
        try:
            calculated_ias = calculate_indicated_airspeed(float(flight_data[i][9]),float(flight_data[i][5]))
        except:
            pass
        calculated_ias = round(calculated_ias,2)
        
        flight_data[i][13] = calculated_ias

    return flight_data

def count_thermal_info(thermal_info):
    # Initialize counters
    discard_time = 75 #seconds
    discard_count = 0
    useful_count = 0
    altitude_gain_threshold = 500 #ft
    
    # Iterate through the keys in thermal_info
    for key in thermal_info:
        # Check if the key is valid and has 'thermal_time_s'
        if isinstance(thermal_info[key], dict) and 'thermal_time_s' in thermal_info[key]:
            # Check if thermal_time_s is less than discard_time
            if thermal_info[key]['thermal_time_s'] < discard_time and thermal_info[key]['thermal_height_gained_ft'] < altitude_gain_threshold:
                discard_count += 1
            else:
                useful_count += 1
    
    # Return the counts
    return discard_count, useful_count


def extract_max_start_height(igc_data):
    # Extract the start time from igc_data
    detected_max_start_height_m = None
    for line in igc_data:
        if line.startswith("LCONFPLTPAltitude1="):
            detected_max_start_height_m = line.split("=")[1].replace(":", "")
            break
    detected_max_start_height_ft = float(detected_max_start_height_m) * 3.28084
    detected_max_start_height_ft = int(detected_max_start_height_ft)

    return detected_max_start_height_ft

def extract_start_time(igc_data):
    # Extract the start time from igc_data
    detected_start_time = None
    for line in igc_data:
        if line.startswith("LCONFlightInfoTaskStart="):
            detected_start_time = line.split("=")[1].replace(":", "")
            break

    return detected_start_time


def extract_task_time(igc_data):
    detected_task_time = None
    for line in igc_data:
        if line.startswith("LCONFlightInfoTaskTime="):
            task_time_str = line.split("=")[1].strip()  # Extract the task time string
            # Convert task time string to timedelta
            task_time_delta = datetime.strptime(task_time_str, "%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")
            # Format timedelta as HH:MM:SS
            detected_task_time = str(task_time_delta)
            break

    return detected_task_time

def find_and_set_task_start(flight_data, detected_start_time):
    # Find the matching record in flight_data and set 'TaskStart' in flight_data[i][11]
    for i in range(1, len(flight_data)):
        if flight_data[i][1] == detected_start_time:
            flight_data[i][12] = 'TaskStart'
            break
    print("Task Start at: ",detected_start_time)
    
    return flight_data

def calculate_task_finish(flight_data, igc_data):
    """
    Calculates the task finish time based on task duration and start time extracted from IGC data,
    then updates the flight data to mark the finish time.

    Parameters:
    - flight_data (list): A list of lists where each inner list represents a row of flight data.
    - igc_data (list): A list of strings representing lines from an IGC file.

    Returns:
    - list: Updated flight data with 'TaskFinish' marked.
    """
    # Extract the task time from igc_data
    detected_task_duration = None
    print("Extracting task duration from IGC data...")
    for line in igc_data:
        #print(f"Checking line: {line.strip()}")
        if line.startswith("LCONFlightInfoTaskTime="):
            detected_task_duration = line.split("=")[1].replace(":", "")
            print(f"Detected task duration: {detected_task_duration}")
            break
    if not detected_task_duration:
        print("Error: Task duration not found in IGC data.")
        return flight_data

    # Extract the start time from igc_data
    detected_start_time = None
    print("Extracting start time from IGC data...")
    for line in igc_data:
        #print(f"Checking line: {line.strip()}")
        if line.startswith("LCONFlightInfoTaskStart="):
            detected_start_time = line.split("=")[1].replace(":", "")
            print(f"Detected start time: {detected_start_time}")
            break
    if not detected_start_time:
        print("Error: Start time not found in IGC data.")
        return flight_data

    # Convert task duration and start time to HHMMSS
    task_duration_hhmmss = detected_task_duration[:6]
    start_time_hhmmss = detected_start_time[:6]
    print(f"Task duration in HHMMSS: {task_duration_hhmmss}")
    print(f"Start time in HHMMSS: {start_time_hhmmss}")

    # Convert string times to datetime objects
    try:
        task_duration_time = datetime.strptime(task_duration_hhmmss, "%H%M%S")
        start_time = datetime.strptime(start_time_hhmmss, "%H%M%S")
    except ValueError as e:
        print(f"Error parsing times: {e}")
        return flight_data

    print(f"Parsed task duration time: {task_duration_time}")
    print(f"Parsed start time: {start_time}")

    # Calculate the task finish time (timedelta)
    calculated_task_finish_timedelta = timedelta(
        hours=task_duration_time.hour,
        minutes=task_duration_time.minute,
        seconds=task_duration_time.second
    )
    print(f"Calculated task finish timedelta: {calculated_task_finish_timedelta}")

    # Add timedelta to start_time to get finish time (datetime)
    calculated_task_finish_datetime = start_time + calculated_task_finish_timedelta
    print(f"Calculated task finish datetime: {calculated_task_finish_datetime}")

    # Convert the result back to string in HHMMSS format
    calculated_task_finish = calculated_task_finish_datetime.strftime("%H%M%S")
    print(f"Calculated task finish time (HHMMSS): {calculated_task_finish}")

    # Look for a match in flight_data[i][1] for calculated_task_finish
    print("Searching for the calculated task finish time in flight data...")
    found_task_finish = False
    for i in range(1, len(flight_data)):
        #print(f"Checking flight data row {i}: {flight_data[i]}")
        if flight_data[i][1] == calculated_task_finish:
            flight_data[i][12] = 'TaskFinish'
            print(f"Task finish time matched at row {i}, marking as 'TaskFinish'.")
            found_task_finish = True
            break

    if not found_task_finish:
        print("No match found for calculated task finish time in flight data.")

    return flight_data


# helperFile.py

def analyze_heading_changes(flight_data):
    window_size = 10  # Number of records to consider

    for i in range(window_size, len(flight_data)):
        current_heading_str = flight_data[i][7]

        try:
            current_heading = int(current_heading_str)

            # Calculate the sum of absolute heading changes over the last window_size records
            heading_changes_sum = sum(
                min((int(flight_data[j][7]) - int(flight_data[j - 1][7])) % 360, (int(flight_data[j - 1][7]) - int(flight_data[j][7])) % 360)
                for j in range(i - window_size + 1, i + 1)
            )

            # Place the sum in flight_data[i][10]
            flight_data[i][10] = heading_changes_sum

        except ValueError:
            # Handle the case where conversion to int fails
            #print(f"Error converting heading values to integers at index {i}")
            pass

    return flight_data

def analyze_heading_changes_old(flight_data):
    window_size = 10  # Number of records to consider

    for i in range(window_size, len(flight_data)):
        current_heading_str = flight_data[i][7]

        try:
            current_heading = int(current_heading_str)

            # Calculate the sum of absolute heading changes over the last window_size records
            heading_changes_sum = sum(
                (int(flight_data[j][7]) - int(flight_data[j - 1][7])) % 360 if int(flight_data[j][7]) > int(flight_data[j - 1][7]) else -(int(flight_data[j][7]) - int(flight_data[j - 1][7])) % 360
                for j in range(i - window_size + 1, i + 1)
            )

            # Place the sum in flight_data[i][10]
            flight_data[i][10] = heading_changes_sum

        except ValueError:
            # Handle the case where conversion to int fails
            #print(f"Error converting heading values to integers at index {i}")
            pass

    return flight_data


def trim_records_by_task(flight_data):
    """
    Trims the flight data records between 'TaskStart' and 'TaskFinish' markers.

    Parameters:
    - flight_data (list): A list of lists where each inner list represents a row of flight data.

    Returns:
    - list: Trimmed flight data including only records between 'TaskStart' and 'TaskFinish'.
    """
    task_start_index = None
    task_finish_index = None

    # Find indices for 'TaskStart' and 'TaskFinish'
    print("Searching for 'TaskStart' and 'TaskFinish' in the flight data...")

    for i, row in enumerate(flight_data):
        # Debug: Show current row being checked
        #print(f"Checking row {i}: {row}")

        if row[12] == 'TaskStart':
            task_start_index = i
            print(f"'TaskStart' found at index {task_start_index}")

        elif row[12] == 'TaskFinish':
            task_finish_index = i
            print(f"'TaskFinish' found at index {task_finish_index}")

    # Check if both indices were found and trim records based on them
    if task_start_index is not None and task_finish_index is not None:
        print(f"Trimming data from index {task_start_index} to {task_finish_index}")
        flight_data = flight_data[task_start_index: task_finish_index + 1]
    else:
        if task_start_index is None:
            print("Warning: 'TaskStart' not found in the flight data.")
        if task_finish_index is None:
            print("Warning: 'TaskFinish' not found in the flight data.")
        print("No trimming performed due to missing markers.")

    # Debug: Show the trimmed data
    print("Trimmed flight data:")
    for i, row in enumerate(flight_data):
        #print(f"Row {i}: {row}")
        break
    return flight_data

# helperFile.py

def label_thermal_series_old(flight_data, threshold=80):
    thermal_label = None
    thermal_count = 1
    #####Change threshold to make glide/climb detection more or less sensitive
    for i in range(len(flight_data)):
        if flight_data[i][10] is not None and flight_data[i][10] > threshold:
            if thermal_label is None:
                thermal_label = f'Thermal{thermal_count}'
                thermal_count += 1
        else:
            thermal_label = None
            for j in range(max(0, i - 8), i):
                flight_data[j][11] = ''

        if thermal_label is not None:
            flight_data[i][11] = thermal_label

    return flight_data

def label_thermal_series(flight_data, threshold=60, window_size=20):
    thermal_label = None
    thermal_count = 1

    for i in range(len(flight_data)):
        if flight_data[i][10] not in (None, "") and flight_data[i][10] > threshold:
            # Check the condition for the record at index i + window_size
            if (
                i + window_size < len(flight_data)
                and flight_data[i + window_size][10] is not None
                and flight_data[i + window_size][10] > threshold
            ):
                if thermal_label is None:
                    #thermal_label = f'Thermal{thermal_count}'
                    flight_data[i][11] = f'Thermal'
                    thermal_count += 1
                    #print('flight_data[i]',flight_data[i])
            else:
                thermal_label = None
                for j in range(max(0, i - 8), i):
                    flight_data[j][11] = ''
        else:
            thermal_label = None
            for j in range(max(0, i - 8), i):
                flight_data[j][11] = ''

        if thermal_label is not None:
            flight_data[i][11] = thermal_label

    return flight_data


def replace_thermal_sequences(flight_data, replacement_string = 'extended', extension_rows=25):
    #detect number of seconds to extend by
    for i in range(len(flight_data)):
        if flight_data[i][11] == 'Thermal':
            # Find the end of the sequence
            end_of_sequence = i + 1
            while end_of_sequence < len(flight_data) and flight_data[end_of_sequence][11] == 'Thermal':
                end_of_sequence += 1
            
            # Replace the sequence with the replacement string
            #for j in range(i, end_of_sequence):
                #flight_data[j][11] = replacement_string
            
            # Extend the replacement string for 15 rows after the last 'Thermal'
            extension_end = min(end_of_sequence + extension_rows, len(flight_data))
            for j in range(end_of_sequence, extension_end):
                flight_data[j][11] = replacement_string

    for i in range(len(flight_data)):
        if flight_data[i][11] == replacement_string:
            flight_data[i][11] = 'Thermal'
            
    return flight_data


def detect_thermal(flight_data):
    count = 0
    sequence_count = 0
    for i in range(len(flight_data)):
        if flight_data[i][11] == 'Thermal':
            count += 1
        else:
            if count > 0:
                sequence_count += 1
                for j in range(i-count, i):
                    flight_data[j][11] += str(sequence_count)
                count = 0
    if count > 0:
        sequence_count += 1
        for j in range(len(flight_data)-count, len(flight_data)):
            flight_data[j][11] += str(sequence_count)
    return flight_data



def label_glide_series(flight_data):
    glide_count = 1
    glide_flag = False

    for i in range(len(flight_data)):
        if flight_data[i][11] == '':
            flight_data[i][11] = f'Glide{glide_count}'
            glide_flag = True
        elif glide_flag == True:
            glide_count += 1
            glide_flag = False

    return flight_data

def calculate_perfect_start_J(task_start_height_ft: float) -> float:
    """
    Calculate the total energy of a perfect race start.
    
    Parameters:
        task_start_height_ft (float): The start height in feet.
    
    Returns:
        float: The total energy in joules.
    """
    mass = 600  # in kilograms
    speed_knots = 91.7927  # speed in knots
    # Convert speed from knots to m/s (1 knot = 0.514444 m/s)
    speed_m_s = speed_knots * 0.514444
    
    # Calculate kinetic energy: KE = 0.5 * mass * v^2
    kinetic_energy = 0.5 * mass * speed_m_s**2
    
    # Convert height from feet to meters (1 foot = 0.3048 m)
    height_m = task_start_height_ft * 0.3048
    
    # Calculate potential energy: PE = mass * g * height, with g = 9.81 m/s^2
    gravitational_acceleration = 9.81
    potential_energy = mass * gravitational_acceleration * height_m
    
    # Total energy is the sum of kinetic and potential energy
    total_energy = kinetic_energy + potential_energy
    return total_energy


def calculate_actual_energy(start_altitude_ft: float, start_speed_gs_kts: float) -> float:
    """
    Calculate the actual energy of the glider based on its start altitude and start speed.
    
    Parameters:
        start_altitude_ft (float): The glider's starting altitude in feet.
        start_speed_gs_kts (float): The glider's starting speed in knots.
    
    Returns:
        float: The glider's actual total energy in joules.
    """
    mass = 600  # in kilograms
    
    # Convert speed from knots to m/s (1 knot = 0.514444 m/s)
    speed_m_s = start_speed_gs_kts * 0.514444
    kinetic_energy = 0.5 * mass * speed_m_s ** 2
    
    # Convert altitude from feet to meters (1 foot = 0.3048 m)
    height_m = start_altitude_ft * 0.3048
    gravitational_acceleration = 9.81  # m/s^2
    potential_energy = mass * gravitational_acceleration * height_m
    
    total_energy = kinetic_energy + potential_energy
    return total_energy

def calculate_start_efficiency_score(start_altitude_ft: float, start_speed_gs_kts: float, task_start_height_ft: float) -> float:
    """
    Calculate the start efficiency score for the glider's start.
    
    The score is based on:
      1. Calculating the efficiency percentage as:
             (actual_start_energy_J / task_perfect_start_J) * 100
      2. If this efficiency percentage is greater than 100, the excess is multiplied by 3
         and subtracted from 100.
      3. Finally, subtract 90 from the adjusted efficiency percentage and round to 2 decimals.
    
    Parameters:
        start_altitude_ft (float): The glider's starting altitude in feet.
        start_speed_gs_kts (float): The glider's starting speed in knots.
    
    Returns:
        float: The start efficiency score.
    """
    actual_energy = calculate_actual_energy(start_altitude_ft, start_speed_gs_kts)
    perfect_energy = calculate_perfect_start_J(task_start_height_ft)
    efficiency_percentage = (actual_energy / perfect_energy) * 100
    print("actual_energy",actual_energy,"perfect_energy",perfect_energy)
    
    if efficiency_percentage > 100:
        excess = efficiency_percentage - 100
        efficiency_percentage = 100 - (excess * 3)
    
    # Apply the final adjustment of subtracting 90
    start_efficiency_score = round(efficiency_percentage - 90, 2)
    #start_efficiency_score = efficiency_percentage
    return start_efficiency_score

def calculate_total_effective_height_loss(altitude_deficit_ft: float, speed_deficit_kts: float,
                                            mass: float = 600, perfect_speed_kts: float = 91.7927,
                                            g: float = 9.81) -> float:
    """
    Convert a speed deficit (in knots) into an equivalent height loss (in feet) using the kinetic energy difference,
    then add the measured altitude deficit.

    Parameters:
        altitude_deficit_ft (float): The measured altitude deficit in feet.
        speed_deficit_kts (float): The speed deficit in knots.
        mass (float): Mass in kg (default is 600 kg).
        perfect_speed_kts (float): The perfect start speed in knots (default is 91.7927 kts).
        g (float): Acceleration due to gravity (default 9.81 m/s^2).

    Returns:
        float: The total effective height loss in feet.
    """
    # Convert speeds from knots to m/s (1 knot = 0.514444 m/s)
    perfect_speed_mps = perfect_speed_kts * 0.514444
    actual_speed_mps = (perfect_speed_kts - speed_deficit_kts) * 0.514444

    # Calculate the kinetic energy difference (in joules)
    ke_diff = 0.5 * mass * (perfect_speed_mps**2 - actual_speed_mps**2)

    # Convert the kinetic energy difference to an equivalent height loss (in meters)
    height_loss_m = ke_diff / (mass * g)

    # Convert the height loss from meters to feet (1 m = 3.28084 ft)
    height_loss_ft = height_loss_m * 3.28084

    # Total effective height loss is the measured altitude deficit plus the equivalent loss from speed deficit
    return altitude_deficit_ft + height_loss_ft


def calculate_perfect_finish_J(task_finish_height_ft: float) -> float:
    """
    Calculate the total energy of a perfect race finish.
    
    This function uses a perfect finish speed of 70 knots and the given finish altitude.
    
    Parameters:
        task_finish_height_ft (float): The finish altitude in feet.
    
    Returns:
        float: The total energy in joules under perfect finish conditions.
    """
    mass = 600  # in kilograms
    perfect_speed_knots = 70  # perfect finish speed in knots
    # Convert speed from knots to m/s (1 knot = 0.514444 m/s)
    speed_m_s = perfect_speed_knots * 0.514444
    
    # Calculate kinetic energy: KE = 0.5 * m * v^2
    kinetic_energy = 0.5 * mass * speed_m_s**2
    
    # Convert finish height from feet to meters (1 ft = 0.3048 m)
    height_m = task_finish_height_ft * 0.3048
    
    # Calculate potential energy: PE = m * g * h, with g = 9.81 m/s^2
    gravitational_acceleration = 9.81
    potential_energy = mass * gravitational_acceleration * height_m
    
    # Total energy is the sum of kinetic and potential energy
    total_energy = kinetic_energy + potential_energy
    return total_energy


def calculate_actual_finish_energy_J(finish_altitude_ft: float, finish_speed_gs_kts: float) -> float:
    """
    Calculate the actual finish energy of the glider based on its finish altitude and finish speed.
    
    Parameters:
        finish_altitude_ft (float): The glider's finish altitude in feet.
        finish_speed_gs_kts (float): The glider's finish speed in knots.
    
    Returns:
        float: The glider's actual finish energy in joules.
    """
    mass = 600  # in kilograms
    
    # Convert finish speed from knots to m/s (1 knot = 0.514444 m/s)
    speed_m_s = finish_speed_gs_kts * 0.514444
    kinetic_energy = 0.5 * mass * speed_m_s ** 2
    
    # Convert finish altitude from feet to meters (1 ft = 0.3048 m)
    height_m = finish_altitude_ft * 0.3048
    gravitational_acceleration = 9.81  # m/s^2
    potential_energy = mass * gravitational_acceleration * height_m
    
    total_energy = kinetic_energy + potential_energy
    return total_energy

def calculate_finish_efficiency_score(finish_altitude_ft: float, finish_speed_gs_kts: float, task_finish_height_ft: float) -> float:
    """
    Calculate the finish efficiency score for the glider's finish.
    
    The score is based on:
      1. Calculating the efficiency percentage as:
             (actual_finish_energy_J / task_perfect_finish_J) * 100
      2. If this efficiency percentage is greater than 100, the excess is multiplied by 3
         and subtracted from 100.
      3. Finally, subtract 90 from the adjusted efficiency percentage and round to 2 decimals.
    
    Parameters:
        finish_altitude_ft (float): The glider's finish altitude in feet.
        finish_speed_gs_kts (float): The glider's finish speed in knots.
        task_finish_height_ft (float): The ideal finish altitude in feet to calculate the perfect finish energy.
    
    Returns:
        float: The finish efficiency score.
    """
    actual_finish_energy = calculate_actual_finish_energy_J(finish_altitude_ft, finish_speed_gs_kts)
    perfect_finish_energy = calculate_perfect_finish_J(task_finish_height_ft)
    
    efficiency_percentage = (perfect_finish_energy/actual_finish_energy) * 100
    if efficiency_percentage > 100:
        excess = efficiency_percentage - 100
        efficiency_percentage = 100 - (excess * 4)
    
    #finish_efficiency_score = round(efficiency_percentage - 90, 2)
    finish_efficiency_score = round(efficiency_percentage /10, 2)
    #finish_efficiency_score = efficiency_percentage
    return finish_efficiency_score


def calculate_total_energy(flight_data):
    # Constants
    m = 600  # mass in kg
    g = 9.8  # acceleration due to gravity in m/s^2

    # Calculate for TaskStart (first row)
    h_start = float(flight_data[0][5])  # altitude in meters
    #print('h_start',h_start)
    v_kmh_start = float(flight_data[0][9])  # groundspeed in km/h
    #print('v_kmh_start',v_kmh_start)
    v_ms_start = v_kmh_start / 3.6  # Convert groundspeed to m/s
    total_energy_start = int(m * g * h_start + 0.5 * m * v_ms_start ** 2)
    #print(total_energy_start)

    # Calculate for TaskFinish (last row)
    h_finish = float(flight_data[-1][5])  # altitude in meters
    v_kmh_finish = float(flight_data[-1][9])  # groundspeed in km/h
    v_ms_finish = v_kmh_finish / 3.6  # Convert groundspeed to m/s
    total_energy_finish = int(m * g * h_finish + 0.5 * m * v_ms_finish ** 2)

    return total_energy_start, total_energy_finish

def calculate_start_parameters(flight_data):
    v_start_kmh = flight_data[0][9]
    alt_start_m = int(flight_data[0][5])

    return v_start_kmh, alt_start_m

def calculate_finish_parameters(flight_data):   
    v_finish_kmh = flight_data[-1][9]
    alt_finish_m = int(flight_data[-1][5])
    
    return v_finish_kmh, alt_finish_m
    
def extract_specific_labels(flight_data):
    glide_data = {}
    thermal_data = {}

    for row in flight_data:
        label = row[11]

        if label.startswith('Glide'):
            if label not in glide_data:
                glide_data[label] = [row.copy()]
            else:
                glide_data[label].append(row.copy())
        elif label.startswith('Thermal'):
            if label not in thermal_data:
                thermal_data[label] = [row.copy()]
            else:
                thermal_data[label].append(row.copy())

    return glide_data, thermal_data


def calculate_height_difference(flight_data):
    # Start from index 1 to avoid index out of range error
    for i in range(1, len(flight_data)):
        # Calculate the difference in height
        height_difference_in_meters = float(flight_data[i][5]) - float(flight_data[i - 1][5])
        
        # Convert the height difference to feet (1 meter = 3.28084 feet)
        height_difference_in_feet = height_difference_in_meters * 3.28084
        height_difference_in_feet = round(height_difference_in_feet,4)
        
        # Store the result in flight_data[i][14]
        flight_data[i][14] = str(height_difference_in_feet)

def calculate_sink_rate(flight_data):
    # Start from index 1 to avoid index out of range error
    for i in range(1, len(flight_data)):
        # Calculate the change in height in feet
        change_in_height_m = float(flight_data[i][5]) - float(flight_data[i - 1][5])
        change_in_height_ft = change_in_height_m * 3.28084
        # Calculate the sink rate in feet per second
        sink_rate_fps = change_in_height_ft / 1  # Assuming each step is 1 second
        
        # Convert the sink rate to knots (1 knot = 1.68781 feet per second)
        sink_rate_kts = sink_rate_fps / 1.68781
        
        sink_rate_kts = round(sink_rate_kts,4)
        
        # Store the sink rate in flight_data[i][15]
        flight_data[i][15] = str(sink_rate_kts)

def calculate_glide_ratio(flight_data):
    # Start from index 1 to avoid index out of range error
    for i in range(1, len(flight_data)):
        # Calculate the change in distance in meters
        change_in_distance = float(flight_data[i][8])
        
        # Calculate the change in height in meters
        change_in_height = float(flight_data[i][5]) - float(flight_data[i - 1][5])
        
        # Calculate glide ratio (LD)
        if change_in_height != 0:  # Avoid division by zero
            glide_ratio = change_in_distance / change_in_height
        else:
            glide_ratio = float(-10000)  # Set to a high number if change in height is zero
        
        glide_ratio = glide_ratio * -1 # positive glide ratio is down
        glide_ratio = round(glide_ratio,2)
            
        # Store the glide ratio in flight_data[i][16]
        flight_data[i][16] = str(glide_ratio)


def calculate_ias_kt(flight_data):
    # Start from index 1 to avoid index out of range error
    for i in range(1, len(flight_data)):
        ias_kmh = float(flight_data[i][13])
        ias_kt = ias_kmh * 0.539957
        
        ias_kt = round(ias_kt,2)
        
        flight_data[i][17] = str(ias_kt)


def calculate_MC_equivalent(flight_data, igc_data):
    #find glider class in igc file
    for line in igc_data:
        if 'LCONFPLName=' in line:
            # Find the index of '=' and return the substring after it
            index = line.index('=')
            glider_class =  line[index + 1:].strip()
        
            # Append '.csv' onto the end of the result
            glider_class += '.csv'
            print(glider_class)
            
            #return result
    #use glider_class in csv lookup
    file_path = glider_class #"18-meter.csv" #uses JS3 at max gross because thats the best
    MC_table = []

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            MC_table.append(row)
    #print(MC_table)
    
    #use MC_table to lookup
    for i in range(1, len(flight_data)):
        # Assuming IAS_kt is at index 17 in each sublist of flight_data
        ias_kt = flight_data[i][17]

        # Convert IAS_kt to float for comparison
        ias_kt = float(ias_kt)

        # Initialize variables to keep track of the closest match
        closest_diff = float('inf')
        closest_row = None

        # Iterate through MC_table starting from the second row (index 1) for airspeed
        for row in MC_table[1:]:
            current_diff = abs(ias_kt - float(row[1]))
            if current_diff < closest_diff:
                closest_diff = current_diff
                closest_row = row

        # Update flight_data with the MC LD value    
        flight_data[i][18] = closest_row[2]
        
        # Update flight_data with the MC sinkrate value    
        flight_data[i][19] = closest_row[3]
    
def calculate_netto(flight_data):
    for i in range(2, len(flight_data)):
        # Check if flight_data[i][11] contains "Glide"
        if "Glide" in flight_data[i][11]:
            # Assuming flight_data[i][15] is sinkrate_kt and flight_data[i][19] is sinkrate_MC_at_ias_kt
            sinkrate_kt = float(flight_data[i][15])
            sinkrate_MC_at_ias_kt = float(flight_data[i][19]) ### error here means no csv file format correct

            # Check if both sinkrate_kt and sinkrate_MC_at_ias_kt are not None
            if sinkrate_kt is not None and sinkrate_MC_at_ias_kt is not None:
                # Subtract sinkrate_MC_at_ias_kt from sinkrate_kt to get netto_kt
                netto_kt = sinkrate_kt - sinkrate_MC_at_ias_kt
                netto_kt = round(netto_kt,3)

                # Write netto_kt to flight_data[i][20]
                flight_data[i][20] = str(netto_kt)

def calculate_netto_positive_instances(flight_data):
    #count the number of seconds that the glider is netto positive IN GLIDE ONLY
    #netto_count = 0
    for i in range(2,len(flight_data)):
        # Check if flight_data[i][11] contains "Glide"
        if "Glide" in flight_data[i][11]:
            # Assuming flight_data[i][20] is netto_kt
            netto_kt = float(flight_data[i][20])

            # Check if netto_kt is not None and is greater than 0
            if netto_kt is not None and netto_kt != '' and netto_kt > 0:
                # Increment count_netto_positive for this instance
                flight_data[i][21] = 1 



def count_netto_positive_instances(flight_data):
    #count the number of seconds that the glider is netto positive IN GLIDE ONLY
    netto_count = 0
    for i in range (2, len(flight_data)):
        if "Glide" in flight_data[i][11] and flight_data[i][21] == 1:
           netto_count = netto_count + 1
           #print(i)
           #print('netto_count',netto_count)
    return netto_count
           
       
           
       
        
def calculate_glide_positive_instances(flight_data):
    #count the number of seconds that the glider is sinkrate positive IN GLIDE ONLY
    for i in range(2, len(flight_data)):
        if "Glide" in flight_data[i][11]:
            sinkrate_kt = float(flight_data[i][15])
            #print('sinkrate_kt',sinkrate_kt)
            
            if sinkrate_kt is not None and sinkrate_kt != '' and sinkrate_kt > 0:
                flight_data[i][22] = 1
                #print(i)
                
                
def count_glide_positive_isntances(flight_data):
    sinkrate_positive_count = 0
    for i in range(2, len(flight_data)):
        if "Glide" in flight_data[i][11] and flight_data[i][22] == 1:
            sinkrate_positive_count = sinkrate_positive_count + 1
    return sinkrate_positive_count
       


def calculate_average_netto(flight_data):
    # Initialize variables to keep track of count and sum
    count_netto = 0
    sum_netto = 0

    for i in range(2,len(flight_data)):
        #print(i)
        # Assuming flight_data[i][20] is netto_kt
        if "Glide" in flight_data[i][11]:
            netto_kt = float(flight_data[i][20])
            #print(i)
            #print('netto_kt',netto_kt)
            # Check if netto_kt is not None
            count_netto += 1
            sum_netto += netto_kt
                

        # Calculate average netto if there are instances
        if count_netto > 0:
            average_netto = sum_netto / count_netto
        else:
            average_netto = None
    average_netto = round(average_netto,2)
    
    return average_netto



def calculate_percent_glide_positive_netto(flight_data):
    # Initialize variables to keep track of count
    count_glide_positive_netto = 0
    count_glide_instances = 0

    for i in range(2, len(flight_data)):
        # Check if flight_data[i][11] contains "glide"
        if "Glide" in flight_data[i][11]:
            count_glide_instances += 1

            # Check if flight_data[i][21] is 1
            if flight_data[i][21] == 1 and flight_data[i][26] > 0: #[26] ensures TE increasing
                count_glide_positive_netto += 1

    # Calculate the percentage if there are glide instances
    percent_glide_positive_netto = (count_glide_positive_netto / count_glide_instances) * 100 if count_glide_instances > 0 else None
    
    percent_glide_positive_netto = int(round(percent_glide_positive_netto,0))
    
    return percent_glide_positive_netto


def calculate_percent_glide_positive_sinkrate(flight_data):
    # Initialize variables to keep track of count
    count_glide_positive_sinkrate = 0
    count_glide_instances = 0

    for i in range(2, len(flight_data)):
        # Check if flight_data[i][11] contains "glide"
        if "Glide" in flight_data[i][11]:
            count_glide_instances += 1

            # Check if flight_data[i][22] is 1
            if flight_data[i][22] == 1 and flight_data[i][26] > 0: #[26] ensures TE increasing
                count_glide_positive_sinkrate += 1

    # Calculate the percentage if there are glide instances
    percent_glide_positive_sinkrate = (count_glide_positive_sinkrate / count_glide_instances) * 100 if count_glide_instances > 0 else None
    
    percent_glide_positive_sinkrate = int(round(percent_glide_positive_sinkrate,0))
    
    return percent_glide_positive_sinkrate   



def calculate_energy(flight_data):
    # Constants
    mass = 550  # kg, assuming a constant mass

    for i in range(len(flight_data)):
        # Conversion factor for speed from km/h to m/s
        speed_kmh = float(flight_data[i][13])
        speed_ms = speed_kmh * (1000 / 3600)  # Conversion from km/h to m/s

        # Kinetic energy calculation: KE = 0.5 * m * v^2
        kinetic_energy = 0.5 * mass * speed_ms ** 2

        # Potential energy calculation: PE = m * g * h
        altitude = float(flight_data[i][5])
        gravitational_acceleration = 9.81  # m/s^2, standard gravitational acceleration on Earth
        potential_energy = mass * gravitational_acceleration * altitude

        # Total energy calculation: TE = KE + PE
        total_energy = kinetic_energy + potential_energy

        # Update flight_data with calculated kinetic, potential, and total energy
        flight_data[i][24] = int(kinetic_energy)
        flight_data[i][23] = int(potential_energy)
        flight_data[i][25] = int(total_energy)


def calculate_total_energy_difference(flight_data):
    # Assuming flight_data is a list of lists where each sublist represents flight information
    # e.g., flight_data = [[...], [...], ...]
    compensation_factor = 1.00 #TE decays because of glide ratio (height loss) at constant speed

    for i in range(2, len(flight_data)):
        # Accessing total energy values for the current and previous entries
        total_energy_current = float(flight_data[i][25])
        total_energy_previous = float(flight_data[i - 1][25])

        # Calculate the total energy difference
        total_energy_difference = (compensation_factor * total_energy_current - total_energy_previous)

        # Update flight_data with the total energy difference
        flight_data[i][26] = int(total_energy_difference)



def calculate_average_rate_of_climb_for_all(thermal_data):
    average_rate_of_climbs = {}

    for key, data in thermal_data.items():
        if not data:
            print(f"No data for {key}.")
            average_rate_of_climbs[key] = None
        else:
            # Extract altitude and time data from thermal_data[key]
            altitudes = [row[5] for row in data]
            times = list(range(len(data)))

            # Calculate the average rate of climb
            if times[-1] != 0:
                average_rate_of_climb = (float(altitudes[-1]) - float(altitudes[0])) / times[-1]
                average_rate_of_climbs[key] = average_rate_of_climb
            else:
                #print(f"Error: Division by zero (time is zero) for {key}.")
                average_rate_of_climbs[key] = None

    return average_rate_of_climbs

def thermal_sequence(thermal_data):
    thermal_info = {}
    overall_height_gained = 0
    overall_time_s = 0

    for key, data in thermal_data.items():
        if not data:
            print(f"No data for {key}.")
            thermal_info[key] = None
        else:
            # Extract altitude, time, and speed data from thermal_data[key]
            altitudes = [row[5] for row in data]
            times = list(range(len(data)))
            speeds_kmh = [row[9] for row in data]

            # Calculate average rate of climb
            if times[-1] != 0:
                average_rate_of_climb_ms = round((float(altitudes[-1]) - float(altitudes[0])) / times[-1],2)
            else:
                #print(f"Error: Division by zero (time is zero) for {key}.")
                average_rate_of_climb_ms = .00001

            # Calculate thermal time
            thermal_time_s = len(data)

            # Calculate thermal speed
            average_speed_kmh = sum(speeds_kmh) / len(speeds_kmh)
            
            average_rate_of_climb_kts = average_rate_of_climb_ms * 1.94384
            average_speed_kts = average_speed_kmh * 0.539957
            
            # Calculate thermal height gained
            thermal_height_gained_m = float(altitudes[-1]) - float(altitudes[0])
            thermal_height_gained_ft = thermal_height_gained_m * 3.28084
            
            overall_height_gained += thermal_height_gained_m
            overall_time_s += thermal_time_s
            thermal_time_mmss = convert_seconds_to_mmss(thermal_time_s)
            
            utc_of = find_utc_of(thermal_data,key)

            thermal_info[key] = {
                'average_rate_of_climb_ms': round(average_rate_of_climb_ms,2),
                'average_rate_of_climb_kts': round(average_rate_of_climb_kts,2),
                'thermal_time_s': int(thermal_time_s),
                'thermal_time_mmss': thermal_time_mmss,
                'average_speed_kmh': int(average_speed_kmh),
                'average_speed_kts': int(average_speed_kts),
                'thermal_height_gained_m': int(thermal_height_gained_m),
                'thermal_height_gained_ft': int(thermal_height_gained_ft),
                'starting_utc': utc_of
            }

    # Calculate Overall Rate of Climb
    if overall_time_s != 0:
        overall_rate_of_climb_ms = round(overall_height_gained / overall_time_s, 2)
    else:
        overall_rate_of_climb_ms = 0
        
    overall_rate_of_climb_kts = overall_rate_of_climb_ms * 1.94384
    overall_time_mmss = convert_seconds_to_mmss(overall_time_s)

    thermal_info['Overall'] = {
        'overall_rate_of_climb_ms': round(overall_rate_of_climb_ms,2),
        'overall_rate_of_climb_kts': round(overall_rate_of_climb_kts,2),
        'overall_time_s': overall_time_s,
        'overall_time_mmss':overall_time_mmss
    }
    
    
    return thermal_info



def angular_difference_deg(a, b):
    return (a - b + 180) % 360 - 180

def thermal_sequence_with_bank_and_radius(thermal_data, thermal_radius=100):
    thermal_info = {}
    overall_height_gained = 0
    overall_time_s = 0

    for key, data in thermal_data.items():
        if not data:
            print(f"No data for {key}.")
            thermal_info[key] = None
        else:
            # Extract altitude, time, speed, and heading data from thermal_data[key]
            altitudes = [row[5] for row in data]
            times = list(range(len(data)))
            speeds_kmh = [row[9] for row in data]
            headings_deg = [row[7] for row in data]

            # Calculate average rate of climb
            if times[-1] != 0:
                average_rate_of_climb_ms = round((float(altitudes[-1]) - float(altitudes[0])) / times[-1], 2)
            else:
                average_rate_of_climb_ms = .00001

            # Calculate thermal time
            thermal_time_s = len(data)

            # Calculate thermal speed
            average_speed_kmh = sum(speeds_kmh) / len(speeds_kmh)

            # Calculate rate of change of heading for each step
            delta_headings_deg = [angular_difference_deg(headings_deg[i], headings_deg[i - 1]) for i in range(1, len(headings_deg))]
            
            # Calculate average rate of change of heading
            average_rate_of_change_of_heading_deg_per_s = sum(delta_headings_deg) / thermal_time_s

            print('average_rate_of_change_of_heading_deg_per_s',average_rate_of_change_of_heading_deg_per_s)
            
            # Calculate bank angle
            g = 9.81  # acceleration due to gravity in m/s^2
            bank_angle_rad = math.atan((rate_of_change_of_heading_deg_per_s * average_speed_kmh) / g)
            average_bank_angle = math.degrees(bank_angle_rad)

            # Calculate thermal height gained
            thermal_height_gained_m = float(altitudes[-1]) - float(altitudes[0])
            thermal_height_gained_ft = thermal_height_gained_m * 3.28084

            overall_height_gained += thermal_height_gained_m
            overall_time_s += thermal_time_s
            thermal_time_mmss = convert_seconds_to_mmss(thermal_time_s)

            utc_of = find_utc_of(thermal_data, key)

            thermal_info[key] = {
                'average_rate_of_climb_ms': round(average_rate_of_climb_ms, 2),
                'average_rate_of_climb_kts': round(average_rate_of_climb_ms * 1.94384, 2),
                'thermal_time_s': int(thermal_time_s),
                'thermal_time_mmss': thermal_time_mmss,
                'average_speed_kmh': int(average_speed_kmh),
                'average_speed_kts': int(average_speed_kmh * 0.539957),
                'average_bank_angle': round(average_bank_angle, 2),
                'thermal_height_gained_m': int(thermal_height_gained_m),
                'thermal_height_gained_ft': int(thermal_height_gained_ft),
                'starting_utc': utc_of,
                'thermal_radius_m': thermal_radius
            }

    return thermal_info

"""
    # Calculate Overall Rate of Climb
    if overall_time_s != 0:
        overall_rate_of_climb_ms = round(overall_height_gained / overall_time_s, 2)
    else:
        overall_rate_of_climb_ms = 0
        
    overall_rate_of_climb_kts = overall_rate_of_climb_ms * 1.94384
    overall_time_mmss = convert_seconds_to_mmss(overall_time_s)

    thermal_info['Overall'] = {
        'overall_rate_of_climb_ms': round(overall_rate_of_climb_ms,2),
        'overall_rate_of_climb_kts': round(overall_rate_of_climb_kts,2),
        'overall_time_s': overall_time_s,
        'overall_time_mmss':overall_time_mmss
    }
    
    
    return thermal_info
"""

def calculate_total_distance_between_fixes(fix1, fix2):
    lat1, lon1 = convert_lat_lon_to_decimal(fix1[2], fix1[3])
    lat2, lon2 = convert_lat_lon_to_decimal(fix2[2], fix2[3])
    return calculate_haversine_distance(lat1, lon1, lat2, lon2)


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    # Calculate the Haversine distance between two sets of latitude and longitude
    R = 6371  # Earth radius in kilometers

    # Convert latitude and longitude from DDMMmmmN/S, DDDMMmmmE/W format to decimal degrees
    #lat1, lon1 = convert_lat_lon_to_decimal(lat1, lon1)
    #lat2, lon2 = convert_lat_lon_to_decimal(lat2, lon2)

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # Distance in kilometers

    return distance
    



def glide_sequence(glide_data):
    #print('len(glide_data)',len(glide_data))
    if not glide_data or len(glide_data) < 1:
        print("Insufficient data for L/D ratio calculation.")
        return None

    def convert_lat_lon_to_decimal(lat_str, lon_str):
        lat_dir, lon_dir = lat_str[-1], lon_str[-1]
        lat_deg, lon_deg = float(lat_str[:2]), float(lon_str[:3])
        lat_min, lon_min = float(lat_str[2:4] + '.' + lat_str[4:-1]), float(lon_str[3:5] + '.' + lon_str[5:-1])
        lat_decimal = lat_deg + lat_min / 60
        lon_decimal = lon_deg + lon_min / 60
        lat_decimal = lat_decimal if lat_dir.upper() == 'N' else -lat_decimal
        lon_decimal = lon_decimal if lon_dir.upper() == 'E' else -lon_decimal
        return lat_decimal, lon_decimal

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000  # Radius of the Earth in meters
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance

    glide_info = {}
    total_glide_time_s = 0
    total_glide_distance = 0
    total_glide_height_gained = 0
    total_glide_ias_foraverage = 0
    glide_ias_counter = 0


    for key, data in glide_data.items():
        if not data or len(data) < 2:
            print(f"Insufficient data for glide sequence calculation for {key}.")
            glide_info[key] = None
            continue

        total_distance = 0
        total_height_gained = float(data[0][5]) - float(data[-1][5])
        glide_time_s = len(data)

        for i in range(len(data) - 1):
            lat1, lon1 = convert_lat_lon_to_decimal(data[i][2], data[i][3])
            lat2, lon2 = convert_lat_lon_to_decimal(data[i + 1][2], data[i + 1][3])
            total_distance += haversine(lat1, lon1, lat2, lon2)

        if glide_time_s != 0:
            glide_speed_kmh = total_distance/1000 / glide_time_s * 3600
            glide_ias_kmh = calculate_indicated_airspeed(glide_speed_kmh, float(data[i][5]))
        else:
            #print(f"Error: Division by zero (glide_time_s is zero for {key}).")
            glide_speed_kmh = None

        if total_distance != 0 and total_height_gained != 0:
            ld_ratio = total_distance / total_height_gained
        elif total_height_gained == 0:
            ld_ratio = .00001
        else:
            #print(f"Error: Division by zero (total_distance is zero for {key}).")
            ld_ratio = .00001
        
        total_distance_km = total_distance / 1000
        total_distance_nmi = total_distance * 0.000539957
        
        glide_time_mmss = convert_seconds_to_mmss(glide_time_s)
        glide_speed_kts = glide_speed_kmh * 0.539957
        glide_ias_kts = glide_ias_kmh * 0.539957
        
        #print('key',key)
        utc_of = find_utc_of(glide_data,key)
        #print('utc_of',utc_of)

        glide_info[key] = {
            'ld_ratio': round(ld_ratio,1),
            'glide_time_s': glide_time_s,
            'glide_time_mmss': glide_time_mmss,
            'glide_speed_kmh': int(glide_speed_kmh),
            'glide_speed_kts': int(glide_speed_kts),
            'glide_ias_kmh': int(glide_ias_kmh),
            'glide_ias_kts': int(glide_ias_kts),
            'total_distance_km': round(total_distance_km,2),
            'total_distance_nmi': round(total_distance_nmi,2),
            'starting_utc': utc_of
        }
        #print('glide_info',glide_info)
        
        total_glide_time_s += glide_time_s
        total_glide_distance += total_distance
        total_glide_height_gained += total_height_gained
        total_glide_ias_foraverage += glide_ias_kmh
        glide_ias_counter += 1
        
        
    # Calculate overall L/D ratio
    if total_glide_height_gained != 0:
        overall_ld_ratio = total_glide_distance / total_glide_height_gained
    else:
        #print("Error: Division by zero (total_glide_height_gained is zero).")
        overall_ld_ratio = None
        
    overall_glide_speed_ms = total_glide_distance / total_glide_time_s
    overall_glide_speed_kmh = overall_glide_speed_ms * 3.6
    overall_glide_speed_kts = overall_glide_speed_ms * 1.94384
    overall_glide_ias_kmh = total_glide_ias_foraverage / glide_ias_counter
    overall_glide_ias_kts = overall_glide_ias_kmh * 0.539957
    overall_glide_ias_kmh = overall_glide_ias_kmh
    overall_glide_ias_kts = overall_glide_ias_kts
    #print('overall_glide_ias_kmh',overall_glide_ias_kmh)
    
    
    total_glide_time_mmss = convert_seconds_to_mmss(total_glide_time_s)
    
    total_glide_height_gained_ft = total_glide_height_gained * 3.28084
    total_glide_distance_ft = total_glide_distance * 3.28084
    total_glide_distance_km = total_glide_distance / 1000
    glide_distance_nmi = total_glide_distance * 0.000539957

    glide_info['Overall'] = {
        'ld_ratio': round(overall_ld_ratio,1),
        'glide_time_s': total_glide_time_s,
        'total_glide_time_mmss': total_glide_time_mmss,
        'overall_glide_speed_kmh': int(overall_glide_speed_kmh),
        'overall_glide_speed_kts': int(overall_glide_speed_kts),
        'overall_glide_ias_kmh': int(overall_glide_ias_kmh),
        'overall_glide_ias_kts': int(overall_glide_ias_kts),
        'glide_distance_km': round(total_glide_distance_km,2),
        'glide_distance_nmi': round(glide_distance_nmi,2)
        
    }

    return glide_info

def find_utc_of(glide_info, target_key):
    for key, value_list in glide_info.items():
        for i, inner_list in enumerate(value_list):
            if inner_list[11] == target_key:
                return inner_list[1]


def extract_task_distance(igc_data):
    # Find the line containing "LCONFlightInfoDistanceFlown="
    distance_line = next((line for line in igc_data if "LCONFlightInfoDistanceFlown=" in line), None)

    if distance_line:
        # Extract the distance value after the '=' sign
        task_distance_str = distance_line.split("=")[1].strip()

        # Assuming the value is in the format '197.32 km', convert it to a numeric value
        try:
            task_distance_km = float(task_distance_str.split()[0])
            task_distance_nmi = task_distance_km * 0.539957  # Conversion from km to nautical miles
            return task_distance_km, task_distance_nmi
        except ValueError:
            print("Error: Unable to convert task distance to a numeric value.")
            return None, None
    else:
        print("Error: Unable to find line with task distance information.")
        return None, None


def calculate_average_altitude(flight_data):
    if not flight_data:
        print("Error: Flight data is empty.")
        return None, None

    try:
        # Convert altitude values from strings to floats
        altitudes = [float(row[5]) for row in flight_data]

        # Calculate average altitude in meters
        average_altitude_m = sum(altitudes) / len(altitudes)

        # Convert average altitude to feet
        average_altitude_ft = average_altitude_m * 3.28084

        return int(average_altitude_m), int(average_altitude_ft)
    except ValueError:
        print("Error: Unable to convert altitude values to numeric values.")
        return None, None

def percent_difference(value1, value2):
    diff = round(abs((value1 - value2) / ((value1 + value2) / 2)) * 100,2)
    if value1 < value2:
        diff = diff * -1
    return diff


def calculate_indicated_airspeed(tas, altitude):
    # Constants
    rho0_sea_level = 1.225  # kg/m³, sea-level standard atmospheric density
    lapse_rate = 0.0065  # K/m, standard atmospheric lapse rate

    # Altitude conversion to meters
    altitude_meters = altitude

    # Standard atmospheric density at sea level
    rho0 = rho0_sea_level * math.pow((1 - lapse_rate * altitude_meters / 288.15), (9.80665 / (lapse_rate * 287.05)))

    # Atmospheric density at the given altitude
    rho = rho0 * math.exp(-altitude_meters * 0.0341632 / 288.15)

    # Calculate indicated airspeed
    ias = tas * math.sqrt(rho / rho0)

    return round(ias,2)


def MC_lookup(airspeed, MC_table):
    # Convert airspeed to float for comparison
    airspeed = float(airspeed)

    # Initialize variables to keep track of the closest match
    closest_diff = float('inf')
    closest_row = None

    # Iterate through MC_table starting from the second row (index 1)
    for row in MC_table[1:]:
        current_diff = abs(airspeed - float(row[1]))
        if current_diff < closest_diff:
            closest_diff = current_diff
            closest_row = row

    return float(closest_row[0])



def ideal_MC_given_avg_ias_kts(igc_data, airspeed, climbrate):
    #find glider class in igc file
    for line in igc_data:
        if 'LCONFPLName=' in line:
            # Find the index of '=' and return the substring after it
            index = line.index('=')
            glider_class =  line[index + 1:].strip()
        
            # Append '.csv' onto the end of the result
            glider_class += '.csv'
            #print(glider_class)
            
            #return result
    #use glider_class in csv lookup
    file_path = glider_class #"18-meter.csv" #uses JS3 at max gross because thats the best
    MC_table = []

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            MC_table.append(row)
    #print(MC_table)
    
    # Convert to float for comparison
    airspeed = float(airspeed)
    climbrate = float(climbrate)

    # Initialize variables to keep track of the closest match
    closest_diff = float('inf')
    closest_row = None

    # Iterate through MC_table starting from the second row (index 1) for airspeed
    for row in MC_table[1:]:
        current_diff = abs(airspeed - float(row[1]))
        if current_diff < closest_diff:
            closest_diff = current_diff
            closest_row_airspeed = row
            #print('closest_row_airspeed',closest_row_airspeed)
            
    # Initialize variables to keep track of the closest match
    closest_diff = float('inf')
    closest_row = None
    
    # Iterate through MC_table starting from the second row (index 1) for MC setting
    for row in MC_table[1:]:
        current_diff = abs(climbrate - float(row[0]))
        if current_diff < closest_diff:
            closest_diff = current_diff
            closest_row_climbrate = row    

    return float(closest_row_airspeed[0]), float(closest_row_climbrate[1]), float(closest_row_airspeed[2])

def get_pilot_cn_and_name(igc_data):
    pilot_name = None
    competition_id = None
    fallback_filename = None

    for line in igc_data:

        
        if 'HFPLTPILOT:' in line or 'HFPLTPILOTINCHARGE:' in line:
            colon_index = line.index(':')
            pilot_name = line[colon_index + 1:].strip()
            #print(f"Found pilot name: {pilot_name}")  # Debug print for pilot name

        elif 'HFCIDCOMPETITIONID:' in line or 'HFGIDGLIDERID:' in line:
            colon_index = line.index(':')
            competition_id = line[colon_index + 1:].strip()
            #print(f"Found competition ID: {competition_id}")  # Debug print for competition ID

        elif 'KIGCFILENAME=' in line:
            equal_index = line.index('=')
            fallback_filename = line[equal_index + 1:].strip()
            #print(f"Found fallback filename: {fallback_filename}")  # Debug print for fallback filename

    # Check and print if fallback filename was found
    if not fallback_filename:
        print("Fallback filename not found or empty.")

    # Construct the result string or use the fallback filename if pilot name or competition ID is missing
    if competition_id and pilot_name:
        result_str = f"{competition_id} - {pilot_name}"
    else:
        result_str = fallback_filename

    print(f"Final result: {result_str}")  # Debug print for the final result
    return result_str


def find_task_speed(igc_data):
    
    for line in igc_data:
        if 'LCONFlightInfoAverageSpeed=' in line:
            
            equal_index = line.index('=')
            task_speed = line[equal_index + 1:].strip()
            task_speed = float(task_speed.strip(' km/h'))
            
    return task_speed


def determine_if_task_completed(igc_data):
    
    for line in igc_data:
        if 'LCONFlightInfoPlayerStatus=' in line:
            equal_index = line.index('=')
            finished_yes_no = line[equal_index + 1:].strip()
            if finished_yes_no == 'FINISHED':
                finish_status = 'Task Completed'
            else:
                finish_status = 'Task Not Completed'
    return finish_status

def reorder_csv_by_speed(file_path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Add a new "rank" column based on the "task_speed_kmh" column
    df['rank'] = df['task_speed_kmh'].rank(ascending=False)

    # Define the desired order of rows based on the calculated ranks
    desired_order = df.sort_values(by='rank')['Name'].tolist()

    # Use loc to reorder the DataFrame based on the desired order
    df = df.loc[df['Name'].isin(desired_order)].sort_values(by='Name', key=lambda x: x.map({name: i for i, name in enumerate(desired_order)}))

    # Save the reordered DataFrame to a new CSV file
    df.to_csv(file_path, index=False)

    print(f"Reordered CSV saved to {file_path} based on Rank")
    
def order_csv_by_starting_utc(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Convert 'starting_utc' to string
    df['starting_utc'] = df['starting_utc'].astype(str)

    # Add colon to 'starting_utc'
    df['starting_utc'] = df['starting_utc'].apply(lambda x: x[:2] + ':' + x[2:4] + ':' + x[4:])

    # Sort the DataFrame by 'starting_utc'
    df = df.sort_values(by='starting_utc')

    # Save the sorted DataFrame back to the CSV file
    df.to_csv(file_path, index=False)


def count_valid_rows(glide_info):
    count = 0
    for key, value in glide_info.items():
        if key != 'Overall' and value['total_distance_km'] > 2:
            count += 1
    return count


def calculate_groundspeed_frequency(glide_data):
    """
    Extracts groundspeed data from glide_data, converts it from m/s to knots, 
    rounds each value to the nearest whole number, discards invalid values above 160 knots,
    calculates frequency, and returns an array of frequency and groundspeed in knots.
    
    :param glide_data: A dictionary containing glide data with groundspeed values.
    :return: A list of tuples (frequency, groundspeed_kts).
    """
    groundspeeds_kts = []

    print("Starting to process glide_data...")
    
    # Extract groundspeed values from glide_data and convert to knots
    for key, records in glide_data.items():
        #print(f"Processing key: {key}")
        for index, record in enumerate(records):
            try:
                # Extract groundspeed value in m/s (index 8)
                groundspeed_mps = record[8]
                #print(f"Record {index}: Extracted groundspeed (m/s): {groundspeed_mps}")

                # Convert groundspeed from m/s to knots (1 m/s = 1.94384 knots)
                groundspeed_kts = groundspeed_mps * 1.94384
                #print(f"Record {index}: Converted groundspeed to knots: {groundspeed_kts}")

                # Round to the nearest whole number
                #groundspeed_kts = round(groundspeed_kts)
                #groundspeed_kts = 5 * round(groundspeed_kts / 5)
                groundspeed_kts = 3 * round(groundspeed_kts / 3)
                #print(f"Record {index}: Rounded groundspeed (knots): {groundspeed_kts}")

                # Discard groundspeed values above 250 knots
                if groundspeed_kts > 250:
                    print(f"Record {index}: Discarded invalid groundspeed above 160 kts: {groundspeed_kts}")
                    continue

                # Append to list
                groundspeeds_kts.append(groundspeed_kts)
            except (ValueError, TypeError) as e:
                # Skip if groundspeed is invalid
                print(f"Record {index}: Error processing groundspeed value - {e}")
                continue

    print(f"All extracted and converted groundspeeds (knots): {groundspeeds_kts}")

    # Calculate the frequency of each rounded groundspeed value
    frequency_counter = Counter(groundspeeds_kts)
    print(f"Frequency counter: {frequency_counter}")

    # Convert to a list of tuples (frequency, groundspeed_kts)
    freq_gs_kts = [(freq, gs_kts) for gs_kts, freq in frequency_counter.items()]

    # Sort by groundspeed for better readability
    freq_gs_kts.sort(key=lambda x: x[1])
    print(f"Final sorted list of (frequency, groundspeed_kts): {freq_gs_kts}")

    return freq_gs_kts



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