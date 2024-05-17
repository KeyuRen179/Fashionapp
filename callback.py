# callbacks.py
from dash.dependencies import Input, Output, State
from dash import html, dcc
from app import app
from components.fashion_generation import update_fashion
from layouts.registration_modal import toggle_modal
import dash
from database import register_user, validate_login
from flask import session


# Callback for registration page
@app.callback(
    [Output('reg_output', 'children'),  # To display a registration status message
     Output('redirect-trigger', 'children', allow_duplicate=True)],  # To trigger redirection
    [Input('submit_reg', 'n_clicks')],
    [State('reg_email', 'value'),
     State('reg_password', 'value'),
     State('reg_password_confirm', 'value')],
    prevent_initial_call=True
)
def handle_registration(n_clicks, email, password, confirm_password):
    if n_clicks > 0:
        if password != confirm_password:
            return html.Div("Passwords do not match.", className="alert alert-warning"), dash.no_update

        try:

            registration_feedback = register_user(email, password)

            if registration_feedback == "Registration successful. Redirecting...":
                return html.Div(registration_feedback, className="alert alert-success"), '/main'
            else:
                return html.Div(registration_feedback, className="alert alert-danger"), dash.no_update
        except Exception as e:
            # Handle specific exceptions related to registration failures, e.g., email already exists
            return html.Div(f"Registration failed: {str(e)}", className="alert alert-danger"), dash.no_update

    # If the callback was triggered but did not meet any conditions
    return dash.no_update, dash.no_update


# Callback for login
@app.callback(
    [Output('login_feedback', 'children'),
     Output('redirect-trigger', 'children', allow_duplicate=True)],
    [Input('login_submit', 'n_clicks')],
    [State('login_email', 'value'), State('login_password', 'value')],
    prevent_initial_call=True  # Ensure this callback only runs in response to a user action
)
def handle_login(n_clicks, email, password):
    if n_clicks > 0:
        user_id = validate_login(email, password)
        if user_id:
            session['user_id'] = user_id
            # Here we return a tuple with two elements to match the expected output structure
            return [html.Div("Login successful!", className="alert alert-success"), '/main']
        else:
            # In case of failure, make sure to return a value for each Output
            return [html.Div("Invalid credentials.", className="alert alert-danger"), dash.no_update]
    return [dash.no_update, dash.no_update]


# Callback for toggling the registration modal (if you keep it)
@app.callback(
    Output('registration_modal', 'is_open'),
    [Input('open_register_modal', 'n_clicks'), Input('close_register_modal', 'n_clicks')],
    [State('registration_modal', 'is_open')]
)
def toggle_registration_modal(n1, n2, is_open):
    return toggle_modal(n1, n2, is_open)


# Callback for poem (fashion content) generation
@app.callback(
    Output('poem_output', 'children'),  # Ensure this ID matches the target element in your layout
    [Input('submit_poem', 'n_clicks')],  # Ensure this ID matches your submit button
    [State('poem_input', 'value')]  # Ensure this ID matches your input field
)
def handle_poem_generation(n_clicks, poem_input):
    if n_clicks > 0:
        # Call the poem generation function
        return update_fashion(poem_input)
    return dash.no_update
