from dash import dcc, html, Input, Output, State, callback_context as ctx, dash
from app import app
import layouts.main_layout as main_layout
import layouts.registration_page as registration_page
import layouts.login_page as login_page
import os
from flask import session, redirect

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='redirect', refresh=True),  # 用于捕捉重定向请求
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
        return login_page.get_login_layout()
    elif pathname == "/history":
        if user_is_logged_in:
            return html.Div([
                html.H1('History Query Page'),
                dcc.Input(id='query-input', type='text', placeholder='Enter your query'),
                html.Button('Search', id='search-button', n_clicks=0),
                html.Div(id='query-results')
            ])
        else:
            return login_page.get_login_layout()
    elif pathname == "/reset-password":
        return get_reset_password_layout()
    else:
        return login_page.get_login_layout()

# 回调函数控制按钮显示
@app.callback(
    [Output('login-link', 'style'),
     Output('register-link', 'style'),
     Output('logout-link', 'style')],
    [Input('url', 'pathname')]
)
def update_nav_links(pathname):
    user_is_logged_in = 'user_id' in session
    if user_is_logged_in:
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'block'}, {'display': 'none'}

# 处理登出按钮点击事件
@app.callback(
    Output('redirect', 'pathname'),
    Input('logout-link', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        session.pop('user_id', None)
        return '/login'
    return dash.no_update

# 添加重置密码页面布局
def get_reset_password_layout():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H2("Reset Password", style={'textAlign': 'center', 'marginBottom': '50px'}),
                    dcc.Input(id='reset_password_email', type='email', placeholder='Enter your email',
                              style={'marginBottom': '10px'}),
                    dcc.Input(id='reset_old_password', type='password', placeholder='Enter old password',
                              style={'marginBottom': '10px'}),
                    dcc.Input(id='reset_confirm_old_password', type='password', placeholder='Confirm old password',
                              style={'marginBottom': '10px'}),
                    dcc.Input(id='reset_new_password', type='password', placeholder='Enter new password',
                              style={'marginBottom': '10px'}),
                    html.Button('Submit', id='reset_password_submit', n_clicks=0, style={'marginBottom': '10px'}),
                    html.Div(id='reset_password_feedback', style={'marginBottom': '10px'}),
                ],
                style={'width': '100%', 'maxWidth': '400px', 'margin': '0 auto', 'padding': '20px',
                       'boxShadow': '0px 0px 10px #aaa'}
            )
        ],
        style={'width': '100vw', 'height': '100vh', 'display': 'flex', 'alignItems': 'center',
               'justifyContent': 'center', 'flexDirection': 'column'}
    )

import callback

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=os.environ.get('PORT', '8000'), debug=True)
