# plotGlideSpeeds.py
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import glob
import random

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

        # Expand the data according to frequency
        expanded_data = []
        for _, row in df.iterrows():
            expanded_data.extend([row['Groundspeed_kts']] * row['Frequency'])

        # Compute the correct average groundspeed
        if expanded_data:
            avg_groundspeed = sum(expanded_data) / len(expanded_data)
        else:
            avg_groundspeed = 0  # Handle case where no data is available

        #print(f"Corrected Average groundspeed for {dataset_name}: {avg_groundspeed}")

        # Choose a unique random color and shape
        while True:
            color = random.choice(colors)
            shape = random.choice(shapes)
            if (color, shape) not in color_dict.values():
                break

        # Store color and shape for the current dataset
        color_dict[csv_file] = (color, shape)

        # Create a scatter plot trace
        trace = go.Scatter(
            x=df['Groundspeed_kts'],
            y=df['Frequency'],
            mode='markers',
            name=dataset_name,  # Use the dataset name for consistency
            marker=dict(
                size=10,  # Set marker size
                color=color,  # Set marker color
                symbol=shape  # Set marker shape
            ),
            hoverinfo='text',
            text=[f"Pilot: {dataset_name}<br>Groundspeed: {gs}<br>Frequency: {freq}" for gs, freq in zip(df['Groundspeed_kts'], df['Frequency'])]
        )

        # Add the scatter trace to the list of traces
        traces.append(trace)

        # Add the average line trace matching the dataset's color
        avg_line_trace = go.Scatter(
            x=[avg_groundspeed, avg_groundspeed],
            y=[df['Frequency'].min(), df['Frequency'].max()],
            mode='lines',
            name=f'Avg - {dataset_name}',
            line=dict(color=color, width=2, dash='dash'),  # Dotted line style matching color
            hoverinfo='none'  # No hover info for the average line
        )

        # Add the average line trace to the list of traces
        traces.append(avg_line_trace)

    # Define the layout of the plot with x-axis bounds set and grid lines every 5 knots
    layout = go.Layout(
        title='Groundspeed vs Frequency',
        xaxis=dict(
            title='Groundspeed (kts)',
            range=[40, 150],  # Set the x-axis range
            dtick=5,  # Set grid and tick interval to 5 knots
            showgrid=True,  # Enable grid lines
            gridcolor='lightgray'  # Set grid line color
        ),
        yaxis=dict(
            title='Frequency'
        ),
        showlegend=True
    )

    # Create the figure
    fig = go.Figure(data=traces, layout=layout)

    # Generate the interactive HTML plot
    pyo.plot(fig, filename='groundspeed_vs_frequency.html')

    print("Plot generated successfully: groundspeed_vs_frequency.html")

# Uncomment to run the plotting function directly
#plot_freq_vs_groundspeed()
