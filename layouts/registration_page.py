from dash import html, dcc

def get_layout():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H1("Registration", style={'textAlign': 'center', 'marginBottom': '30px'}),
                    dcc.Input(id='reg_email', type='email', placeholder='Email', className='mb-2', style={'marginBottom': '10px', 'width': '100%'}),
                    dcc.Input(id='reg_password', type='password', placeholder='Password', className='mb-2', style={'marginBottom': '10px', 'width': '100%'}),
                    dcc.Input(id='reg_password_confirm', type='password', placeholder='Confirm Password', className='mb-2', style={'marginBottom': '10px', 'width': '100%'}),
                    html.Button('Submit', id='submit_reg', n_clicks=0, style={'width': '100%', 'marginBottom': '20px'}),
                    dcc.Loading(
                        id="loading-reg-output",
                        type="circle",
                        children=html.Div(id='reg_output', style={'marginBottom': '20px'})
                    ),
                    dcc.Link('Have an account? Login here.', href='/login', style={'display': 'block', 'marginBottom': '5px', 'textAlign': 'center'}),
                    dcc.Link('Continue as guest', href='/fashiongeneration', style={'display': 'block', 'textAlign': 'center'}),
                ],
                style={'maxWidth': '400px', 'margin': '0 auto', 'padding': '20px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'textAlign': 'center'}
            )
        ],
        style={'width': '100vw', 'height': '100vh', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}
    )
