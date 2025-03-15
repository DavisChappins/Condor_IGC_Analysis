# plotGlideSpeeds.py
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import glob

def interleave_list(lst):
    """
    Reorders a list by alternately taking from the start and end.
    E.g., [A, B, C, D, E] -> [A, E, B, D, C]
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

def plot_freq_vs_groundspeed():
    # Find all CSV files that match the pattern 'freq_gs_kts*.csv'
    csv_files = glob.glob('freq_gs_kts*.csv')

    # Read summary data to determine the order of datasets
    try:
        summary_df = pd.read_csv('summary.csv')
        summary_df['Name'] = summary_df['Name'].str.split().str[0]
        ordered_dataset_names = summary_df['Name'].tolist()
        print("Ordered dataset names from summary.csv:", ordered_dataset_names)
    except Exception as e:
        print("Error reading summary.csv or extracting dataset names:", e)
        ordered_dataset_names = []

    # Predefined list of colors and shapes
    base_colors = [
        'black', 'blue', 'brown', 'crimson', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 
        'darkgreen', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkred', 'darksalmon', 
        'darkseagreen', 'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'firebrick', 'gray', 
        'green', 'indigo', 'maroon', 'midnightblue', 'navy', 'olive', 'orangered', 'purple', 'rebeccapurple', 
        'rosybrown', 'saddlebrown', 'slategray', 'slategrey', 'teal'
    ]
    # Interleave the colors to mix up similar hues
    colors = interleave_list(base_colors)
    shapes = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'hexagon', 'star', 'hexagram']

    # Create empty dictionary to track color and shape usage (optional)
    color_dict = {}

    # Create an empty list to store data traces
    traces = []

    # Iterate through each dataset name in the ordered list
    for index, dataset_name in enumerate(ordered_dataset_names):
        # Find the corresponding CSV file safely
        matching_files = [file for file in csv_files if str(dataset_name) in file]
        
        # Check if matching files were found before accessing
        if not matching_files:
            continue
        
        csv_file = matching_files[0]  # Access the first matching file safely

        # Read the CSV file into a DataFrame
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Error reading CSV file {csv_file}: {e}")
            continue

        # Calculate total frequency for normalization
        total_frequency = df['Frequency'].sum()

        # Calculate normalized frequency as a percentage
        df['Frequency_Percent'] = (df['Frequency'] / total_frequency) * 100

        # Expand the data according to frequency
        expanded_data = []
        for _, row in df.iterrows():
            try:
                # Convert frequency to an integer before using it for expansion
                expanded_data.extend([row['Groundspeed_kts']] * int(row['Frequency']))
            except ValueError as e:
                print(f"Error expanding data for {dataset_name} at groundspeed {row['Groundspeed_kts']}: {e}")
                continue

        # Compute the correct average groundspeed
        if expanded_data:
            avg_groundspeed = sum(expanded_data) / len(expanded_data)
        else:
            avg_groundspeed = 0  # Handle case where no data is available

        # Deterministically assign a color and shape based on the index
        color = colors[index % len(colors)]
        shape = shapes[index % len(shapes)]
        color_dict[dataset_name] = (color, shape)

        # Create a scatter plot trace with normalized frequency
        trace = go.Scatter(
            x=df['Groundspeed_kts'],
            y=df['Frequency_Percent'],  # Use normalized frequency
            mode='lines+markers',  # Add lines between points
            name=dataset_name,  # Use the dataset name for consistency
            marker=dict(
                size=10,  # Set marker size
                color=color,  # Set marker color
                symbol=shape  # Set marker shape
            ),
            hoverinfo='text',
            text=[f"Pilot: {dataset_name}<br>Groundspeed: {gs}<br>Frequency: {freq:.2f}%" 
                  for gs, freq in zip(df['Groundspeed_kts'], df['Frequency_Percent'])]
        )

        # Add the scatter trace to the list of traces
        traces.append(trace)

        # Find the maximum frequency percentage for the dataset to cap the average line height
        max_freq_percent = df['Frequency_Percent'].max()

        # Add the average line trace matching the dataset's color
        avg_line_trace = go.Scatter(
            x=[avg_groundspeed, avg_groundspeed],
            y=[0, max_freq_percent],  # Max at the highest frequency percentage
            mode='lines',
            name=f'Avg - {dataset_name}',
            line=dict(color=color, width=2, dash='dash'),  # Dotted line style matching color
            hoverinfo='none'  # No hover info for the average line
        )

        # Add the average line trace to the list of traces
        traces.append(avg_line_trace)

    # Define the layout of the plot with extended x-axis and grid lines every 5 knots
    layout = go.Layout(
        title='Groundspeed vs % Time Spent',
        xaxis=dict(
            title='Groundspeed (kts)',
            range=[40, 170],
            dtick=5,  # Set grid and tick interval to 5 knots
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title='% Time Spent',
            tickformat='.1f'
        ),
        showlegend=True
    )

    # Create the figure
    fig = go.Figure(data=traces, layout=layout)

    # Generate the interactive HTML plot
    pyo.plot(fig, filename='groundspeed_vs_percent_time_spent.html', auto_open=False)

    print("Plot generated successfully: groundspeed_vs_percent_time_spent.html")

# Uncomment to run the plotting function directly
# plot_freq_vs_groundspeed()
