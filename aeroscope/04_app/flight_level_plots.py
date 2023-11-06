# @Time : 02/10/2023 10:31
# @Author : a.salgas
# @File : flight_level_plots.py
# @Software: PyCharm


import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns 
import matplotlib;pyplot as plt
import random

def flights_map_plot(flights_gpb_df, value_watched_flights):
    # Create the scattergeo figure
    fig = go.Figure()

    meanwidth = flights_gpb_df[value_watched_flights].mean()

    for i in range(len(flights_gpb_df)):
        fig.add_trace(
            go.Scattergeo(
                lon=[flights_gpb_df['departure_lon'][i], flights_gpb_df['arrival_lon'][i]],
                lat=[flights_gpb_df['departure_lat'][i], flights_gpb_df['arrival_lat'][i]],
                mode='lines',
                line=dict(width=flights_gpb_df[value_watched_flights][i] / (1.5*meanwidth), color="#023047"),
                opacity=0.8
            )
        )

    # group by airport

    airport_df = flights_gpb_df.groupby('iata_arrival').agg({
        'co2': 'sum',
        'ask': 'sum',
        'seats': 'sum',
        'arrival_lon': 'first',
        'arrival_lat': 'first'}).reset_index()

    fig.add_trace(go.Scattergeo(
        lon=airport_df['arrival_lon'],
        lat=airport_df['arrival_lat'],
        hoverinfo='text',
        text=airport_df[value_watched_flights],
        mode='markers',
        marker=dict(
            size=airport_df[value_watched_flights] / (.01 * airport_df[value_watched_flights].mean()),
            color='#ffb703',
            sizemode='area',
            opacity=0.8,
            line=dict(width=0.5, color='black'),
        ),
        customdata=airport_df['iata_arrival'],
        hovertemplate="Flights to: " + "%{customdata}<br>" +
                      value_watched_flights + ": %{text:.0f}<br>" +
                      "<extra></extra>",

    ))

    fig.update_geos(showcountries=True)
    fig.update_layout(showlegend=False, height=800, title='Route values for {}'.format(value_watched_flights))
    fig.update_layout(margin=dict(l=5, r=5, t=60, b=5))  # Adjust layout margins and padding
    return fig


def flights_treemap_plot(flights_df, value_watched_flights):
    fig = px.treemap(flights_df,
                     path=[px.Constant("Total currently selected"), 'iata_departure', 'iata_arrival', 'airline_iata',
                           'acft_icao'],
                     values=value_watched_flights,
                     color_discrete_sequence=px.colors.qualitative.T10,
                     title='Treemap for {}'.format(value_watched_flights))

    fig.update_layout(margin=dict(l=5, r=5, t=60, b=5))
    fig.update_traces(
        marker=dict(cornerradius=5),
    )

    if value_watched_flights == 'co2':
        fig.update_traces(hovertemplate='Flow=%{id}<br>CO<sub>2</sub>=%{value:.2f} (lg)')
    elif value_watched_flights == 'ask':
        fig.update_traces(hovertemplate='Flow=%{id}<br>ASK=%{value:.2f}')
    elif value_watched_flights == 'seats':
        fig.update_traces(hovertemplate='Flow=%{id}<br>Seats=%{value:.2f}')

    return fig


def distance_histogramm_plot_flights(flights_df, value_watched_flights):
    fig = px.histogram(
        flights_df,
        x="distance_km",
        y=value_watched_flights,
        histfunc="sum",
        color_discrete_sequence=px.colors.qualitative.T10,
        title='Repartition of {} by flight distance'.format(value_watched_flights),

    )

    fig.update_layout(
        # title="Histogram of CO2 Emissions by Distance and Arrival Continent",
        xaxis_title="Distance (km)",
        yaxis_title=value_watched_flights,
        showlegend=True,
    )

    fig.update_traces(xbins=dict(
        start=0.0,
        end=flights_df.distance_km.max(),
        size=500))

    fig.update_layout(
        margin=dict(l=5, r=5, t=60, b=5),
    )

    if value_watched_flights == 'co2':
        fig.update_traces(hovertemplate='Distance group (km)=%{x}<br>CO2 (kg)=%{y:.0f}<extra></extra>')
    elif value_watched_flights == 'ask':
        fig.update_traces(hovertemplate='Distance group (km)=%{x}<br>ASK=%{y:.0f}<extra></extra>')
    elif value_watched_flights == 'seats':
        fig.update_traces(hovertemplate='Distance group (km)=%{x}<br>Seats=%{y:.0f}<extra></extra>')
    return fig


