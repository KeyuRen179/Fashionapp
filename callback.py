from dash.dependencies import Input, Output, State, ALL
from dash import dcc, html
from app import app
from components.fashion_generation import update_fashion
from layouts.registration_modal import toggle_modal
import dash
from database import register_user, validate_login, get_user_history, add_user_search, delete_user_search, reset_password
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
                return html.Div(registration_feedback, className="alert alert-success"), dcc.Location(pathname="/login", id="redirect")
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
            # Ensure proper redirect
            return html.Div("Login successful!", className="alert alert-success"), dcc.Location(
                pathname="/fashiongeneration", id="redirect")
        else:
            return html.Div("Invalid credentials.", className="alert alert-danger"), dash.no_update
    return dash.no_update, dash.no_update


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


# Callback for updating query results and adding delete functionality
@app.callback(
    Output('query-results', 'children'),
    [Input('search-button', 'n_clicks'), Input({'type': 'delete-button', 'index': ALL}, 'n_clicks')],
    [State('query-input', 'value')],
    prevent_initial_call=True
)
def update_query_results(search_clicks, delete_clicks, query):
    user_id = session.get('user_id')
    if not user_id:
        return html.Div("You need to be logged in to view history.", className="alert alert-danger")

    # Handle delete button clicks
    if delete_clicks:
        delete_index = [i for i, n in enumerate(delete_clicks) if n > 0][0]
        history = get_user_history(user_id)
        if history and len(history) > delete_index:
            record_to_delete = history[delete_index]
            delete_user_search(user_id, record_to_delete['id'])
            # Re-fetch updated history
            updated_history = get_user_history(user_id)
            return generate_history_layout(updated_history, query)

    if search_clicks > 0:
        history = get_user_history(user_id)
        if not history:
            return html.Div("No history found.", className="alert alert-warning")

        return generate_history_layout(history, query)

    return dash.no_update

def generate_history_layout(history, query):
    filtered_history = [record for record in history if query in record['search_query']] if query else history
    results_header = html.H2(f'Results for query: {query}') if query else html.H2('Search History')

    history_list = []
    for i, record in enumerate(filtered_history):
        history_list.append(html.Li([
            html.Div(f"{record['created_at']}: {record['search_query']}"),
            html.Img(src=record['image_url'], style={'width': '100px'}),
            html.A("Link", href=record['web_link'], target="_blank", style={'color': 'black'}),  # Set link color to black
            html.Button('Delete', id={'type': 'delete-button', 'index': i}, n_clicks=0)
        ]))

    return html.Div([results_header, html.Ul(history_list)])


# Callback for redirecting to history page
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('history-button', 'n_clicks')],
    prevent_initial_call=True
)
def redirect_to_history(n_clicks):
    if n_clicks > 0:
        return '/history'
    return dash.no_update

# Callback for saving selected images and links
@app.callback(
    [Output({'type': 'save-button', 'index': ALL}, 'children'),
     Output({'type': 'save-button', 'index': ALL}, 'disabled'),
     Output('save-confirmation', 'children')],
    [Input({'type': 'save-button', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def save_selected_links(n_clicks):
    user_id = session.get('user_id')
    if not user_id:
        return dash.no_update, dash.no_update, html.Div("You need to be logged in to save images and links.", className="alert alert-danger")

    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update

    save_indices = [i for i, n in enumerate(n_clicks) if n > 0]
    image_urls = session.get('temp_image_urls', [])
    web_links = session.get('temp_web_links', [])

    if not save_indices:
        return dash.no_update, dash.no_update, html.Div("No images or links selected for saving.", className="alert alert-warning")

    for index in save_indices:
        try:
            # Save the image URL and web link to the user's search history
            add_user_search(user_id, session.get('search_query', ''), [image_urls[index]], [web_links[index]])
        except Exception as e:
            return dash.no_update, dash.no_update, html.Div(f"Failed to save image and link: {e}", className="alert alert-danger")

    updated_button_texts = ['Saved' if i in save_indices else 'Save' for i in range(len(n_clicks))]
    updated_button_disabled = [True if i in save_indices else False for i in range(len(n_clicks))]

    return updated_button_texts, updated_button_disabled, html.Div("Selected images and links saved successfully.", className="alert alert-success")


# Callback for reset password
@app.callback(
    [Output('reset_password_feedback', 'children'),
     Output('redirect-trigger', 'children', allow_duplicate=True)],
    [Input('reset_password_submit', 'n_clicks')],
    [State('reset_password_email', 'value'), State('reset_old_password', 'value'), State('reset_confirm_old_password', 'value'), State('reset_new_password', 'value')],
    prevent_initial_call=True
)
def handle_reset_password(n_clicks, email, old_password, confirm_old_password, new_password):
    if n_clicks > 0:
        if old_password != confirm_old_password:
            return html.Div("Old passwords do not match.", className="alert alert-warning"), dash.no_update
        message = reset_password(email, old_password, new_password)
        if message == "Password reset successful.":
            return html.Div(message, className="alert alert-success"), dcc.Location(pathname="/login", id="redirect")
        else:
            return html.Div(message, className="alert alert-danger"), dash.no_update
    return dash.no_update, dash.no_update
