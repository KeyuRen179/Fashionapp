from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import session

def create_main_layout():
    user_id = session.get('user_id')

    login_or_logout_link = []
    if user_id:
        login_or_logout_link = [
            dbc.NavItem(dbc.NavLink("Logout", href="/logout")),
        ]
    else:
        login_or_logout_link = [
            dbc.NavItem(dbc.NavLink("Login", href="/login")),
            dbc.NavItem(dbc.NavLink("Register", href="/register")),
        ]

    navbar = dbc.NavbarSimple(
        children=login_or_logout_link,
        brand="Costume Network",
        brand_href="/fashiongeneration",
        color="primary",
        dark=True,
        fluid=True,
    )

    layout = dbc.Container(
        [
            dbc.Row(dbc.Col(navbar)),
            dbc.Row(
                dbc.Col(
                    [
                        html.H3(
                            "Welcome to Costume Network",
                            style={'textAlign': 'center', 'marginTop': '2rem', 'color': 'white'}
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id='poem_input',
                                    placeholder='Enter a costume-related keyword',
                                    type='text',
                                    style={'marginRight': '10px', 'width': '30%'},
                                ),
                                html.Button("Let's Create", id='submit_poem', n_clicks=0)
                            ],
                            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center',
                                   'marginBottom': '20px'},
                        ),
                        html.Div(
                            [
                                html.Button('Add another keyword', id='add_keyword', n_clicks=0),
                                html.Div(id='additional_keywords_container', children=[])
                            ],
                            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center',
                                   'marginBottom': '20px'}
                        ),
                        html.Div(
                            "Welcome back, user! Search history:",
                            id='welcome_message',
                            style={'color': 'white', 'textAlign': 'center', 'marginBottom': '20px'}
                        ) if user_id else None,
                        dcc.Loading(
                            id="loading-search-history",
                            type="circle",
                            children=html.Div(id='search_history',
                                              style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'})
                        ) if user_id else None,
                        dcc.Loading(
                            id="loading_poem_output",
                            type="circle",
                            children=html.Div(id="poem_loading")
                        ),
                        html.Div(id='poem_output', className='text-white text-center'),
                        html.Div(id='poem_image', className='ml-auto mr-auto d-block'),
                    ],
                    className='justify-content-center',
                )
            ),
        ],
        fluid=True,
        style={'backgroundColor': 'black', 'padding': '20px'},
    )
    return layout
