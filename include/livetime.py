import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz

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
    #t0 - timedelta(hours=5)
    s1 = t1#.astimezone(tz=central_tz)
    #t1 - timedelta(hours=5)

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