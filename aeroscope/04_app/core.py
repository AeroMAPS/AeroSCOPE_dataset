import pandas as pd
from dataclasses import dataclass


@dataclass
class AeroscopeDataClass:
    continental_flows: pd.DataFrame
    continental_flows_non_dir: pd.DataFrame
    conti_scatter: pd.DataFrame
    flights_df_conti: pd.DataFrame
    country_flows: pd.DataFrame
    country_fixed: pd.DataFrame
    flights_df: pd.DataFrame
