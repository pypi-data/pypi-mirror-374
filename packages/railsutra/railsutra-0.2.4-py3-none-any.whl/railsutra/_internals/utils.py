import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import json
from .station_data import arrStationList

def get_stn_name(stn_code:str):
    """
    :param stn_code: Station Code
    :return: Station Name
    """
    try:
        dtf = pd.DataFrame(arrStationList)
        dtf.set_index(dtf['code'], inplace=True)
        dtf.drop('code', axis=1, inplace=True)
        return dtf.loc[stn_code.upper(), 'name'] or None
    except KeyError:
        return None

def get_trains_list(from_stn: str, to_stn: str) -> list:
    def parse_train_text(text: str) -> dict:
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # 1st line → Train number + name
        first_line = lines[0]
        match = re.match(r"(\d+)\s+(.*)", first_line)
        train_no = match.group(1).strip() if match else ""
        train_name = match.group(2).strip() if match else ""

        # 2nd line → Days running + type
        second_line = lines[1] if len(lines) > 1 else ""
        if "|" in second_line:
            days_running, train_type = [x.strip() for x in second_line.split("|", 1)]
        else:
            days_running, train_type = second_line, ""

        # Remaining lines → source, duration/classes, destination
        src_time, src_station, src_code = "", "", ""
        dest_time, dest_station, dest_code = "", "", ""
        duration, classes = "", ""

        # Identify blocks by regex
        for line in lines[2:]:
            # Source or Destination line → starts with time
            time_match = re.match(r"(\d{2}:\d{2})(.+?)([A-Z]{2,4})$", line)
            if time_match:
                t, station, code = time_match.groups()
                if not src_time:  # First match → source
                    src_time, src_station, src_code = t, station.strip(), code
                else:  # Second match → destination
                    dest_time, dest_station, dest_code = t, station.strip(), code

            # Duration + Classes
            elif "Hrs." in line:
                dur_match = re.search(r"--(\d{2}:\d{2}) Hrs.--", line)
                if dur_match:
                    duration = dur_match.group(1)
                # Classes (remove hrs part)
                cls = re.sub(r"--.*?--", "", line).strip()
                if cls:
                    classes = cls

        return {
            "train_no": train_no,
            "train_name": train_name,
            "service_days": days_running,
            "train_type": train_type,
            "src_time": src_time,
            "src_station": src_station,
            "src_code": src_code,
            "dest_time": dest_time,
            "dest_station": dest_station,
            "dest_code": dest_code,
            "duration": duration,
            "classes": classes
        }

    try:
        url = 'https://enquiry.indianrail.gov.in/mntes/q?opt=TrainsBetweenStation&subOpt=tbs'
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/117.0 Mobile Safari/604.1",
        ]
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Referer": "https://enquiry.indianrail.gov.in/mntes/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        session = requests.Session()
        request_data = {
            "lan": 'en',
            "jFromStationInput": from_stn,
            "jToStationInput": to_stn
        }
        response = session.post(url, headers=headers, data=request_data)

        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        table_data = tables[1].find_all('td')
        trains_list = []

        for data in table_data:
            trains_list.append(parse_train_text(data.text))

        return trains_list
    except:
        return []


