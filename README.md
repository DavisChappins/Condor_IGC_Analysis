# Condor IGC Analysis

Copy .FPL file into the same folder as generateSummary.py

For AAT tasks, use CoFliCo to convert FTR tracks to IGC files (as Condor Club .IGC files are missing AAT distance flown). Or use aatConvert.py and manually add in AAT data from Condor.Club.

Run generateSummary.py to generate summary.csv for all .igc files inside the folder /igcFiles

All of the data is from task start to task finish


  The 4 rules are:  
  1) Glide better
  2) Climb better
  3) Fly a shorter distance
  4) Don't do anything where you have to give up rules 1 2 or 3 to survive (dont put yourself in jail)

These are the only ways to fly faster than another glider. The columns analyze these rules to see where you have gained or lost vs others.

# Summary columns

**Rule1_glide_avg_gs_kts** groundspeed during glide segments, average  
**Rule1_glide_avg_ias_kts** indicated air speed during glide, average  
**Rule1_glide_ratio** L/D for all glide segments, average  
**Rule1_glide_ratio_better_actual_MC** L/D better (or worse) than the polar value at that IAS. Higher is better.  
**Rule1_ideal_MC_ias_given_avg_climb_kts** Based on your avg climb, the IAS that you should have flown to fly at your ideal MC IAS.  
**Rule1_glide_avg_dist_nmi** distance between climbs, average  
**Rule1_avg_glide_netto_kt** netto value for all glide segments, average. Higher is better.  
**Rule1_%_of_glide_netto_positive** % of the gliding segments in positive netto  
**Rule1_%_of_glide_sinkrate_positive** % of the gliding segmenets in postitive sinkrate  
**Rule2_avg_climb_rate_kts** climb rate for all thermals, average  
**Rule2_actual_MC_given_avg_ias_kts** actual MC IAS flown for all glide segments, average  
**Num_useful_thermals** number of thermals  
**Num_discarded_thermals_<75s_or_<500ft** number of discarded thermals less than 75 seconds in duration or less than 500ft gained  
**Percent_discarded_thermals** % of thermals discarded  
**Rule3_total_glide_distance_km** total gliding distance  
**Rule3_total_glide_more_percent** % of gliding distance more than the task, in %  
**Rule4_avg_altitude_ft** average altitude for the flight  
**start_speed_gs_kts** start speed in kts, ground speed  
**start_altitude_ft** start altitude in feet  
**finish_speed_gs_kts** finish speed in kts, ground speed  
**finish_altitude_ft** finish altitude in feet  
**task_speed_kmh** task speed in kmh  
**task_distance_km** task distance in kmh  
**task_time_hmmss** task time in h mm ss  
**total_glide_time_mmss** gliding time in mm ss  
**total_thermal_time_mmss** thermal time in mm ss  
**rank** place in results  
**task_time_behind_rank1_mmss** task time behind rank 1 in mm ss  
**Rule1_time_behind_rank1_mmss** a summation of the next two columns in mm ss  
**Rule1_time_behind_rank1_from_gs_mmss** time lost to glide speed difference in mm ss  
**Rule1_time_behind_rank1_from_ld_mmss** time lost to L/D difference (in height lost) and time to climb that back in mm ss  
**Rule2_time_behind_best_climb_mmss** time lost due to climb rate difference from the best climb rate pilot of the day in mm ss  
**Rule3_absolute_time_lost_mmss** time lost due to flying a longer distance than the task distance in mm ss  
**Rule3_time_behind_straightest_mmss** time lost due to flying a longer distance behind the shortest flight in mm ss  
