from datetime import datetime, timedelta, timezone
import sys
import time

# Import functions
print("Importing functions...")
sys.path.append('include/')


import livetime
import sbnd_daqrun_spreadsheet
import plotting_macros
import redis_utilities

import matplotlib.pyplot as plt
plt.style.use('include/style.mplstyle')


# Settings
NAP_TIME = 60  # in second
RUN_PERIOD = "run2"

# Establish Redis connection
print("Establishing Redis connection...")
redis_client = redis_utilities.establish_redis_connection()

try:
    while True:
      print("Updating POT plots!")

      ## Get the current time in UTC
      current_time = datetime.now(timezone.utc)
      print(f"Current time (UTC): {current_time}")

      ## Updating livetime data
      print("Updating livetime data...")
      sbnd_daqrun_spreadsheet.update_daq_runs(RUN_PERIOD)
      livetime.extract_livetime_info(RUN_PERIOD, current_time)
    
      ## Making last week plots
      plot_end = current_time.replace(minute=0, second=0, microsecond=0)  # Round down to the nearest hour
      plot_start = plot_end - timedelta(days=7)
      print("Making last week plots for period:", plot_start, "to", plot_end)

      ## DAQ uptime
      plotting_macros.plot_weekly_livetime(plot_start, plot_end, RUN_PERIOD)
      ## POT efficiency
      plotting_macros.plot_weekly_potefficiency(plot_start, plot_end, RUN_PERIOD)

      ## Making run 2 cumulative plots
      print("Making run 2 cumulative plots...")
      plotting_macros.plot_run2_cumulative(plot_end)
      
      plotting_macros.plot_total_cumulative(plot_end, True)

      ## Pushing plot to Redis
      if redis_client is not None:
          redis_utilities.push_to_redis(redis_client)
      else:
          print("Redis client not available. Skipping push to Redis.")

      print(f"Done, waiting for {NAP_TIME} seconds")
      time.sleep(NAP_TIME)

except KeyboardInterrupt:
    print("\nScript interrupted by user...")
    sys.exit(0)