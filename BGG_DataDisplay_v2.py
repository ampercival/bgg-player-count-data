import dash
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd

# Read in data
df = pd.read_csv('PlayerCountDataList.csv')

# Get unique types for the "Type" column dropdown
unique_types = df['Type'].unique()

# Round data to two decimal places
df['Average Rating'] = df['Average Rating'].round(2)
df['Score Factor'] = df['Score Factor'].round(2)


# Initialize Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Loading(
        id="loading-1",
        type="circle",  # You can use "circle", "cube", "dot", or "default"
        children= [
            dcc.Dropdown(
                id='type-dropdown',
                options=unique_types,
                value=None,  # Default value
                placeholder="Select a Type",
                multi=True  # Allow selecting multiple types
            ),  
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                # filter_action='native',
                sort_action='native',
                page_action='native',
                #page_size=10,
                #style_table={'height': '400px', 'overflowY': 'auto'},
                style_cell={
                    'minWidth': '0px', 'width': '50px', 'maxWidth': '180px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'padding': '10px',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'whiteSpace': 'normal',  # Allows the text to wrap
                    'height': 'auto',  # Adjusts height to fit the content
                    'textAlign': 'center',
                },               
            )
        ]
    )
])

# Callback to update table data based on dropdown selection
@app.callback(
    Output('table', 'data'),
    [Input('type-dropdown', 'value')]
)
def filter_table(selected_types):
    if not selected_types:
        filtered_df = df
    else:
        filtered_df = df[df['Type'].isin(selected_types)]
    return filtered_df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)