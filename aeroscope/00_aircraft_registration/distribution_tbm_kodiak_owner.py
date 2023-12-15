# @Time : 30/11/2023 11.48
# @Author : f.lutz
# @File : parse_wikipedia_registration_prefix.py
# @Software: PyCharm

import copy
import os.path as pth

import pandas as pd

import plotly.graph_objects as go

from distribution_plane_owner import sample_plane_owner


def concatenate_dict(dict_1, dict_2):

    merged_dict = copy.deepcopy(dict_2)

    for dict_1_key in list(dict_1.keys()):
        if dict_1_key in list(dict_2.keys()):
            merged_dict[dict_1_key] += dict_1[dict_1_key]
        else:
            merged_dict[dict_1_key] = dict_1[dict_1_key]

    return merged_dict


def convert_dict_to_dataframe(dict_to_convert: dict):

    list_of_list = []

    for dict_key in list(dict_to_convert.keys()):
        list_of_list.append([dict_key, dict_to_convert[dict_key]])

    dataframe = pd.DataFrame(list_of_list, columns=["Country", "Number of aircraft"])

    return dataframe


if __name__ == "__main__":

    database_name = "aircraft-database-complete-2023-11-utf_8.csv"
    database_path = pth.join(pth.join(pth.dirname(__file__), "data"), database_name)

    # Get value for both variants of Kodiak
    country_of_registration_with_count_k100 = sample_plane_owner(database_path, "K100")
    country_of_registration_with_count_k900 = sample_plane_owner(database_path, "KODI")

    country_of_registration_with_count_k = concatenate_dict(
        country_of_registration_with_count_k100, country_of_registration_with_count_k900
    )

    # Get value for all variants of the TBM 900
    country_of_registration_with_count_tbm_9 = sample_plane_owner(database_path, "TBM9")

    # We should make sure that both dictionary have the same country list since we will plot both
    # on the same graph
    for country_tbm in list(country_of_registration_with_count_tbm_9.keys()):
        if country_tbm not in list(country_of_registration_with_count_k.keys()):
            country_of_registration_with_count_k[country_tbm] = 0

    for country_k in list(country_of_registration_with_count_k.keys()):
        if country_k not in list(country_of_registration_with_count_tbm_9.keys()):
            country_of_registration_with_count_tbm_9[country_k] = 0

    # Country level plot

    # Sort the dict so that the same countries are in the same order
    country_of_registration_with_count_k = dict(
        sorted(country_of_registration_with_count_k.items())
    )
    country_of_registration_with_count_tbm_9 = dict(
        sorted(country_of_registration_with_count_tbm_9.items())
    )

    fig_combined = go.Figure()
    fig_combined.add_trace(
        go.Bar(
            x=list(country_of_registration_with_count_tbm_9.keys()),
            y=list(country_of_registration_with_count_tbm_9.values()),
            marker_color="crimson",
            name="TBM 900",
        )
    )
    fig_combined.add_trace(
        go.Bar(
            x=list(country_of_registration_with_count_k.keys()),
            y=list(country_of_registration_with_count_k.values()),
            base=0,
            marker_color="lightslategrey",
            name="Kodiak number",
        )
    )

    fig_combined.update_layout(
        xaxis={"categoryorder": "total descending"},
        title="Number of aircraft and variants registered in each country",
    )
    fig_combined.update_layout(title_x=0.5)
    # fig_combined.show()

    # Continent level plot

    # Get value for both variants of Kodiak
    continent_of_registration_with_count_k100 = sample_plane_owner(
        database_path, "K100", granularity="continent"
    )
    continent_of_registration_with_count_k900 = sample_plane_owner(
        database_path, "KODI", granularity="continent"
    )

    continent_of_registration_with_count_k = concatenate_dict(
        continent_of_registration_with_count_k100,
        continent_of_registration_with_count_k900,
    )

    # Get value for all variants of the TBM 900
    continent_of_registration_with_count_tbm_9 = sample_plane_owner(
        database_path, "TBM9", granularity="continent"
    )

    # We should make sure that both dictionary have the same continent list since we will plot both
    # on the same graph
    for continent_tbm in list(continent_of_registration_with_count_tbm_9.keys()):
        if continent_tbm not in list(continent_of_registration_with_count_k.keys()):
            continent_of_registration_with_count_k[continent_tbm] = 0

    for continent_k in list(continent_of_registration_with_count_k.keys()):
        if continent_k not in list(continent_of_registration_with_count_tbm_9.keys()):
            continent_of_registration_with_count_tbm_9[continent_k] = 0

    continent_list = list(continent_of_registration_with_count_tbm_9.keys())
    # Displaying results as a geomMap

    coord_geo_center_continent = {
        "South America": [-8.7832, -55.4915],
        "Europe": [48.5734053, 7.7521113],
        "Africa": [9.70, 21.0],
        "North America": [43.000, -100.00],
        "Oceania": [-25.2744, 133.7751],
        "Asia": [34.0479, 100.6197],
    }

    fig_geo = go.Figure()

    for continent in continent_list:
        if (
            continent_of_registration_with_count_tbm_9[continent]
            > continent_of_registration_with_count_k[continent]
        ):
            fig_geo.add_trace(
                go.Scattergeo(
                    lat=[coord_geo_center_continent[continent][0]],
                    lon=[coord_geo_center_continent[continent][1]],
                    mode="markers",
                    marker=dict(
                        color="Crimson",
                        size=continent_of_registration_with_count_tbm_9[continent],
                    ),
                    opacity=0.75,
                    showlegend=False,
                    name="TBM 900 " + continent,
                )
            )
            fig_geo.add_trace(
                go.Scattergeo(
                    lat=[coord_geo_center_continent[continent][0]],
                    lon=[coord_geo_center_continent[continent][1]],
                    mode="markers",
                    marker=dict(
                        color="LightSlateGrey",
                        size=continent_of_registration_with_count_k[continent],
                    ),
                    opacity=0.75,
                    showlegend=False,
                    name="Kodiak " + continent,
                )
            )
        else:
            fig_geo.add_trace(
                go.Scattergeo(
                    lat=[coord_geo_center_continent[continent][0]],
                    lon=[coord_geo_center_continent[continent][1]],
                    mode="markers",
                    marker=dict(
                        color="LightSlateGrey",
                        size=continent_of_registration_with_count_k[continent],
                    ),
                    opacity=0.75,
                    showlegend=False,
                    name="Kodiak " + continent,
                )
            )
            fig_geo.add_trace(
                go.Scattergeo(
                    lat=[coord_geo_center_continent[continent][0]],
                    lon=[coord_geo_center_continent[continent][1]],
                    mode="markers",
                    marker=dict(
                        color="Crimson",
                        size=continent_of_registration_with_count_tbm_9[continent],
                    ),
                    opacity=0.75,
                    showlegend=False,
                    name="TBM 900 " + continent,
                )
            )

    # Add dummy figure for the legend
    fig_geo.add_trace(
        go.Scattergeo(
            lon=[None],
            lat=[None],
            mode="markers",
            marker=dict(
                color="LightSlateGrey",
                size=50,
            ),
            opacity=0.75,
            showlegend=True,
            name="Kodiak 100 and Kodiak 900",
        )
    )
    fig_geo.add_trace(
        go.Scattergeo(
            lon=[None],
            lat=[None],
            mode="markers",
            marker=dict(
                color="Crimson",
                size=50,
            ),
            opacity=0.75,
            showlegend=True,
            name="TBM900 and variants",
        )
    )

    fig_geo.update_layout(
        title="Registration of DAHER aircraft by continent",
        showlegend=True,
    )
    fig_geo.update_layout(title_x=0.5)
    fig_geo.update_layout(
        margin=dict(l=5, r=5, t=60, b=5),
        legend=dict(
            yanchor="bottom",
            y=0.03,
            xanchor="left",
            x=0.08,
            bgcolor="rgba(220, 220, 220, 0.7)",
        ),
    )
    # fig_geo.show()
