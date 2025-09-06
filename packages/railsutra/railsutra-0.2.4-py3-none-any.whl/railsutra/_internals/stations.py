import pandas as pd
import numpy as np
from .utils import get_trains_live_stn

def get_live_stn(stn_code: str) -> pd.DataFrame:
    try:
        trains = get_trains_live_stn(stn_code)
        dtf = pd.DataFrame(
            columns=['train_no', 'train_name', 'src', 'dest', 'sch_arr', 'exp_arr', 'arr_delay', 'sch_dep', 'exp_dep',
                     'dep_delay', 'pf'])

        for train in trains:
            route_split = train['route'].split('-')
            dtf.loc[len(dtf)] = [train['train_no'], train['train_name'], route_split[0], route_split[1],
                                 train['arrival']['scheduled'], train['arrival']['expected'],
                                 train['arrival']['status'], train['departure']['scheduled'],
                                 train['departure']['expected'], train['departure']['status'], train['platform']]

        dtf['arr_delay'].replace('On', np.nan, inplace=True)
        dtf['exp_arr'] = dtf['exp_arr'].str.replace('*', '')
        dtf['arr_delay'] = dtf['arr_delay'].apply(lambda x: x if '-' not in str(x) else np.nan)
        dtf['dep_delay'] = dtf['dep_delay'].apply(lambda x: x if '-' not in str(x) else np.nan)
        dtf['exp_dep'] = dtf['exp_dep'].str.replace('*', '')
        dtf['dep_delay'].replace('Destination', np.nan, inplace=True)
        dtf['dep_delay'].replace('On', np.nan, inplace=True)
        dtf['pf'] = dtf['pf'].apply(lambda x: x if str(x).isdigit() else np.nan)
        return dtf
    except Exception as e:
        return pd.DataFrame()
