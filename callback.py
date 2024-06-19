import string
from random import random
from dash.dependencies import Input, Output, State, ALL
from dash import html, dcc, callback_context, dash
from flask import session
from app import app
from components.fashion_generation import update_fashion
from database import register_user, validate_login, verify_code, store_verification_code, reset_user_password, \
    send_verification_email, get_user_searches, get_search_history_images, get_search_history_weblinks, \
    clear_user_search, save_image, save_link, delete_user_search, delete_image, delete_link, \
    get_folder_images, get_folder_weblinks, delete_folder_image, delete_folder_link

# 用户注册回调
@app.callback(
    [Output('reg_output', 'children'),
     Output('redirect-trigger', 'children', allow_duplicate=True)],
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
            return html.Div(f"Registration failed: {str(e)}", className="alert alert-danger"), dash.no_update
    return dash.no_update, dash.no_update

# 用户登录回调
@app.callback(
    [Output('login_feedback', 'children'),
     Output('redirect-trigger', 'children', allow_duplicate=True)],
    [Input('login_submit', 'n_clicks')],
    [State('login_email', 'value'), State('login_password', 'value')],
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password):
    if n_clicks > 0:
        user_id = validate_login(email, password)
        if user_id:
            session['user_id'] = user_id
            return [html.Div("Login successful!", className="alert alert-success"), '/fashiongeneration']
        else:
            return [html.Div("Invalid credentials.", className="alert alert-danger"), dash.no_update]
    return [dash.no_update, dash.no_update]

# 显示用户搜索历史
def display_search_history(user_id):
    searches = get_user_searches(user_id)
    if searches:
        search_history_items = []
        for search in searches:
            search_history_items.append(
                html.Div(
                    [
                        html.Button(
                            f"{search[1]}",
                            id={'type': 'search-item', 'index': search[0]},
                            n_clicks=0,
                            style={'display': 'inline-block', 'margin': '5px'}
                        ),
                        html.Button(
                            "Delete",
                            id={'type': 'delete-search-item', 'index': search[0]},
                            n_clicks=0,
                            style={
                                'display': 'inline-block',
                                'margin': '5px',
                                'fontSize': '12px',
                                'padding': '5px 10px',
                                'backgroundColor': '#f0f0f0',
                                'color': '#666',
                                'border': 'none',
                                'borderRadius': '3px',
                                'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
                            }
                        )
                    ],
                    style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}
                )
            )
        clear_search_button = html.Button(
            "Clear All Search History",
            id={'type': 'clear-search-history', 'index': 0},
            n_clicks=0,
            style={'display': 'block', 'margin': '5px', 'background-color': 'red', 'color': 'white'}
        )
        return search_history_items + [clear_search_button]
    return "Oops, no search history..."

