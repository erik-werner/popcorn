import dash
from dash import html, dcc, callback, Input, Output, State, no_update, ctx, dash_table
from dash.exceptions import PreventUpdate
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
import re
import numpy as np

from utils import add_user, add_event
import os

DEBUG = eval(os.getenv("DEBUG", "False"))
host = "popcorn_db" if not DEBUG else "localhost"

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server


login_modal = dbc.Modal(
    [
        dbc.ModalHeader("Användarkod"),
        dbc.ModalBody(
            [
                dbc.Input(placeholder="zyx", id="username", pattern="[a-zA-Z]{3}", maxLength=3, invalid=False,
                          minLength=3, type="text", debounce=True, autoFocus=True),
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Button("Login", id="login-button", className="ml-auto"),
            ]
        ),
    ],
    id="login-modal",
    is_open=True,
    backdrop="static",
)

available_popcorn = np.arange(1, 11)

popcorn_rater_widget = html.Div(
    [
        html.H2("Rejta Popcorn! 🍿"),
        html.Hr(style={"padding-bottom": "3rem"}),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H5("Popcorn 1", style={"text-align": "center"}),
                                dbc.Select(
                                    available_popcorn,
                                    None,
                                    id="popcorn-1",
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        html.H5("Föreslå!", style={"text-align": "center", "font-size": "1rem"}),
                                    ],
                                    justify="center",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Button("🍿", id="suggest-popcorn", color="secondary", 
                                                   style={"font-size": "1.5rem", "max-width": "50px", "max-height": "50px"}),
                                    ],
                                    justify="center",
                                ),
                            ],
                            width=2,
                        ),
                        dbc.Col(
                            [
                                html.H5("Popcorn 2", style={"text-align": "center"}),
                                dbc.Select(
                                    available_popcorn,
                                    None,
                                    id="popcorn-2",
                                ),
                            ],
                            width={"size": 4, "offset": 0},
                        ),
                    ],
                    justify="center",
                    style={"padding-bottom": "5rem"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Slider(
                                    id="popcorn-score",
                                    min=-2,
                                    max=2,
                                    value=0,
                                    marks={
                                        -2: {"label": "+2", "style": {"font-size": "1rem"}}, 
                                        -1: {"label": "+1", "style": {"font-size": "1rem"}}, 
                                        0: {"label": "0", "style": {"font-size": "1rem"}}, 
                                        1: {"label": "+1", "style": {"font-size": "1rem"}}, 
                                        2: {"label": "+2", "style": {"font-size": "1rem"}}
                                    },
                                    step=0.001,
                                    included=False,
                                ),
                            ],
                            width=9,
                            # style={"margin-left": "10%", "margin-right": "10%",},
                        ),
                    ],
                    justify="center",
                    style={"padding-bottom": "5rem"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button("Lägg till betyg", id="add-score", color="primary"),
                            ],
                            width=4,
                        ),
                    ],
                    justify="end",
                    style={"padding-bottom": "5rem", "padding-top": "1rem"},
                ),
            ]
        ),
    ]
)


app.layout = dbc.Container(
    [
        login_modal,
        popcorn_rater_widget
    ],
    className="p-5",
)

# Callbacks
@app.callback(
    Output("login-modal", "is_open"),
    Output("username", "invalid"),
    Output("username", "valid"),
    [Input("login-button", "n_clicks"),
     Input("username", "n_submit"),
     State("username", "value"),
     State("username", "pattern")],
    prevent_initial_call=True,
)
def login(n_clicks, n_submit, username, pattern):
    if (n_clicks or n_submit) and username:
        if re.match(pattern, username):
            add_user(username, host=host)
            return False, False, True
        else:
            return True, True, False
    
    return True, True, False


@app.callback(
    Output("popcorn-1", "value"),
    Output("popcorn-2", "value"),
    Output("popcorn-score", "value"),
    [Input("suggest-popcorn", "n_clicks"),
     Input("add-score", "n_clicks"),
     State("popcorn-1", "value"),
     State("popcorn-2", "value"),
     State("popcorn-score", "value"),
        State("username", "value")],
    prevent_initial_call=True,
)
def set_input_states(suggest_clicks, add_clicks, popcorn_1, popcorn_2, score, user_id):
    if ctx.triggered_id == "suggest-popcorn":
        popcorn_id_1 = np.random.choice(available_popcorn)
        popcorn_id_2 = np.random.choice(list(set(available_popcorn) - {popcorn_id_1}))
        return popcorn_id_1, popcorn_id_2, no_update
    elif ctx.triggered_id == "add-score":
        if popcorn_1 and popcorn_2 and score:
            add_event(user_id, popcorn_1, popcorn_2, score, int(datetime.now().timestamp()), host=host)
            return None, None, 0
        else:
            return no_update, no_update, no_update


if __name__ == "__main__":
    app.run_server(port=8051, debug=True)
