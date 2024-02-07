# @Time : 30/11/2023 9:56
# @Author : f.lutz
# @File : parse_wikipedia_registration_prefix.py
# @Software: PyCharm

import os.path as pth

import requests

from bs4 import BeautifulSoup

import re

import pandas as pd

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_aircraft_registration_prefixes"

if __name__ == "__main__":

    res = requests.get(WIKI_URL).text
    soup = BeautifulSoup(res, "html.parser")

    all_items = soup.find("table", class_="wikitable")
    treated_line = 0

    # Because there are multiple possible prefix for each country, we will have the registration
    # prefix as the key for this dict and the country name as value
    combination_dict = {}

    previous_country_name = "Hyrule"  # See comments ^^'

    for items in all_items.find_all("tr")[1::1]:

        data = items.find_all(["th", "td"])

        country_container = data[0].a

        # If the "container is None it means it is a sub-cell of a table where one country can have
        # multiple registration prefix so we take the previous country name which we change only
        # when we have valid name
        if country_container is None:
            country_name = previous_country_name
        else:
            # The first line of the table will never have a sub-cell so we are ensured that we
            # will go through this if first but as a precaution. We can also sometimes encounter
            # the string that starts and end with brackets which we will weed out
            if country_container.text[0] == "[" and country_container.text[-1] == "]":
                country_name = previous_country_name
            else:
                country_name = country_container.text.replace("\n", "")
                previous_country_name = country_name

        # We now treat the data for registration prefix, we will curate it by removing the string
        # "  plus national emblem" everytime it appears as well as citation brackets. Also if we
        # are in the case where there are sub-cells for a same country, as the country name is
        # None there is only two columns in the data object

        if len(data) == 3:
            raw_registration_prefix = data[1].text
        else:
            raw_registration_prefix = data[0].text

        raw_registration_prefix = raw_registration_prefix.replace(
            " plus national emblem", ""
        )

        # We'll use ReGex to remove everything inside brackets from the string
        pattern = r"\[.*?\]"
        curated_registration_prefix = re.sub(pattern, "", raw_registration_prefix)

        # Most simple case, there is only one registration in the cell, this can be checked by
        # seeing whether or not there is a space in the cell
        if len(curated_registration_prefix.split(" ")) == 1:
            combination_dict[curated_registration_prefix.replace("\n", "")] = (
                country_name
            )
            treated_line += 1

        else:
            # Now we treat the case where there are multiple prefix separated with commas
            if len(curated_registration_prefix.split(",")) != 1:
                for prefix in curated_registration_prefix.split(","):
                    combination_dict[prefix.replace(" ", "").replace("\n", "")] = (
                        country_name
                    )
                treated_line += 1

            # There are also cases where we have a "See [Country]" which we will not treat as
            # they are often geographical region of other country. We will keep track of them
            # however for our sanity checks

            elif curated_registration_prefix.startswith("See "):
                treated_line += 1

            elif len(curated_registration_prefix.split(" - ")) != 1:
                combination_dict[curated_registration_prefix.split(" - ")[0]] = (
                    country_name
                )
                treated_line += 1

    # We now have a curated dictionary where each entry is a prefix which we can associate a
    # country to. We'll save that to a .csv for future use. Before that however, we'll do a sanity
    # check

    non_unique_country_list = list(combination_dict.values())
    unique_country_list = list(set(non_unique_country_list))

    # Should be 241
    print(treated_line)

    csv_path = pth.join(
        pth.join(pth.dirname(__file__), "data"), "registration_database.csv"
    )

    data = {
        "Registration prefix": list(combination_dict.keys()),
        "Country": list(combination_dict.values()),
    }
    data_as_pd = pd.DataFrame.from_dict(data)
    data_as_pd.to_csv(csv_path)
