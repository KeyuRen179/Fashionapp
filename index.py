import os

from dash import dcc, html, Input, Output, ClientsideFunction
from flask import session

import layouts.login_page as login_page
import layouts.main_layout as main_layout
import layouts.registration_page as registration_page
from app import app

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
    elif pathname == "/history":  # New history query page path
        return html.Div([
            html.H1('History Query Page'),
            dcc.Input(id='query-input', type='text', placeholder='Enter your query'),
            html.Button('Search', id='search-button', n_clicks=0),
            html.Div(id='query-results')
        ])
    else:
        # Redirect to login page if pathname is not recognized
        return login_page.get_login_layout()


@app.callback(
    Output('query-results', 'children'),
    Input('search-button', 'n_clicks'),
    Input('query-input', 'value')
)
def update_query_results(n_clicks, query):
    if n_clicks > 0 and query:
        # 查询数据库或执行其他操作获取结果，这里假设返回一个简单的示例结果
        return html.Div([
            html.H2(f'Results for query: {query}'),
            html.Ul([
                html.Li('Result 1'),
                html.Li('Result 2'),
                html.Li('Result 3')
            ])
        ])
    return html.Div()


# Client-side callback for redirection
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='redirect'
    ),
    Output('url', 'pathname'),
    [Input('redirect-trigger', 'children')]
)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=os.environ.get('PORT', '8000'), debug=True)
