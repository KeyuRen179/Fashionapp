import dash
import dash_bootstrap_components as dbc
from flask import Flask, request, jsonify
from database import create_tables, insert_user_history, get_user_history
import os

# Initialize database tables
create_tables()

# Initialize the Flask server
server = Flask(__name__)
server.secret_key = os.environ.get('FLASK_SECRET_KEY')  # Ensure you've set this environment variable

# Initialize the Dash app with the Flask server
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://platform.linkedin.com/in.js"],
    server=server  # Pass the Flask server to Dash
)

# Define Flask routes on the server object
@server.route('/add_action', methods=['POST'])
def add_action():
    data = request.get_json()
    user_id = data['user_id']
    action = data['action']
    insert_user_history(user_id, action)
    return jsonify({"status": "success"}), 200

@server.route('/history', methods=['GET'])
def history():
    user_id = request.args.get('user_id')
    history = get_user_history(user_id)
    return jsonify(history)

if __name__ == '__main__':
    app.run_server(debug=True)
