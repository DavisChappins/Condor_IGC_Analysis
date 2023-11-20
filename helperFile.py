# helperFile.py
from math import radians, sin, cos, sqrt, atan2, degrees
import math
from collections import deque
from datetime import datetime, timedelta
import csv
import pandas as pd


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
    column_names = ["record", "timeutc", "latitude", "longitude", "validity", "pressAlt", "gnssAlt", "heading", "distance", "groundspeed", "headingChange","glideOrThermal", "task"]
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

        flight_data[index] = [record, timeutc, latitude, longitude, validity, pressAlt, gnssAlt, heading, distance, groundspeed, headingChange, glide_or_thermal, task]

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


def extract_start_time(igc_data):
    # Extract the start time from igc_data
    detected_start_time = None
    for line in igc_data:
        if line.startswith("LCONFlightInfoTaskStart="):
            detected_start_time = line.split("=")[1].replace(":", "")
            break

    return detected_start_time

def find_and_set_task_start(flight_data, detected_start_time):
    # Find the matching record in flight_data and set 'TaskStart' in flight_data[i][11]
    for i in range(1, len(flight_data)):
        if flight_data[i][1] == detected_start_time:
            flight_data[i][12] = 'TaskStart'
            break

    return flight_data

def calculate_task_finish(flight_data, igc_data):
    # Extract the task time from igc_data
    detected_task_duration = None
    for line in igc_data:
        if line.startswith("LCONFlightInfoTaskTime="):
            detected_task_duration = line.split("=")[1].replace(":", "")
            break

    # Extract the start time from igc_data
    detected_start_time = None
    for line in igc_data:
        if line.startswith("LCONFlightInfoTaskStart="):
            detected_start_time = line.split("=")[1].replace(":", "")
            break

    # Convert task duration and start time to HHMMSS
    task_duration_hhmmss = detected_task_duration[:6]
    start_time_hhmmss = detected_start_time[:6]

    # Convert string times to datetime objects
    task_duration_time = datetime.strptime(task_duration_hhmmss, "%H%M%S")
    start_time = datetime.strptime(start_time_hhmmss, "%H%M%S")

    # Calculate the task finish time (timedelta)
    calculated_task_finish_timedelta = timedelta(
        hours=task_duration_time.hour,
        minutes=task_duration_time.minute,
        seconds=task_duration_time.second
    )

    # Add timedelta to start_time to get finish time (datetime)
    calculated_task_finish_datetime = start_time + calculated_task_finish_timedelta

    # Convert the result back to string in HHMMSS format
    calculated_task_finish = calculated_task_finish_datetime.strftime("%H%M%S")
    
    
    # Calculate the task finish time and convert it to HHMMSS
    #calculated_task_finish = str(int(task_duration_hhmmss) + int(start_time_hhmmss))
    
    
    
    
    # Look for a match in flight_data[i][1] for calculated_task_finish
    for i in range(1, len(flight_data)):
        if flight_data[i][1] == calculated_task_finish:
            flight_data[i][12] = 'TaskFinish'
            break

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


def trim_records_by_task(flight_data):
    task_start_index = None
    task_finish_index = None

    # Find indices for 'TaskStart' and 'TaskFinish'
    for i, row in enumerate(flight_data):
        if row[12] == 'TaskStart':
            task_start_index = i
        elif row[12] == 'TaskFinish':
            task_finish_index = i

    # Trim records based on 'TaskStart' and 'TaskFinish'
    if task_start_index is not None and task_finish_index is not None:
        flight_data = flight_data[task_start_index: task_finish_index + 1]

    return flight_data

# helperFile.py

def label_thermal_series(flight_data, threshold=80):
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

