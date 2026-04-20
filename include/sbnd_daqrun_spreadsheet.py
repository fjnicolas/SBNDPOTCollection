import gdown
import pandas as pd
import sys
sys.path.append('../')
from config import DATA_DIR

# SBND DAQ runs - Run 2
gspread_url = "https://docs.google.com/spreadsheets/d/1LfNJ11Bbob8WQSgDakEVNZQ-OBHmskYqF0NADQM9kJM/edit?gid=1379562188#gid=1379562188"

def update_daq_runs(run_period, verbose=False):

    # output_path is in  'PosixPath' format, convert it to string
    output_path = str(DATA_DIR)

    # Download the file from Google Drive
    output_path_xlsx = output_path + '/download_DAQRuns.xlsx'
    if(verbose):
        print("Downloading DAQ runs spreadsheet to:", output_path_xlsx)
    gdown.download(gspread_url, output_path_xlsx, quiet=False)#, fuzzy=True)

    # Select the appropriate URL based on the run period
    if run_period == "run1":
        sheetName = "DAQ Runs (Run 1)"
    elif run_period == "run2":
        sheetName = "DAQ Runs"
    else:
        raise ValueError("Invalid run period. Please choose 'Run 1' or 'Run 2'.")

    # Read the downloaded Excel file, skipping the first 3 rows
    df = pd.read_excel(output_path_xlsx, skiprows=[0, 2], sheet_name=sheetName)

    # Get only the first 3 columns
    df = df.iloc[:, :3]
    if(verbose):
        print(df.head())
        print(df.tail())

    # Remove bad rows
    df = df[df['Run'].notna() & df['Start time'].notna()]

    # If the end time contains 'Running', replace it with a string "now"
    df['End time'] = df['End time'].apply(lambda x: "now" if isinstance(x, str) and 'Running' in x else x)

    # Save dataframe to runNums, starts, ends _run* txt files
    df.to_csv(output_path+'/runNums_'+run_period+'.txt', columns=[df.columns[0]], index=False, header=False)
    df.to_csv(output_path+'/starts_'+run_period+'.txt', columns=[df.columns[1]], index=False, header=False)
    df.to_csv(output_path+'/ends_'+run_period+'.txt', columns=[df.columns[2]], index=False, header=False)
    if(verbose):
        print(f"Saved run numbers to {output_path+'/runNums_'+run_period+'.txt'}")
        print(f"Saved start times to {output_path+'/starts_'+run_period+'.txt'}")
        print(f"Saved end times to {output_path+'/ends_'+run_period+'.txt'}")