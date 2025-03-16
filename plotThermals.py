import warnings
import plotly.graph_objs as go
import plotly.offline as pyo
import pandas as pd
import glob
import os

def convert_duration_to_seconds(duration):
    """Convert duration from mm:ss format to total seconds."""
    try:
        minutes, seconds = map(int, duration.split(':'))
        return minutes * 60 + seconds
    except ValueError:
        print(f"Error converting duration '{duration}' to seconds.")
        return None

def interleave_list(lst):
    """
    Return a new list that interleaves items from the start and end of the input list.
    E.g. [A, B, C, D, E] -> [A, E, B, D, C]
    """
    result = []
    left = 0
    right = len(lst) - 1
    while left <= right:
        if left == right:
            result.append(lst[left])
        else:
            result.append(lst[left])
            result.append(lst[right])
        left += 1
        right -= 1
    return result

def plotThermalsInteractive():
    # Suppress warnings
    warnings.filterwarnings("ignore", message="Could not infer format, so each element will be parsed individually")

    # Find all CSV files starting with 'sequenceData_'
    csv_files = glob.glob(os.path.join('temp', 'sequenceData_*.csv'))

    # Read summary data
    summary_df = pd.read_csv('summary.csv')

    # Extract dataset names up until the space character
    summary_df['Name'] = summary_df['Name'].str.split().str[0]

    # Sort dataset names based on their order in Column A of 'summary.csv'
    ordered_dataset_names = summary_df['Name'].tolist()

    # Print the entire ordered dataset to inspect any inconsistencies
    print("Full ordered dataset names list:")
    print(ordered_dataset_names)

    # Pre-defined list of colors
    base_colors = [
        'black', 'blue', 'brown', 'crimson', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 
        'darkgreen', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkred', 'darksalmon', 
        'darkseagreen', 'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'firebrick', 'gray', 
        'green', 'indigo', 'maroon', 'midnightblue', 'navy', 'olive', 'orangered', 'purple', 'rebeccapurple', 
        'rosybrown', 'saddlebrown', 'slategray', 'slategrey', 'teal'
    ]
    # Interleave the colors to mix them up
    colors = interleave_list(base_colors)
    
    # Predefined list of shapes (will cycle if pilots > len(shapes))
    shapes = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'hexagon', 'star', 'hexagram']

    # Create empty dictionaries to track color and shape usage (optional)
    color_dict = {}
    shape_dict = {}

    # Create an empty list to store data traces
    traces = []

    # Initialize a list to store all the maximum data points
    max_data_points = []

    # Iterate through each dataset name in the ordered list
    for index, dataset_name in enumerate(ordered_dataset_names):
        print(f"Index: {index}, Type of dataset_name: {type(dataset_name)}, Value: {dataset_name}")

        if pd.isna(dataset_name):
            print(f"Skipping NaN dataset_name at index {index}. Full row: {ordered_dataset_names[index]}")
            continue

        matching_files = [file for file in csv_files if str(dataset_name) in file]

        if not matching_files:
            print(f"No matching file found for dataset_name '{dataset_name}' at index {index}")
            continue

        csv_file = matching_files[0]
        print(f"Processing file: {csv_file} for dataset_name: {dataset_name}")

        df = pd.read_csv(csv_file)

        # Clean and validate the 'starting_utc' column before conversion
        df['starting_utc'] = df['starting_utc'].apply(lambda x: x if pd.to_datetime(x, errors='coerce') is not pd.NaT else None)

        # Remove or correct problematic entries in 'starting_utc'
        if df['starting_utc'].isnull().any():
            invalid_entries = df[df['starting_utc'].isnull()]
            print(f"Found invalid 'starting_utc' entries in {csv_file}:")
            print(invalid_entries[['Sequence', 'starting_utc']])
            # Optionally, drop rows with invalid 'starting_utc'
            df = df.dropna(subset=['starting_utc'])

        # Convert 'starting_utc' column to datetime objects
        df['starting_utc'] = pd.to_datetime(df['starting_utc'], errors='coerce')

        # Convert 'duration_mmss' to seconds
        df['duration_s'] = df['duration_mmss'].apply(convert_duration_to_seconds)

        # Filter rows with data in necessary columns and filter for Thermal sequences
        thermals_df = df[df['Sequence'].str.contains('Thermal')].dropna(subset=['average_rate_of_climb_kts', 'starting_utc', 'duration_s'])

        # Calculate total thermal duration
        total_duration = thermals_df['duration_s'].sum()

        # Sort by thermal strength
        thermals_df = thermals_df.sort_values(by='average_rate_of_climb_kts', ascending=False)

        # Calculate cumulative percentage time for x-axis
        thermals_df['cumulative_duration_s'] = thermals_df['duration_s'].cumsum()
        thermals_df['percentage_time'] = thermals_df['cumulative_duration_s'] / total_duration * 100

        # Deterministically assign a color and shape based on the index
        color = colors[index % len(colors)]
        shape = shapes[index % len(shapes)]
        color_dict[dataset_name] = (color, shape)

        # Add a column with the original duration_mmss for tooltip display
        thermals_df['tooltip_info'] = thermals_df.apply(
            lambda row: f"Pilot: {dataset_name}<br>Strength: {row['average_rate_of_climb_kts']} kts<br>Duration: {row['duration_mmss']}",
            axis=1
        )

        # Create scatter trace for the dataset (points)
        trace = go.Scatter(
            x=thermals_df['percentage_time'],
            y=thermals_df['average_rate_of_climb_kts'],
            mode='markers',
            name=dataset_name,
            marker=dict(
                size=15,
                color=color,
                symbol=shape
            ),
            legendgroup=dataset_name,  # Group markers with this pilot
            hoverinfo='text',
            text=thermals_df['tooltip_info']
        )
        traces.append(trace)

        # Create a line trace connecting the points for this pilot
        line_trace = go.Scatter(
            x=thermals_df['percentage_time'],
            y=thermals_df['average_rate_of_climb_kts'],
            mode='lines',
            name=f"{dataset_name} segments",
            legendgroup=dataset_name,  # Group segments with the same pilot
            line=dict(color=color, width=2),
            hoverinfo='skip',
            showlegend=False
        )
        traces.append(line_trace)

        # Add a horizontal line from the y-axis to the first point
        first_x = thermals_df['percentage_time'].iloc[0]
        first_y = thermals_df['average_rate_of_climb_kts'].iloc[0]
        horizontal_trace = go.Scatter(
            x=[0, first_x],
            y=[first_y, first_y],
            mode='lines',
            name=f"{dataset_name} y-axis connector",
            legendgroup=dataset_name,  # Ensures it toggles with the pilot
            line=dict(color=color, width=2),
            hoverinfo='skip',
            showlegend=False
        )
        traces.append(horizontal_trace)

        # Find average climb rate for the dataset from summary data
        avg_climb_rate = summary_df.loc[summary_df['Name'] == dataset_name, 'Rule2_avg_climb_rate_kts'].values[0]

        # Add average line trace for the dataset
        avg_line_trace = go.Scatter(
            x=[0, 100],
            y=[avg_climb_rate, avg_climb_rate],
            mode='lines',
            name='avg',
            line=dict(color=color, width=2, dash='dash'),
            visible='legendonly'
        )
        traces.append(avg_line_trace)

        # Append maximum data point to the list of maximum data points
        max_data_points.append(thermals_df['average_rate_of_climb_kts'].max())

    max_y_range = max(max_data_points) + 0.5

    layout = go.Layout(
        title='Average Rate of Climb vs Percentage of Total Thermal Time',
        xaxis=dict(title='Percentage of Total Thermal Time', range=[0, 100]),
        yaxis=dict(title='Average Rate of Climb (kts)', range=[0, max_y_range], dtick=1),
        showlegend=True,
        updatemenus=[{
            'buttons': [{
                'label': 'All',
                'method': 'update',
                'args': [{'visible': [True] * len(traces)},
                         {'xaxis': {'title': 'Percentage of Total Thermal Time', 'range': [0, 100]},
                          'yaxis': {'title': 'Average Rate of Climb (kts)', 'range': [0, max_y_range], 'dtick': 1}}]
            }]
        }]
    )

    fig = go.Figure(data=traces, layout=layout)
    pyo.plot(fig, filename='summaryClimb_interactive.html', auto_open=False)
    
    print("Thermals plotted successfully")
