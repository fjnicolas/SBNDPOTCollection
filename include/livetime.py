import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
import pytz
import os, sys
from tqdm import tqdm

from config import DATA_DIR, DATA_CSV_DIR
from config import RUN1_START_TIME, RUN2_START_TIME
from config import DELTA_T

# Base URL for the IF Database
base = 'https://dbdata1vm.fnal.gov:9443/ifbeam/data'

def query_pot_interval(t0, t1):
    """
    Query IFDB for the number of spills and the total POT in the
    specified time interval. The time interval is specified by
    the start and end times, t0 and t1. The times should be in
    UTC.
    
    Parameters
    ----------
    t0 : datetime
        Start of the interval to query. This should be in UTC.
    t1 : datetime
        End of the interval to query. This should be in UTC.
    
    Returns
    -------
    spills : int
        Number of spills in the specified interval.
    pot : float
        Total POT in the specified interval.
    """
    central_tz = pytz.timezone('US/Central')
    # Convert to Central Time
    s0 = t0#.astimezone(tz=central_tz)
    s1 = t1#.astimezone(tz=central_tz)

    device_name = 'E:TOR875'
    url = f'{base}/data?v={device_name}&e=e,1d&t0={int(s0.timestamp())}&t1={int(s1.timestamp())}&f=csv'
    response = requests.get(url)
    
    if response.status_code != 200:
        raise RuntimeError(f'Error querying data: {response.status_code}')
 
    data = np.array([line.split(',')[-1] for line in response.text.split('\n')[1:] if line], dtype=float)
    return len(data), float(np.sum(data))

def get_livetime_interval(t0, t1, starts, ends):
    """
    Calculates the livetime for the interval determined
    by t0 and t1. The livetime is calculated by calculating
    the total overlap interval between the queried interval
    and the DAQ intervals specified by starts and ends.

    This calculation also uses IFDB to return the collected
    and delivered spills/POT for the interval.

    Parameters
    ----------
    t0 : datetime
        Start of the interval to query.
    t1 : datetime
        End of the interval to query.

    starts : list of datetime
        List of start times of the DAQ intervals.
    ends : list of datetime
        List of end times of the DAQ intervals.
    
    Returns
    -------
    livetime : float
        The livetime in seconds for the interval.
    livetime_fraction : float
        The livetime fraction for the interval.
    delivered_spills : int
        The number of spills delivered during the interval.
    collected_spills : int
        The number of spills collected during the interval.
    delivered_pot : float
        The amount of POT delivered during the interval.
    collected_pot : float
        The amount of POT collected during the interval.
    """
    # Initialize quantities to zero
    overlap = timedelta(0)
    collected_spills = 0
    collected_pot = 0

    # Loop through the starts and ends to calculate the overlap
    # with the interval t0 to t1
    for start, end in zip(starts, ends):
        if start > t1 or end < t0:
            continue
        s0 = max(t0, start)
        s1 = min(t1, end)
        overlap += s1 - s0
        query = query_pot_interval(s0, s1)
        collected_spills += query[0]
        collected_pot += query[1]
    
    # Calculate the delivered spills and POT
    query = query_pot_interval(t0, t1)
    delivered_spills = query[0]
    delivered_pot = query[1]

    # Finally, calculate the livetime and livetime fraction
    livetime = overlap.total_seconds()
    livetime_fraction = livetime / (t1 - t0).total_seconds()

    return livetime, livetime_fraction, delivered_spills, collected_spills, delivered_pot, collected_pot


