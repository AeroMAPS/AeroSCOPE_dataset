# @Time : 02/10/2023 10:23
# @Author : a.salgas
# @File : country_level_plots.py
# @Software: PyCharm

import plotly.express as px
import plotly.graph_objects as go

def countries_map_plot(country_flows, value_watched_ctry):
    # Create the scattergeo figure
    fig = go.Figure(

    )

    for i in range(len(country_flows)):
        fig.add_trace(
            go.Scattergeo(
                lon=[country_flows['departure_lon'][i], country_flows['arrival_lon'][i]],
                lat=[country_flows['departure_lat'][i], country_flows['arrival_lat'][i]],
                mode='lines',
                line=dict(width=country_flows[value_watched_ctry][i] / (.05 * max(country_flows[value_watched_ctry])),
                          color='#EE9B00'),
                opacity=1
            )
        )

    fig.add_trace(go.Scattergeo(
        lon=country_flows['arrival_lon'],
        lat=country_flows['arrival_lat'],
        hoverinfo='text',
        text=country_flows[value_watched_ctry],
        mode='markers',
        marker=dict(
            size=country_flows[value_watched_ctry] / (.01 * max(country_flows[value_watched_ctry])),
            color='purple',
            line=dict(width=0.5, color='white'), opacity=1
        ),
        customdata=country_flows[['departure_country_name', 'arrival_country_name']],
        hovertemplate="Flights from: %{customdata[0]}" + " to: " + "%{customdata[1]}<br>" +
                      value_watched_ctry + ": %{text:.0f}<br>" +
                      "<extra></extra>",
    ))

    fig.update_geos(showcountries=True)
    fig.update_layout(showlegend=False, height=800, title='Country pair flows of {}'.format(value_watched_ctry))
    fig.update_layout(margin=dict(l=5, r=5, t=60, b=5))  # Adjust layout margins and padding
    return fig


def countries_global_plot(country_fixed, value_watched_ctry):
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=country_fixed['departure_lon'],
        lat=country_fixed['departure_lat'],
        hoverinfo='text',
        text=country_fixed[value_watched_ctry],
        mode='markers',
        marker=dict(
            size=country_fixed[value_watched_ctry] / (.005 * max(country_fixed[value_watched_ctry])),
            color='#EE9B00',
            line=dict(width=0.5, color='white'), opacity=1
        ),
        customdata=country_fixed[['departure_country_name']],
        hovertemplate="Total departures from: %{customdata[0]}<br>" +
                      value_watched_ctry + ": %{text:.0f}<br>" +
                      "<extra></extra>",

    ))
    fig.update_geos(showcountries=True)
    fig.update_layout(showlegend=False, height=800, title='Country values for {}'.format(value_watched_ctry))
    fig.update_layout(margin=dict(l=5, r=5, t=60, b=5))  # Adjust layout margins and padding
    return fig


def countries_treemap_plot(country_flows, value_watched_ctry):
    fig = px.treemap(country_flows,
                     path=[px.Constant("Total currently selected"), 'departure_country_name', 'arrival_country_name'],
                     values=value_watched_ctry,
                     color_discrete_sequence=px.colors.qualitative.T10,
                     color='arrival_country_name',
                     title='Treemap for {}'.format(value_watched_ctry),
                     )

    fig.update_layout(margin=dict(l=5, r=5, t=60, b=5))
    fig.update_traces(
        marker=dict(cornerradius=5),
    )

    if value_watched_ctry == 'co2':
        fig.update_traces(hovertemplate='Flow=%{id}<br>CO<sub>2</sub>=%{value:.2f} (lg)')
    elif value_watched_ctry == 'ask':
        fig.update_traces(hovertemplate='Flow=%{id}<br>ASK=%{value:.2f}')
    elif value_watched_ctry == 'seats':
        fig.update_traces(hovertemplate='Flow=%{id}<br>Seats=%{value:.2f}')

    return fig


def distance_histogramm_plot_country(flights_df, value_watched_ctry):
    fig = px.histogram(
        flights_df,
        x="distance_km",
        y=value_watched_ctry,
        histfunc="sum",
        color_discrete_sequence=px.colors.qualitative.T10,
        title='Repartition of {} by flight distance'.format(value_watched_ctry),

    )

    fig.update_traces(xbins=dict(
        start=0.0,
        end=flights_df.distance_km.max(),
        size=500))

    fig.update_layout(
        # title="Histogram of CO2 Emissions by Distance and Arrival Continent",
        xaxis_title="Distance (km)",
        yaxis_title=value_watched_ctry,
        showlegend=False,
    )

    fig.update_layout(
        margin=dict(l=5, r=5, t=60, b=5),
    )

    if value_watched_ctry == 'co2':
        fig.update_traces(hovertemplate='Distance group (km)=%{x}<br>CO2 (kg)=%{y:.0f}<extra></extra>')
    elif value_watched_ctry == 'ask':
        fig.update_traces(hovertemplate='Distance group (km)=%{x}<br>ASK=%{y:.0f}<extra></extra>')
    elif value_watched_ctry == 'seats':
        fig.update_traces(hovertemplate='Distance group (km)=%{x}<br>Seats=%{y:.0f}<extra></extra>')
    return fig


def aircraft_pie(flights_df, value_watched_ctry):
    top_aircraft = flights_df.groupby('acft_icao')[value_watched_ctry].sum().nlargest(10)
    other_total = flights_df[value_watched_ctry].sum() - top_aircraft.sum()
    top_aircraft.loc['Other'] = other_total
    fig = px.pie(
        values=top_aircraft,
        names=top_aircraft.index,
        color_discrete_sequence=px.colors.qualitative.T10,
        labels={'names': 'Aircraft', 'values': value_watched_ctry},
    )
    fig.update_traces(textposition='inside')
    fig.update_layout(
        margin=dict(l=60, r=60, t=60, b=60),
        title="{} by aircraft model".format(value_watched_ctry),
        legend=dict(
            title='Aircraft type:',
        )
    )
    return fig


def aircraft_user_pie(flights_df, value_watched_ctry):
    top_airlines = flights_df.groupby('airline_iata')[value_watched_ctry].sum().nlargest(10)
    other_total = flights_df[value_watched_ctry].sum() - top_airlines.sum()
    top_airlines.loc['Other'] = other_total
    fig = px.pie(
        values=top_airlines,
        names=top_airlines.index,
        color_discrete_sequence=px.colors.qualitative.T10,
        labels={'names': 'Airline', 'values': value_watched_ctry},
    )
    fig.update_traces(textposition='inside')
    fig.update_layout(
        margin=dict(l=60, r=60, t=60, b=60),
        title="{} by aircraft airline (code)".format(value_watched_ctry),
        legend=dict(
            title='Airline IATA code:',
        )
    )
    return fig