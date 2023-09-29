# @Time : 07/06/2022 11:50
# @Author : a.salgas
# @File : us_bts.py
# @Software: PyCharm
import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from flights import *
import pandas as pd


class FlightBts(FlightData):
    """
    This class handle US BTS files noted as "T100"
    """

    def __init__(self):
        super().__init__()
        self.datatype = 'BTS'

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
        assert self.df is not None
        # BTS does not provide aircraft designator as specified by ICAO; a correspondence table is used
        # Get the absolute path of the root directory

        # Define the relative path to the data file
        data_path = os.path.join(root_path, '03_routes_schedule', 'data/BTS/aircraft_codes_icao_joined.csv')

        ac_ref = pd.read_csv(data_path, sep=';')
        ac_ref.fillna('zzz',inplace=True)

        print('Size of df at begining {}'.format(len(self.df.index)))
        self.df.columns = self.df.columns.str.lower()
        self.df = pd.merge(self.df, ac_ref, left_on='aircraft_type', right_on='Code', how='left', sort=False)
        print('Size of df after adding aircraft info {}, number of flights: {}'.format(len(self.df.index), self.df.departures_performed.sum()))
        # standardizing column names
        self.df.rename(columns={"unique_carrier": "airline_iata",
                                "ICAO_Code": "acft_icao", "YEAR": "year", "MONTH": "month",
                                "departures_performed": "n_flights", 'class':'flight_class'}, inplace=True)

        size_after_drops = sum(self.df.n_flights)
        # dropping unnecessary columns (standardisation procedure)

        self.df = self.df.loc[:, ['airline_iata', 'unique_carrier_entity', 'origin', 'dest', 'flight_class','aircraft_type', 'acft_icao','acft_class','seymour_proxy', 'year', 'month',
                                  'n_flights', 'seats', 'passengers', 'freight', 'mail', 'distance', 'air_time', 'ramp_to_ramp', 'quarter']]

        if not keep_time:
            self.sum_data()

        print('Size of df after grouping {}; number flights {}'.format(len(self.df.index),self.df.n_flights.sum()))
        # computing average payload per flight. and converting payload from lbs to kg
        # Payload provided originally is a global aircraft type average and not specific to each relation
        self.df["mail"]=self.df["mail"]/2.2
        self.df['freight']=self.df['freight']/2.2

        self.df["total_payload"] = (self.df["mail"] + self.df["freight"]
                                    + self.df["passengers"] * 100) / \
                                   self.df["n_flights"]


        # convert miles to km (point to point flight distance is reported in nm)
        self.df['distance_km'] = self.df['distance'] * 1.609344

        # computing an additional time spend by aircraft on teh ground before and after the flight (aircraft type idependent time)
        self.df['block_time_supl'] = self.df['ramp_to_ramp'] - self.df['air_time']

        # adding airport GPS coordinates
        self.add_airports_coord()

        self.df.aircraft_type = self.df.aircraft_type.replace("999", "zzz")

        self.df['rpk']= self.df["distance_km"]*self.df["passengers"]

        self.n_flights_file=size_after_drops
        print('Size of df after airports process {}; number flights {}'.format(len(self.df.index), self.df.n_flights.sum()))

        self.preprocessed = True

    def sum_data(self):
        """
        This function allows to significantly reduce the size of the data by eliminating the temporal variables
        by aggregating dataframe value on all other indexes
        """
        self.df = self.df.groupby(['airline_iata','unique_carrier_entity', 'origin', 'dest', 'flight_class', 'aircraft_type', 'acft_icao','acft_class','seymour_proxy'],
                                  as_index=False).agg({'n_flights': 'sum', 'seats': 'sum',
                                                       'passengers': 'sum', 'freight': 'sum',
                                                       'mail': 'sum', 'distance': 'first', 'air_time': 'sum', 'ramp_to_ramp':'sum'})



    def add_airports_coord(self, ):
        """
        Add Airport GPS coordinates to a standard flight data object, previously standardized.
jupyter lab        """
        airport_path = os.path.join(root_path, '03_routes_schedule', 'data/BTS/T_MASTER_CORD_unique.csv')
        airports_df = pd.read_csv(airport_path, keep_default_na=False,sep=';')

        continents_path = os.path.join(root_path, '03_routes_schedule', 'data/country_codes.csv')
        continents=pd.read_csv(continents_path,keep_default_na=False)
        airports_df = airports_df.merge(continents[['Continent_Code','Two_Letter_Country_Code']],
                                        right_on='Two_Letter_Country_Code', left_on='AIRPORT_COUNTRY_CODE_ISO',how='left')
        airports_df.rename(columns={'AIRPORT':'bts_code','AIRPORT_COUNTRY_CODE_ISO':'iso_country','Continent_Code':'continent'},inplace=True)
        airports_df.drop(columns=['Two_Letter_Country_Code'],inplace=True)

        self.df = self.df.merge(airports_df[['bts_code', 'LONGITUDE',
                                             'LATITUDE', 'iso_country', 'continent']], left_on='origin',
                                right_on='bts_code', how='left')
        self.df.rename(columns={'LONGITUDE': 'origin_lon', 'LATITUDE': 'origin_lat',
                                'iso_country': 'origin_country', 'continent': "origin_continent"}, inplace=True)
        self.df = self.df.merge(airports_df[['bts_code', 'LONGITUDE', 'LATITUDE',
                                             'iso_country', 'continent']], left_on='dest',
                                right_on='bts_code', how='left')
        self.df.rename(columns={'LONGITUDE': 'dest_lon', 'LATITUDE': 'dest_lat',
                                'iso_country': 'dest_country', 'continent': "dest_continent"}, inplace=True)
        self.df.drop(
            columns=['bts_code_x', 'bts_code_y'], inplace=True)
        self.df['origin_iata'] = self.df['origin']
        self.df['dest_iata'] = self.df['dest']
        return 0