def extract_livetime_info(run, plot_end, verbose=False):
    

    # Warnings for the user if the plot_start and plot_end are not aligned with the run start and end times
    if(run == 'run1'):
        plot_start = RUN1_START_TIME
    elif(run == 'run2'):
        plot_start = RUN2_START_TIME

    # Input files with the run start and end times
    startsFilePath = str(DATA_DIR) + '/starts_' + run + '.txt'
    endsFilePath = str(DATA_DIR) + '/ends_' + run + '.txt'

    # Read the run start times from `starts.txt`
    with open(startsFilePath, 'r') as f:
        lines = f.readlines()
        starts = [datetime.strptime(line.strip(), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc) for line in lines]

    # Read the run end times from `ends.txt`
    with open(endsFilePath, 'r') as f:
        lines = f.readlines()
        ends = [datetime.strptime(line.strip(), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc) if line != 'now\n' else datetime.now(timezone.utc) for line in lines]

    # Self consistency with the pre-samepled data: hour for plot_start must be multiple of DELTA_T, round down if not
    if plot_start.hour % (DELTA_T.seconds//3600) != 0:
        print(f"Warning: plot_start hour {plot_start.hour} is not a multiple of DELTA_T hours {DELTA_T.seconds//3600}, rounding down to nearest multiple.")
        plot_start = plot_start.replace(hour=(plot_start.hour // (DELTA_T.seconds//3600)) * (DELTA_T.seconds//3600), minute=0, second=0, microsecond=0)
        print(f"Rounded plot_start: {plot_start}")

    # Create ranges for the intervals
    range_starts = []
    range_ends = []
    start = plot_start
    while start < plot_end:
        end = start + DELTA_T
        range_starts.append(start)
        range_ends.append(end)
        start += DELTA_T

    # Convert to pd.Timestamp for comparison
    range_starts_ts = [pd.Timestamp(s) for s in range_starts]
    range_ends_ts   = [pd.Timestamp(e) for e in range_ends]

    # Check which intervals are already in sbnd_livetime_run2.csv
    run_csv_path = str(DATA_CSV_DIR) + "/sbnd_livetime_" + run + '.csv'
    if os.path.exists(run_csv_path):
        existing_df = pd.read_csv(run_csv_path, index_col=0)
        existing_df = existing_df.reset_index(drop=True)
        existing_df['start'] = pd.to_datetime(existing_df['start'], utc=True)
        existing_df['end']   = pd.to_datetime(existing_df['end'], utc=True)
    else:
        existing_df = pd.DataFrame()
        print("No existing ' sbnd_livetime_' + run + '.csv' found, will download all intervals.")

    print(existing_df.tail())
    # Always update the last interval, since it may be still running and the existing value may be outdated
    existing_df = existing_df[0:-1]
    print(existing_df.tail())

    # Split intervals into cached vs needs download
    cached_pairs = []
    to_download = []
    for s, e in zip(range_starts_ts, range_ends_ts):
        if not existing_df.empty:
            match = existing_df[
                (existing_df['start'] <= s) &
                (existing_df['end'] >= e)
            ]
            if not match.empty:
                cached_pairs.append((s, e))
            else:
                to_download.append((s, e))
        else:
            to_download.append((s, e))

    if(verbose):
        print(f"Found {len(cached_pairs)} intervals in cache, downloading {len(to_download)} new ones.")

    # Get the livetime data in each 'DELTA_T' interval
    new_downloaded_data = {'start': [], 'end': [], 'livetime': [],
                    'livetime_fraction': [], 'delivered_spills': [],
                    'collected_spills': [], 'delivered_pot': [],
                    'collected_pot': []}

    # Download only missing intervals
    for start, end in tqdm(to_download, total=len(to_download), desc='Processing intervals'):
        livetime = get_livetime_interval(start, end, starts, ends)
        new_downloaded_data['start'].append(start)
        new_downloaded_data['end'].append(end)
        new_downloaded_data['livetime'].append(livetime[0])
        new_downloaded_data['livetime_fraction'].append(livetime[1])
        new_downloaded_data['delivered_spills'].append(livetime[2])
        new_downloaded_data['collected_spills'].append(livetime[3])
        new_downloaded_data['delivered_pot'].append(livetime[4])
        new_downloaded_data['collected_pot'].append(livetime[5])

    # Combine cached rows for the window + newly downloaded
    new_downloaded_df = pd.DataFrame(new_downloaded_data)

    if not existing_df.empty:
        cached_df = existing_df[
            existing_df['start'].isin(range_starts_ts) &
            existing_df['end'].isin(range_ends_ts)
        ]
        new_df = pd.concat([cached_df, new_downloaded_df], ignore_index=True)
    else:
        new_df = new_downloaded_df

    new_df['start'] = pd.to_datetime(new_df['start'], utc=True)
    new_df['end']   = pd.to_datetime(new_df['end'], utc=True)
    new_df = new_df.sort_values('start').reset_index(drop=True)

    if(verbose):
        display(new_df.head(20))
        display(new_df.tail(20))
        
    new_df.to_csv(str(DATA_CSV_DIR) + '/sbnd_livetime_' + run + '.csv', index=True)

def update_run_accumulated_livetime(run):
    
    #Run 2 file
    livetime_run_df = pd.read_csv( str(DATA_CSV_DIR) + '/sbnd_livetime_' + run + '.csv', index_col=0)
    #The week of data
    livetime_week_df = pd.read_csv( str(DATA_CSV_DIR) + '/sbnd_livetime_week.csv', index_col=0)
    #Combine them
    livetime_df = pd.concat([livetime_run2_df, livetime_week_df], ignore_index=True)
    #Remove the duplicated intervals
    livetime_df  = livetime_df.drop_duplicates(
        subset=["start", "end"],  # your date columns
        keep="first"  # keeps existing, ignores new duplicates
    )
    livetime_df.to_csv(str(DATA_CSV_DIR) + '/sbnd_livetime_' + run + '.csv', index=True)