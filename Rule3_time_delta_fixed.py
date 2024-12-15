def Rule3_add_time_delta(csv_file_path):
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
        
        # Calculate time in seconds (keeping negative values)
        time_seconds = (remaining_distance / float(speed)) * 3600
        
        # Convert time to MM:SS format while preserving sign
        is_negative = time_seconds < 0
        abs_seconds = abs(time_seconds)
        minutes = int(abs_seconds // 60)
        seconds = int(abs_seconds % 60)
        time_str = f"{minutes:02}:{seconds:02}"
        if is_negative:
            time_str = "-" + time_str
        
        # Store the results in lists (preserving negative values)
        rule3_absolute_time_sec.append(str(int(time_seconds)))  # Keep negative value
        rule3_absolute_time_lost_mmss.append(time_str)

    # Add values to summary
    for i, time_sec in enumerate(rule3_absolute_time_sec):
        summary[i]['rule3_absolute_time_sec'] = time_sec
    for i, time_str in enumerate(rule3_absolute_time_lost_mmss):
        summary[i]['rule3_absolute_time_mmss'] = time_str

    # Convert the strings to seconds (integer), preserving negative values
    time_values_sec = [int(time_str) for time_str in rule3_absolute_time_sec]
    
    # Find the most negative time value
    min_time_sec = min(time_values_sec)  # This will now find the most negative value

    # Calculate relative times (all positive values relative to most negative)
    result_sec = [time - min_time_sec for time in time_values_sec]
    
    # Format relative times with proper MM:SS
    rule3_relative_time_lost_mmss = []
    for time in result_sec:
        minutes = abs(time) // 60
        seconds = abs(time) % 60
        time_str = f"{minutes:02}:{seconds:02}"
        if time < 0:  # Should not happen now since we subtract the minimum
            time_str = "-" + time_str
        rule3_relative_time_lost_mmss.append(time_str)

    new_header = ['Rule3_absolute_time_lost_mmss', 'Rule3_time_behind_straightest_mmss']

    # Read and update the CSV file
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Add the new header to the end of the existing header row
    header_row = rows[0]
    for header in new_header:
        header_row.append(header)

    for i in range(len(rows) - 1):
        rows[i + 1].append("'" + rule3_absolute_time_lost_mmss[i])
        rows[i + 1].append("'" + rule3_relative_time_lost_mmss[i])

    # Write the updated rows back to the CSV file
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("Added [rule3_absolute_time_lost_mmss, rule3_relative_time_lost_mmss] to analysis")
