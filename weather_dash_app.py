
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

df = pd.read_csv(r"C:\Users\Dell\Desktop\Weather App - Minoli\weatherHistory.csv")
df['Formatted Date'] = pd.to_datetime(df['Formatted Date'], utc=True)



# Initialize the Dash application
app = dash.Dash(__name__)

# Create the layout with multiple tabs
app.layout = html.Div(className='app-container', children=[
    dcc.Tabs(className='dash-tabs', children=[
        dcc.Tab(label='Line Chart', children=[
            html.H2(className='section-title', children='Line Chart'),
            dcc.DatePickerRange(
                id='line-chart-date-picker',
                display_format='DD/MM/YYYY',
                min_date_allowed=min(df['Formatted Date']),
                max_date_allowed=max(df['Formatted Date']),
                initial_visible_month=max(df['Formatted Date']),
                start_date=min(df['Formatted Date']),
                end_date=max(df['Formatted Date'])
            ),
            dcc.Dropdown(
                id='line-chart-dropdown',
                options=[{'label': col, 'value': col} for col in ['Temperature (C)','Wind Speed (km/h)','Wind Bearing (degrees)','Pressure (millibars)']],
                value=['Temperature (C)', 'Wind Bearing (degrees)'],
                multi=True,
                className='dropdown'
            ),
            dcc.Graph(id='line-chart', className='chart')
        ]),

        dcc.Tab(label='Scatter Plot', children=[
            html.H2(className='section-title', children='Scatter Plot'),
            dcc.RadioItems(
                id='scatter-plot-radio',
                options=[{'label': col, 'value': col} for col in ['Temperature (C)','Humidity','Pressure (millibars)']],
                value='Wind Speed (km/h)',
                className='radio-items'
            ),
            dcc.Graph(id='scatter-plot', className='chart')
        ]),

        dcc.Tab(label='Interactive Charts', children=[
            html.H2(className='section-title', children='Interactive Charts'),
            html.Div(className='interactive-charts-container', children=[
                dcc.Graph(
                    id='chart1',
                    figure=px.scatter(df, x='Temperature (C)', y='Humidity'),
                    className='chart'
                ),
                dcc.Graph(
                    id='chart2',
                    figure=px.line(df, x='Formatted Date', y='Wind Speed (km/h)'),
                    className='chart'
                )
            ])
        ]),

        dcc.Tab(label='Custom Graph', children=[
            html.H2(className='section-title', children='Custom Graph'),
            dcc.Graph(
                id='custom-chart',
                figure={
                    'data': [
                        {'x': df['Summary'], 'y': df['Humidity'], 'type': 'bar', 'name': 'Humidity'},
                    ],
                    'layout': {
                        'title': 'Humidity Vs Weather Summary',
                        'xaxis': {'title': 'Summary'},
                        'yaxis': {'title': 'Humidity'},
                    }
                },
                className='chart'
            ),
            dcc.Graph(
                id='custom-pie-chart',
                figure={
                    'data': [
                        {'labels': df['Summary'], 'values': df['Temperature (C)'], 'type': 'pie', 'name': 'Temperature (C)'},
                    ],
                    'layout': {
                        'title': 'Temperature Against to the Summary',
                    }
                },
                className='chart'
            )
        ])
    ]),

    html.Footer(
        'Created by: Sandali Minoli Hemachandra (Index: cohndds23.2f-022)',
        style={'position': 'fixed', 'bottom': '0', 'left': '0', 'width': '100%', 'background-color': 'white',
               'padding': '5px'}
    )
])


# Callback for line chart
@app.callback(
    Output('line-chart', 'figure'),
    [Input('line-chart-date-picker', 'start_date'),
     Input('line-chart-date-picker', 'end_date'),
     Input('line-chart-dropdown', 'value')])
def update_line_chart(start_date, end_date, selected_vars):
    filtered_df = df[(df['Formatted Date'] >= start_date) & (df['Formatted Date'] <= end_date)][['Formatted Date'] + selected_vars]
    fig = px.line(filtered_df, x='Formatted Date', y=selected_vars)
    return fig


# Callback for scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('scatter-plot-radio', 'value')])
def update_scatter_plot(selected_var):
    correlation = df[['Wind Speed (km/h)', selected_var]].corr().iloc[0, 1]
    fig = px.scatter(df, x='Wind Speed (km/h)', y=selected_var, title=f'Correlation of Wind Speed (km/h)) vs {selected_var}: {correlation:.2f}')
    return fig


# Callback for interactive charts
@app.callback(
    [Output('chart1', 'figure'),
     Output('chart2', 'figure')],
    [Input('chart1', 'clickData'),
     Input('chart1', 'selectedData'),
     Input('chart1', 'relayoutData')])
def update_interactive_charts(click_data, selected_data, relayout_data):
    ctx = dash.callback_context
    triggered_component = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_component == 'chart1':
        selected_point = click_data['points'][0] if click_data and 'points' in click_data else None
        selected_points = selected_data['points'] if selected_data and 'points' in selected_data else None

        if selected_point:
            temperature = selected_point['x']
            filtered_df = df[df['Temperature (C)'] == temperature]
            fig2 = px.line(filtered_df, x='Formatted Date', y='Wind Speed (km/h)')
        elif selected_points:
            temperature = [point['x'] for point in selected_points]
            filtered_df = df[df['Temperature (C)'].isin(temperature)]
            fig2 = px.line(filtered_df, x='Formatted Date', y='Wind Speed (km/h)')
        else:
            fig2 = px.line(df, x='Formatted Date', y='Wind Speed (km/h)')

        return dash.no_update, fig2

    elif triggered_component == 'chart2':
        relayout_xaxis_range = relayout_data.get('xaxis.range')

        if relayout_xaxis_range:
            start_date, end_date = relayout_xaxis_range
            filtered_df = df[(df['Formatted Date'] >= start_date) & (df['Formatted Date'] <= end_date)]
            fig1 = px.scatter(filtered_df, x='Temperature (C)', y='Humidity')
        else:
            fig1 = px.scatter(df, x='Temperature (C)', y='Humidity')

        return fig1, dash.no_update

    else:
        return dash.no_update, dash.no_update
    
    


# Run the application
if __name__ == '__main__':
    app.run_server(port=5000)
