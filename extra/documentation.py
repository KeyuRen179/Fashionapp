import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import Dash, dcc, html, Input, Output, ctx, State, ALL, MATCH, callback
from openai import OpenAI
from flask import Flask, session
# from flask_session import Session
import sqlite3
import os

"""server = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
server.config["SESSION_PERMANENT"] = False
server.config["SESSION_TYPE"] = "filesystem"
session(server)"""

# Initialize OpenAI client with your API key
openai_client = OpenAI(api_key="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")

# Registration Modal
registration_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Register")),
        dbc.ModalBody([
            dcc.Input(id='reg_email', type='email', placeholder='Email', className='mb-2'),
            dcc.Input(id='reg_password', type='password', placeholder='Password', className='mb-2'),
            dcc.Input(id='reg_password_confirm', type='password', placeholder='Confirm Password', className='mb-2'),
            dbc.Button('Register', id='register_btn', className='ms-auto', n_clicks=0),
        ]),
        dbc.ModalFooter(
            dbc.Button("Close", id='close_register_modal', className='ms-auto', n_clicks=0)
        ),
    ],
    id='registration_modal',
    is_open=False,
)


layout = dbc.Container([
     dbc.Row([
        dbc.Col(html.Button('Register', id='open_register_modal', n_clicks=0)),
        registration_modal
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Welcome to the Fashion Life", style={'color': 'white', 'text-align': 'center', 'margin-top': '5vh'}),
            html.Div([
                dcc.Input(
                    id='poem_input',
                    placeholder='Enter a fashion-related keyword',
                    type='text',
                    value='',
                    style={'margin-left': '1rem'}
                ),
                html.Button('Fashion Search', id='submit_poem', n_clicks=0, style={'margin-left': '1rem'}),
            ], style={'display': 'flex', 'justify-content': 'center', 'text-align': 'center'}),
            html.Br(), html.Br(),
            html.Div(id='poem_output', className='text-white text-center'),
            html.Br(), html.Br(),
            html.Div(id='poem_image', className='ml-auto mr-auto d-block'),
            html.Div(html.H3('', className='text-white', style={'margin-bottom': '0.5rem'})),
        ], className='justify-content-center')
    ], style={'background-color': 'black'}),
], fluid=True)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://platform.linkedin.com/in.js"])
app.layout = layout

# Callback to toggle the registration modal
@app.callback(
    Output('registration_modal', 'is_open'),
    [Input('open_register_modal', 'n_clicks'), Input('close_register_modal', 'n_clicks')],
    [State('registration_modal', 'is_open')]
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('poem_output', 'children'),
    [Input('submit_poem', 'n_clicks')],
    [State('poem_input', 'value')]
)

def update_poem(submit_poem, poem_input):
    if ctx.triggered_id == 'submit_poem':
        # Generate images based on the input keyword
        response = openai_client.images.generate(
            prompt=f"Generate a high-resolution image of beautiful people wearing fashion in the style of {poem_input}.",
            #prompt=f"Generate a high-resolution image of a {poem_input}. Please ensure the colors are vibrant. The image should be suitable for use as a desktop wallpaper."
            n=6,  # Generate six images
        )

        # Initialize a list to store image components
        image_components = []

        # Create image components for each generated image
        for i, image_data in enumerate(response.data):
            image_url = image_data.url
            image_component = html.Div([
                html.Img(src=image_url, className='img-fluid'),
                html.Br(),
                html.A('Download Image', href=image_url, download=f'fashion_image_{i}.jpg', className='btn btn-primary')
            ], style={'margin-bottom': '20px'})
            image_components.append(image_component)


        #Web Links
        weblinks = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Generate website links with online stores that sell clothing and fashion in the style of {poem_input}. Please output weblinks only."}
            ]
        )
        websites = weblinks.choices[0].message.content.strip()
            
        # Split the string by numbering
        website_parts = websites.split()

        # Create a list of dictionaries for fashion links
        fashion_links = []

        for i in range(0, len(website_parts), 2):
            link = website_parts[i + 1]
            fashion_links.append({"text": f"Link {i//2 + 1}", "href": link})

        # Create HTML elements for fashion links
        fashion_links_html = html.Div([
            html.A(
                link['text'],
                href=link['href'],
                target='_blank',
                style={'color': 'white', 'text-decoration': 'none', 'margin-right': '1rem'}
            ) for link in fashion_links
        ], style={'display': 'flex', 'justify-content': 'center', 'text-align': 'center', 'margin-top': '3vh'})

        # Fashion website link
        fashion_website_link = html.Div(
            fashion_links_html,
            style={'display': 'flex', 'justify-content': 'center', 'text-align': 'center', 'margin-top': '3vh'}
        )
    
        return image_components + [fashion_website_link]

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=os.environ.get('PORT', '8000'), debug=True)

