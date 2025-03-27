# main_script.py
from helperFile import *
import csv
import os
import re


#do not run this file, run generateSummary.py
#file_name = "US Soaring Q4 2023 Oct Nov Dec-Competition day 13-DC1-256263.igc"



def add_igc_to_summary(file_name, tp_adjustment_km, task_start_height_ft, task_finish_height_ft):
    # Read the file and store each line as an element in a list
    print("Opening ",file_name)
    with open(file_name, 'r') as file:
        igc_data = [line.strip() for line in file.readlines()]

    # Use the helper function to process the IGC data
    flight_data = process_igc_data(igc_data)

    pilot_id = get_pilot_cn_and_name(igc_data)
    print("pilot_id",pilot_id)

    glider_type = get_glider_type(igc_data)
    print("glider_type",glider_type)

    task_finish_status = determine_if_task_completed(igc_data)

    if task_finish_status == 'Task Completed':
            
        
        task_speed_kmh = find_task_speed(igc_data)
        task_speed_kts = round(task_speed_kmh * 0.539957,2)
        
        
        # Extract the start time using the new function
        detected_start_time = extract_start_time(igc_data)
        
        detected_task_time = extract_task_time(igc_data)
        task_time_hmmss = detected_task_time
        
        max_start_height_ft = extract_max_start_height(igc_data)
        #print('max_start_height',max_start_height)

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
        
        flight_data = add_calculated_ias(flight_data)
        
        flight_data = trim_records_by_task(flight_data)
        
        

        flight_data = label_thermal_series(flight_data)
        flight_data = replace_thermal_sequences(flight_data)
        flight_data = detect_thermal(flight_data)
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


        #print('glide_data',glide_data)
        
        #new function to calculate (frequency, gs_kts)
        freq_gs_kts = calculate_groundspeed_frequency(glide_data)
        print(freq_gs_kts)
        
        



        
        
        #average_rate_of_climb = calculate_average_rate_of_climb(thermal_data['Thermal1'])
        average_rate_of_climb = calculate_average_rate_of_climb_for_all(thermal_data)
        
        
        thermal_info = thermal_sequence(thermal_data)
        #print(thermal_info)
        total_thermal_time_mmss = "'"+thermal_info['Overall']['overall_time_mmss']
        

        #experimental netto stuff
        calculate_height_difference(flight_data)
        calculate_sink_rate(flight_data)
        calculate_glide_ratio(flight_data)
        calculate_ias_kt(flight_data)
        calculate_MC_equivalent(flight_data, igc_data)
        calculate_netto(flight_data)
        calculate_netto_positive_instances(flight_data)
        netto_positive_count = count_netto_positive_instances(flight_data) # count the number of seconds that the glider is netto positive IN GLIDE
        calculate_glide_positive_instances(flight_data)
        sinkrate_positive_count = count_glide_positive_isntances(flight_data) # count the number of seconds that the glider is sinkrate positive IN GLIDE
        
        avg_netto_kt = calculate_average_netto(flight_data)
        

        calculate_energy(flight_data)
        calculate_total_energy_difference(flight_data)
        
        percent_glide_netto_positive = calculate_percent_glide_positive_netto(flight_data)
        percent_glide_sinkrate_positive = calculate_percent_glide_positive_sinkrate(flight_data)
        
        
         #

        discarded_thermals, useful_thermals = count_thermal_info(thermal_info)
        
        print('number_of_thermals',number_of_thermals)
        print('useful_thermals',useful_thermals)
        print('discarded_thermals',discarded_thermals)
        
        if number_of_thermals != 0:
            thermal_discard_percent = int((discarded_thermals / number_of_thermals) * 100)
        else:
            thermal_discard_percent = 0

        print('thermal_discard_percent',thermal_discard_percent)

        average_altitude_m, average_altitude_ft = calculate_average_altitude(flight_data)


        glide_info = glide_sequence(glide_data)
        #print('glide_info-summary-time',glide_info['Overall']['total_glide_time_mmss'])
        total_glide_time_mmss = "'"+glide_info['Overall']['total_glide_time_mmss']


        task_distance_km, task_distance_nmi = extract_task_distance(igc_data)
        
        #add in adjustments
        tp_adjustment_mi = tp_adjustment_km * 0.539957
        
        task_distance_km = task_distance_km + tp_adjustment_km
        task_distance_nmi = task_distance_nmi + tp_adjustment_mi
    
        
        #print(task_distance_nmi)
        #print('task_distance_km',task_distance_km)
        #print(thermal_data)
        
        #average_ias_kmh = glide_info['Overall']['overall_glide_ias_kmh']
        #average_ias_kts = glide_info['Overall']['overall_glide_ias_kts']
        
        average_ias_kmh = calculate_indicated_airspeed(glide_info['Overall']['overall_glide_speed_kmh'], average_altitude_m)
        average_ias_kmh = calculate_indicated_airspeed(glide_info['Overall']['overall_glide_speed_kmh'], average_altitude_m)
        average_ias_kts = round(average_ias_kmh * 0.539957,2)
        
        #get valid glides (>2km) for counting average, see count_valid_rows function
        #modified_number_of_glides = count_valid_rows(glide_info )
        
        #average_glide_dist_km = glide_info['Overall']['glide_distance_km'] / modified_number_of_glides #number_of_glides
        average_glide_dist_km = glide_info['Overall']['glide_distance_km'] / number_of_glides
        average_glide_dist_nmi = average_glide_dist_km * 0.539957
        average_glide_dist_km = round(average_glide_dist_km,2)
        average_glide_dist_nmi = round(average_glide_dist_nmi,2)
        
        
        
        #calcualte start and finish energy and time
        if task_start_height_ft is not None:
            #Start
            start_efficiency_score = calculate_start_efficiency_score(start_altitude_ft, start_speed_gs_kts, task_start_height_ft)
            print("start_efficiency_percent",start_efficiency_score)
            height_loss_due_to_start_energy_ft = int(calculate_energy_height_difference(
                actual_height_ft=start_altitude_ft,
                actual_speed_kts=start_speed_gs_kts,
                perfect_height_ft=task_start_height_ft,
                perfect_speed_kts=IDEAL_START_SPEED_KTS
            ))
            print("height_loss_due_to_start_ft",height_loss_due_to_start_energy_ft)
            
            #Finish
            finish_efficiency_score = calculate_finish_efficiency_score(finish_altitude_ft, finish_speed_gs_kts, task_finish_height_ft)
            print("finish_efficiency_score",finish_efficiency_score)
            height_loss_due_to_finish_energy_ft = int(calculate_energy_height_difference(
                actual_height_ft=finish_altitude_ft,
                actual_speed_kts=finish_speed_gs_kts,
                perfect_height_ft=task_finish_height_ft,
                perfect_speed_kts=IDEAL_FINISH_SPEED_KTS,
                is_finish=True
            ))
            print("height_loss_due_to_finish_energy_ft",height_loss_due_to_finish_energy_ft)
        else:
            print("No start height provided. Skipping start height related processing.")
        

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
        Rule3_total_glide_distance_km = Rule3_total_glide_distance_nmi * 1.852
        Rule3_total_glide_distance_km = round(Rule3_total_glide_distance_km,2)
        #Rule 4 - Don't put yourself in jail (stay high)
        Rule4_avg_altitude_ft = average_altitude_ft

        Rule2_ideal_MC_given_avg_ias_kts, Rule1_ideal_ias_given_avg_climb_kts, Rule1_glide_avg_ias_MC_GR = ideal_MC_given_avg_ias_kts(igc_data, Rule1_glide_avg_ias_kts,Rule2_avg_climb_rate_kts)

        
        
        Rule1_glide_ratio_better_actual_MC = round(Rule1_glide_ratio - Rule1_glide_avg_ias_MC_GR,1)
        
        #print('Rule1_glide_ratio_better_actual_MC',Rule1_glide_ratio_better_actual_MC)
        
        #Rule1_glide_better_actual_MC


        #write to summary csv


        # Define column names and data row
        columns = ["Name", "Glider Type",
                   "Rule1_glide_avg_gs_kts", "Rule1_glide_avg_ias_kts", "Rule1_glide_ratio", "Rule1_glide_ratio_better_actual_MC","Rule1_ideal_MC_ias_given_avg_climb_kts", "Rule1_glide_avg_dist_nmi",
                   "Rule1_avg_glide_netto_kt", "Rule1_%_of_glide_netto_positive", "Rule1_%_of_glide_sinkrate_positive",
                   "Rule2_avg_climb_rate_kts", "Rule2_actual_MC_given_avg_ias_kts", "Num_useful_thermals", "Num_discarded_thermals_<75s_or_<500ft","Percent_discarded_thermals",
                   "Rule3_total_glide_distance_km", "Rule3_total_glide_more_percent",
                   "Rule4_avg_altitude_ft",
                   "start_speed_gs_kts", "start_altitude_ft", "start_efficiency_score", "height_loss_due_to_start_energy_ft",
                   "finish_speed_gs_kts", "finish_altitude_ft", "finish_efficiency_score", "height_loss_due_to_finish_energy_ft",
                   "task_speed_kmh", "task_distance_km","task_time_hmmss", "total_glide_time_mmss", "total_thermal_time_mmss"
                   ]

        row_data = [pilot_id, glider_type,
                   Rule1_glide_avg_gs_kts, Rule1_glide_avg_ias_kts, Rule1_glide_ratio, Rule1_glide_ratio_better_actual_MC, Rule1_ideal_ias_given_avg_climb_kts, Rule1_glide_avg_dist_nmi,
                   avg_netto_kt, percent_glide_netto_positive, percent_glide_sinkrate_positive,
                   Rule2_avg_climb_rate_kts, Rule2_ideal_MC_given_avg_ias_kts, useful_thermals, discarded_thermals, thermal_discard_percent,
                   Rule3_total_glide_distance_km, Rule3_total_glide_more_percent,
                   Rule4_avg_altitude_ft,
                   start_speed_gs_kts, start_altitude_ft, start_efficiency_score, height_loss_due_to_start_energy_ft,
                   finish_speed_gs_kts, finish_altitude_ft, finish_efficiency_score, height_loss_due_to_finish_energy_ft,
                   task_speed_kmh, task_distance_km, task_time_hmmss, total_glide_time_mmss, total_thermal_time_mmss
                   ]

        #write to summary csv
        # Specify the CSV file path
        csv_file_path = "summary.csv"


        # Check if the file already exists
        file_exists = os.path.exists(csv_file_path)

        with open(csv_file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)

            # If the file doesn't exist, write the column headers
            if not file_exists:
                writer.writerow(columns)

            # Write the data row
            writer.writerow(row_data)
            

        # WRITE COMBINED INFO
        # Create the csv file name with the pilot_id or base_name
        csv_file_name = os.path.join('temp', 'sequenceData_' + re.sub(r'[<>:"/\\|?*]', '_', str(pilot_id if pilot_id is not None else base_name)).strip() + '.csv')

        # new section after freq_gs_kts calculation
        freq_gs_kts_csv_file = os.path.join('temp', 'freq_gs_kts_' + re.sub(r'[<>:"/\\|?*]', '_', str(pilot_id if pilot_id is not None else base_name)).strip() + '.csv')

        # Write freq_gs_kts to the new CSV file
        with open(freq_gs_kts_csv_file, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write the header
            csv_writer.writerow(['Frequency', 'Groundspeed_kts'])
            # Write the data rows
            for frequency, groundspeed_kts in freq_gs_kts:
                csv_writer.writerow([frequency, groundspeed_kts])

        print(f'freq_gs_kts has been written to {freq_gs_kts_csv_file}.')
        




        # Open the CSV file in write mode
        with open(csv_file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            #header row
            csv_writer.writerow(['Sequence', 'ld_ratio', 'glide_speed_gs_kts', 'glide_distance_nmi', 'average_rate_of_climb_kts', 'thermal_height_gained_ft', 'duration_mmss', 'starting_utc'])

            # Write the data rows
            try:
                for glide, data in list(glide_info.items())[:-1]:
                    csv_writer.writerow([glide, data['ld_ratio'], data['glide_speed_kts'], data['total_distance_nmi'], '', '', data['glide_time_mmss'], data['starting_utc']])
            except:
                pass
            
            try:
                for thermal, data in list(thermal_info.items())[:-1]:
                    csv_writer.writerow([thermal,'','','',data['average_rate_of_climb_kts'], data['thermal_height_gained_ft'], data['thermal_time_mmss'], data['starting_utc']])
            except:
                pass
        
        print(f'The data has been written to {csv_file_name}.')

        order_csv_by_starting_utc(csv_file_name)

        return [pilot_id, glider_type,
                Rule1_glide_avg_gs_kts, Rule1_glide_avg_ias_kts, Rule1_glide_ratio, Rule1_glide_ratio_better_actual_MC, Rule1_ideal_ias_given_avg_climb_kts,
                Rule1_glide_avg_dist_nmi,Rule2_avg_climb_rate_kts, Rule2_ideal_MC_given_avg_ias_kts, Rule3_total_glide_distance_nmi,
                Rule3_total_glide_more_percent, Rule4_avg_altitude_ft, start_speed_gs_kts, start_altitude_ft,
                total_energy_start_MJ, max_start_height_ft, finish_speed_gs_kts, finish_altitude_ft, total_energy_finish_MJ,
                task_speed_kmh, task_time_hmmss, task_distance_km, total_glide_time_mmss, total_thermal_time_mmss]

    else:
        print(pilot_id,'did not finish the task so this calculation will not run')
        
    return
        
