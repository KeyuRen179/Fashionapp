import dash_bootstrap_components as dbc
from dash import dcc

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


def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
