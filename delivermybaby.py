# -*- coding: utf-8 -*-

import math
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from collections import OrderedDict
import numpy as np
import pandas as pd

# Load data

zipcode_data = pd.read_csv('data/zipcode.csv', header=None)
zipcode_data = zipcode_data.set_index(0)

hospital_data = pd.read_csv('data/hospital8.csv', header=None)
hospital_data = hospital_data.set_index(0)

# Calculate the population avgs of the data variables

avg_csec = np.mean(hospital_data[3]) # avg low-risk primary c-section rate(%)
avg_vbac = np.mean(hospital_data[4])#avg VBAC rate(%)
avg_nicu = np.mean(hospital_data[5]) # avg total NICU discharges in 2005

# Calculate the population stdev of the data variables

sd_csec = np.std(hospital_data[3]) # avg low-risk primary c-section rate(%)
sd_vbac = np.std(hospital_data[4]) # avg VBAC rate(%)
sd_nicu = np.std(hospital_data[5]) # avg total NICU discharges in 2005

# Convert DataFrames to dictionaries

zipcode_data = zipcode_data.to_dict('index')
hospital_data = hospital_data.rename(
    index=str,
    columns={1: "lat", 2: "lng", 3: "c-sec", 4: "vbac", 5: "nicu", 6: "city", 7: "hpsa"}
)
hospital_data = hospital_data.to_dict('index')


# Define functions

def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 3959
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return (d)

# Dash app

css = [
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

js = [
    {
        'src': 'https://code.jquery.com/jquery-3.3.1.slim.min.js',
        'integrity': 'sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo',
        'crossorigin': 'anonymous'
    },
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js',
        'integrity': 'sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49',
        'crossorigin': 'anonymous'
    },
    {
        'src': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js',
        'integrity': 'sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__, external_stylesheets=css, external_scripts=js)

app.title = 'Delivery!'

# Layout

app.layout = html.Div(
    [
        html.Div(
            html.Div(
                [
                    html.H1(
                        'Delivery!', #Text that shows up on webpage
                        className='display-4'
                    ),
                    html.P(
                        'Find the best hospital for you.',
                        className='lead'
                    )
                ],
                className='container'
            ),
            className='jumbotron jumbotron-fluid' #style of webpage
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label('Enter your home zipcode'),
                        dcc.Input(type='text', id='zipcode-input', className='form-control')
                    ],
                    className='form-group'
                ),
                html.Div(
                    [
                        html.Label('How far are you willing to travel to your hospital (miles)?'),
                        dcc.Input(type='text', id='distance-max-input', className='form-control')
                    ],
                    className='form-group'
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label('Distance of hospital from your home'),
                                dcc.Slider(id='weight-close-slider', min=0, max=10, marks={0: 'Not Important', 10: 'Very Important'}, value=5)
                            ],
                            className='form-group mb-5'
                        ),
                        html.Div(
                            [
                                html.Label('Low Cesarean-section rates'),
                                dcc.Slider(id='weight-csec-slider', min=0, max=10, marks={0: 'Not Important', 10: 'Very Important'}, value=5)
                            ],
                            className='form-group mb-5'
                        ),
                        html.Div(
                            [
                                html.Label('High vaginal birth after C-section (VBAC) rates'),
                                dcc.Slider(id='weight-vbac-slider', min=0, max=10, marks={0: 'Not Important', 10: 'Very Important'}, value=5)
                            ],
                            className='form-group mb-5'
                        ),
                        html.Div(
                            [
                                html.Label('Large neonatal intensive care unit (NICU)'),
                                dcc.Slider(id='weight-nicu-slider', min=0, max=10, marks={0: 'Not Important', 10: 'Very Important'}, value=5)
                            ],
                            className='form-group mb-5'
                        )
                    ],
                    style={'width': '100%'} # Sliders at a horizontal scrollbar when > 70% width
                ),
                html.Div(
                    [
                        html.Button('Submit', id='submit-button', n_clicks=0, className='btn btn-primary'),
                    ],
                    className='form-group'
                ),
                html.Div([], id='results')
            ],
            className='container'
        )
    ]
)

# Callbacks

