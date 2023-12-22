import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from assets import styles


def build_navbar(brand, pages):
    return dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(title, href=url)) for title, url in pages.items()
        ],
    brand=brand,
    brand_href="#",
    color="primary",
    dark=True,
)

def build_dropdown_menu(menu):
    return dcc.Dropdown(id=menu['id'], 
                        options=menu['options'], 
                        value=menu['value'],
                        style=styles.dropdown_style)

def maybe_label(menu, label_flag):
    if label_flag:
        return html.Label(children=menu['Label']),
    else:
        return

def build_dropdown_row(menus_list, label_flag=False):
    style = {'width' : '15%'}
    menus_html =[
        html.Div(style=style, children=[
            maybe_label(menu, label_flag),
            build_dropdown_menu(menu)
        ]) for menu in menus_list ]
    return menus_html

def build_button_row(buttons_list):
    style = {'width': '15%'}
    buttons_html = [
        html.Div(style=style, children = [
            html.Button(children=button['children'], 
                id=button['id'], n_clicks=0,
                style=button['style']),
        ]) for button in buttons_list
    ]
    return buttons_html

# sidebar = html.Div(
#     [
#         html.H2("Sidebar", className="display-4"),
#         html.Hr(),
#         html.P(
#             "A simple sidebar layout with navigation links", className="lead"
#         ),
#         dbc.Nav(
#             [
#                 dbc.NavLink("Home", href="/", active="exact"),
#                 dbc.NavLink("Page 1", href="/page-1", active="exact"),
#                 dbc.NavLink("Page 2", href="/page-2", active="exact"),
#             ],
#             vertical=True,
#             pills=True,
#         ),
#     ],
#     style=SIDEBAR_STYLE,
# )



# content = html.Div(id="page-content", style=CONTENT_STYLE)

