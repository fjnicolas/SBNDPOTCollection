# Setup

Use the `setup.sh` script to create and activate a python virtual environment and install all the necessary libraries

# Credentials
Need to add a `redis_settings.py` file to the project with the following content
Ask a DQM expert for the connection credentials. Do not make them public in GitHub.

```
REDIS_HOST = 'sbnd-db03.fnal.gov'
REDIS_PORT = 0000
REDIS_PASSWORD = '1234556'
```

# Macros
- `main.py`: update plots ebery 4 hours and push to Redis. Run in a tmux session.
- `sbnd_pot.ipynb`:  python notebook to set custom range to the POT and DAQ uptime plots.