@app.callback(
    Output('results', 'children'),
    [
        Input('submit-button', 'n_clicks')
    ],
    [
        State('zipcode-input', 'value'), #passes the user's input values to the code
        State('distance-max-input', 'value'),
        State('weight-close-slider', 'value'),
        State('weight-csec-slider', 'value'),
        State('weight-vbac-slider', 'value'),
        State('weight-nicu-slider', 'value')
    ]
)
def get_hospitals(n_clicks, zipcode, distance_max, w_close, w_csec, w_vbac, w_nicu):
    zipcode = int(zipcode)
    distance_max = int(distance_max)
    w_close = float(w_close)
    w_csec = float(w_csec)
    w_vbac = float(w_vbac)
    w_nicu = float(w_nicu)

    zipcode = zipcode_data[zipcode]
    origin = (zipcode[1], zipcode[2]) # (lat, lng)

    # Normalized weights of all factors (sum = 1)
    b1 = w_csec / (w_csec + w_vbac + w_nicu + w_close)
    b2 = w_vbac / (w_csec + w_vbac + w_nicu + w_close)
    b3 = w_nicu / (w_csec + w_vbac + w_nicu + w_close)
    b4 = w_close / (w_csec + w_vbac + w_nicu + w_close)

    results = {} # this will be a dictionary of all the hospitals and their associated data
    for hospital, values in hospital_data.items(): #key is the hospital; value is the information variables
        destination = (values['lat'], values['lng'])
        dist_to_hosp = distance(origin, destination)
        if dist_to_hosp <= distance_max:

            # Copy the hospital values to results
            results[hospital] = values.copy()

            # Z-score of the c-section parameter:
            d_csec = np.subtract(values['c-sec'], avg_csec)
            z_csec = np.divide(d_csec, sd_csec)

            # Z-score of the VBAC parameter:
            d_vbac = np.subtract(values['vbac'], avg_vbac)
            z_vbac = np.divide(d_vbac, sd_vbac)

            # Z-score of the NICU parameter:
            d_nicu = np.subtract(values['nicu'], avg_nicu)
            z_nicu = np.divide(d_nicu, sd_nicu)

            # Calculate hospital scores
            results[hospital]['h_score'] = b1 * (1 - z_csec) + b2 * z_vbac + b3 * z_nicu - b4 * dist_to_hosp

            # add distance to hospital to the dictionary
            results[hospital]['dist'] = '{0:.2f}'.format(dist_to_hosp) #format for 2 decimals

            if values['hpsa'] == 1:
                results[hospital]['hpsa'] = 'Alert: This is a registered Health Professional Shortage Area (HPSA).'
            else:
                results[hospital]['hpsa'] = ''

    sorted_keys = sorted(results.keys(), key=lambda y: (results[y]['h_score']), reverse=True)

    # Data for the DataFrame
    data = []
    for hospital in sorted_keys:
        data.append([
            hospital,
            results[hospital]['city'],
            results[hospital]['dist'],
            str(results[hospital]['c-sec']),
            str(results[hospital]['vbac']),
            str(results[hospital]['nicu']),
            results[hospital]['hpsa']
        ])

 	# Column names for the DataFrame
    column_names = [
        'Hospital',
        'City',
        'Distance',
        'Cesarean-section rate (%) - Lower is better',
        'Vaginal Birth After C-Section rate (%) - Higher is better',
        'NICU volume per year - Higher is better',
        'Health Professional Shortage Area Status'
    ]

    # Sorted results as a DataFrame
    sorted_results = pd.DataFrame(data, columns=column_names)

    # Create Dash table form DataFrame
    table_row = []
    for column_name in sorted_results.columns:
    	table_column = html.Th(column_name)
    	table_row.append(table_column)
    table_row = html.Tr(table_row)
    table_header = html.Thead(table_row)

    table_rows = []
    for i in range(len(sorted_results)):
    	table_row = []
    	for column_name in sorted_results.columns:
    		table_column = html.Td(sorted_results.iloc[i][column_name])
    		table_row.append(table_column)
    	table_row = html.Tr(table_row)
    	table_rows.append(table_row)
    table_body = html.Tbody(table_rows)

    table = html.Table(
    	[table_header, table_body],
    	className='table table-striped'
    )

    # Title for table
    table_title = html.H4('Hospital Results')

    return [table_title, table]

# Output is in the form of: hospital name, city, distance to hospital(mi), c-sec rate, VBAC rate, NICU size, h_score

# Flask server

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
