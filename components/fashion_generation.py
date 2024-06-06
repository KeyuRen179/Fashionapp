from dash import html, ctx
from openai import OpenAI
import os
from dotenv import load_dotenv
from database import add_user_search
from flask import session

# load_dotenv()

openai_api_key = os.environ.get('OPENAI_API_KEY')

openai_client = OpenAI(api_key=openai_api_key)

def update_fashion(poem_input):
    if ctx.triggered_id == 'submit_poem':
        user_id = session.get('user_id')
        if not poem_input:
            return html.Div("Poem input cannot be empty.", className='alert alert-danger')

        # Generate images based on the input keyword
        response = openai_client.images.generate(
            prompt=f"generate images of costume in the style of {poem_input} and make fashion image photorealistic, ultra-detailed, high-definition 4k photograph, vibrant natural colors, 8k, UHD.",
            n=6,  # Generate six images
        )

        # Initialize a list to store image components
        image_components = []
        image_urls = []

        # Create image components for each generated image
        for i, image_data in enumerate(response.data):
            image_url = image_data.url
            image_component = html.Div([
                html.Img(src=image_url, className='img-fluid'),
                html.Br(),
                html.A('Download Image', href=image_url, target="_blank", download=f'fashion_image_{i}.jpg',
                       className='btn btn-primary'),
                html.Button('Save Image and Link', id={'type': 'save-button', 'index': i}, n_clicks=0, className='btn btn-success')
            ], style={'margin-bottom': '20px'})
            image_components.append(image_component)
            image_urls.append(image_url)

        # Web Links
        weblinks = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user",
                 "content": f"Generate exactly 6 website links with online stores that sell clothing and fashion in the style of {poem_input}. Please output weblinks only and make sure the websites are working."}
            ]
        )
        websites = weblinks.choices[0].message.content.strip()

        # Split the string into parts and ensure we only get 6 links
        website_parts = websites.split()[:12]  # Ensure we don't exceed 6 links

        # Create a list of dictionaries for fashion links
        fashion_links = []
        web_links = []

        for i in range(0, len(website_parts), 2):
            if i + 1 < len(website_parts):
                link = website_parts[i + 1]
                web_links.append(link)
                fashion_links.append({"text": f"Link {i // 2 + 1}", "href": link})
            else:
                # Handle the case where the link is missing
                web_links.append("")
                fashion_links.append({"text": f"Link {i // 2 + 1}", "href": '#'})

        # Ensure web_links has exactly 6 items
        while len(web_links) < 6:
            web_links.append("")

        # Create HTML elements for fashion links
        fashion_links_html = html.Div([
            html.Div(
                children=[
                    html.A(
                        link['text'],
                        href=link['href'],
                        target='_blank',
                        style={'color': 'white', 'text-decoration': 'none', 'margin-right': '1rem'}
                    )
                ] + [html.Button('Save Image and Link', id={'type': 'save-button', 'index': idx}, n_clicks=0, className='btn btn-success')],
                style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '20px'}
            ) for idx, link in enumerate(fashion_links)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'margin-top': '3vh'})

        if user_id:
            # Store generated links temporarily in session for saving later
            session['temp_image_urls'] = image_urls
            session['temp_web_links'] = web_links

        return image_components + [fashion_links_html]
    return []




