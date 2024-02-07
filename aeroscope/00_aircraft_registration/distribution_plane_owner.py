# @Time : 30/11/2023 11.48
# @Author : f.lutz
# @File : parse_wikipedia_registration_prefix.py
# @Software: PyCharm

import os.path as pth

import pandas as pd


def sample_plane_owner(
    aircraft_database_path: str,
    plane_code: str,
    manufacturer_icao: str = None,
    granularity: str = "country",
) -> dict:
    """
    Sample a database of plane registration and returns a dictionary with the location in which a
    plane is registered with the number of plane for each location. It can be in terms of
    countries or continent. A manufacturer name can also be provided to double check the results
    in case the plane type code is not reliable enough.

    :param aircraft_database_path: the path to the plane registration database
    :param plane_code: the type code of the plane
    :param manufacturer_icao: the ICAO code for the plane manufacturer
    :param granularity: a string indicating whether the registration should be looked at country
    level or continent level can be "country" or "continent"

    :return: a dict with the location of plane with their count
    """

    # This step takes a lot of time given the size of the .csv, maybe there is a way to
    registered_aircraft_database = pd.read_csv(aircraft_database_path, dtype=str)
    registered_aircraft_database.columns = [
        "icao24",
        "registration",
        "manufacturericao",
        "manufacturername",
        "model_os",
        "typecode",
        "serialnumber",
        "linenumber",
        "icaoaircrafttype",
        "operator_os",
        "operatorcallsign",
        "operatoricao",
        "operatoriata",
        "owner",
        "categoryDescription",
    ]

    extracted_database = registered_aircraft_database.loc[
        registered_aircraft_database["typecode"] == plane_code
    ]

    # Additional filtering if manufacturer's ICAO number is given
    if manufacturer_icao:
        extracted_database = extracted_database.loc[
            registered_aircraft_database["manufacturericao"] == manufacturer_icao
        ]

    country_of_registration_with_count = {}

    # Building the translator which will match the registration prefix to the country
    registration_database_name = "registration_database_with_continents.csv"
    registration_database_path = pth.join(
        pth.join(pth.dirname(__file__), "data"), registration_database_name
    )
    registration_database = pd.read_csv(registration_database_path, dtype=str)
    registration_database_dict = registration_database.to_dict(orient="list")
    registration_dict = dict(
        zip(
            registration_database_dict["Registration prefix"],
            registration_database_dict["Country"],
        )
    )
    countries_to_continents = dict(
        zip(
            registration_database_dict["Country"],
            registration_database_dict["Continents"],
        )
    )

    # We can now browse through the registration number of the selected aircraft
    for index, row in extracted_database.iterrows():

        # Unfortunately, there are some registration prefix which correspond to the start og
        # other registration prefix so we'll do a two time search
        matching_registration_prefixes = []

        # This is very suboptimal but I can't see another way to do it
        for key in list(registration_dict.keys()):

            if row["registration"].startswith(key):
                matching_registration_prefixes.append(key)

        longest_matching_prefix = ""

        # If more than one prefix matches, we take the longest one which works
        for matching_registration_prefix in matching_registration_prefixes:
            if len(matching_registration_prefix) > len(longest_matching_prefix):
                longest_matching_prefix = matching_registration_prefix

        # Then we add the longest matching prefix in a dict but not before checking if it is
        # already a key in which case we'll simply increment the counter
        country_name = registration_dict[longest_matching_prefix]

        if country_name in list(country_of_registration_with_count.keys()):
            country_of_registration_with_count[country_name] += 1
        else:
            country_of_registration_with_count[country_name] = 1

    if granularity == "continent":

        # Convert to continent
        continent_of_registration_with_count = {}
        for country in list(country_of_registration_with_count.keys()):

            continent = countries_to_continents[country]
            if continent in list(continent_of_registration_with_count.keys()):
                continent_of_registration_with_count[
                    continent
                ] += country_of_registration_with_count[country]

            else:
                continent_of_registration_with_count[continent] = (
                    country_of_registration_with_count[country]
                )

        return continent_of_registration_with_count

    else:

        return country_of_registration_with_count


if __name__ == "__main__":

    database_name = "aircraft-database-complete-2023-11-utf_8.csv"
    database_path = pth.join(pth.join(pth.dirname(__file__), "data"), database_name)

    # Just here for tests
    country_of_registration_with_count_k100 = sample_plane_owner(database_path, "K100")
    country_of_registration_with_count_k900 = sample_plane_owner(database_path, "KODI")

    country_of_registration_with_count_tbm_9 = sample_plane_owner(database_path, "TBM9")