# 加载页面时显示用户搜索历史
@app.callback(
    Output('search_history', 'children', allow_duplicate=True),
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def load_search_history(pathname):
    if pathname == '/fashiongeneration':
        user_id = session.get('user_id')
        if user_id:
            return display_search_history(user_id)
    return dash.no_update

# 生成诗句（时装内容）回调
@app.callback(
    Output('poem_output', 'children'),
    Output('poem_loading', 'children'),
    [Input('submit_poem', 'n_clicks')],
    [State('poem_input', 'value'), State({'type': 'search-keyword', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def handle_poem_generation(n_clicks, poem_input, additional_keywords):
    if n_clicks > 0:
        # 合并主关键词和附加关键词
        keywords = [poem_input] + [kw for kw in additional_keywords if kw]
        combined_input = ', '.join(keywords)
        # 调用生成函数
        result = update_fashion(combined_input)
        return result, dash.no_update
    return dash.no_update, dash.no_update

# 生成搜索历史记录回调
@app.callback(
    Output('search_history', 'children', allow_duplicate=True),
    [Input('submit_poem', 'n_clicks'),
     Input({'type': 'clear-search-history', 'index': ALL}, 'n_clicks'),
     Input({'type': 'delete-search-item', 'index': ALL}, 'n_clicks')],
    [State({'type': 'search-item', 'index': ALL}, 'id')],
    prevent_initial_call=True
)
def handle_generate_search_history(sub_n_clicks, clear_n_clicks, delete_n_clicks, ids):
    user_id = session.get('user_id')
    if user_id:
        triggered = callback_context.triggered[0]['prop_id'].split('.')[0]
        if 'clear-search-history' in triggered:
            clear_user_search(user_id)
        elif 'delete-search-item' in triggered:
            search_id = eval(triggered)['index']
            delete_user_search(search_id)

        searches = get_user_searches(user_id)
        if searches:
            search_history_items = []
            for search in searches:
                search_history_items.append(
                    html.Div(
                        [
                            html.Button(
                                f"{search[1]}",
                                id={'type': 'search-item', 'index': search[0]},
                                n_clicks=0,
                                style={'display': 'inline-block', 'margin': '5px'}
                            ),
                            html.Button(
                                "Delete",
                                id={'type': 'delete-search-item', 'index': search[0]},
                                n_clicks=0,
                                style={
                                    'display': 'inline-block',
                                    'margin': '5px',
                                    'fontSize': '12px',
                                    'padding': '5px 10px',
                                    'backgroundColor': '#f0f0f0',
                                    'color': '#666',
                                    'border': 'none',
                                    'borderRadius': '3px',
                                    'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
                                }
                            )
                        ],
                        style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}
                    )
                )
            clear_search_button = html.Button(
                "Clear All Search History",
                id={'type': 'clear-search-history', 'index': 0},
                n_clicks=0,
                style={'display': 'block', 'margin': '5px', 'background-color': 'red', 'color': 'white'}
            )
            return search_history_items + [clear_search_button]
        return "Oops, no search history..."
    return dash.no_update

# 加载搜索结果回调
@app.callback(
    Output('poem_output', 'children', allow_duplicate=True),
    Output('poem_loading', 'children', allow_duplicate=True),
    [Input({'type': 'search-item', 'index': ALL}, 'n_clicks')],
    [State({'type': 'search-item', 'index': ALL}, 'id')],
    prevent_initial_call=True
)
def load_search_results(n_clicks, ids):
    if all(n == 0 for n in n_clicks):
        return dash.no_update, dash.no_update
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    search_id = eval(button_id)['index']

    image_urls = get_search_history_images(search_id)
    web_links = get_search_history_weblinks(search_id)

    image_components = []
    for i, (image_id, image_url) in enumerate(image_urls):
        image_component = html.Div([
            html.Img(src=image_url, className='img-fluid'),
            html.Br(),
            html.A('Download image', href=image_url, target="_blank", download=f'fashion_image_{i}.jpg', className='btn btn-primary'),
            html.Button(
                "Delete",
                id={'type': 'delete-image-button', 'index': image_id, 'search_id': search_id},
                n_clicks=0,
                style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'fontSize': '12px',
                    'padding': '5px 10px',
                    'backgroundColor': '#f0f0f0',
                    'color': '#666',
                    'border': 'none',
                    'borderRadius': '3px',
                    'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
                }
            )
        ], style={'margin-bottom': '20px'})
        image_components.append(image_component)

    fashion_links = [{"text": f"Link {i+1}", "href": link[1], "id": link[0]} for i, link in enumerate(web_links)]

    fashion_links_html = html.Div([
        html.Div([
            html.A(
                link['text'],
                href=link['href'],
                target='_blank',
                style={'color': 'white', 'text-decoration': 'none', 'margin-right': '1rem'}
            ),
            html.Button(
                "Delete",
                id={'type': 'delete-link-button', 'index': link['id'], 'search_id': search_id},
                n_clicks=0,
                style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'fontSize': '12px',
                    'padding': '5px 10px',
                    'backgroundColor': '#f0f0f0',
                    'color': '#666',
                    'border': 'none',
                    'borderRadius': '3px',
                    'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
                }
            )
        ]) for link in fashion_links
    ], style={'display': 'flex', 'justify-content': 'center', 'text-align': 'center', 'margin-top': '3vh'})

    fashion_website_link = html.Div(
        fashion_links_html,
        style={'display': 'flex', 'justify-content': 'center', 'text-align': 'center', 'margin-top': '3vh'}
    )

    return image_components + [fashion_website_link], dash.no_update

# 删除链接按钮回调
@app.callback(
    Output('search_history', 'children', allow_duplicate=True),
    [Input({'type': 'delete-link-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'delete-link-button', 'index': ALL}, 'id')],
    prevent_initial_call=True
)
def delete_link_callback(n_clicks, ids):
    if any(n > 0 for n in n_clicks):
        ctx = callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        index = eval(button_id)['index']
        search_id = eval(button_id)['search_id']
        delete_link(index)
        return load_search_results([1], [search_id])
    return dash.no_update

# 在特定文件夹内删除图像按钮回调
@app.callback(
    Output('folder_content', 'children', allow_duplicate=True),
    [Input({'type': 'delete-folder-image-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'delete-folder-image-button', 'index': ALL}, 'id')],
    prevent_initial_call=True
)
def delete_folder_image_callback(n_clicks, ids):
    ctx = callback_context
    if ctx.triggered and any(n > 0 for n in n_clicks):
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        image_id = eval(button_id)['index']
        folder_id = eval(button_id)['folder_id']
        delete_folder_image(image_id)
        return load_folder_content(folder_id)
    return dash.no_update

# 在特定文件夹内删除链接按钮回调
@app.callback(
    Output('folder_content', 'children', allow_duplicate=True),
    [Input({'type': 'delete-folder-link-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'delete-folder-link-button', 'index': ALL}, 'id')],
    prevent_initial_call=True
)
def delete_folder_link_callback(n_clicks, ids):
    ctx = callback_context
    if ctx.triggered and any(n > 0 for n in n_clicks):
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        link_id = eval(button_id)['index']
        folder_id = eval(button_id)['folder_id']
        delete_folder_link(link_id)
        return load_folder_content(folder_id)
    return dash.no_update

# 保存图像按钮回调
@app.callback(
    Output({'type': 'save-image-button', 'index': ALL}, 'children'),
    Output({'type': 'save-image-button', 'index': ALL}, 'disabled'),
    Input({'type': 'save-image-button', 'index': ALL}, 'n_clicks'),
    State('search-id', 'data'),
    State({'type': 'save-image-button', 'index': ALL}, 'id'),
    State({'type': 'save-image-button', 'index': ALL}, 'data-url'),
    prevent_initial_call=True
)
def save_image_callback(n_clicks, search_id, button_ids, image_urls):
    if not any(n_clicks):
        return dash.no_update, dash.no_update

    results = ["Save image"] * len(button_ids)
    disabled_states = [False] * len(button_ids)

    for i, (n_click, button_id, image_url) in enumerate(zip(n_clicks, button_ids, image_urls)):
        if n_click:
            try:
                save_image(search_id, image_url)
                results[i] = "Saved"
                disabled_states[i] = True
            except Exception as e:
                results[i] = f"Failed: {str(e)}"
                disabled_states[i] = False

    return results, disabled_states

# 保存链接按钮回调
@app.callback(
    Output({'type': 'save-link-button', 'index': ALL}, 'children'),
    Output({'type': 'save-link-button', 'index': ALL}, 'disabled'),
    Input({'type': 'save-link-button', 'index': ALL}, 'n_clicks'),
    State('search-id', 'data'),
    State({'type': 'save-link-button', 'index': ALL}, 'id'),
    State({'type': 'save-link-button', 'index': ALL}, 'data-url'),
    prevent_initial_call=True
)
def save_link_callback(n_clicks, search_id, button_ids, link_urls):
    if not any(n_clicks):
        return dash.no_update, dash.no_update

    results = ["Save link"] * len(button_ids)
    disabled_states = [False] * len(button_ids)

    for i, (n_click, button_id, link_url) in enumerate(zip(n_clicks, button_ids, link_urls)):
        if n_click:
            try:
                save_link(search_id, link_url)
                results[i] = "Saved"
                disabled_states[i] = True
            except Exception as e:
                results[i] = f"Failed: {str(e)}"
                disabled_states[i] = False

    return results, disabled_states

# 发送验证码回调
@app.callback(
    Output('reset_feedback', 'children'),
    [Input('send_verification_code', 'n_clicks')],
    [State('reset_email', 'value')],
    prevent_initial_call=True
)
def send_verification_code_callback(n_clicks, email):
    if n_clicks > 0:
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        store_verification_code(email, verification_code)
        send_verification_email(email, verification_code)
        return html.Div("Verification code sent to your email.", className="alert alert-success")
    return dash.no_update

# 重置密码回调
@app.callback(
    Output('reset_password_feedback', 'children'),
    [Input('reset_password', 'n_clicks')],
    [State('reset_email', 'value'),
     State('verification_code', 'value'),
     State('new_password', 'value')],
    prevent_initial_call=True
)
def reset_password_callback(n_clicks, email, code, new_password):
    if n_clicks > 0:
        if verify_code(email, code):
            reset_user_password(email, new_password)
            return html.Div("Password reset successfully.", className="alert alert-success")
        else:
            return html.Div("Invalid verification code.", className="alert alert-danger")
    return dash.no_update

# 添加附加关键词输入框回调
@app.callback(
    Output('additional_keywords_container', 'children'),
    Input('add_keyword', 'n_clicks'),
    State('additional_keywords_container', 'children'),
    prevent_initial_call=True
)
def add_additional_keyword_input(n_clicks, children):
    new_input = dcc.Input(
        id={'type': 'search-keyword', 'index': n_clicks},
        type='text',
        placeholder=f'Enter additional keyword {n_clicks + 1}',
        style={'marginRight': '10px', 'width': '30%'}
    )
    children.append(new_input)
    return children

def load_folder_content(folder_id):
    """加载特定文件夹内的内容，包括图片和链接"""
    images = get_folder_images(folder_id)
    links = get_folder_weblinks(folder_id)

    image_components = []
    for i, (image_id, image_url) in enumerate(images):
        image_component = html.Div([
            html.Img(src=image_url, className='img-fluid'),
            html.Br(),
            html.A('Download image', href=image_url, target="_blank", download=f'folder_image_{i}.jpg', className='btn btn-primary'),
            html.Button(
                "Delete",
                id={'type': 'delete-folder-image-button', 'index': image_id, 'folder_id': folder_id},
                n_clicks=0,
                style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'fontSize': '12px',
                    'padding': '5px 10px',
                    'backgroundColor': '#f0f0f0',
                    'color': '#666',
                    'border': 'none',
                    'borderRadius': '3px',
                    'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
                }
            )
        ], style={'margin-bottom': '20px'})
        image_components.append(image_component)

    link_components = []
    for i, (link_id, link) in enumerate(links):
        link_component = html.Div([
            html.A(
                f"Link {i+1}",
                href=link,
                target='_blank',
                style={'color': 'white', 'text-decoration': 'none', 'margin-right': '1rem'}
            ),
            html.Button(
                "Delete",
                id={'type': 'delete-folder-link-button', 'index': link_id, 'folder_id': folder_id},
                n_clicks=0,
                style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'fontSize': '12px',
                    'padding': '5px 10px',
                    'backgroundColor': '#f0f0f0',
                    'color': '#666',
                    'border': 'none',
                    'borderRadius': '3px',
                    'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
                }
            )
        ], style={'margin-bottom': '20px'})
        link_components.append(link_component)

    return image_components + link_components
