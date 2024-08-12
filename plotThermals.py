import warnings
import plotly.graph_objs as go
import plotly.offline as pyo
import pandas as pd
import glob
import random

def convert_duration_to_seconds(duration):
    """Convert duration from mm:ss format to total seconds."""
    minutes, seconds = map(int, duration.split(':'))
    return minutes * 60 + seconds

def plotThermalsInteractive():
    # Suppress warnings
    warnings.filterwarnings("ignore", message="Could not infer format, so each element will be parsed individually")

    # Find all CSV files starting with 'sequenceData_'
    csv_files = glob.glob('sequenceData_*.csv')

    # Read summary data
    summary_df = pd.read_csv('summary.csv')

    # Extract dataset names up until the space character
    summary_df['Name'] = summary_df['Name'].str.split().str[0]

    # Sort dataset names based on their order in Column A of 'summary.csv'
    ordered_dataset_names = summary_df['Name'].tolist()

    # Predefined list of colors and shapes
    colors = [
        'black', 'blue', 'brown', 'crimson', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 
        'darkgreen', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkred', 'darksalmon', 
        'darkseagreen', 'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'firebrick', 'gray', 
        'green', 'indigo', 'maroon', 'midnightblue', 'navy', 'olive', 'orangered', 'purple', 'rebeccapurple', 
        'rosybrown', 'saddlebrown', 'slategray', 'slategrey', 'teal'
    ]

    shapes = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'hexagon', 'star', 'hexagram']

    # Create empty dictionaries to track color and shape usage
    color_dict = {}
    shape_dict = {}

    # Create an empty list to store data traces
    traces = []

    # Initialize a list to store all the maximum data points
    max_data_points = []

    # Iterate through each dataset name in the ordered list
    for dataset_name in ordered_dataset_names:
        # Find the corresponding CSV file
        csv_file = [file for file in csv_files if dataset_name in file][0]
        
        # Read CSV file into pandas DataFrame
        df = pd.read_csv(csv_file)
        
        # Convert 'starting_utc' column to datetime objects
        df['starting_utc'] = pd.to_datetime(df['starting_utc'])
        
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
        
        # Choose a unique random color and shape
        while True:
            color = random.choice(colors)
            shape = random.choice(shapes)
            if (color, shape) not in color_dict.values():
                break
        
        # Store color and shape for dataset
        color_dict[dataset_name] = (color, shape)
        
        # Add a column with the original duration_mmss for tooltip display
        thermals_df['tooltip_info'] = thermals_df.apply(
            lambda row: f"Pilot: {dataset_name}<br>Strength: {row['average_rate_of_climb_kts']} kts<br>Duration: {row['duration_mmss']}",
            axis=1
        )
        
        # Create scatter trace for the dataset
        trace = go.Scatter(
            x=thermals_df['percentage_time'],
            y=thermals_df['average_rate_of_climb_kts'],
            mode='markers',
            name=dataset_name,
            marker=dict(
                size=20,  # Set the marker size
                color=color,  # Set the marker color
                symbol=shape  # Set the marker shape
            ),
            hoverinfo='text',
            text=thermals_df['tooltip_info']  # Display tooltip information on hover
        )
        
        # Append trace to the list of traces
        traces.append(trace)

        # Find average climb rate for the dataset from summary data
        avg_climb_rate = summary_df.loc[summary_df['Name'] == dataset_name, 'Rule2_avg_climb_rate_kts'].values[0]
        
        # Add average line trace for the dataset
        avg_line_trace = go.Scatter(
            x=[0, 100],
            y=[avg_climb_rate, avg_climb_rate],
            mode='lines',
            name='avg',
            line=dict(color=color, width=2, dash='dash'),
            visible='legendonly'  # Hide the average line by default
        )
        
        # Append average line trace to the list of traces
        traces.append(avg_line_trace)
        
        # Append maximum data point to the list of maximum data points
        max_data_points.append(thermals_df['average_rate_of_climb_kts'].max())

    # Calculate the maximum y-axis range
    max_y_range = max(max_data_points) + 0.5

    # Create layout with fixed x-axis and y-axis range and ticks at every integer
    layout = go.Layout(
        title='Average Rate of Climb vs Percentage of Total Thermal Time',
        xaxis=dict(title='Percentage of Total Thermal Time', range=[0, 100]),  # Fix x-axis range from 0 to 100
        yaxis=dict(title='Average Rate of Climb (kts)', range=[0, max_y_range], dtick=1),  # Fix y-axis range and set tick interval to 1
        showlegend=True,
        updatemenus=[
            dict(
                buttons=[dict(label='All',
                               method='update',
                               args=[{'visible': [True] * (len(traces) // 2)},  # Toggle visibility of all traces (excluding average lines)
                                     {'xaxis': {'title': 'Percentage of Total Thermal Time', 'range': [0, 100]},  # Ensure x-axis is always from 0 to 100
                                      'yaxis': {'title': 'Average Rate of Climb (kts)', 'range': [0, max_y_range], 'dtick': 1}}])]
            )
        ]
    )

    # Create figure
    fig = go.Figure(data=traces, layout=layout)

    # Plot
    pyo.plot(fig, filename='summaryClimb_interactive.html')
    
    print("Thermals plotted successfully")

plotThermalsInteractive()
