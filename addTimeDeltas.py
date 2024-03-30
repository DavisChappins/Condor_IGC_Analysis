import csv
from datetime import datetime

def Rule4_add_leeching_stats(csv_file_path):
    #  We will assume flights never span midnight, because... that would be madness and I'm lazy :-).
   
    min_time = datetime.strptime('23:59:59','%H:%M:%S')
    max_time = datetime.strptime('00:00:00','%H:%M:%S')
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start_time = datetime.strptime(row['start_time'],'%H:%M:%S')
            if start_time < min_time:
                min_time = start_time
            if max_time < start_time:
                max_time = start_time
    #print(f"Min start time = {min_time}.  Max start time = {max_time}")
    #  Loop again, but this time record our deltas...
    behind_ahead = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start_time = datetime.strptime(row['start_time'],'%H:%M:%S')
            # subtracting times give a timedelta, which always prints as hh:mm:ss.
            # strftime isn't available, so hack this by converting to string and grabbing last 5
            # this will not display correctly if the time delta is > 1 hour.
            delta_behind_first_starter = f"{start_time - min_time}"[-5:]
            delta_before_last_starter = f"{max_time - start_time}"[-5:]
            behind_ahead.append([delta_behind_first_starter, delta_before_last_starter])

    # Initialize an empty list to store the data
    summary = []

    # Open the CSV file and read its contents
    with open(csv_file_path, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Read the header row to get the keys
        header = next(csv_reader, None)

        # Check if the header row exists
        if header:
            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Create a dictionary for each row using the header as keys
                row_dict = dict(zip(header, row))

                # Append the dictionary to the list
                summary.append(row_dict)

    new_header = ['Rule4_time_delta_behind_first_starter_mmss', 'Rule4_time_delta_before_last_starter_mmss']
    # Read the existing CSV file
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Add the new header to the end of the existing header row
    header_row = rows[0]
    for i in range(len(new_header)):
        header_row.append(f'{new_header[i]}')

    for i in range(len(rows) - 1):  # Assuming the lengths of the data lists match the number of rows
        rows[i + 1].append(behind_ahead[i][0])
        rows[i + 1].append(behind_ahead[i][1])

    # Write the updated rows back to the CSV file
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Added {new_header}")

def Rule3_add_time_delta(csv_file_path):
    # Convert task_distance_km to nautical miles using the conversion factor
    #task_distance_nmi = task_distance_km * 0.53996

    # Initialize an empty list to store the data
    summary = []

    # Open the CSV file and read its contents
    with open(csv_file_path, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Read the header row to get the keys
        header = next(csv_reader, None)

        # Check if the header row exists
        if header:
            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Create a dictionary for each row using the header as keys
                row_dict = dict(zip(header, row))

                # Append the dictionary to the list
                summary.append(row_dict)

    # Rule 3 calculations
    smallest_time_seconds = float('inf')  # Initialize with positive infinity
    rule3_absolute_time_sec = []
    rule3_absolute_time_lost_mmss = []

    # Iterate through each index in summary
    for i in range(len(summary)):
        task_distance_km = summary[i]['task_distance_km']
        task_distance_nmi =  float(task_distance_km) * 0.53996
        speed_kts = summary[i]['Rule1_glide_avg_gs_kts']
        speed = float(speed_kts) * 1.852
        total_distance = summary[i]['Rule3_total_glide_distance_km']

        # Calculate remaining distance
        remaining_distance = float(total_distance) - float(task_distance_km)
        #print('total_distance',total_distance)
        #print('task_distance_km',task_distance_km)
        #print('remaining_distance',remaining_distance)
        # Calculate time in seconds
        time_seconds = (remaining_distance / float(speed)) * 3600
        #print('time_seconds',time_seconds)
        
        is_negative = time_seconds < 0
        
        time_seconds = abs(time_seconds)
        
        # Convert time to MM:SS format
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        time_str = f"{minutes:02}:{seconds:02}"
        
        if is_negative:
            time_str = "-" + time_str
        #print('DEBUG FOR TIME LOST')
        # Store the results in lists
        rule3_absolute_time_sec.append(str(int(time_seconds)))
        #print('rule3_absolute_time_sec',rule3_absolute_time_sec)
        rule3_absolute_time_lost_mmss.append(time_str)
        #print('rule3_absolute_time_lost_mmss',rule3_absolute_time_lost_mmss)

        # Update smallest_time_seconds
        smallest_time_seconds = min(smallest_time_seconds, time_seconds)

    # Add 'rule3_absolute_time_sec' to summary using indices
    for i, time_sec in enumerate(rule3_absolute_time_sec):
        summary[i]['rule3_absolute_time_sec'] = time_sec

    # Add 'rule3_absolute_time_mmss to summary using indices
    for i, time_sec in enumerate(rule3_absolute_time_lost_mmss):
        summary[i]['rule3_absolute_time_mmss'] = time_sec

    # Convert the strings to seconds (integer)
    time_values_sec = [int(time_str) for time_str in rule3_absolute_time_sec]
    #print(f'time_values_sec = {time_values_sec}')
    # Find the smallest time value in seconds
    min_time_sec = min(time_values_sec)

    # Subtract all values by the smallest one and convert back to string format
    result_sec = [time - min_time_sec for time in time_values_sec]
    rule3_relative_time_s = str(result_sec)
    rule3_relative_time_lost_mmss = [f'{time // 60:02}:{time % 60:02}' for time in result_sec]

    #print(rule3_relative_time_lost_mmss)

    new_header = ['Rule3_absolute_time_lost_mmss', 'Rule3_time_behind_straightest_mmss']

    # Read the existing CSV file
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Add the new header to the end of the existing header row
    header_row = rows[0]
    for i in range(len(new_header)):
        header_row.append(f'{new_header[i]}')

    for i in range(len(rows) - 1):  # Assuming the lengths of the data lists match the number of rows
        rows[i + 1].append("'"+rule3_absolute_time_lost_mmss[i])
        rows[i + 1].append("'"+rule3_relative_time_lost_mmss[i])

    # Write the updated rows back to the CSV file
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("Added [rule3_absolute_time_lost_mmss, rule3_relative_time_lost_mmss] to analysis")
    
    
    
    
    
###### MAKE THIS A DEF FOR RULE 2 CLIMB DIFF
#climb difference from best climb rate
    
#csv_file_path = 'summary.csv'
    # Convert task_distance_km to nautical miles using the conversion factor
    #task_distance_nmi = task_distance_km * 0.53996

def Rule2_add_time_delta(csv_file_path):
    # Initialize an empty list to store the data
    summary = []

    # Open the CSV file and read its contents
    with open(csv_file_path, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Read the header row to get the keys
        header = next(csv_reader, None)

        # Check if the header row exists
        if header:
            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Create a dictionary for each row using the header as keys
                row_dict = dict(zip(header, row))

                # Append the dictionary to the list
                summary.append(row_dict)
                
    #print(summary)

    #csv_file = 'summary.csv'

    # Find the maximum climb rate
    max_climb_rate = max(float(entry['Rule2_avg_climb_rate_kts']) for entry in summary)


    # Iterate through the summary
    for entry in summary:
        
        # Remove the single quote at the beginning of 'mm:ss' format
        mmss_format = entry['total_thermal_time_mmss'][1:]
        
        # Calculate the average climb rate for the current entry
        avg_climb_rate = float(entry['Rule2_avg_climb_rate_kts'])

        # Calculate the climb rate loss
        climb_rate_loss = max_climb_rate - avg_climb_rate

        # Convert 'mm:ss' format to seconds for total thermal time
        minutes, seconds = map(int, mmss_format.split(':'))
        total_thermal_time_seconds = minutes * 60 + seconds
        
        # Calculate the time you WOULD have spent climbing at the maximum rate
        if climb_rate_loss == 0 or total_thermal_time_seconds == 0 or max_climb_rate == 0:
            climb_rate_loss_seconds = 0
        else:
            climb_rate_loss_seconds = climb_rate_loss * total_thermal_time_seconds / max_climb_rate

        # Convert back to 'mm:ss' format
        climb_rate_loss_mmss = '{:02}:{:02}'.format(int(climb_rate_loss_seconds // 60), int(climb_rate_loss_seconds % 60))

        # Add climb_rate_loss_mmss to the entry
        entry['Rule2_time_behind_best_climb_mmss'] = "'"+climb_rate_loss_mmss

        # Print or use climb_rate_loss_mmss as needed
        #print(f"For entry {entry}: Climb Rate Loss: {climb_rate_loss_mmss}")
        

    # Update the existing 'summary.csv' file with the new column
    output_csv_file_path = csv_file_path

    # Add the new column to the header if it doesn't exist
    if 'Rule2_time_behind_best_climb_mmss' not in header:
        header.append('Rule2_time_behind_best_climb_mmss')

    # Add the new column value to each row
    #for row in summary:
        # Add the new column value to the row
        #row['Rule2_relative_time_lost_mmss'] = next((entry['Rule2_relative_time_lost_mmss'] for entry in summary if entry['id'] == row['id']), '')
        #print(row)
    # Write the updated data back to 'summary.csv'
    with open(output_csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(summary)
        
    print("Added [Rule2_relative_time_lost_mmss] to analysis")

    #print(f"Updated data written to {output_csv_file_path}")
    
    
    

#add time delta behind first place    
    
#csv_file_path = 'summary.csv'


def Task_time_behind_rank1(csv_file_path):
    # Initialize an empty list to store the data
    summary = []

    # Open the CSV file and read its contents
    with open(csv_file_path, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Read the header row to get the keys
        header = next(csv_reader, None)

        # Check if the header row exists
        if header:
            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Create a dictionary for each row using the header as keys
                row_dict = dict(zip(header, row))

                # Append the dictionary to the list
                summary.append(row_dict)
                
    # Convert task_time_hmmss to seconds for each entry
    time_seconds_list = []
    for entry in summary:
        task_time_hmmss = entry['task_time_hmmss']
        time_object = datetime.strptime(task_time_hmmss, "%H:%M:%S")
        time_seconds = time_object.hour * 3600 + time_object.minute * 60 + time_object.second
        time_seconds_list.append(time_seconds)

    # Find the fastest time
    fastest_time = min(time_seconds_list)

    # Calculate the time behind rank 1 for each entry
    for i, entry in enumerate(summary):
        task_time_behind_rank1 = time_seconds_list[i] - fastest_time
        #entry['task_time_behind_rank1'] = task_time_behind_rank1

        # Convert task_time_behind_rank1 to 'mm:ss' format
        mm, ss = divmod(task_time_behind_rank1, 60)
        entry['task_time_behind_rank1_mmss'] = "'"+'{:02}:{:02}'.format(mm, ss)

    # Print the updated summary
    #for entry in summary:
    #    print(entry)

    # Update the existing 'summary.csv' file with the new column
    output_csv_file_path = csv_file_path

    # Add the new column to the header if it doesn't exist
    if 'task_time_behind_rank1_mmss' not in header:
        header.append('task_time_behind_rank1_mmss')

    # Add the new column value to each row
    #for row in summary:
        # Add the new column value to the row
        #row['Rule2_relative_time_lost_mmss'] = next((entry['Rule2_relative_time_lost_mmss'] for entry in summary if entry['id'] == row['id']), '')
        #print(row)
    # Write the updated data back to 'summary.csv'
    with open(output_csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(summary)




def calculate_height_lost(speed_kts, distance_km, glide_ratio):
    speed_kts = float(speed_kts)
    distance_km = float(distance_km)
    glide_ratio = float(glide_ratio)
    
    # Convert speed from knots to km/h
    speed_kmh = speed_kts * 1.852  # 1 knot = 1.852 km/h
    
    # Calculate time using the formula: time = distance / speed
    time_hours = distance_km / speed_kmh
    
    # Calculate height lost using the formula: height lost = distance / glide ratio
    height_lost_km = distance_km / glide_ratio
    
    # Convert height lost from kilometers to feet
    height_lost_feet = height_lost_km * 3280.84  # 1 kilometer = 3280.84 feet
        
    return height_lost_feet

def calculate_average_speed(distance, time):
    return float(distance) / time

def calculate_time_saved(speed1, speed2, distance, time2):
    time1 = float(distance) / float(speed1)
    time_saved = time2 - time1
    return time_saved

def hours_to_mmss(hours):
    minutes = int(hours * 60)
    seconds = int((hours * 60 - minutes) * 60)
    return f"'{minutes:02d}:{seconds:02d}"

'''
task_distance_km = 170.56
csv_file_path = 'summary.csv'
# Initialize an empty list to store the data
summary = []

# Open the CSV file and read its contents
with open(csv_file_path, 'r') as csvfile:
    # Create a CSV reader object
    csv_reader = csv.reader(csvfile)

    # Read the header row to get the keys
    header = next(csv_reader, None)

    # Check if the header row exists
    if header:
        # Iterate through each row in the CSV file
        for row in csv_reader:
            # Create a dictionary for each row using the header as keys
            row_dict = dict(zip(header, row))

            # Append the dictionary to the list
            summary.append(row_dict)
            
            
height_lost_list = []

for entry in summary:
    speed_kts = entry.get('Rule1_glide_avg_gs_kts', 0)
    speed_kts = float(speed_kts)
    distance_km = task_distance_km
    glide_ratio = entry.get('Rule1_glide_ratio', 1)
    glide_ratio = float(glide_ratio)
    
    height_lost_feet = calculate_height_lost(speed_kts, distance_km, glide_ratio)
    height_lost_list.append(height_lost_feet)       

'''



#csv_file_path = 'summary.csv'
# Initialize an empty list to store the data
# Initialize an empty list to store the data
def AAT_Task_time_behind_rank1(csv_file_path):
    summary = []

    # Open the CSV file and read its contents
    with open(csv_file_path, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Read the header row to get the keys
        header = next(csv_reader, None)

        # Check if the header row exists
        if header:
            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Create a dictionary for each row using the header as keys
                row_dict = dict(zip(header, row))

                # Append the dictionary to the list
                summary.append(row_dict)
                
    # Convert task_time_hmmss to seconds for each entry
    time_seconds_list = []
    for entry in summary:
        #task_time_hmmss = entry['task_time_hmmss']
        #print('task_time_hmmss',task_time_hmmss)
        #time_object = datetime.strptime(task_time_hmmss, "%H:%M:%S")
        #time_seconds = time_object.hour * 3600 + time_object.minute * 60 + time_object.second
        #time_seconds_list.append(time_seconds)
        
        #print('entry[task_distance_km]',entry['task_distance_km'])
        
        dist = float(entry['task_distance_km'])
        speed = float(entry['task_speed_kmh'])
        
        # Calculate task_time_h as a float value
        task_time_h = dist / speed
        print('task_time_h', task_time_h)
        
        # Extract hours and fractional minutes directly from the float value
        hours = int(task_time_h)
        minutes = (task_time_h - hours) * 60
        
        # Convert "h.hhhh" format to seconds
        time_seconds = int((hours * 3600) + (minutes * 60))
        
        # Append the result to the time_seconds_list
        time_seconds_list.append(time_seconds)
    
        
    print('time_seconds_list',time_seconds_list)

    # Find rank 1 at the top
    #rank1_time_seconds = min(time_seconds_list)
    rank1_time_seconds = time_seconds_list[0]

    # Assume there is at least one task in the summary
    result_list = []

    for i, task in enumerate(summary):
        # Extract task details
        distance1 = summary[0]['task_distance_km']
        speed1 = summary[0]['task_speed_kmh']
        time1 = time_seconds_list[0]
        time1 - time1 / 3600
        
        distance2 = task['task_distance_km']
        speed2 = task['task_speed_kmh']
        time2 = time_seconds_list[i]
        time2 = time2 / 3600
        

        # Calculate average speeds
        average_speed1 = summary[0]['task_speed_kmh']
        average_speed2 = task['task_speed_kmh']

        # Calculate time saved if airplane 2 were traveling at the speed of airplane 1
        time_saved_hours = calculate_time_saved(average_speed1, speed2, distance2, time2)
        #print('time_saved_hours',time_saved_hours)
        # Convert time saved to mm:ss format
        time_saved_mmss = hours_to_mmss(time_saved_hours)

        # Append the results to the result_list
        result_list.append({
            "average_speed1": average_speed1,
            "average_speed2": average_speed2,
            "time_saved_mmss": time_saved_mmss
        })

    # Extract the 'time_saved_mmss' values from the result_list
    time_saved_values = [item['time_saved_mmss'] for item in result_list]

    # Update the existing 'summary.csv' file with the new column
    output_csv_file_path = csv_file_path

    # New column header and data
    new_column_header = 'AAT_time_behind_mmss'
    new_column_data = time_saved_values


    # Add new column header to each dictionary
    for row in summary:
        row[new_column_header] = None  # Initialize with None

    # Add new data to the corresponding dictionaries
    for i, row in enumerate(summary):
        row[new_column_header] = new_column_data[i]

    # Extract headers from the first dictionary in the list
    headers = list(summary[0].keys())

    # Write the updated data back to the CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        
        # Write the header
        writer.writeheader()
        
        # Write the data
        writer.writerows(summary)
        
    print('Added AAT specific time behind leader')

# Add the new column to the header if it doesn't exist
#if 'AAT_task_time_behind_rank1_mmss' not in header:
    #header.append('AAT_task_time_behind_rank1_mmss')

# Add the new column value to each row
#for row in summary:
    # Add the new column value to the row
    #row['Rule2_relative_time_lost_mmss'] = next((entry['Rule2_relative_time_lost_mmss'] for entry in summary if entry['id'] == row['id']), '')
    #print(row)
# Write the updated data back to 'summary.csv'
#with open(output_csv_file_path, 'w', newline='') as csvfile:
    #writer = csv.DictWriter(csvfile, fieldnames=header)
    #writer.writeheader()
    #writer.writerows(summary)
    

def solve_for_h(E, m, v):
    #m in kg
    #v in knots
    #E in joules
    m = float(m)
    v_ms = float(v) * 0.514444
    g = 9.8  # m/s^2, assuming Earth's gravitational acceleration
    height_m = (E - (0.5 * m * (v_ms)**2)) / (m * g)
    height_ft = height_m * 3.28084
    return height_ft


def calculate_total_energy(m, v, h):
    #m in kg
    #v in knots
    #h in feet
    m_kg = float(m)
    v_ms = float(v) * 0.514444
    h_m = float(h) * 0.3048
    g = 9.8  # m/s^2, assuming Earth's gravitational acceleration
    KE = 0.5 * m_kg * (v_ms**2)
    PE = m_kg * g * h_m
    total_energy = KE + PE
    return total_energy

def find_max_start_speed_kts(data_list):
    max_start_speed = 0

    for entry in data_list:
        start_speed_str = entry.get('start_speed_gs_kts', '0')  # Get the start altitude as a string, default to '0' if not present
        start_speed = int(start_speed_str)

        if start_speed > max_start_speed:
            max_start_speed = start_speed

    return max_start_speed
'''
#pass in
max_start_height_ft = 4951 
mass_kg = 600 #18m is 600, 15m is 500, club is 250

csv_file_path = 'summary.csv'
summary = []


# Open the CSV file and read its contents
with open(csv_file_path, 'r') as csvfile:
    # Create a CSV reader object
    csv_reader = csv.reader(csvfile)

    # Read the header row to get the keys
    header = next(csv_reader, None)

    # Check if the header row exists
    if header:
        # Iterate through each row in the CSV file
        for row in csv_reader:
            # Create a dictionary for each row using the header as keys
            row_dict = dict(zip(header, row))

            # Append the dictionary to the list
            summary.append(row_dict)

start_speed_kts = float(summary[0]['start_speed_gs_kts'])
start_height_ft = float(summary[0]['start_altitude_ft'])
TE = calculate_total_energy(mass_kg, start_speed_kts, start_height_ft)

#calculated height diff from max start height
height_diff_ft = max_start_height_ft - start_height_ft

#find max start speed
max_start_speed_gs_kts = find_max_start_speed_kts(summary)

#find start speed
start_speed_diff_kts = max_start_speed_gs_kts - start_speed_kts

#find speed diff height equivalent
start_speed_equivalent_height_diff_ft = solve_for_h(TE, mass_kg, start_speed_diff_kts)

'''

'''    
# Write the 'time_saved_mmss' values to a new CSV file
with open(output_csv_file_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    
    # Write header row (if needed)
    writer.writerow(['AAT_time_saved_mmss'])
    
    # Write the values from the result_list to the CSV file
    writer.writerows(map(lambda x: [x], time_saved_values))

print(f'CSV file "{output_csv_file_path}" created successfully.')
'''


import csv

csv_file_path = 'summary.csv'



def Rule1_add_time_delta(csv_file_path):
    summary = []

    # Open the CSV file and read its contents
    with open(csv_file_path, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Read the header row to get the keys
        header = next(csv_reader, None)

        # Check if the header row exists
        if header:
            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Create a dictionary for each row using the header as keys
                row_dict = dict(zip(header, row))

                # Append the dictionary to the list
                summary.append(row_dict)

    # Conversion factor from knots to km/h
    knots_to_kmh = 1.852

    # Keep summary[0] fixed
    

    # Lists to store time_behind_rank1_from_gs_s, time_behind_rank1_from_gs_mmss, and time_behind_rank1_from_gs
    time_behind_gs_s_values = []
    time_behind_gs_mmss_values = []
    time_behind_gs_values = []

    # Lists to store ld_time_diff_s, ld_time_diff_mmss, composite_time_diff_s, and composite_time_diff_mmss
    ld_time_diff_s_values = []
    ld_time_diff_mmss_values = []
    composite_time_diff_s_values = []
    composite_time_diff_mmss_values = []

    # Iterate through summary starting from index 1
    for i in range(len(summary)):
        # Calculate the expressions for each row
        time_behind_rank1_from_gs = (
            (float(summary[i]['task_distance_km']) / (float(summary[i]['Rule1_glide_avg_gs_kts']) * knots_to_kmh)) -
            (float(summary[i]['task_distance_km']) / (float(summary[0]['Rule1_glide_avg_gs_kts']) * knots_to_kmh))
        )

        # Append the results to the respective lists
        time_behind_gs_values.append(time_behind_rank1_from_gs)

        # Calculate time_behind_rank1_from_gs_s and append to the list
        time_behind_rank1_from_gs_s = time_behind_rank1_from_gs * 3600
        time_behind_gs_s_values.append(int(time_behind_rank1_from_gs_s))

        # Calculate time_behind_rank1_from_gs_mmss and append to the list
        if time_behind_rank1_from_gs > 0:
            hours = int(time_behind_rank1_from_gs)
            minutes = int((time_behind_rank1_from_gs - hours) * 60)
            seconds = int(((time_behind_rank1_from_gs - hours) * 60 - minutes) * 60)
            time_behind_rank1_from_gs_mmss = "{:02d}:{:02d}".format(minutes, seconds)
        else:
            time_behind_rank1_from_gs = time_behind_rank1_from_gs * -1
            hours = int(time_behind_rank1_from_gs)
            minutes = int((time_behind_rank1_from_gs - hours) * 60)
            seconds = int(((time_behind_rank1_from_gs - hours) * 60 - minutes) * 60)
            time_behind_rank1_from_gs = time_behind_rank1_from_gs * -1
            time_behind_rank1_from_gs_mmss = "-{:02d}:{:02d}".format(minutes, seconds)
        
        time_behind_gs_mmss_values.append("'"+time_behind_rank1_from_gs_mmss)

        # Step 1: Calculate height loss for summary[0] and summary[1]
        height_loss_rank1_ft = (float(summary[i]['task_distance_km']) * 3280.84) / float(summary[0]['Rule1_glide_ratio'])
        height_loss_rank2_ft = (float(summary[i]['task_distance_km']) * 3280.84) / float(summary[i]['Rule1_glide_ratio'])

        # Step 2: Find the difference between height loss
        height_loss_difference_ft = height_loss_rank2_ft - height_loss_rank1_ft

        # Step 3: Convert climb rate from kts to ft for summary[0]
        climb_rate_fps = float(summary[i]['Rule2_avg_climb_rate_kts']) * 1.68781  

        # Step 4: Calculate rank1 climb rate / difference
        if climb_rate_fps != 0 and height_loss_difference_ft != 0:
            ld_time_diff_s = height_loss_difference_ft / climb_rate_fps
        else:
            ld_time_diff_s = 0
        #print('ld_time_diff_s',ld_time_diff_s)
        # Append the results to the respective lists
        ld_time_diff_s_values.append(int(ld_time_diff_s))

        # Calculate ld_time_diff_mmss and append to the list
        if ld_time_diff_s > 0:
            hours = ld_time_diff_s // 3600
            minutes = (ld_time_diff_s) // 60
            seconds = ld_time_diff_s % 60
            ld_time_diff_mmss = "{:02}:{:02}".format(int(minutes), int(seconds))
        else:
            ld_time_diff_s = ld_time_diff_s * -1
            hours = ld_time_diff_s // 3600
            minutes = (ld_time_diff_s) // 60
            seconds = ld_time_diff_s % 60
            ld_time_diff_s = ld_time_diff_s * -1
            ld_time_diff_mmss = "-{:02}:{:02}".format(int(minutes), int(seconds))

        ld_time_diff_mmss_values.append("'"+ld_time_diff_mmss)

        # Calculate composite_time_diff_s and append to the list
        composite_time_diff_s = time_behind_rank1_from_gs_s + ld_time_diff_s
        print('time_behind_rank1_from_gs_s',time_behind_rank1_from_gs_s)
        print('ld_time_diff_s',ld_time_diff_s)
        print('composite_time_diff_s',composite_time_diff_s)
        composite_time_diff_s_values.append(int(composite_time_diff_s))

        # Check if the time difference is negative
        is_negative = composite_time_diff_s < 0

        # Convert the time difference into a positive value
        composite_time_diff_s = abs(composite_time_diff_s)

        hours = composite_time_diff_s // 3600
        minutes = (composite_time_diff_s) // 60
        seconds = composite_time_diff_s % 60

        # Format the time difference as a string
        composite_time_diff_mmss = "{:02}:{:02}".format(int(minutes), int(seconds))

        # If the original time difference was negative, add a negative sign to the output string
        if is_negative:
            composite_time_diff_mmss = "-" + composite_time_diff_mmss

        print('composite_time_diff_mmss', composite_time_diff_mmss)    
        
        composite_time_diff_mmss_values.append("'"+composite_time_diff_mmss)




    # Print the lists of time_behind values
    print("List of time_behind_rank1_from_gs_s values:", time_behind_gs_s_values)
    print("List of time_behind_rank1_from_gs_mmss values:", time_behind_gs_mmss_values)
    print("List of time_behind_rank1_from_gs values:", time_behind_gs_values)

    # Print the lists of ld_time_diff and composite_time_diff values
    print("List of ld_time_diff_s values:", ld_time_diff_s_values)
    print("List of ld_time_diff_mmss values:", ld_time_diff_mmss_values)
    print("List of composite_time_diff_s values:", composite_time_diff_s_values)
    print("List of composite_time_diff_mmss values:", composite_time_diff_mmss_values)




    # Assuming you want to use the 'Rule1_time_behind_rank1_mmss' as the new column header
    #new_column_header = 'Rule1_time_behind_rank1_mmss'
    new_column_headers = ['Rule1_time_behind_rank1_mmss','Rule1_time_behind_rank1_from_gs_mmss','Rule1_time_behind_rank1_from_ld_mmss']


    # Update the existing 'summary.csv' file with the new column
    output_csv_file_path = 'summary.csv'  # Use a different file path if needed

    # New column data
    #new_column_data = composite_time_diff_mmss_values
    # New column data
    new_column_data1 = composite_time_diff_mmss_values
    new_column_data2 = time_behind_gs_mmss_values
    new_column_data3 = ld_time_diff_mmss_values

    # Add new column header to each dictionary
    #for row in summary:
        #row[new_column_header] = None  # Initialize with None
    # Add new columns headers to each dictionary
    for row in summary:
        for header in new_column_headers:
            row[header] = None  # Initialize with None

    # Add new data to the corresponding dictionaries
    for i, row in enumerate(summary):
        row[new_column_headers[0]] = new_column_data1[i]
        row[new_column_headers[1]] = new_column_data2[i]
        row[new_column_headers[2]] = new_column_data3[i]

    # Extract headers from the first dictionary in the list
    headers = list(summary[0].keys())

    # Write the updated data back to the CSV file
    with open(output_csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        
        # Write the header
        writer.writeheader()
        
        # Write the data
        writer.writerows(summary)
        
    print('Added glide time behind rank 1')




"""
csv_file_path = 'summary.csv'
summary = []


# Open the CSV file and read its contents
with open(csv_file_path, 'r') as csvfile:
    # Create a CSV reader object
    csv_reader = csv.reader(csvfile)

    # Read the header row to get the keys
    header = next(csv_reader, None)
    
        # Check if the header row exists
    if header:
        # Iterate through each row in the CSV file
        for row in csv_reader:
            # Create a dictionary for each row using the header as keys
            row_dict = dict(zip(header, row))

            # Append the dictionary to the list
            summary.append(row_dict)
            

# Conversion factor from knots to km/h
knots_to_kmh = 1.852

# Keep summary[0] fixed
reference_row = summary[0]

# List to store time_behind_rank1_from_gs values
time_behind_values = []

# Calculate the expressions
time_behind_rank1_from_gs = (
    (float(summary[1]['task_distance_km']) / (float(summary[1]['Rule1_glide_avg_gs_kts']) * knots_to_kmh)) -
    (float(summary[0]['task_distance_km']) / (float(summary[0]['Rule1_glide_avg_gs_kts']) * knots_to_kmh))
)
print(time_behind_rank1_from_gs)
time_behind_rank1_from_gs_s = time_behind_rank1_from_gs * 3600
print('time_behind_rank1_from_gs_s',time_behind_rank1_from_gs_s)

if time_behind_rank1_from_gs > 0:
    # Convert the result to hours, minutes, and seconds
    hours = int(time_behind_rank1_from_gs)
    minutes = int((time_behind_rank1_from_gs - hours) * 60)
    seconds = int(((time_behind_rank1_from_gs - hours) * 60 - minutes) * 60)
    time_behind_rank1_from_gs_mmss = "{:02d}:{:02d}".format(minutes, seconds)
else:
    time_behind_rank1_from_gs = time_behind_rank1_from_gs * -1
    # Convert the result to hours, minutes, and seconds
    hours = int(time_behind_rank1_from_gs)
    minutes = int((time_behind_rank1_from_gs - hours) * 60)
    seconds = int(((time_behind_rank1_from_gs - hours) * 60 - minutes) * 60)
    time_behind_rank1_from_gs_mmss = "-{:02d}:{:02d}".format(minutes, seconds)    

# Format the result as "hh:mm:ss"


# Print the formatted result
print('time_behind_rank1_from_gs_mmss',time_behind_rank1_from_gs_mmss)




# Step 1: Calculate height loss for summary[0] and summary[1]
height_loss_rank1_ft = (float(summary[0]['task_distance_km']) * 3280.84) / float(summary[0]['Rule1_glide_ratio'])
height_loss_rank2_ft = (float(summary[1]['task_distance_km']) * 3280.84) / float(summary[1]['Rule1_glide_ratio'])
#print('height_loss_rank2',height_loss_rank2)
# Step 2: Find the difference between height loss
height_loss_difference_ft =  height_loss_rank2_ft - height_loss_rank1_ft
print('height_loss_difference_ft',height_loss_difference_ft)
# Step 3: Convert climb rate from kts to ft for summary[0]
climb_rate_fps = float(summary[0]['Rule2_avg_climb_rate_kts']) * 1.68781  
print('climb_rate_fps',climb_rate_fps)

# Step 4: Calculate rank1 climb rate / difference
if climb_rate_fps != 0 and height_loss_difference_ft != 0:
    ld_time_diff_s = height_loss_difference_ft / climb_rate_fps
else:
    ld_time_diff_s = 0




# Print the result
print("time_diff_s:", ld_time_diff_s)

#time_diff_s = 12345  # replace this with your actual time difference in seconds

if ld_time_diff_s > 0:
    hours = ld_time_diff_s // 3600
    minutes = (ld_time_diff_s) // 60
    seconds = ld_time_diff_s % 60
    ld_time_diff_mmss = "{:02}:{:02}".format(int(minutes), int(seconds))

else:
    ld_time_diff_s = ld_time_diff_s * -1
    hours = ld_time_diff_s // 3600
    minutes = (ld_time_diff_s) // 60
    seconds = ld_time_diff_s % 60
    ld_time_diff_mmss = "-{:02}:{:02}".format(int(minutes), int(seconds))



print('ld_time_diff_mmss',ld_time_diff_mmss)



composite_time_diff_s = time_behind_rank1_from_gs_s + ld_time_diff_s
print('composite_time_diff_s',composite_time_diff_s)



hours = composite_time_diff_s // 3600
minutes = (composite_time_diff_s) // 60
seconds = composite_time_diff_s % 60
composite_time_diff_mmss = "{:02}:{:02}".format(int(minutes), int(seconds))
print('composite_time_diff_mmss',composite_time_diff_mmss)

"""

"""
# Update the existing 'summary.csv' file with the new column
output_csv_file_path = csv_file_path

# New column header and data
new_column_header = 'Rule1_time_behind_rank1_mmss'
new_column_data = time_saved_values
#now loop composite through all, keep rank 1 as rank 1 but the other as i

# Add new column header to each dictionary
for row in summary:
    row[new_column_header] = None  # Initialize with None

# Add new data to the corresponding dictionaries
for i, row in enumerate(summary):
    row[new_column_header] = new_column_data[i]

# Extract headers from the first dictionary in the list
headers = list(summary[0].keys())

# Write the updated data back to the CSV file
with open(csv_file_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    
    # Write the header
    writer.writeheader()
    
    # Write the data
    writer.writerows(summary)
    
print('Added glide time behind rank 1')
"""
