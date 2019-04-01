import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import data_analysis as da
from settings import months, cols, metadataDB
import db_engine as db
from db_info import db_info

app = dash.Dash(__name__)

# initial data frame 
empty_df = pd.DataFrame()

def convert_to_json(current_dataframe):
    '''
        converts all the data to a JSON string
    '''
    jsonStr = current_dataframe.to_json(orient='split')
    return jsonStr

def convert_to_df(jsonified_data):
    '''
        converts the JSON string back to a dataframe
    '''
    jsonStr = r'{}'.format(jsonified_data)
    dff = pd.read_json(jsonStr, orient='split')
    return dff

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='GLEON MC Data Analysis')
    ], className="title"),

    html.Div([
        html.Details([
            html.Summary('Upload New Data'),
            html.Div(children=[
                html.Div([
                    html.Div([
                        html.P('Name'),
                        dcc.Input(id='user-name', type='text'),
                    ], className='one-third column'),
                    html.Div([
                        html.P('Institution'),
                        dcc.Input(id='user-inst', type='text'),
                    ], className='one-third column'),
                    html.Div([
                        html.P('Database Name'),
                        dcc.Input(id='db-name', type='text')
                    ], className='one-third column'),   
                ], className='row'),           
                dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    },
                    # allow single file upload
                    multiple=False
                ),
                html.Div(id='upload-output'),
                html.Button(id='done-button', n_clicks=0, children='Done', 
                    style={
                        'margin': '10px 0px 10px 0px'   
                    }
                ),
                html.P(id='upload-msg'),
            ], className="row p"),
        ]),  
    ], className="row"),

    html.Button(id='refresh-db-button', children='Refresh', 
            style={
                'margin': '10px 0px 10px 0px'   
            }
    ),

    dash_table.DataTable(
        id='metadata_table',
        columns=[{"name": i, "id": i} for i in metadataDB.columns],
        data=metadataDB.to_dict("rows"),
        row_selectable='multi',
        selected_rows=[],
        style_as_list_view=True,
        sorting=True,
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
    ),

    html.Button(id='apply-filters-button', children='Filter Data', 
            style={
                'margin': '10px 0px 10px 0px' 
            }
    ),

    html.Div([
        html.H2('Microcystin Concentration'),
        dcc.Graph(id='geo_plot'),
        html.Div([
            dcc.RadioItems(
            id="geo_plot_option",
            options=[{'label': 'Show Concentration Plot', 'value': 'CONC'},
                    {'label': 'Show Log Concentration Change Plot', 'value': 'LOG'}],
                    value='CONC'),
        ]),
        html.Div([
            html.Div(html.P("Year:")),
            html.Div(
                dcc.Dropdown(
                    id='year-dropdown',
                    multi=True,
                ),
            )
        ]),
        html.Div([
            html.P("Month:"),
            dcc.Slider(
                id='month-slider',
                min=0,
                max=11,
                value=1,
                marks={i: months[i] for i in range(len(months))}
            )
        ]),
    ], className="row"),
    
    html.Div([
        html.H2('Total Phosphorus vs Total Nitrogen'),

        dcc.Graph(
            id="tn_tp_scatter",
        ),

        html.Div([
            html.P("Log TN:"),
            dcc.RangeSlider(
                id="tn_range",
                min=0,
                step=0.5,
                marks={
                    1000: '1',
                    4000: '100',
                    7000: '1000',
                    10000: '10000'
                },
            ),
        ]),

        html.Div([
            html.P("Log TP:"),
            dcc.RangeSlider(
                id="tp_range",
                min=0,
                step=0.5,
                marks={
                    1000: '1',
                    4000: '100',
                    7000: '1000',
                    10000: '10000'
                },
            ),
        ]),
    ], className="row"),
    
    html.Div([
        html.H2('Data Trends by Lake'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id="temporal-lake-scatter",
                )
            ], className='six columns'),
            html.Div([
                dcc.Graph(
                    id="temporal-lake-pc-scatter",
                )
            ], className='six columns'),
        ]),
        dcc.Dropdown(
            id="temporal-lake-col",
            options=[{'label': c, 'value': c} for c in cols],
            value=cols[0],
            className='six columns'
        ),
        dcc.Dropdown(
            id='temporal-lake-location',
            className='six columns'
        )
    ], className="row"),
    
    html.Div([
        html.H2('Overall Temporal Data Trends'),
        html.P('Includes data from all lakes'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id="temporal-avg-scatter",
                )
            ], className='six columns'),
            html.Div([
                dcc.Graph(
                    id="temporal-pc-scatter",
                )
            ], className='six columns'),
        ]),
        dcc.Dropdown(
            id="temporal-avg-col",
            options=[{'label': c, 'value': c} for c in cols],
            value=cols[0]
        )
    ], className='row'),
    
    html.Div([
        html.H2('Raw Data'),
        dcc.Graph(
            id="temporal-raw-scatter",
        ),
        html.Div([
            html.Div([
                dcc.RadioItems(
                    id="temporal-raw-option",
                    options=[{'label': 'Show All Raw Data', 'value': 'RAW'},
                            {'label': 'Show Data Within 3 Standard Deviations', 'value': '3SD'}],
                            value='RAW'
                )
            ], className='six columns'),
            html.Div([
                dcc.Dropdown(
                    id="temporal-raw-col",
                    options=[{'label': c, 'value': c} for c in cols],
                    value=cols[0]
                )
            ], className='six columns')
        ])
    ], className='row'),

    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'}, children=convert_to_json(empty_df))
])

