from dash import html, dcc

def get_forgot_password_layout():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Img(src='/assets/logo.jpg', style={'width': '200px', 'height': 'auto', 'display': 'block', 'marginBottom': '20px'}),
                    html.H1("Reset Your Password", style={'textAlign': 'center', 'marginBottom': '50px'}),
                    html.Div(
                        children=[
                            dcc.Input(id='reset_email', type='email', placeholder='Enter your email', autoComplete='email', style={'marginBottom': '10px'}),
                            html.Button('Send Verification Code', id='send_verification_code', n_clicks=0, style={'marginBottom': '10px'}),
                            dcc.Loading(
                                id="loading-reset-feedback",
                                type="circle",
                                children=html.Div(id='reset_feedback', style={'marginBottom': '10px'})
                            ),
                            dcc.Input(id='verification_code', type='text', placeholder='Enter verification code', style={'marginBottom': '10px'}),
                            dcc.Input(id='new_password', type='password', placeholder='Enter new password', autoComplete='new-password', style={'marginBottom': '10px'}),
                            html.Button('Reset Password', id='reset_password', n_clicks=0, style={'marginBottom': '10px'}),
                            dcc.Loading(
                                id="loading-reset-password-feedback",
                                type="circle",
                                children=html.Div(id='reset_password_feedback', style={'marginBottom': '10px'})
                            ),
                            dcc.Link('Back to login', href='/login', style={'display': 'block', 'marginBottom': '5px'}),
                        ],
                        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}
                    )
                ],
                style={'width': '100%', 'maxWidth': '400px', 'margin': '0 auto', 'padding': '20px', 'boxShadow': '0px 0px 10px #aaa'}
            )
        ],
        style={'width': '100vw', 'height': '100vh', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'flexDirection': 'column'}
    )
