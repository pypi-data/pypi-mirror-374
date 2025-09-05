import pandas as pd
from .station_data import arrStationList

dtf = pd.DataFrame(arrStationList)
dtf.set_index(dtf['code'], inplace=True)
dtf.drop('code', axis=1, inplace=True)


def get_stn_name(stn_code:str):
    """
    :param stn_code: Station Code
    :return: Station Name
    """
    try:
        return dtf.loc[stn_code.upper(), 'name'] or None
    except KeyError:
        return None
