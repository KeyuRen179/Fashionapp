from dash import dcc, html, callback, Input, Output
from app import app
import layouts.main_layout as main_layout
from layouts.forgetpassword_page import get_forgot_password_layout
import layouts.registration_page as registration_page
import layouts.login_page as login_page
import os
from dash.dependencies import Input, Output, ClientsideFunction
from flask import session



# app.layout = main_layout.create_main_layout()

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(id='redirect-trigger', style={'display': 'none'}),  # For client-side redirection
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def display_page(pathname):
    user_is_logged_in = 'user_id' in session  # Check if the user is logged in

    if pathname == '/fashiongeneration':
        return main_layout.create_main_layout()
    elif pathname == "/register":
        return registration_page.get_layout()
    elif pathname == "/login":
        # Allow access to the login page regardless of login state
        return login_page.get_login_layout()
    elif pathname == "/logout":
        # Clear the session and redirect to fashiongeneration
        session.pop('user_id', None)
        return dcc.Location(href='/login', id='redirect')
    elif pathname == '/forgot-password':
        return get_forgot_password_layout()
    else:
        # Redirect to login page if pathname is not recognized
        return login_page.get_login_layout()

# Client-side callback for redirection
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='redirect'
    ),
    Output('url', 'pathname'),
    [Input('redirect-trigger', 'children')]
)

import callback


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=os.environ.get('PORT', '8000'), debug=True)
