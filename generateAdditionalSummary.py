import csv

def generate_slim_summary():
    # Dictionary mapping "old_name" -> "new_name"
    columns_map = {
        "rank": "Rank",
        "Name": "Name",
        "Rule1_glide_avg_ias_kts": "Ave Glide IAS (kts)",
        "Rule1_glide_ratio": "Glide L/D",
        "Rule1_glide_avg_dist_nmi": "Avg Glide Dist (nmi)",
        "Rule1_avg_glide_netto_kt": "Avg Netto (kts)",
        "Rule2_avg_climb_rate_kts": "Avg Climb (kts)",
        "Rule3_total_glide_more_percent": "Deviation Flown (%)",
        "Rule4_avg_altitude_ft": "Avg Alt (ft)",
        "task_speed_kmh": "Task Speed (km/h)",
        "task_time_hmmss": "Task Time",
        "task_time_behind_rank1_mmss": "Gap",
        "Rule1_time_behind_rank1_mmss": "Glide Gap",
        "Rule1_time_behind_rank1_from_gs_mmss": "'-- from Glide Speed",
        "Rule1_time_behind_rank1_from_ld_mmss": "'-- from Glide L/D",
        "Rule2_time_behind_rank1": "Climb Gap",
        "Rule3_time_behind_rank1": "Deviation Gap"
    }
    
    original_csv = "summary.csv"
    slim_csv = "slim_summary.csv"
    
    # Read the entire summary.csv
    with open(original_csv, "r", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    # Build a new list of rows containing only the columns in columns_map
    slim_rows = []
    for row in rows:
        new_row = {}
        # For each original->new name mapping:
        for old_col, new_col in columns_map.items():
            # If old_col doesn't exist in row, default to empty string
            new_row[new_col] = row.get(old_col, "")
        slim_rows.append(new_row)

    # The new CSV's header is the *values* of columns_map (the "new" names)
    new_header = list(columns_map.values())

    # Write the slim rows to slim_summary.csv
    with open(slim_csv, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_header)
        writer.writeheader()
        writer.writerows(slim_rows)

    print(f"Created '{slim_csv}' with only the requested columns.")
    
    

def generate_slim_rules_summary():
    # List of columns to keep in the slim_rules_summary CSV
    columns_to_keep = [
        "Rank",
        "Name",
        "Ave Glide IAS (kts)",
        "Glide L/D",
        "Avg Glide Dist (nmi)",
        "Avg Netto (kts)",
        "Avg Climb (kts)",
        "Deviation Flown (%)",
        "Avg Alt (ft)"
    ]
    
    input_csv = "slim_summary.csv"
    output_csv = "slim_summary_rules.csv"
    
    # Read the slim_summary.csv file
    with open(input_csv, "r", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = []
        for row in reader:
            # Create a new row with only the columns we want
            new_row = {col: row.get(col, "") for col in columns_to_keep}
            rows.append(new_row)
    
    # Write the new rows to slim_rules_summary.csv
    with open(output_csv, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=columns_to_keep)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Created '{output_csv}' with only the columns: {', '.join(columns_to_keep)}")
    
    
def generate_slim_timing_summary():
    columns_to_keep = [
        "Rank",
        "Name",
        "Task Speed (km/h)",
        "Task Time",
        "Gap"
    ]
    
    input_csv = "slim_summary.csv"
    output_csv = "slim_summary_timing.csv"
    
    with open(input_csv, "r", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = []
        for row in reader:
            # Create a new row with only the columns we want
            new_row = {col: row.get(col, "") for col in columns_to_keep}
            rows.append(new_row)
    
    with open(output_csv, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=columns_to_keep)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Created '{output_csv}' with only the columns: {', '.join(columns_to_keep)}")
    

def generate_slim_gap_analysis_summary():
    columns_to_keep = [
        "Rank",
        "Name",
        "Gap",
        "Glide Gap",        
        "'-- from Glide Speed",        
        "'-- from Glide L/D",
        "Climb Gap",     
        "Deviation Gap",        
    ]
    
    input_csv = "slim_summary.csv"
    output_csv = "slim_summary_gap_analysis.csv"
    
    with open(input_csv, "r", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = []
        for row in reader:
            # Create a new row with only the columns we want
            new_row = {col: row.get(col, "") for col in columns_to_keep}
            rows.append(new_row)
    
    with open(output_csv, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=columns_to_keep)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Created '{output_csv}' with only the columns: {', '.join(columns_to_keep)}")