@app.callback(
    dash.dependencies.Output('metadata_table', 'data'),
    [dash.dependencies.Input('refresh-db-button', 'n_clicks')])
def upload_file(n_clicks):
    # read from MetadataDB to update the table 
    metadataDB = pd.read_csv("data/MetadataDB.csv")
    return metadataDB.to_dict("rows")     

@app.callback(
    dash.dependencies.Output('geo_plot', 'figure'),
    [dash.dependencies.Input('year-dropdown', 'value'),
     dash.dependencies.Input('month-slider', 'value'),
     dash.dependencies.Input('geo_plot_option','value'),
     dash.dependencies.Input('intermediate-value', 'children')])
def update_geo_plot(selected_years, selected_month, geo_option, jsonified_data):
    dff = convert_to_df(jsonified_data)
    return da.geo_plot(selected_years, selected_month, geo_option, dff)

@app.callback(
    dash.dependencies.Output('temporal-lake-scatter', 'figure'),
    [dash.dependencies.Input('temporal-lake-col', 'value'),
     dash.dependencies.Input('temporal-lake-location', 'value'),
     dash.dependencies.Input('intermediate-value', 'children')])
def update_output(selected_col, selected_loc, jsonified_data):
    dff = convert_to_df(jsonified_data)
    return da.temporal_lake(selected_col, selected_loc, 'raw', dff)

@app.callback(
    dash.dependencies.Output('temporal-lake-pc-scatter', 'figure'),
    [dash.dependencies.Input('temporal-lake-col', 'value'),
     dash.dependencies.Input('temporal-lake-location', 'value'),
     dash.dependencies.Input('intermediate-value', 'children')])
def update_output(selected_col, selected_loc, jsonified_data):
    dff = convert_to_df(jsonified_data)
    return da.temporal_lake(selected_col, selected_loc, 'pc', dff)

@app.callback(
    dash.dependencies.Output('tn_tp_scatter', 'figure'),
    [dash.dependencies.Input('tn_range', 'value'),
     dash.dependencies.Input('tp_range', 'value'),
     dash.dependencies.Input('intermediate-value', 'children')])
def update_output(tn_val, tp_val, jsonified_data):
    dff = convert_to_df(jsonified_data)
    return da.tn_tp(tn_val, tp_val, dff)

@app.callback(
    dash.dependencies.Output('temporal-avg-scatter', 'figure'),
    [dash.dependencies.Input('temporal-avg-col', 'value'),
    dash.dependencies.Input('intermediate-value', 'children')])
def update_output(selected_col, jsonified_data):
    dff = convert_to_df(jsonified_data)
    return da.temporal_overall(selected_col, 'avg', dff)

@app.callback(
    dash.dependencies.Output('temporal-pc-scatter', 'figure'),
    [dash.dependencies.Input('temporal-avg-col', 'value'),
    dash.dependencies.Input('intermediate-value', 'children')])
def update_output(selected_col, jsonified_data):
    dff = convert_to_df(jsonified_data)
    return da.temporal_overall(selected_col, 'pc', dff)

