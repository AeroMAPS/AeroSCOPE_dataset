# @Time : 10/05/2022 10:56
# @Author : a.salgas
# @File : flights.py
# @Software: PyCharm

"""
This file takes data inputs and standardizes them into data classes.
Class inheritance is used to handle different possibilities between data sources
"""

# import structure libraries

from abc import ABC, abstractmethod
import pandas as pd



class FlightData(ABC):
    """
    Creator class, returning an object of flight_data type.
    """

    def __init__(self):
        self.df = None
        self.preprocessed = False
        self.datatype = 'None'
        self.n_flights_file = 0

    def load_new_file(self, relative_path: str, sample_ratio: int = 1):
        if sample_ratio != 1:
            self.df = pd.read_csv(relative_path).sample(frac=sample_ratio, random_state=6)
        else:
            self.df = pd.read_csv(relative_path)
        # In case the file is from us bts, possibility to filter on scheduled passenger flights:
        # if 'CLASS' in self.df.columns:
        #     self.df.query('`CLASS` == "F"', inplace=True)
        return 0




