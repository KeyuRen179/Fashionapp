from dash import html, dcc
from dash.dependencies import Input, Output, State
from flask import request

def get_login_layout():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Img(src='/assets/logo.jpg',
                             style={'width': '200px', 'height': 'auto', 'display': 'block', 'marginBottom': '20px'}),

                    html.H1("Welcome to Costume Network", style={'textAlign': 'center', 'marginBottom': '50px'}),
                    html.Div(
                        children=[
                            dcc.Input(id='login_email', type='email', placeholder='Email', autoComplete='username',
                                      style={'marginBottom': '10px'}),
                            dcc.Input(id='login_password', type='password', placeholder='Password',
                                      autoComplete='current-password', style={'marginBottom': '10px'}),
                            html.Button('Login', id='login_submit', n_clicks=0, style={'marginRight': '10px'}),
                            html.Div(id='login_feedback', style={'marginBottom': '10px'}),
                            dcc.Link('New here? Register', href='/register',
                                     style={'display': 'block', 'marginBottom': '5px'}),
                            dcc.Link('Continue as guest', href='/fashiongeneration', style={'display': 'block'}),
                            dcc.Link('forgot password?', href='/reset-password',
                                     style={'display': 'block', 'marginTop': '10px'})  # Update this link
                        ],
                        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}
                    )
                ],
                style={'width': '100%', 'maxWidth': '400px', 'margin': '0 auto', 'padding': '20px',
                       'boxShadow': '0px 0px 10px #aaa'}
            )
        ],
        style={'width': '100vw', 'height': '100vh', 'display': 'flex', 'alignItems': 'center',
               'justifyContent': 'center', 'flexDirection': 'column'}
    )
