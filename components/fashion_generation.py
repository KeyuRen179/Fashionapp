from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State
from flask import session
import os
import concurrent.futures
from openai import OpenAI
from database import add_user_search, add_folder, save_image, save_link

# Load environment variables and API key
openai_api_key = os.environ.get('OPENAI_API_KEY')
openai_client = OpenAI(api_key=openai_api_key)


# Function to generate a link component
def generate_link_component(link, index, is_logged_in):
    if is_logged_in:
        return html.Div([
            html.A(
                link['text'],
                href=link['href'],
                target='_blank',
                style={'color': 'white', 'text-decoration': 'none', 'margin-right': '1rem'}
            ),
            html.Br(),
            dcc.Loading(
                id={'type': 'loading-save-link-button', 'index': index},
                type='circle',
                children=html.Button(
                    'Save link',
                    id={'type': 'save-link-button', 'index': index},
                    **{'data-url': link['href']},
                    n_clicks=0,
                    className='btn btn-primary'
                )
            )
        ], style={'margin-bottom': '20px'})
    else:
        return html.Div([
            html.A(
                link['text'],
                href=link['href'],
                target='_blank',
                style={'color': 'white', 'text-decoration': 'none', 'margin-right': '1rem'}
            )
        ], style={'margin-bottom': '20px'})


# Function to generate an image component
def generate_image_component(image_url, index, is_logged_in):
    if is_logged_in:
        return html.Div([
            html.Img(src=image_url, className='img-fluid'),
            html.Br(),
            dcc.Loading(
                id={'type': 'loading-save-image-button', 'index': index},
                type="circle",
                children=html.Button(
                    'Save image to search history',
                    id={'type': 'save-image-button', 'index': index},
                    **{'data-url': image_url},
                    n_clicks=0,
                    className='btn btn-primary'
                )
            )
        ], style={'margin-bottom': '20px'})
    else:
        return html.Div([
            html.Img(src=image_url, className='img-fluid'),
            html.Br(),
            html.A(
                'Download image',
                href=image_url,
                target="_blank",
                download=f'fashion_image_{index}.jpg',
                className='btn btn-primary'
            )
        ], style={'margin-bottom': '20px'})


# Function to update fashion content
def update_fashion(poem_input, folder_name=None):
    user_id = session.get('user_id')
    folder_id = None
    if user_id and folder_name:
        folder_id = add_folder(user_id, folder_name)

    # Generate an image using OpenAI
    def generate_image(prompt, quality):
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            quality=quality,
            n=1
        )
        return response

    # Create the prompt for image generation
    prompt = f"Generate image of costume in the style of {poem_input}. Add some randomness so that you won't generate too similar images when asked twice."
    quality = "standard"

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_image, prompt, quality) for _ in range(6)]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error: {e}")

    image_components = []
    image_urls = []

    for i, response in enumerate(results):
        image_data = response.data[0]
        image_url = image_data.url
        image_component = generate_image_component(image_url, i, user_id)
        image_components.append(image_component)
        image_urls.append(image_url)

        if folder_id:
            save_image(folder_id, image_url)

    # Generate links using OpenAI
    weblinks = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user",
             "content": f"Generate 6 website links with online stores that sell clothing and fashion in the style of {poem_input}. Please output weblinks only and make sure the websites are working."}
        ]
    )
    websites = weblinks.choices[0].message.content.strip()
    website_parts = websites.split()

    fashion_links = []
    for i in range(0, len(website_parts), 2):
        link = website_parts[i + 1]
        fashion_links.append({"text": f"Link {i // 2 + 1}", "href": link})
        if folder_id:
            save_link(folder_id, link)

    fashion_links_html = html.Div([
        generate_link_component(link, i, user_id) for i, link in enumerate(fashion_links)
    ], style={'display': 'flex', 'justify-content': 'center', 'text-align': 'center', 'margin-top': '3vh'})

    fashion_website_link = html.Div(
        fashion_links_html,
        style={'display': 'flex', 'justify-content': 'center', 'text-align': 'center', 'margin-top': '3vh'}
    )

    if user_id:
        search_id = add_user_search(user_id, poem_input)
        image_components.append(dcc.Store(id='search-id', data=search_id))

    return image_components + [fashion_website_link]
