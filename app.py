import dash
import dash_bootstrap_components as dbc
from flask import Flask
from database import create_tables
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