def distance_ecdf_plot_flights(flights_df):
    sns.set_style("darkgrid")
    # Create a new figure with a single subplot
    fig, ax = plt.subplots(figsize=(5,5))
    sns.ecdfplot(flights_df, x='distance_km', weights='seats', label='Seats',stat='percent', ax=ax)
    sns.ecdfplot(flights_df, x='distance_km', weights='ask', label= 'ASK', stat='percent',ax=ax)
    sns.ecdfplot(flights_df, x='distance_km', weights='co2', label= '$\mathregular{CO_2}$',stat='percent', ax=ax)
    
    ax.legend()

    # Set the title, x-axis label, and y-axis label
    ax.set_title("Metrics cumulative distribution vs flight distance")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Cumulative distribution (%)")

    return fig

def distance_kdeplot_flight(flights_df):
    sns.set_style("darkgrid")
    
    # Create a new figure with a single subplot
    fig, ax = plt.subplots(figsize=(5,5))
    # sns.histplot(flights_df, x='distance_km', weights='seats',bins=30, hue='acft_class', multiple='fill', edgecolor='None',ax=ax)
    sns.kdeplot(flights_df, 
                x='distance_km', 
                weights='seats', 
                hue='acft_class', 
                multiple='fill', 
                bw_adjust=1.5, 
                clip=(0, None), 
                edgecolor='None', 
                ax=ax)

    def formatter(x, pos):
        del pos
        return str(round(x*100))
    ax.yaxis.set_major_formatter(formatter)
    ax.set_title("Aircraft class used vs flight distance")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Aircraft class distribution (%)")
    
def distance_kdeplot_dom_int_flight(flights_df):
    # Create a new figure with a single subplot
    fig, ax = plt.subplots(figsize=(5,5))
    # sns.histplot(flights_df, x='distance_km', weights='seats',bins=30, hue='acft_class', multiple='fill', edgecolor='None',ax=ax)
    sns.kdeplot(flights_df, 
                x='distance_km', 
                weights='seats', 
                hue='domestic', 
                multiple='fill', 
                bw_adjust=1, 
                clip=(0, None), 
                edgecolor='None', 
                ax=ax)

    def formatter(x, pos):
        del pos
        return str(round(x*100))
    ax.yaxis.set_major_formatter(formatter)
    # Set the title, x-axis label, and y-axis label

    ax.legend(title='Flight Type', labels=['Domestic', 'International'])
    ax.set_title("Flight type vs flight distance")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Flight type distribution (%)")
    return fig



def aircraft_pie_flights(flights_df, value_watched_flights):
    top_aircraft = flights_df.groupby('acft_icao')[value_watched_flights].sum().nlargest(10)
    other_total = flights_df[value_watched_flights].sum() - top_aircraft.sum()
    top_aircraft.loc['Other'] = other_total
    fig = px.pie(
        values=top_aircraft,
        names=top_aircraft.index,
        color_discrete_sequence=px.colors.qualitative.T10,
        labels={'names': 'Aircraft', 'values': value_watched_flights},
    )
    fig.update_traces(textposition='inside')
    fig.update_layout(
        margin=dict(l=60, r=60, t=60, b=60),
        title="{} by aircraft model".format(value_watched_flights),
        legend=dict(
            title='Aircraft type:',
        )
    )
    return fig


def aircraft_user_pie_flights(flights_df, value_watched_flights):
    
    
    
    
    top_airlines = flights_df.groupby('airline_iata')[value_watched_flights].sum().nlargest(10)
    other_total = flights_df[value_watched_flights].sum() - top_airlines.sum()
    top_airlines.loc['Other'] = other_total
    fig = px.pie(
        values=top_airlines,
        names=top_airlines.index,
        color_discrete_sequence=px.colors.qualitative.T10,
        labels={'names': 'Airline', 'values': value_watched_flights},
    )
    fig.update_traces(textposition='inside')
    fig.update_layout(
        margin=dict(l=60, r=60, t=60, b=60),
        title="{} by airline".format(value_watched_flights),
        legend=dict(
            title='Aircraft type:',
        )
    )
    return fig
