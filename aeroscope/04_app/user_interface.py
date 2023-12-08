from datetime import datetime
import ipyvuetify as v

from continental_front import ContinentalTab
from country_front import CountriesTab
from detailled_front import DetailledTab
from passenger_front import PassengerTab
from aeromaps_front import AeroMAPSTab


# Create the layout
v.theme.dark = False

v_img = v.Img(
    cover=True,
    max_width='25%',
    src="logo/aeroscope.png",
    class_='mx-auto'
)

divider = v.Divider(vertical=True)

title_layout = v.AppBar(
    app=True,
    color='white',
    children=[
        v.Spacer(),
        v.ToolbarTitle(children=[v_img]),
        v.Spacer(),
        v.Btn(icon=True,
              href='https://zenodo.org/records/10143773',
              target='_blank',
              children=[v.Icon(children=['mdi-database'])]),
        v.Btn(icon=True,
              href='https://github.com/AeroMAPS/AeroSCOPE',
              target='_blank',
              children=[v.Icon(children=['mdi-github-circle'])]),
    ]
)

footer_layout = v.Footer(class_=" text-center d-flex flex-column", style_='background-color: white;', children=[
    v.Col(
        class_="text-center mt-4",
        children=[
            f"{datetime.now().year} — ",
            v.Html(tag="strong", children=["©ISAE-SUPAERO"])
        ]
    )
])

class UserInterface(v.Card):

    def __init__(self, aeroscope_data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize_tabs(aeroscope_data)

        self.children = [
            title_layout,
            v.Spacer(),
            self.tabs_layout,
            v.Divider(vertical=False),
            footer_layout
        ]

    def initialize_tabs(self, aeroscope_data):

        continental_tab = ContinentalTab(aeroscopedataclass=aeroscope_data)
        countries_tab = CountriesTab(aeroscopedataclass=aeroscope_data)
        detailled_tab = DetailledTab(aeroscopedataclass=aeroscope_data)
        passenger_tab = PassengerTab(aeroscopedataclass=aeroscope_data)
        aeromaps_tab = AeroMAPSTab(aeroscopedataclass=aeroscope_data)

        self.tabs_layout = v.Tabs(
            fixed_tabs=True,
            background_color="#050A30",
            children=[
                v.Tab(children=['Continental Mode'], style_="color: white;", active_class="teal--text text--lighten-1"),
                v.Tab(children=['Country Mode'], style_="color: white;", active_class="teal--text text--lighten-1"),
                # Darken text color for active tab
                v.Tab(children=['Detailed Mode'], style_="color: white;", active_class="teal--text text--lighten-1"),
                # Darken text color for active tab
                v.Tab(children=['Passenger Mode'], style_="color: white;", active_class="teal--text text--lighten-1"),
                # Darken text color for active tab
                v.Tab(children=['AeroMAPS Export'], style_="color: white;", active_class="teal--text text--lighten-1"),
                # Darken text color for active tab

                v.TabItem(children=[v.Container(fluid=True, children=[continental_tab.layout])],
                          style_="background-color: white;"),
                v.TabItem(children=[v.Container(fluid=True, children=[countries_tab.layout])],
                          style_="background-color: white;"),
                v.TabItem(children=[v.Container(fluid=True, children=[detailled_tab.layout])],
                          style_="background-color: white;"),
                v.TabItem(children=[v.Container(fluid=True, children=[passenger_tab.layout])],
                          style_="background-color: white;"),
                v.TabItem(children=[v.Container(fluid=True, children=[aeromaps_tab.layout])],
                          style_="background-color: white;")
            ]
        )
