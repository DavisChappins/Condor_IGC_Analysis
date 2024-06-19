

import csv



task_distance_nmi = 92.0950324 #pass this in when a def

# Specify the file path
csv_file_path = 'summary.csv'

# Initialize an empty dictionary to store the data
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

# Display the list of dictionaries
#for row_dict in summary:
    #print(row_dict)

#find time lost via task
#rule 1 time, glide at mc speed
#rule 2 time, climb at the best rate
#rule 3 time, diff from task distance at glide_avg_gs
#rule 4 time n/a
#time lost during start, compared to best start, convert speed to seconds and convert height to seconds??
#time lost during finish, compared to min energy
            
   
   
   
#rule 3 time, diff from task distance at glide_avg_gs
smallest_time_seconds = float('inf')  # Initialize with positive infinity

# Lists to store the results
rule3_absolute_time_sec = []
rule3_absolute_time_lost_mmss = []


# Iterate through each index in summary
for i in range(len(summary)):
    speed = summary[i]['Rule1_glide_avg_gs_kts']
    total_distance = summary[i]['Rule3_total_glide_distance_nmi']

    # Calculate remaining distance
    remaining_distance = float(total_distance) - task_distance_nmi

    # Calculate time in seconds
    time_seconds = (remaining_distance / float(speed)) * 3600
    # Convert time to MM:SS format
    minutes = int(time_seconds // 60)
    seconds = int(time_seconds % 60)
    time_str = f"{minutes:02}:{seconds:02}"

    # Store the results in lists
    rule3_absolute_time_sec.append(str(int(time_seconds)))
    rule3_absolute_time_lost_mmss.append(time_str)

    # Update smallest_time_seconds
    smallest_time_seconds = min(smallest_time_seconds, time_seconds)

# Add 'rule3_absolute_time_sec' to summary using indices
for i, time_sec in enumerate(rule3_absolute_time_sec):
    summary[i]['rule3_absolute_time_sec'] = time_sec
    #print(summary[i])
# Add 'rule3_absolute_time_mmss to summary using indices
for i, time_sec in enumerate(rule3_absolute_time_lost_mmss):
    summary[i]['rule3_absolute_time_mmss'] = time_sec

        

# Convert the strings to seconds (integer)
time_values_sec = [int(time_str) for time_str in rule3_absolute_time_sec]

# Find the smallest time value in seconds
min_time_sec = min(time_values_sec)

# Subtract all values by the smallest one and convert back to string format
#rule3_relative_time_s = [str(time - min_time_sec) for time in time_values_sec]
# Subtract all values by the smallest one
result_sec = [time - min_time_sec for time in time_values_sec]
rule3_relative_time_s = str(result_sec)
rule3_relative_time_lost_mmss = [f'{time // 60:02}:{time % 60:02}' for time in result_sec]

print(rule3_relative_time_lost_mmss)




# Display the results
#for key, diff in time_diff_seconds.items():
    #print(f"For key '{key}': Time difference from the smallest time: {diff} seconds")



new_header = ['rule3_absolute_time_lost_mmss','rule3_relative_time_lost_mmss']

# Read the existing CSV file
with open(csv_file_path, 'r') as file:
    reader = csv.reader(file)
    rows = list(reader)

# Add the new header to the end of the existing header row
header_row = rows[0]
for i in range(len(new_header)):
    header_row.append(f'{new_header[i]}')
    

for i in range(len(rows) - 1):  # Assuming the lengths of the data lists match the number of rows
    rows[i + 1].append(rule3_absolute_time_lost_mmss[i])
    rows[i + 1].append(rule3_relative_time_lost_mmss[i])

# Write the updated rows back to the CSV file
with open(csv_file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(rows)


