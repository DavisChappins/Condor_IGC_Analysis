# Condor IGC Analysis

Run generateSummary.py to generate summary.csv for all .igc files inside the folder /igcFiles  
Run analyzeSingleIGC.py to analyze a single .igc file inside / (same location where analyzeSingleIGC.py is located)  
MC and energy estimations only valid for 18 meter class at the moment  
All of the data is from task start to task finish

# Summary columns

**Rule1_glide_avg_gs_kts:** groundspeed during glide, average  
**Rule1_glide_avg_ias_kts:** estimated indicated air speed during glide, average  
**Rule1_glide_ratio:** L/D for glides, total  
**Rule1_ideal_MC_ias_given_avg_climb_kts:** given the actual climb rate, what MC cruise speed does that correspond to  
**Rule1_glide_avg_dist_nmi:** distance between glides, average  
**Rule2_avg_climb_rate_kts:** thermal climb rate, average  
**Rule2_ideal_MC_given_avg_ias_kts:** given the actual cruise speed, what MC climb rate does that correspond with 
**Rule3_total_glide_distance_nmi:** total distance covered during glides  
**Rule3_total_glide_more_percent:** % longer distance flown than exact task distance  
**Rule4_avg_altitude_ft:** average altitude during the task  
**start_speed_gs_kts:** start speed groundspeed  
**start_altitude_ft:** start altitude  
**total_energy_start_MJ:** kinetic + potential energy at start  
**finish_speed_gs_kts:** finish speed groundspeed  
**finish_altitude_ft:** finish altitude  
**total_energy_finish_MJ:** kinetic + potential energy at finish  
**task_speed_kmh:** task speed as recorded by condor.club  
**rank:** ranking for this summary comparison  
