import dash_bootstrap_components as dbc
from dash import dcc, html

def create_main_layout():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Login", href="/login", id="login-link")),
            dbc.NavItem(dbc.NavLink("Register", href="/register", id="register-link")),
            dbc.NavItem(dbc.NavLink("Logout", href="/", id="logout-link", style={'display': 'none'})),
            dbc.NavItem(dbc.NavLink("Query History", href="/history", id="history-link")),
        ],
        brand="Costume Network",
        brand_href="/main",
        color="primary",
        dark=True,
        fluid=True,
    )

    layout = dbc.Container(
        [
            dbc.Row(dbc.Col(navbar)),
            dbc.Row(
                dbc.Col(
                    html.Div(id='save-confirmation')
                )
            ),
            dbc.Row(
                dbc.Col(
                    [
                        html.H3("Welcome to Costume Network",
                                style={'textAlign': 'center', 'marginTop': '2rem', 'color': 'white'}),
                        html.Div(
                            [
                                dcc.Input(
                                    id='poem_input',
                                    placeholder='Enter a custom-related keyword',
                                    type='text',
                                    style={'marginRight': '10px', 'width': '30%'},
                                ),
                                html.Button('Custom Search', id='submit_poem', n_clicks=0),
                            ],
                            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center',
                                   'marginBottom': '20px'},
                        ),
                        html.Div(id='poem_output', className='text-white text-center'),
                        html.Div(id='poem_image', style={'textAlign': 'center'}),
                    ]
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.Div(id='image_link_section')
                )
            )
        ],
        fluid=True,
    )
    return layout

def update_image_link_section(images, links):
    return html.Div(
        [
            html.Div(
                [
                    html.Img(src=images[i], style={'width': '100px'}),
                    html.Button('Save', id={'type': 'save-button', 'index': i}, n_clicks=0)
                ],
                style={'display': 'inline-block', 'margin': '10px'}
            ) for i in range(len(images))
        ]
    )