@app.callback(
    dash.dependencies.Output('temporal-raw-scatter', 'figure'),
    [dash.dependencies.Input('temporal-raw-option', 'value'),
     dash.dependencies.Input('temporal-raw-col', 'value'),
     dash.dependencies.Input('intermediate-value', 'children')])
def update_output(selected_option, selected_col, jsonified_data):
    dff = convert_to_df(jsonified_data)
    return da.temporal_raw(selected_option, selected_col, dff)

@app.callback(dash.dependencies.Output('upload-output', 'children'),
              [dash.dependencies.Input('upload-data', 'contents')],
              [dash.dependencies.State('upload-data', 'filename')])
def update_uploaded_file(contents, filename):
    if contents is not None:
        return html.Div([
            html.H6(filename),
        ])

@app.callback(
    dash.dependencies.Output('upload-msg', 'children'),
    [dash.dependencies.Input('done-button', 'n_clicks')],
    [dash.dependencies.State('db-name', 'value'),
    dash.dependencies.State('user-name', 'value'),
    dash.dependencies.State('user-inst', 'value'),
    dash.dependencies.State('upload-data', 'contents'),
    dash.dependencies.State('upload-data', 'filename')])
def upload_file(n_clicks, dbname, username, userinst, contents, filename):
    if n_clicks != None and n_clicks > 0:
        if username == None or not username.strip():
            return 'Name field cannot be empty.'
        elif userinst == None or not userinst.strip():
            return 'Institution cannot be empty.'
        elif dbname == None or not dbname.strip():
            return 'Database name cannot be empty.'
        elif contents is None:
            return 'Please select a file.'
        else:
            new_db = db_info(dbname, username, userinst)
            return db.upload_new_database(new_db, contents, filename)

@app.callback(
    [dash.dependencies.Output('intermediate-value', 'children'),
     dash.dependencies.Output('tn_range', 'max'),
     dash.dependencies.Output('tn_range', 'value'),
     dash.dependencies.Output('tp_range', 'max'),
     dash.dependencies.Output('tp_range', 'value'),
     dash.dependencies.Output('year-dropdown', 'options'),
     dash.dependencies.Output('year-dropdown', 'value'),
     dash.dependencies.Output('temporal-lake-location', 'options'),
     dash.dependencies.Output('temporal-lake-location', 'value')],
    [dash.dependencies.Input('apply-filters-button', 'n_clicks')],
    [dash.dependencies.State('metadata_table', 'derived_virtual_selected_rows'),
    dash.dependencies.State('metadata_table', 'derived_virtual_data')])
def update_graph(n_clicks, derived_virtual_selected_rows, dt_rows):
    if n_clicks != None and n_clicks > 0 and derived_virtual_selected_rows is not None:       
        # update the user's data based on the selected databases 
        selected_rows = [dt_rows[i] for i in derived_virtual_selected_rows]
        new_df = db.update_dataframe(selected_rows)    
        jsonStr = convert_to_json(new_df)

        tn_max = np.max(new_df["Total Nitrogen (ug/L)"])
        tn_value = [0, np.max(new_df["Total Nitrogen (ug/L)"])]
        
        tp_max = np.max(new_df["Total Phosphorus (ug/L)"])
        tp_value = [0, np.max(new_df["Total Phosphorus (ug/L)"])]
        
        # update the date ranges
        year = pd.to_datetime(new_df['DATETIME']).dt.year
        years = range(np.min(year), np.max(year)+1)
        years_options = [{'label': str(y), 'value': y} for y in years]
        years_value = np.min(years)

        # update the lake locations 
        locs = list(new_df["Body of Water Name"].unique())
        locs.sort()

        # Identify all body of waters with more than 2 years of data 
        # locations = [] # use locations instead of locs in output 
        # for l in locs:
        #     l_data = new_df[new_df["Body of Water Name"] == l]
        #     l_years = pd.to_datetime(l_data['DATETIME']).dt.year.unique()
        #     if len(l_years) > 2:
        #         locations.append(l)
        locs_options = [{'label': loc, 'value': loc} for loc in locs]
        locs_value = locs[0]

        return jsonStr, tn_max, tn_value, tp_max, tp_value, years_options, years_value, locs_options, locs_value

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://codepen.io/chriddyp/pen/bWLwgP.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True)