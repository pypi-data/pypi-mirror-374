import pandas as pd
import numpy as np
from .utils import get_trains_list,get_stn_name

def get_trains_btw_stns(from_stn: str, to_stn: str, flex_stn: bool = False) -> pd.DataFrame:
    """
    :param from_stn: From Station Code
    :param to_stn: To Station Code
    :param flex_stn: If **False**, include only trains strictly between the given stations;if **True**, allow trains partially matching or passing nearby the provided stations.
    """
    from_station = f'{get_stn_name(from_stn.upper())} - {from_stn.upper()}'
    to_station = f'{get_stn_name(to_stn.upper())} - {to_stn.upper()}'

    dtf = pd.DataFrame(get_trains_list(from_station,to_station))
    dtf.replace('',np.nan,inplace=True)
    if not flex_stn:
        dtf = dtf[(dtf['src_code'] == from_stn.upper()) & (dtf['dest_code'] == to_stn.upper())]
    return dtf