def calculate_total_energy(flight_data):
    # Constants
    m = 600  # mass in kg
    g = 9.8  # acceleration due to gravity in m/s^2

    # Calculate for TaskStart (first row)
    h_start = float(flight_data[0][5])  # altitude in meters
    v_kmh_start = float(flight_data[0][9])  # groundspeed in km/h
    v_ms_start = v_kmh_start / 3.6  # Convert groundspeed to m/s
    total_energy_start = int(m * g * h_start + 0.5 * m * v_ms_start ** 2)

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

            thermal_info[key] = {
                'average_rate_of_climb_ms': round(average_rate_of_climb_ms,2),
                'average_rate_of_climb_kts': round(average_rate_of_climb_kts,2),
                'thermal_time_s': int(thermal_time_s),
                'thermal_time_mmss': thermal_time_s,
                'average_speed_kmh': int(average_speed_kmh),
                'average_speed_kts': int(average_speed_kts),
                'thermal_height_gained_m': int(thermal_height_gained_m),
                'thermal_height_gained_ft': int(thermal_height_gained_ft)
            }

    # Calculate Overall Rate of Climb
    if overall_time_s != 0:
        overall_rate_of_climb_ms = round(overall_height_gained / overall_time_s, 2)
    else:
        overall_rate_of_climb_ms = None
        
    overall_rate_of_climb_kts = overall_rate_of_climb_ms * 1.94384
    overall_time_mmss = convert_seconds_to_mmss(overall_time_s)

    thermal_info['Overall'] = {
        'overall_rate_of_climb_ms': round(overall_rate_of_climb_ms,2),
        'overall_rate_of_climb_kts': round(overall_rate_of_climb_kts,2),
        'overall_time_s': overall_time_s,
        'overall_time_mmss':overall_time_mmss
    }
    
    
    return thermal_info


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
    if not glide_data or len(glide_data) < 2:
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


        glide_info[key] = {
            'ld_ratio': round(ld_ratio,1),
            'glide_time_s': glide_time_s,
            'glide_time_mmss': glide_time_mmss,
            'glide_speed_kmh': int(glide_speed_kmh),
            'glide_speed_kts': int(glide_speed_kts),
            'total_distance_km': round(total_distance_km,2),
            'total_distance_nmi': round(total_distance_nmi,2)
        }
        
        total_glide_time_s += glide_time_s
        total_glide_distance += total_distance
        total_glide_height_gained += total_height_gained
        
        
    # Calculate overall L/D ratio
    if total_glide_height_gained != 0:
        overall_ld_ratio = total_glide_distance / total_glide_height_gained
    else:
        #print("Error: Division by zero (total_glide_height_gained is zero).")
        overall_ld_ratio = None
        
    overall_glide_speed_ms = total_glide_distance / total_glide_time_s
    overall_glide_speed_kmh = overall_glide_speed_ms * 3.6
    overall_glide_speed_kts = overall_glide_speed_ms * 1.94384
    
    
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
        'glide_distance_km': round(total_glide_distance_km,2),
        'glide_distance_nmi': round(glide_distance_nmi,2)      
        
    }

    return glide_info


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
        if 'LCONFPLClass=' in line:
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
            
    # Initialize variables to keep track of the closest match
    closest_diff = float('inf')
    closest_row = None
    
    # Iterate through MC_table starting from the second row (index 1) for MC setting
    for row in MC_table[1:]:
        current_diff = abs(climbrate - float(row[0]))
        if current_diff < closest_diff:
            closest_diff = current_diff
            closest_row_climbrate = row    

    return float(closest_row_airspeed[0]), int(closest_row_climbrate[1])

def get_pilot_cn_and_name(igc_data):
    pilot_name = None
    competition_id = None

    for line in igc_data:
        if 'HFPLTPILOT:' in line:
            colon_index = line.index(':')
            pilot_name = line[colon_index + 1:].strip()

        elif 'HFCIDCOMPETITIONID:' in line:
            colon_index = line.index(':')
            competition_id = line[colon_index + 1:].strip()
    
    result_str = competition_id+' - '+pilot_name

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

    print(f"Reordered CSV saved to {file_path}")
    

def count_valid_rows(glide_info):
    count = 0
    for key, value in glide_info.items():
        if key != 'Overall' and value['total_distance_km'] > 2:
            count += 1
    return count