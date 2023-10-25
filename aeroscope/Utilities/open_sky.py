# @Time : 07/06/2022 14:36
# @Author : a.salgas
# @File : open_sky.py
# @Software: PyCharm
import os

from flights import *
from datetime import datetime
from geopy import distance

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class FlightOpenSky(FlightData):

    def __init__(self):
        super().__init__()
        self.datatype = 'opensky'

    def preprocess_data(self, keep_time=False):
        """
        Preprocessing the data to prepare analyses.
        The resulting table fields are:
        Departure and arrival airport IATA Code(Three letter)
        Departure and arrival airport Coordinates
        Aircraft ICAO Code
        Airline IATA Code
        Number of flights per data entry
        Additional fields: pax, freight and mail carried for us BTS
        Columns not yet relevant for this framework are deleted
        """
        # Checking if data waws well loaded into the dataframe

        # selecting only the columns interesting us
        self.df = self.df.loc[:, ['day', 'destination', 'origin', 'icao24']]
        # Drop flight with no known origin and destination (mandatory because of our computation method)
        size_before_drops = len(self.df.index)
        self.df.dropna(subset=["destination", "origin"], inplace=True)
        size_after_drops = len(self.df.index)
        print(
            '{}% of flights deleted after removing '
            'flights with no origin and destination. {} Flights in the dataset'.format(
                (size_before_drops - size_after_drops) / size_before_drops * 100, size_after_drops))
        # Converting dates to a suitable format
        self.df['year'] = self.df.apply(lambda x: get_month_year(x['day'])[0], axis=1)
        self.df['month'] = self.df.apply(lambda x: get_month_year(x['day'])[1], axis=1)

        # Opensky only gets aircraft transponder code, not its registration.
        # Hopefully, it can be merged with an aircraft database, for example opensky aircraft database
        data_path = os.path.join(root_path, '03_routes_schedule', 'data/open_sky/aircraftdata.csv')
        ac_ref = pd.read_csv(data_path, sep=',')
        # Drop aircraft where there is no clean typecode (50% approx...)
        ac_ref = ac_ref.dropna(subset=['typecode'])
        # Even if each aircraft has a unique icao24 code, some are present several times in the database.
        # Duplicates are therefore dropped before merging the dataframes.
        ac_ref = ac_ref[['icao24', 'typecode', 'operator_jz', 'operatoricao']].drop_duplicates(subset='icao24',
                                                                                               keep='last')
        self.df = pd.merge(self.df, ac_ref, left_on='icao24', right_on='icao24', how='left', sort=False)

        # we use ailine ICAO code, but it is named IATA in the following for compatibility reasons
        self.df.rename(columns={"operatoricao": "airline_iata",
                                "typecode": "aircraft_type"}, inplace=True)
        self.df.aircraft_type = self.df.aircraft_type.replace("ZZZZ", "zzz")
        self.df.aircraft_type.fillna('zzz', inplace=True)
        self.df.airline_iata.fillna('ZZZ', inplace=True)

        # # Counting flight per aircraft type /route/airline each month
        if keep_time:
            self.df = self.df.groupby(
                ['airline_iata', 'origin', 'destination', 'aircraft_type', 'month', 'year'],
                as_index=False, dropna=False).size()
        else:
            # allows to significantly reduce the size of the data by eliminating the temporal variables
            #         by aggregating whole dataframe values
            self.df = self.df.groupby(
                ['airline_iata', 'origin', 'destination', 'aircraft_type'],
                as_index=False, dropna=False).size()

        self.df.rename(columns={"size": "n_flights"}, inplace=True)
        print(
            'Size of df after_grouping: {}; number of flights: {}'.format(len(self.df.index), self.df.n_flights.sum()))

        data_path = os.path.join(root_path, '03_routes_schedule', 'data/open_sky/aircraft_classification.csv')

        ac_cla = pd.read_csv(data_path, sep=';')
        self.df = self.df.merge(ac_cla, left_on='aircraft_type', right_on='aircraft_osky', how='left')
        self.df.drop(columns=['aircraft_osky'], inplace=True)

        self.df.acft_icao.fillna('zzz', inplace=True)
        self.df.acft_class.fillna('OTHER', inplace=True)
        self.df.seymour_proxy.fillna('zzz', inplace=True)

        print('Size of df after ac info: {}; number of flights {}'.format(len(self.df.index), self.df.n_flights.sum()))

        # similarly, we merge an airport database to have info on airport iata designator, and gps coordinates.
        # All major airports have IATA designator.
        data_path = os.path.join(root_path, '03_routes_schedule', 'data/ourairports.csv')
        arpt_ref = pd.read_csv(data_path, sep=';', keep_default_na=False, na_values='')

        self.df = self.df.merge(arpt_ref[['ident', 'iata_code', 'longitude_deg',
                                          'latitude_deg', 'iso_country', 'continent']], left_on='origin',
                                right_on='ident', how='left', sort=False)
        self.df.rename(columns={'longitude_deg': 'origin_lon', 'latitude_deg': 'origin_lat',
                                'iso_country': 'origin_country', 'continent': "origin_continent",
                                "iata_code": "origin_iata"}, inplace=True)

        self.df = self.df.merge(arpt_ref[['ident', 'iata_code', 'longitude_deg',
                                          'latitude_deg', 'iso_country', 'continent']], left_on='destination',
                                right_on='ident', how='left', sort=False)
        self.df.rename(columns={'destination': 'dest', 'longitude_deg': 'dest_lon', 'latitude_deg': 'dest_lat',
                                'iso_country': 'dest_country', 'continent': "dest_continent", "iata_code": "dest_iata"},
                       inplace=True)
        self.df.drop(
            columns=['ident_x', 'ident_y'], inplace=True)

        # Some airports have ICAO codes problems => for instance, Bale-Mulhouse (LFSB) flights are sometimes assigned
        # to LSZM, due to the international status of the airport (French-Swiss) However, LSZM is now associated to
        # another swiss airport. In this case matching gps ident (unique, LSZM not attributed) with opensky airport
        # code could result in nan being returned. Some flights are therefore not plotted.
        # If destination and origin coordinates are not known, it creates fake (0 miles flights).
        # We therefore chose to delete them.
        self.df.dropna(subset=["dest_lon", "origin_lon", "dest_lat", "origin_lat"], inplace=True)

        print(
            'Size of df after arpt info: {}, number of flights: {}'.format(len(self.df.index), self.df.n_flights.sum()))

        # compute great circle distance in km if airports coordinates are known
        self.df.loc[:, "distance_km"] = self.df.apply(
            lambda x: distance.distance((float(x.origin_lat), float(x.origin_lon)),
                                        (float(x.dest_lat), float(x.dest_lon))).km if not (
                        pd.isna(x.origin_lat) or pd.isna(x.origin_lon)
                        or pd.isna(x.dest_lon) or pd.isna(x.dest_lat)) else 0, axis=1)

        # Keeping track of how many aircraft-miles with no aircraft known/with aircraft not handeld by seymour/with
        # no proxi affected

        self.n_flights_file = size_before_drops
        self.preprocessed = True

    def sum_data(self):
        """
        This function allows to significantly reduce the size of the data by eliminating the temporal variables
        by aggregating dataframe value on all other indexes
        Update: Not used anymore
        """
        self.df = self.df.groupby(
            ['airline_iata', 'origin_iata', 'dest_iata', 'acft_icao'],
            as_index=False).agg({'n_flights': 'sum'})




def get_month_year(osky_date):
    """
    :param osky_date: date as formatted by the opensky file: "2019-01-01 00:00:00+00:00"
    :return: {'year':2019, 'month':01}
    """
    date = datetime.strptime(osky_date.split(" ", 1)[0], '%Y-%m-%d')
    return date.year, date.month
