import csv
from datetime import datetime

def Rule3_add_time_delta(csv_file_path):
    # Initialize an empty list to store the data
    summary = []

    # Open the CSV file and read its contents
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader, None)
        if header:
            for row in csv_reader:
                row_dict = dict(zip(header, row))
                summary.append(row_dict)

    # Rule 3 calculations
    rule3_absolute_time_sec = []
    rule3_absolute_time_lost_mmss = []

    for i in range(len(summary)):
        task_distance_km = summary[i]['task_distance_km']
        task_distance_nmi = float(task_distance_km) * 0.53996
        speed_kts = summary[i]['Rule1_glide_avg_gs_kts']
        speed = float(speed_kts) * 1.852
        total_distance = summary[i]['Rule3_total_glide_distance_km']

        remaining_distance = float(total_distance) - float(task_distance_km)
        time_seconds = (remaining_distance / float(speed)) * 3600

        is_negative = time_seconds < 0
        abs_seconds = abs(time_seconds)
        minutes = int(abs_seconds // 60)
        seconds = int(abs_seconds % 60)
        time_str = f"{minutes:02}:{seconds:02}"
        if is_negative:
            time_str = "-" + time_str

        rule3_absolute_time_sec.append(int(time_seconds))
        rule3_absolute_time_lost_mmss.append(time_str)

    # For Rule3, compute two delta values:
    #   - Rule3_time_behind_rank1: delta relative to the first (rank1) row
    #   - Rule3_time_behind_straightest_mmss: delta relative to the best (minimum) value
    time_values_sec = rule3_absolute_time_sec
    rank1_time_sec = time_values_sec[0]
    best_time_sec = min(time_values_sec)

    rule3_time_behind_rank1_list = []
    rule3_time_behind_straightest_list = []

    for t in time_values_sec:
        delta_rank1 = t - rank1_time_sec
        mm = int(delta_rank1 // 60)
        ss = int(delta_rank1 % 60)
        rule3_time_behind_rank1_list.append("'" + '{:02}:{:02}'.format(mm, ss))

        delta_straightest = t - best_time_sec
        mm2 = int(delta_straightest // 60)
        ss2 = int(delta_straightest % 60)
        rule3_time_behind_straightest_list.append("'" + '{:02}:{:02}'.format(mm2, ss2))

    # Read and update the CSV file
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # New header order for Rule 3 columns:
    # We now add three columns in this order: Rule3_time_behind_rank1, Rule3_absolute_time_lost_mmss, Rule3_time_behind_straightest_mmss
    new_headers = ['Rule3_time_behind_rank1', 'Rule3_absolute_time_lost_mmss', 'Rule3_time_behind_straightest_mmss']
    header_row = rows[0]
    for h in new_headers:
        if h not in header_row:
            header_row.append(h)

    for i in range(len(rows) - 1):
        # Append the new values in the specified order
        rows[i + 1].append(rule3_time_behind_rank1_list[i])
        rows[i + 1].append("'" + rule3_absolute_time_lost_mmss[i])
        rows[i + 1].append(rule3_time_behind_straightest_list[i])

    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("Added [Rule3_time_behind_rank1, Rule3_absolute_time_lost_mmss, Rule3_time_behind_straightest_mmss] to analysis")


def Rule2_add_time_delta(csv_file_path):
    summary = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader, None)
        if header:
            for row in csv_reader:
                row_dict = dict(zip(header, row))
                summary.append(row_dict)
                
    max_climb_rate = max(float(entry['Rule2_avg_climb_rate_kts']) for entry in summary)

    rule2_loss_seconds = []  # store each entry's climb loss in seconds
    for entry in summary:
        # Remove the single quote at the beginning of 'mm:ss' format
        mmss_format = entry['total_thermal_time_mmss'][1:]
        
        # Calculate the average climb rate for the current entry
        avg_climb_rate = float(entry['Rule2_avg_climb_rate_kts'])
        climb_rate_loss = max_climb_rate - avg_climb_rate
        
        # Convert 'mm:ss' format to seconds for total thermal time
        minutes, seconds = map(int, mmss_format.split(':'))
        total_thermal_time_seconds = minutes * 60 + seconds
        
        # Calculate the time you WOULD have spent climbing at the maximum rate
        if climb_rate_loss == 0 or total_thermal_time_seconds == 0 or max_climb_rate == 0:
            climb_rate_loss_seconds = 0
        else:
            climb_rate_loss_seconds = climb_rate_loss * total_thermal_time_seconds / max_climb_rate

        rule2_loss_seconds.append(climb_rate_loss_seconds)
        climb_rate_loss_mmss = '{:02}:{:02}'.format(int(climb_rate_loss_seconds // 60), int(climb_rate_loss_seconds % 60))
        entry['Rule2_time_behind_best_climb_mmss'] = "'" + climb_rate_loss_mmss

    # Get rank 1's climb rate and thermal time
    rank1_climb_rate = float(summary[0]['Rule2_avg_climb_rate_kts'])
    rank1_mmss = summary[0]['total_thermal_time_mmss'][1:]  # Remove leading quote
    rank1_minutes, rank1_seconds = map(int, rank1_mmss.split(':'))
    rank1_thermal_time = rank1_minutes * 60 + rank1_seconds
    
    # Calculate how long it would take this pilot to gain rank1's height
    rule2_time_behind_rank1_list = []
    for entry in summary:
        pilot_climb_rate = float(entry['Rule2_avg_climb_rate_kts'])
        if pilot_climb_rate == 0:
            effective_time = rank1_thermal_time
        else:
            effective_time = rank1_thermal_time * (rank1_climb_rate / pilot_climb_rate)
            
        # Time behind rank1 is how much longer it would take
        delta = effective_time - rank1_thermal_time
        mm = int(abs(delta) // 60)
        ss = int(abs(delta) % 60)
        sign = '-' if delta < 0 else ''
        rule2_time_behind_rank1_list.append("'" + sign + '{:02}:{:02}'.format(mm, ss))

    # Update header with new columns if they don't exist
    new_cols = ['Rule2_time_behind_best_climb_mmss', 'Rule2_time_behind_rank1']
    for col in new_cols:
        if col not in header:
            header.append(col)
    
    # Add the new delta column to each entry
    for i, entry in enumerate(summary):
        entry['Rule2_time_behind_rank1'] = rule2_time_behind_rank1_list[i]

    # Ensure header includes any extra keys from the dictionaries
    for entry in summary:
        for key in entry.keys():
            if key not in header:
                header.append(key)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(summary)
        
    print("Added [Rule2_time_behind_rank1, Rule2_time_behind_best_climb_mmss] to analysis")

def Start_energy_add_time_delta(csv_file_path):
    """
    For each row, calculate the time (in seconds) it takes to climb the lost height 
    due to start energy (using the value in 'height_loss_due_to_start_energy_ft') at the pilot's 
    average climb rate ('Rule2_avg_climb_rate_kts', converted from kts to ft/s using 1.68781).
    Then compute the delta compared to the first (rank1) entry as:
         delta = current_entry_time - rank1_time
    The result is formatted in "mm:ss" (with a leading single quote) and added to 
    a new CSV column 'Start_energy_time_behind_rank1'.
    
    Parameters:
        csv_file_path (str): Path to the CSV file to update.
    """
    summary = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        header = csv_reader.fieldnames
        for row in csv_reader:
            summary.append(row)
    
    # Calculate the climb time (in seconds) for each row.
    # Climb time = height_loss_due_to_start_energy_ft / (Rule2_avg_climb_rate_kts * 1.68781)
    for row in summary:
        try:
            height_loss = float(row.get('height_loss_due_to_start_energy_ft', 0))
        except ValueError:
            height_loss = 0
        try:
            avg_climb_rate_kts = float(row.get('Rule2_avg_climb_rate_kts', 0))
        except ValueError:
            avg_climb_rate_kts = 0
        
        climb_rate_fps = avg_climb_rate_kts * 1.68781
        if climb_rate_fps:
            climb_time_seconds = height_loss / climb_rate_fps
        else:
            climb_time_seconds = 0
        
        # Store the computed time temporarily in the row
        row['__start_energy_climb_time_s'] = climb_time_seconds

    # Use the first row's climb time as the rank1 reference.
    rank1_time = summary[0]['__start_energy_climb_time_s']
    
    # Calculate the delta for each row and format it as "mm:ss".
    for row in summary:
        delta = float(row['__start_energy_climb_time_s']) - rank1_time
        # Round the delta to an integer number of seconds.
        delta_sec = int(round(delta))
        if delta_sec < 0:
            mm = int(abs(delta_sec) // 60)
            ss = int(abs(delta_sec) % 60)
            formatted_delta = "'-" + '{:02}:{:02}'.format(mm, ss)
        else:
            mm = int(delta_sec // 60)
            ss = int(delta_sec % 60)
            formatted_delta = "'" + '{:02}:{:02}'.format(mm, ss)
        row['Start_energy_time_behind_rank1'] = formatted_delta

    # Remove the temporary column from header and rows.
    if '__start_energy_climb_time_s' in header:
        header.remove('__start_energy_climb_time_s')
    for row in summary:
        row.pop('__start_energy_climb_time_s', None)
    
    # Ensure the new column is in the header.
    if 'Start_energy_time_behind_rank1' not in header:
        header.append('Start_energy_time_behind_rank1')
    
    # Write the updated rows back to the CSV file.
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(summary)
    
    print("Added [Start_energy_time_behind_rank1] to analysis")


def Finish_energy_add_time_delta(csv_file_path):
    """
    For each entry, calculate the climb time in seconds required to overcome the 
    lost height due to finish energy (height_loss_due_to_finish_energy_ft) using the pilot's 
    average climb rate (Rule2_avg_climb_rate_kts, converted from kts to ft/s using 1.68781).
    Then, compute the time delta relative to the first (rank 1) entry as:
         delta = current_entry_time - rank1_time
    This delta is formatted as "mm:ss" (with a leading single quote) and will be negative
    if the current entry's climb time is less than rank1's.
    
    Parameters:
        csv_file_path (str): Path to the CSV file to update.
    """
    summary = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader, None)
        if header:
            for row in csv_reader:
                row_dict = dict(zip(header, row))
                summary.append(row_dict)
    
    # Calculate the climb time (in seconds) for each entry.
    # Climb time = height_loss_due_to_finish_energy_ft / (Rule2_avg_climb_rate_kts * 1.68781)
    finish_energy_time_seconds = []
    for entry in summary:
        try:
            height_loss = float(entry.get('height_loss_due_to_finish_energy_ft', '0'))
        except ValueError:
            height_loss = 0.0
        try:
            avg_climb_rate = float(entry.get('Rule2_avg_climb_rate_kts', '0'))
        except ValueError:
            avg_climb_rate = 0.0
        climb_rate_fps = avg_climb_rate * 1.68781
        if climb_rate_fps != 0:
            climb_time = height_loss / climb_rate_fps
        else:
            climb_time = 0
        finish_energy_time_seconds.append(climb_time)
    
    # Use the first entry's climb time as the rank1 reference.
    rank1_time = finish_energy_time_seconds[0]
    
    # Compute delta (in seconds) relative to rank1: delta = current_time - rank1_time.
    finish_energy_time_behind_rank1_list = []
    for t in finish_energy_time_seconds:
        delta = t - rank1_time
        # To handle negative values properly, compute the absolute value and then prefix with '-' if needed.
        delta_sec = int(round(delta))
        if delta_sec < 0:
            mm = int(abs(delta_sec) // 60)
            ss = int(abs(delta_sec) % 60)
            formatted_delta = "'-" + '{:02}:{:02}'.format(mm, ss)
        else:
            mm = int(delta_sec // 60)
            ss = int(delta_sec % 60)
            formatted_delta = "'" + '{:02}:{:02}'.format(mm, ss)
        finish_energy_time_behind_rank1_list.append(formatted_delta)
    
    # Add the new column to the header (if not already present) and update each entry.
    new_col = 'Finish_energy_time_behind_rank1'
    if new_col not in header:
        header.append(new_col)
    for i, entry in enumerate(summary):
        entry[new_col] = finish_energy_time_behind_rank1_list[i]
    
    # Write the updated rows back to the CSV file.
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(summary)
        
    print("Added [Finish_energy_time_behind_rank1] to analysis")
def Task_time_behind_rank1(csv_file_path):
    summary = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader, None)
        if header:
            for row in csv_reader:
                row_dict = dict(zip(header, row))
                summary.append(row_dict)
                
    time_seconds_list = []
    for entry in summary:
        task_time_hmmss = entry['task_time_hmmss']
        time_object = datetime.strptime(task_time_hmmss, "%H:%M:%S")
        time_seconds = time_object.hour * 3600 + time_object.minute * 60 + time_object.second
        time_seconds_list.append(time_seconds)

    fastest_time = min(time_seconds_list)

    for i, entry in enumerate(summary):
        task_time_behind_rank1 = time_seconds_list[i] - fastest_time
        mm, ss = divmod(task_time_behind_rank1, 60)
        entry['task_time_behind_rank1_mmss'] = "'" + '{:02}:{:02}'.format(mm, ss)

    output_csv_file_path = csv_file_path
    if 'task_time_behind_rank1_mmss' not in header:
        header.append('task_time_behind_rank1_mmss')
    with open(output_csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(summary)


def AAT_Task_time_behind_rank1(csv_file_path):
    summary = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader, None)
        if header:
            for row in csv_reader:
                row_dict = dict(zip(header, row))
                summary.append(row_dict)
                
    time_seconds_list = []
    for entry in summary:
        dist = float(entry['task_distance_km'])
        speed = float(entry['task_speed_kmh'])
        task_time_h = dist / speed
        hours = int(task_time_h)
        minutes = (task_time_h - hours) * 60
        time_seconds = int((hours * 3600) + (minutes * 60))
        time_seconds_list.append(time_seconds)
    
    rank1_time_seconds = time_seconds_list[0]

    result_list = []
    for i, task in enumerate(summary):
        average_speed1 = summary[0]['task_speed_kmh']
        average_speed2 = task['task_speed_kmh']
        time2 = time_seconds_list[i] / 3600
        time_saved_hours = calculate_time_saved(average_speed1, speed2=task['task_speed_kmh'], distance=task['task_distance_km'], time2=time2)
        time_saved_mmss = hours_to_mmss(time_saved_hours)
        result_list.append({
            "average_speed1": average_speed1,
            "average_speed2": average_speed2,
            "time_saved_mmss": time_saved_mmss
        })

    time_saved_values = [item['time_saved_mmss'] for item in result_list]
    output_csv_file_path = csv_file_path
    new_column_header = 'AAT_time_behind_mmss'
    for row in summary:
        row[new_column_header] = None
    for i, row in enumerate(summary):
        row[new_column_header] = time_saved_values[i]
    headers = list(summary[0].keys())
    with open(output_csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(summary)
    print('Added AAT specific time behind leader')


def Rule1_add_time_delta(csv_file_path):
    summary = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader, None)
        if header:
            for row in csv_reader:
                row_dict = dict(zip(header, row))
                summary.append(row_dict)

    knots_to_kmh = 1.852
    time_behind_gs_s_values = []
    time_behind_gs_mmss_values = []
    ld_time_diff_s_values = []
    ld_time_diff_mmss_values = []
    composite_time_diff_s_values = []
    composite_time_diff_mmss_values = []

    for i in range(len(summary)):
        time_behind_rank1_from_gs = (
            (float(summary[i]['task_distance_km']) / (float(summary[i]['Rule1_glide_avg_gs_kts']) * knots_to_kmh)) -
            (float(summary[i]['task_distance_km']) / (float(summary[0]['Rule1_glide_avg_gs_kts']) * knots_to_kmh))
        )
        time_behind_rank1_from_gs_s = time_behind_rank1_from_gs * 3600
        time_behind_gs_s_values.append(int(time_behind_rank1_from_gs_s))

        if time_behind_rank1_from_gs > 0:
            hours = int(time_behind_rank1_from_gs)
            minutes = int((time_behind_rank1_from_gs - hours) * 60)
            seconds = int(((time_behind_rank1_from_gs - hours) * 60 - minutes) * 60)
            time_behind_rank1_from_gs_mmss = "{:02d}:{:02d}".format(minutes, seconds)
        else:
            time_behind_rank1_from_gs = -time_behind_rank1_from_gs
            hours = int(time_behind_rank1_from_gs)
            minutes = int((time_behind_rank1_from_gs - hours) * 60)
            seconds = int(((time_behind_rank1_from_gs - hours) * 60 - minutes) * 60)
            time_behind_rank1_from_gs_mmss = "-{:02d}:{:02d}".format(minutes, seconds)
        
        time_behind_gs_mmss_values.append("'" + time_behind_rank1_from_gs_mmss)

        height_loss_rank1_ft = (float(summary[i]['task_distance_km']) * 3280.84) / float(summary[0]['Rule1_glide_ratio'])
        height_loss_rank2_ft = (float(summary[i]['task_distance_km']) * 3280.84) / float(summary[i]['Rule1_glide_ratio'])
        height_loss_difference_ft = height_loss_rank2_ft - height_loss_rank1_ft
        climb_rate_fps = float(summary[i]['Rule2_avg_climb_rate_kts']) * 1.68781  

        if climb_rate_fps != 0 and height_loss_difference_ft != 0:
            ld_time_diff_s = height_loss_difference_ft / climb_rate_fps
        else:
            ld_time_diff_s = 0
        ld_time_diff_s_values.append(int(ld_time_diff_s))

        if ld_time_diff_s > 0:
            hours = ld_time_diff_s // 3600
            minutes = (ld_time_diff_s) // 60
            seconds = ld_time_diff_s % 60
            ld_time_diff_mmss = "{:02}:{:02}".format(int(minutes), int(seconds))
        else:
            ld_time_diff_s = -ld_time_diff_s
            hours = ld_time_diff_s // 3600
            minutes = (ld_time_diff_s) // 60
            seconds = ld_time_diff_s % 60
            ld_time_diff_s = -ld_time_diff_s
            ld_time_diff_mmss = "-{:02}:{:02}".format(int(minutes), int(seconds))

        ld_time_diff_mmss_values.append("'" + ld_time_diff_mmss)

        composite_time_diff_s = time_behind_rank1_from_gs_s + ld_time_diff_s
        composite_time_diff_s_values.append(int(composite_time_diff_s))
        is_negative = composite_time_diff_s < 0
        composite_time_diff_s = abs(composite_time_diff_s)
        hours = composite_time_diff_s // 3600
        minutes = (composite_time_diff_s) // 60
        seconds = composite_time_diff_s % 60
        composite_time_diff_mmss = "{:02}:{:02}".format(int(minutes), int(seconds))
        if is_negative:
            composite_time_diff_mmss = "-" + composite_time_diff_mmss
        composite_time_diff_mmss_values.append("'" + composite_time_diff_mmss)

    new_column_headers = ['Rule1_time_behind_rank1_mmss', 'Rule1_time_behind_rank1_from_gs_mmss', 'Rule1_time_behind_rank1_from_ld_mmss']
    output_csv_file_path = 'summary.csv'
    for row in summary:
        for header_item in new_column_headers:
            row[header_item] = None
    for i, row in enumerate(summary):
        row[new_column_headers[0]] = composite_time_diff_mmss_values[i]
        row[new_column_headers[1]] = time_behind_gs_mmss_values[i]
        row[new_column_headers[2]] = ld_time_diff_mmss_values[i]
    headers = list(summary[0].keys())
    with open(output_csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(summary)
        
    print('Added glide time behind rank 1')


def calculate_height_lost(speed_kts, distance_km, glide_ratio):
    speed_kts = float(speed_kts)
    distance_km = float(distance_km)
    glide_ratio = float(glide_ratio)
    speed_kmh = speed_kts * 1.852
    time_hours = distance_km / speed_kmh
    height_lost_km = distance_km / glide_ratio
    height_lost_feet = height_lost_km * 3280.84
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


def solve_for_h(E, m, v):
    m = float(m)
    v_ms = float(v) * 0.514444
    g = 9.8
    height_m = (E - (0.5 * m * (v_ms)**2)) / (m * g)
    height_ft = height_m * 3.28084
    return height_ft

def calculate_total_energy(m, v, h):
    m_kg = float(m)
    v_ms = float(v) * 0.514444
    h_m = float(h) * 0.3048
    g = 9.8
    KE = 0.5 * m_kg * (v_ms**2)
    PE = m_kg * g * h_m
    total_energy = KE + PE
    return total_energy

def find_max_start_speed_kts(data_list):
    max_start_speed = 0
    for entry in data_list:
        start_speed_str = entry.get('start_speed_gs_kts', '0')
        start_speed = int(start_speed_str)
        if start_speed > max_start_speed:
            max_start_speed = start_speed
    return max_start_speed


# Function to reorder the CSV columns in the new order
def reorder_columns(csv_file_path):
    # Desired new order of the nine columns:
    desired_order = [
        "task_time_behind_rank1_mmss",
        "Rule1_time_behind_rank1_mmss",
        "Rule1_time_behind_rank1_from_gs_mmss",
        "Rule1_time_behind_rank1_from_ld_mmss",
        "Rule2_time_behind_rank1",
        "Rule2_time_behind_best_climb_mmss",
        "Rule3_time_behind_rank1",
        "Rule3_absolute_time_lost_mmss",
        "Rule3_time_behind_straightest_mmss"
    ]
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    new_rows = []
    for row in rows:
        new_row = {key: row.get(key, "") for key in desired_order}
        new_rows.append(new_row)
    with open(csv_file_path, 'w', newline='') as csvfile_out:
        writer = csv.DictWriter(csvfile_out, fieldnames=desired_order)
        writer.writeheader()
        writer.writerows(new_rows)

# Example of how you might call the functions in order:
# csv_file_path = 'summary.csv'
# Task_time_behind_rank1(csv_file_path)
# Rule1_add_time_delta(csv_file_path)
# Rule2_add_time_delta(csv_file_path)
# Rule3_add_time_delta(csv_file_path)
# AAT_Task_time_behind_rank1(csv_file_path)
# reorder_columns(csv_file_path)

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