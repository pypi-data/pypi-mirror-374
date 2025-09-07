import pandas as pd
import numpy as np
from datetime import datetime
from .utils import get_trains_list, get_stn_name, get_train_live_status_data
from .train_data import arrTrainList
import json

def get_trains_btw_stns(from_stn: str, to_stn: str, flex_stn: bool = False) -> pd.DataFrame:
    """
    :param from_stn: From Station Code
    :param to_stn: To Station Code
    :param flex_stn: If **False**, include only trains strictly between the given stations;if **True**, allow trains partially matching or passing nearby the provided stations.
    """
    from_station = f'{get_stn_name(from_stn.upper())} - {from_stn.upper()}'
    to_station = f'{get_stn_name(to_stn.upper())} - {to_stn.upper()}'
    dtf = pd.DataFrame(get_trains_list(from_station, to_station))
    dtf.replace('', np.nan, inplace=True)
    if not flex_stn:
        dtf = dtf[(dtf['src_code'] == from_stn.upper()) & (dtf['dest_code'] == to_stn.upper())]
    return dtf


def get_train_name(train_no) -> str:
    """
    :param train_no: 5 digit train number
    """
    try:
        train_lists = []
        for item in arrTrainList:
            clean = item.strip(" ").split('-', 1)
            clean[1] = clean[1].strip(' ')
            train_lists.append(clean)
        dtf = pd.DataFrame(train_lists)
        dtf.set_index(dtf[0], inplace=True)
        dtf.index.name = 'train_no'
        dtf.drop(0, axis=1, inplace=True)
        dtf.rename(columns={1: 'train_name'}, inplace=True)

        return dtf.loc[str(train_no), 'train_name'] or None
    except Exception as e:
        print(e)
        return ""


def get_train_live_status(train_no, date: str, run_df: bool = False) -> dict:
    """
    :param train_no: 5 digit train number.
    :param date: Start date of the train. *(dd-mm-yyyy)*
    :param run_df: Set True to get **DataFrame** of full running.
    """
    req_date = datetime.strptime(date,'%d-%m-%Y').day
    cur_date = datetime.now().day
    date_difference = cur_date-req_date
    date_string = ''
    if date_difference < 0:
        date_string = f'{date_difference}daysafter'
    elif date_difference > 1:
        date_string = f"{date_difference}daysago"
    elif date_difference == 1:
        date_string = "yesterday"
    elif date_difference == -1:
        date_string = 'tomorrow'

    url = f'https://trainstatus.info/running-status/{str(train_no)}-{date_string}'
    status_list = get_train_live_status_data(url)
    status_dict = {'status':status_list[0],'running':None}
    if run_df:
        dtf = pd.DataFrame(status_list[1])
        dtf.replace('',np.nan,inplace=True)
        dtf.replace('--',np.nan,inplace=True)
        status_dict['running'] = dtf

    return status_dict
