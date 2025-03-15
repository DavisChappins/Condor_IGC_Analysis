import plotly.graph_objs as go

# Sample data
x = [1, 2, 3, 4, 5]
y = [1, 4, 9, 16, 25]

# Create trace
trace = go.Scatter(
    x=x,
    y=y,
    mode='markers+lines',
    name='Data',
    marker=dict(
        size=10,
        color='blue',
        symbol='circle',
        opacity=0.8,
        # Specify the position of data labels
        textposition='right'
    ),
    line=dict(
        color='green',
        width=2,
        dash='dot',
        opacity=0.5
    ),
    # Set data labels
    text=['Point {}'.format(i+1) for i in range(len(x))]
)

# Create layout
layout = go.Layout(
    title='Chart with Data Labels',
    xaxis=dict(
        title='X-axis',
    ),
    yaxis=dict(
        title='Y-axis',
    )
)

# Create figure
fig = go.Figure(data=[trace], layout=layout)

# Plot
pyo.plot(fig, filename='chart_with_data_labels.html')