def get_trains_live_stn(stn_code: str) -> list:
    def clean_text(s: str) -> str:
        s = s.replace("\u00a0", " ").replace("\r", " ").replace("\t", " ")
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    def parse_train_row(tr):
        tds = tr.find_all("td")
        if not tds or len(tds) < 5:
            return None  # skip invalid rows

        # --- Train Basic Info ---
        train_info_raw = tds[1].get_text(" ", strip=True)
        parts = train_info_raw.split("|")
        train_no = parts[0].strip()
        train_name = parts[1].split("(")[0].strip() if len(parts) > 1 else ""

        # train type and route (inside <font>)
        train_type = ""
        route = ""
        font_tag = tds[1].find("font")
        if font_tag:
            type_parts = font_tag.get_text(" ", strip=True).split(")")
            if len(type_parts) >= 1:
                route = type_parts[0].replace("(", "").strip()
            if len(type_parts) >= 2:
                train_type = type_parts[1].strip()

        # --- Arrival Info ---
        arrival_info = tds[2].get_text(" ", strip=True).replace("\xa0", " ")
        if "Source" in arrival_info:
            arrival = {"expected": np.nan, "status": "Source", "scheduled": np.nan}
        else:
            arr_parts = arrival_info.split()
            arrival = {
                "expected": arr_parts[0] if arr_parts else np.nan,
                "status": arr_parts[1] if len(arr_parts) > 1 else np.nan,
                "scheduled": arr_parts[-1] if arr_parts else np.nan
            }

        # --- Departure Info ---
        departure_info = tds[3].get_text(" ", strip=True).replace("\xa0", " ")
        if "Destination" in departure_info:
            departure = {"expected": np.nan, "status": "Destination", "scheduled": np.nan}
        else:
            dep_parts = departure_info.split()
            departure = {
                "expected": dep_parts[0] if dep_parts else np.nan,
                "status": dep_parts[1] if len(dep_parts) > 1 else np.nan,
                "scheduled": dep_parts[-1] if dep_parts else np.nan
            }

        # --- Platform Info ---
        platform = tds[4].get_text(" ", strip=True).split()[0].replace("*", "") if tds[4].get_text(
            strip=True) else np.nan

        return {
            "train_no": train_no,
            "train_name": train_name,
            "route": route,
            "arrival": arrival,
            "departure": departure,
            "platform": platform
        }

    def parse_all_trains():
        rows = soup.find_all("tr")
        trains = []
        for tr in rows:
            parsed = parse_train_row(tr)
            if parsed:
                trains.append(parsed)
        return trains
    try:
        url = "https://enquiry.indianrail.gov.in/mntes/q?opt=LiveStation&subOpt=show"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://enquiry.indianrail.gov.in/mntes/",
        }
        payload = {
            "lan": "en",
            "jFromStationInput": f"{get_stn_name(stn_code.upper())} - {stn_code.upper()}",
            "jToStationInput": "",
            "nHr": "8",
            "appLang": "en",
            "jStnName": "",
            "jStation": ""
        }

        session = requests.Session()
        response = session.post(url, headers=headers, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        trains = parse_all_trains()
        return trains

    except Exception as e:
        print("Error:", e)
        return []

def get_train_live_status_data(url: str) -> list:
    try:
        response = requests.post(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        status = soup.find_all('section')[1].find('div').text
        table_rows = soup.find('table').find('tbody').find_all('tr')
        status_lst = [status]
        status_list = []
        for row in table_rows:
            table_data = row.find_all('td')
            if len(table_data) < 7:
                continue
            exp_data = {'stn_name': table_data[1].text, 'sch_arr': table_data[2].text, 'sch_dep': table_data[3].text,
                        'exp_arr_time': table_data[4].text.replace(table_data[5].text, '', 1).split(',')[0]}

            arr_info = table_data[4].text.replace(table_data[5].text, "", 1).split(',')
            if len(arr_info) < 2:
                exp_data['exp_arr_dt'] = ''
                exp_data['arr_delay'] = ''
            else:
                arr_date = arr_info[1].strip(' ').split(" ")
                exp_data['exp_arr_dt'] = arr_date[0] + ' ' + arr_date[1]
                if '-' not in arr_date[2]:
                    exp_data['arr_delay'] = ''
                else:
                    match = re.search(r'(-?\d+:\d+)|(-?\d+)(?=m)', arr_date[2])
                    if match:
                        arr_delay = match.group(0).replace('-', '')
                        exp_data['arr_delay'] = arr_delay

            dep_info = table_data[5].text.split(",")
            exp_data['exp_dep_time'] = dep_info[0]
            if len(dep_info) < 2:
                exp_data['exp_dep_dt'] = ''
                exp_data['dep_delay'] = ''
            else:
                dep_date = dep_info[1].strip(' ').split(' ')
                exp_data['exp_dep_dt'] = dep_date[0] + ' ' + dep_date[1]
                if '-' not in dep_date[2]:
                    exp_data['dep_delay'] = ''
                else:
                    match = re.search(r'(-?\d+:\d+)|(-?\d+)(?=m)', dep_date[2])
                    if match:
                        dep_delay = match.group(0).replace('-', '')
                        exp_data['dep_delay'] = dep_delay

            status_list.append(exp_data)
        status_lst.append(status_list)
        return status_lst
    except Exception as e:
        print(e)
        return []
    # there are some rows which are non-sense like ad-sense between the rows of table, we need to make sure that we don't parse them
