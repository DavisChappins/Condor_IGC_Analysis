# main_script.py
from helperFile import *
import csv
import os



#do not run this file, run generateSummary.py


def add_igc_to_summary(file_name):

    # Read the file and store each line as an element in a list
    with open(file_name, 'r') as file:
        igc_data = [line.strip() for line in file.readlines()]

    # Use the helper function to process the IGC data
    flight_data = process_igc_data(igc_data)

    pilot_id = get_pilot_cn_and_name(igc_data)

    task_finish_status = determine_if_task_completed(igc_data)

    if task_finish_status == 'Task Completed':
            

        task_speed_kmh = find_task_speed(igc_data)
        task_speed_kts = round(task_speed_kmh * 0.539957,2)


        # Extract the start time using the new function
        detected_start_time = extract_start_time(igc_data)


        # Use the new function to calculate distance between fixes and update flight_data
        flight_data = calculate_distance_between_fixes(flight_data)

        # Use the new function to calculate heading between fixes and update flight_data
        flight_data = calculate_heading_between_fixes(flight_data)

        flight_data = calculate_groundspeed(flight_data)

        # Set 'TaskStart' in flight_data
        flight_data = find_and_set_task_start(flight_data, detected_start_time)

        # Calculate 'TaskFinish' and set it in flight_data
        flight_data = calculate_task_finish(flight_data, igc_data)

        flight_data = analyze_heading_changes(flight_data)

        flight_data = trim_records_by_task(flight_data)


        flight_data = label_thermal_series(flight_data)
        flight_data = label_glide_series(flight_data)

        #calculate start and finish energy
        total_energy_start_J, total_energy_finish_J  = calculate_total_energy(flight_data)
        #print('total_energy_start_J',total_energy_start_J)
        #print('total_energy_finish_J',total_energy_finish_J)
        total_energy_start_MJ = round(total_energy_start_J / 1000000 ,2)
        #print('total_energy_start_MJ',total_energy_start_MJ)
        total_energy_finish_MJ = round(total_energy_finish_J / 1000000 ,2)
        #print('total_energy_finish_MJ',total_energy_finish_MJ)

        start_speed_gs_kmh, start_altitude_m = calculate_start_parameters(flight_data)
        finish_speed_gs_kmh, finish_altitude_m = calculate_finish_parameters(flight_data)
        start_speed_gs_kts = int(start_speed_gs_kmh * 0.539957)
        start_altitude_ft = int(start_altitude_m * 3.28084)
        finish_speed_gs_kts = int(finish_speed_gs_kmh * 0.539957)
        finish_altitude_ft = int(finish_altitude_m * 3.28084)
        
        
        #print('start_speed_kmh',start_speed_kmh)


        glide_data, thermal_data = extract_specific_labels(flight_data)

        number_of_thermals = len(thermal_data)
        number_of_glides = len(glide_data)



        #average_rate_of_climb = calculate_average_rate_of_climb(thermal_data['Thermal1'])
        average_rate_of_climb = calculate_average_rate_of_climb_for_all(thermal_data)
        thermal_info = thermal_sequence(thermal_data)

        average_altitude_m, average_altitude_ft = calculate_average_altitude(flight_data)


        glide_info = glide_sequence(glide_data)


        task_distance_km, task_distance_nmi = extract_task_distance(igc_data)


        #average_ias_kmh = calculate_indicated_airspeed(glide_info['Overall']['overall_glide_speed_kmh'], average_altitude_m)
        average_ias_kmh = calculate_indicated_airspeed(glide_info['Overall']['overall_glide_speed_kmh'], average_altitude_m)

        average_ias_kts = round(average_ias_kmh * 0.539957,2)
        
        #get valid glides (>2km) for counting average, see count_valid_rows function
        modified_number_of_glides = count_valid_rows(glide_info )
        
        average_glide_dist_km = glide_info['Overall']['glide_distance_km'] / modified_number_of_glides #number_of_glides
        average_glide_dist_nmi = average_glide_dist_km * 0.539957
        average_glide_dist_km = round(average_glide_dist_km,2)
        average_glide_dist_nmi = round(average_glide_dist_nmi,2)

        #Calculate 4 Rules
        #1 - glide better
        #2 - climb better
        #3 - shorter distance
        #4 - no jail (avg altitude)
        #other analysis, MC speed vs avg glide speed
        #%further flown than task distance, avg glide distance

        #Rule 1 - Glide Better
        Rule1_glide_ratio = glide_info['Overall']['ld_ratio']
        Rule1_glide_avg_gs_kts = glide_info['Overall']['overall_glide_speed_kts']
        Rule1_glide_avg_ias_kts = int(average_ias_kts)
        Rule1_glide_avg_dist_nmi = average_glide_dist_nmi

        #Rule 2 - Climb Better
        Rule2_avg_climb_rate_kts = thermal_info['Overall']['overall_rate_of_climb_kts']

        #Rule 3 - Shorter Distance
        Rule3_total_glide_distance_nmi = glide_info['Overall']['glide_distance_nmi']
        Rule3_total_glide_more_percent = percent_difference(Rule3_total_glide_distance_nmi,task_distance_nmi)
        #Rule 4 - Don't put yourself in jail (stay high)
        Rule4_avg_altitude_ft = average_altitude_ft

        Rule2_ideal_MC_given_avg_ias_kts, Rule1_ideal_ias_given_avg_climb_kts = ideal_MC_given_avg_ias_kts(igc_data, Rule1_glide_avg_ias_kts,Rule2_avg_climb_rate_kts)

        #write to summary csv
        # Specify the CSV file path
        csv_file_path = "summary.csv"

        # Define column names and data row
        columns = ["Name",
                   "Rule1_glide_avg_gs_kts", "Rule1_glide_avg_ias_kts", "Rule1_glide_ratio", "Rule1_ideal_MC_ias_given_avg_climb_kts", "Rule1_glide_avg_dist_nmi",
                   "Rule2_avg_climb_rate_kts", "Rule2_ideal_MC_given_avg_ias_kts",
                   "Rule3_total_glide_distance_nmi", "Rule3_total_glide_more_percent",
                   "Rule4_avg_altitude_ft",
                   "start_speed_gs_kts", "start_altitude_ft", "total_energy_start_MJ",
                   "finish_speed_gs_kts", "finish_altitude_ft", "total_energy_finish_MJ",
                   "task_speed_kmh"
                   ]

        row_data = [pilot_id,
                   Rule1_glide_avg_gs_kts, Rule1_glide_avg_ias_kts, Rule1_glide_ratio, Rule1_ideal_ias_given_avg_climb_kts, Rule1_glide_avg_dist_nmi,
                   Rule2_avg_climb_rate_kts, Rule2_ideal_MC_given_avg_ias_kts,
                   Rule3_total_glide_distance_nmi, Rule3_total_glide_more_percent,
                   Rule4_avg_altitude_ft,
                   start_speed_gs_kts, start_altitude_ft, total_energy_start_MJ,
                   finish_speed_gs_kts, finish_altitude_ft, total_energy_finish_MJ,
                   task_speed_kmh
                   ]


        # Check if the file already exists
        file_exists = os.path.exists(csv_file_path)

        with open(csv_file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)

            # If the file doesn't exist, write the column headers
            if not file_exists:
                writer.writerow(columns)

            # Write the data row
            writer.writerow(row_data)


    else:
        print(pilot_id,'did not finish the task so this calculation will not run')
