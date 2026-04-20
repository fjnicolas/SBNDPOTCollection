import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator, HourLocator
import matplotlib.dates as mdates

from zoneinfo import ZoneInfo
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

from config import DATA_DIR, DATA_CSV_DIR, PLOT_DIR
from config import DATA_DIR, DATA_CSV_DIR
from config import RUN1_START_TIME, RUN2_START_TIME
from config import DELTA_T

def plot_weekly_livetime(plot_start, plot_end, run_period):

    # Read the livetime CSV file for the specified run period
    livetime_df = pd.read_csv(str(DATA_CSV_DIR)+'/sbnd_livetime_'+run_period+'.csv')

    # convert to datetime
    livetime_df['start'] = pd.to_datetime(livetime_df['start'])
    livetime_df['end'] = pd.to_datetime(livetime_df['end'])

    # Reduce the dataframe to only the rows that overlap with the plot range
    mask = (livetime_df['start'] < plot_end) & (livetime_df['end'] > plot_start)
    livetime_df = livetime_df[mask].reset_index(drop=True)

    # Figure creation
    figure = plt.figure(figsize=(12, 5))
    ax = figure.add_subplot()

    # Plot the livetime fraction
    diff = livetime_df['end'] - livetime_df['start']
    centers = livetime_df['start'] + diff / 2
    ax.errorbar(centers,
                100*livetime_df['livetime_fraction'],
                xerr=diff / 2,
                fmt='o',
                label='Livetime fraction',
                markersize=3)
    ax.set_xlabel('Date [UTC]')
    ax.set_ylabel('DAQ Livetime [%]')

    # Only show the x-axis label every day and rotate the labels
    # Set major ticks to be every day
    ax.xaxis.set_major_locator(DayLocator(interval=1))
    ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='center')

    # Set minor ticks to be every 6 hours
    ax.xaxis.set_minor_locator(HourLocator(interval=6))
    plt.setp(ax.xaxis.get_minorticklabels(), rotation=45, ha='center')

    # Set axis limits
    ax.set_xlim(plot_start, plot_end)
    ax.set_ylim(0, 120)
    ax.axhline(100, color='black', linestyle='--', label='100% Livetime')

    # Add a legend, but add statistics showing the average livetime fraction
    h, l = ax.get_legend_handles_labels()
    avg_livetime = np.mean(livetime_df['livetime_fraction'])

    # Add the average livetime to the legend, but with a "blank" handle
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Average Livetime: {avg_livetime:.1%}')
    ax.legend(h, l)
    _ = ax.set_title('SBND DAQ Livetime')

    # Add top right corner: run period and month range
    date_label = ""
    if run_period == "run1": date_label = "Run 1"
    elif run_period == "run2": date_label = "Run 2"
    month_range = plot_start.strftime('%b. %-d') + " - " + plot_end.strftime('%b. %-d, %Y')
    date_label = date_label + " (" + month_range + ")"
    ax.text(x=ax.get_xlim()[1], y=1.07*ax.get_ylim()[1], s=date_label, fontsize=11, color='#d67a11', ha='right', va='top')

    # Add timestamp with minute-level precision to the bottom right corner
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    deltaX = 0.1*(ax.get_xlim()[1] - ax.get_xlim()[0])
    ax.text(x=ax.get_xlim()[0] + deltaX, y=1.04*ax.get_ylim()[1], s=timestamp, fontsize=8, color='#d67a11', ha='right', va='top')

    # Save the figure
    figure.savefig(str(PLOT_DIR) + '/daq_weekly_livetime.png', dpi=1000, bbox_inches='tight')
    figure.savefig(str(PLOT_DIR) + '/daq_weekly_livetime.pdf', dpi=1000, bbox_inches='tight')
    figure.savefig(str(PLOT_DIR) + '/daq_weekly_livetime_light.png', dpi=75, bbox_inches='tight')


def plot_weekly_potefficiency(plot_start, plot_end, run_period):
  
    # Read the livetime CSV file for the week of interest
    livetime_df = pd.read_csv(str(DATA_CSV_DIR) + '/sbnd_livetime_' + run_period + '.csv')

    # convert to datetime
    livetime_df['start'] = pd.to_datetime(livetime_df['start'])
    livetime_df['end'] = pd.to_datetime(livetime_df['end'])

    # Reduce the dataframe to only the rows that overlap with the plot range
    mask = (livetime_df['start'] < plot_end) & (livetime_df['end'] > plot_start)
    livetime_df = livetime_df[mask].reset_index(drop=True)

    # Figure creation for POT delivered and collected
    figure = plt.figure(figsize=(12, 5))
    ax = figure.add_subplot()

    # Centers
    diff = livetime_df['end'] - livetime_df['start']
    centers = livetime_df['start'] + diff / 2

    # Stacked bar plot of the total POT delivered and collected.
    ax.bar(centers, livetime_df['collected_pot']/1e6, width=diff, label='Collected POT', alpha=1, zorder=1, color='C0')
    ax.bar(centers, livetime_df['delivered_pot']/1e6, width=diff, label='Delivered POT', alpha=1, zorder=0, color='blueviolet')
    ax.set_xlabel('Date [UTC]')
    ax.set_ylabel('POT [x$10^{18}$]')

    # Only show the x-axis label every day and rotate the labels
    # Set major ticks to be every day
    ax.xaxis.set_major_locator(DayLocator(interval=1))
    ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='center')

    # Set minor ticks to be every 6 hours
    ax.xaxis.set_minor_locator(HourLocator(interval=6))
    plt.setp(ax.xaxis.get_minorticklabels(), rotation=45, ha='center')

    # Set axis limits
    ax.set_xlim(plot_start, plot_end)
    ax.set_ylim(0, 0.60)

    # Add a legend, but add statistics showing the total delivered POT,
    # collected POT, and the collection efficiency
    h, l = ax.get_legend_handles_labels()
    total_delivered_pot = np.sum(livetime_df['delivered_pot'])
    total_collected_pot = np.sum(livetime_df['collected_pot'])
    collection_efficiency = total_collected_pot / total_delivered_pot

    # Add the average livetime to the legend, but with a "blank" handle
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Total Collected POT: {total_collected_pot*1e12:.2e}'.replace('+', ''))
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Total Delivered POT: {total_delivered_pot*1e12:.2e}'.replace('+', ''))
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Collection Efficiency: {collection_efficiency:.1%}')
    ax.legend(h, l)

    # Title
    _ = ax.set_title('SBND Collection Efficiency')

    # Add top right corner: run period and month range
    date_label = ""
    if run_period == "run1": date_label = "Run 1"
    elif run_period == "run2": date_label = "Run 2"
    month_range = plot_start.strftime('%b. %-d') + " - " + plot_end.strftime('%b. %-d, %Y')
    date_label = date_label + " (" + month_range + ")"
    ax.text(x=ax.get_xlim()[1], y=1.07*ax.get_ylim()[1], s=date_label, fontsize=11, color='#d67a11', ha='right', va='top')

    # Add timestamp with minute-level precision to the bottom right corner
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    deltaX = 0.1*(ax.get_xlim()[1] - ax.get_xlim()[0])
    ax.text(x=ax.get_xlim()[0] + deltaX, y=1.04*ax.get_ylim()[1], s=timestamp, fontsize=8, color='#d67a11', ha='right', va='top')

    # Save the figure
    figure.savefig(str(PLOT_DIR) + '/pot_weekly_collection_efficiency.png', dpi=1000, bbox_inches='tight')
    figure.savefig(str(PLOT_DIR) + '/pot_weekly_collection_efficiency.pdf', dpi=1000, bbox_inches='tight')
    figure.savefig(str(PLOT_DIR) + '/pot_weekly_collection_efficiency_light.png', dpi=75, bbox_inches='tight')


def plot_run2_cumulative(endTime):
    #Run 2 only
    livetime_df = pd.read_csv(str(DATA_CSV_DIR)+'/sbnd_livetime_run2.csv')
    startTime = RUN2_START_TIME
    date_label = f"{startTime.strftime('%b. %-d, %Y')} - {endTime.strftime('%b. %-d, %Y')}"

    livetime_df['start'] = pd.to_datetime(livetime_df['start'])
    livetime_df['end'] = pd.to_datetime(livetime_df['end'])

    figure = plt.figure(figsize=(14, 6.5))
    ax = figure.add_subplot()

    # Center points for the x-axis
    diff = livetime_df['end'] - livetime_df['start']
    centers = livetime_df['start'] + diff / 2

    # Print the times of hitting key values
    pot_of_interest = 17.5
    collected_pot_sofar = 0 #this is e19
    for i, row in livetime_df.iterrows():
        if(collected_pot_sofar < pot_of_interest):
            collected_pot_sofar = collected_pot_sofar + row['collected_pot']/1e7
            if(collected_pot_sofar > pot_of_interest): print("Hit ", pot_of_interest, "at ", row['start'], " + ", (pot_of_interest-(collected_pot_sofar-row['collected_pot']/1e7))/(row['collected_pot']/1e7)*4, "hours \n\t", collected_pot_sofar-row['collected_pot']/1e7, collected_pot_sofar)


    # Annotations
    annotes = {'Run 2 Full Trigger \n Menu Begins': datetime(2025, 10, 31, 17, 19, 56, tzinfo=timezone.utc),}

    # Each time point is a cumulative sum of the delivered / collected POT
    ax.plot(centers, np.cumsum(livetime_df['delivered_pot'])/1e7, label='Cumulative Delivered POT', color='blueviolet')
    ax.plot(centers, np.cumsum(livetime_df['collected_pot'])/1e7, label='Cumulative Collected POT', color='C0')

    ax.set_xlabel('Date [UTC]')
    ax.set_ylabel('Cumulative POT [x$10^{19}$]')
    ax.set_xlim(startTime, endTime)
    yMax = ax.get_ylim()[1]
    ax.set_ylim(0, yMax*1.05)

    # Add a legend, but add statistics showing the total delivered POT,
    # collected POT, and the collection efficiency
    mask = ((livetime_df['start'] >= startTime)
            & (livetime_df['end'] <= endTime))

    h, l = ax.get_legend_handles_labels()
    total_delivered_pot = np.sum(livetime_df['delivered_pot'][mask])
    print(f'Total Delivered POT: {total_delivered_pot}')
    total_collected_pot = np.sum(livetime_df['collected_pot'][mask])
    collection_efficiency = total_collected_pot / total_delivered_pot

    # Add the average livetime to the legend, but with a "blank" handle
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Total Collected POT: {total_collected_pot*1e12:.2e}'.replace('+', ''))
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Total Delivered POT: {total_delivered_pot*1e12:.2e}'.replace('+', ''))
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Collection Efficiency: {collection_efficiency:.1%}')
    ax.legend(h, l, loc='lower right', fontsize=18)

    date_padding = timedelta(days=1)
    for label, date in annotes.items():
        ax.axvline(date, color='black', linestyle='--', lw=2)
        #ax.text(date+date_padding, 37.5-1.0, label, rotation=90, ha='left', va='top', fontsize=18,)
        ax.text(date+date_padding, 0.95, label, rotation=90, ha='left', va='top', fontsize=18,transform=ax.get_xaxis_transform())


    vadj, hadj = 0.02, -0.02
    label = 'SBND Preliminary'

    yrange = ax.get_ylim()
    usey = yrange[1] + 0.03*(yrange[1] - yrange[0]) + vadj*(yrange[1] - yrange[0])
    xrange = ax.get_xlim()
    usex = xrange[0] + 0.025*(xrange[1] - xrange[0]) + hadj*(xrange[1] - xrange[0])
    ax.text(x=usex, y=usey, s=label, fontsize=18, color='#d67a11')


    ax.text(x=xrange[1] + hadj*(xrange[1] - xrange[0]),
            y=usey, s=date_label, fontsize=18, color='#d67a11', ha='right')

    logo = mpimg.imread('include/sbnd_logo.jpeg')
    im = OffsetImage(logo, zoom=0.5, alpha=0.2)

    # create an AnnotationBbox at axes fraction (x=0.5,y=0.5) = the center
    # you can move it to e.g. (0.9,0.1) for bottom-right, etc.
    ab = AnnotationBbox(
        im,
        #(0.12, 0.7),                # x,y in axes fraction
        (0.5, 0.5),
        xycoords='axes fraction',
        frameon=False,             # no border
        pad=0                      # no extra padding
    )
    #ax.add_artist(ab)

    # Add timestamp with minute-level precision to the bottom right corner
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    deltaX = 0.1*(ax.get_xlim()[1] - ax.get_xlim()[0])
    ax.text(x=ax.get_xlim()[0] + deltaX, y=1.025*ax.get_ylim()[1], s=timestamp, fontsize=8, color='#d67a11', ha='right', va='top')

    figure.suptitle('SBND Run 2 Cumulative POT')
    figure.savefig( str(PLOT_DIR) + '/livetime_pot_cumulative_run2.png', dpi=1000, bbox_inches='tight')
    figure.savefig( str(PLOT_DIR) + '/livetime_pot_cumulative_run2.pdf', dpi=1000, bbox_inches='tight')
    figure.savefig( str(PLOT_DIR) + '/livetime_pot_cumulative_run2_light.png', dpi=75, bbox_inches='tight')



def plot_total_cumulative(endTime, addProjection = False):
    startTime = RUN1_START_TIME
    end_time = endTime
    date_label = f"{startTime.strftime('%b. %-d, %Y')} - {end_time.strftime('%b. %-d, %Y')}"

    #Run 1 file
    livetime_run1_df = pd.read_csv( str(DATA_CSV_DIR) + '/sbnd_livetime_run1.csv')
    #Run 2 file
    livetime_run2_df = pd.read_csv( str(DATA_CSV_DIR) + '/sbnd_livetime_run2.csv')
    #Combine them
    livetime_df = pd.concat([livetime_run1_df, livetime_run2_df], ignore_index=True)

    livetime_df['start'] = pd.to_datetime(livetime_df['start'])
    livetime_df['end'] = pd.to_datetime(livetime_df['end'])

    figure = plt.figure(figsize=(14, 6.5))
    ax = figure.add_subplot()

    # Center points for the x-axis
    diff = livetime_df['end'] - livetime_df['start']
    centers = livetime_df['start'] + diff / 2

    # Annotations
    annotes = {'End Run 1': datetime(2025, 7, 11, 17, 19, 56, tzinfo=timezone.utc),'Start Run 2': datetime(2025, 10, 14, 17, 19, 56, tzinfo=timezone.utc),}


    # Print the times of hitting key values
    pot_of_interest = 52.5
    collected_pot_sofar = 0 #this is e19
    for i, row in livetime_df.iterrows():
        if(collected_pot_sofar < pot_of_interest):
            collected_pot_sofar = collected_pot_sofar + row['collected_pot']/1e7
            if(collected_pot_sofar > pot_of_interest): print("Hit ", pot_of_interest, "at ", row['start'], " + ", (pot_of_interest-(collected_pot_sofar-row['collected_pot']/1e7))/(row['collected_pot']/1e7)*4, "hours \n\t", collected_pot_sofar-row['collected_pot']/1e7, collected_pot_sofar)



    # Each time point is a cumulative sum of the delivered / collected POT
    ax.plot(centers, np.cumsum(livetime_df['delivered_pot'])/1e7, label='Cumulative Delivered POT', color='blueviolet')
    ax.plot(centers, np.cumsum(livetime_df['collected_pot'])/1e7, label='Cumulative Collected POT', color='C0')


    if(addProjection):
        # Add projections
        slopeCalcStart = datetime(2025, 10, 16, 0, 0, 0, tzinfo=ZoneInfo('America/Chicago'))
        slopeCalcEnd = endTime
        endTimeProj = datetime(2026, 6, 12, 0, 0, 0, tzinfo=ZoneInfo('America/Chicago'))

        maskCalc = ( (livetime_df['start'] >= slopeCalcStart) & (livetime_df['end'] <= slopeCalcEnd) )
        # mask out entries with collected POT <1000 
        maskCalc = maskCalc & (livetime_df['collected_pot'] > 1000)
        deliveredPOTs = livetime_df['delivered_pot'][maskCalc]
        collectedPOTs = livetime_df['collected_pot'][maskCalc]
        mean_collected_pot = np.mean(collectedPOTs)
        mean_delivered_pot = np.mean(deliveredPOTs)

        print(f"Mean collected POT in the slope calculation period:", mean_collected_pot)
        print(f"Mean delivered POT in the slope calculation period: ", mean_delivered_pot)

        # New dataframe for the projection, starting from the last point in the original dataframe
        last_date = livetime_df['end'].max()
        last_collected_pot = livetime_df['collected_pot'][livetime_df['end'] == last_date].values[0]/1e7
        last_delivered_pot = livetime_df['delivered_pot'][livetime_df['end'] == last_date].values[0]/1e7
        livetime_df_proj = livetime_df
        # Iteratively add rows to the projection dataframe until we reach the end time
        while livetime_df_proj['end'].iloc[-1] < endTimeProj:
            new_start = livetime_df_proj['end'].iloc[-1]
            new_end = new_start + timedelta(hours=4)
            new_collected_pot = mean_collected_pot
            new_delivered_pot = mean_delivered_pot
            #last_collected_pot = new_collected_pot
            #last_delivered_pot = new_delivered_pot
            new_row = pd.DataFrame({
                'start': [new_start],
                'end': [new_end],
                'collected_pot': [new_collected_pot],
                'delivered_pot': [new_delivered_pot],
            })
            livetime_df_proj = pd.concat([livetime_df_proj, new_row], ignore_index=True)


        # Plot the projection
        diffProj = livetime_df_proj['end'] - livetime_df_proj['start']
        centersProj =  livetime_df_proj['start'] + diffProj / 2
        ax.plot(centersProj, np.cumsum(livetime_df_proj['delivered_pot'])/1e7, label='Run 2 projection (delivered)', color='blueviolet', linestyle='--')
        ax.plot(centersProj, np.cumsum(livetime_df_proj['collected_pot'])/1e7, label='Run 2 projection (collected)', color='C0', linestyle='--')
        endTime = endTimeProj

    ax.set_xlabel('Date [UTC]')
    ax.set_ylabel('Cumulative POT [x$10^{19}$]')
    ax.set_xlim(startTime, endTime)
    yMax = ax.get_ylim()[1]
    ax.set_ylim(0, yMax*1.05)

    # Add a legend, but add statistics showing the total delivered POT,
    # collected POT, and the collection efficiency
    mask = (
            (livetime_df['start'] >= startTime)
            & (livetime_df['end'] <= endTime)
            )

    h, l = ax.get_legend_handles_labels()
    total_delivered_pot = np.sum(livetime_df['delivered_pot'][mask])
    print(f'Total Delivered POT: {total_delivered_pot}')
    total_collected_pot = np.sum(livetime_df['collected_pot'][mask])
    collection_efficiency = total_collected_pot / total_delivered_pot

    # Add the average livetime to the legend, but with a "blank" handle
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Total Collected POT: {total_collected_pot*1e12:.2e}'.replace('+', ''))
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Total Delivered POT: {total_delivered_pot*1e12:.2e}'.replace('+', ''))
    h.append(plt.Line2D([0], [0], color='white', lw=0))
    l.append(f'Collection Efficiency: {collection_efficiency:.1%}')
    ax.legend(h, l, loc='upper left', fontsize=18)



    date_padding = timedelta(days=1)
    for label, date in annotes.items():
        ax.axvline(date, color='black', linestyle='--', lw=2)
        #ax.text(date+date_padding, 37.5-1.0, label, rotation=90, ha='left', va='top', fontsize=18,)
    #    ax.text(date+date_padding, 0.95, label, rotation=90, ha='left', va='top', fontsize=18,transform=ax.get_xaxis_transform())

    ax.axvspan(annotes["End Run 1"], annotes["Start Run 2"], color = "gray", alpha = 0.5)


    vadj, hadj = 0.02, -0.02
    label = 'SBND Preliminary'

    yrange = ax.get_ylim()
    usey = yrange[1] + 0.03*(yrange[1] - yrange[0]) + vadj*(yrange[1] - yrange[0])
    xrange = ax.get_xlim()
    usex = xrange[0] + 0.025*(xrange[1] - xrange[0]) + hadj*(xrange[1] - xrange[0])
    ax.text(x=usex, y=usey, s=label, fontsize=18, color='#d67a11')

    # Opposite the previous label, place the dates
    ax.text(x=xrange[1] + hadj*(xrange[1] - xrange[0]),
            y=usey, s=date_label, fontsize=18, color='#d67a11', ha='right')

    logo = mpimg.imread('include/sbnd_logo.jpeg')
    im = OffsetImage(logo, zoom=0.5, alpha=0.2)

    # create an AnnotationBbox at axes fraction (x=0.5,y=0.5) = the center
    # you can move it to e.g. (0.9,0.1) for bottom-right, etc.
    ab = AnnotationBbox(
        im,
        #(0.12, 0.7),                # x,y in axes fraction
        (0.5, 0.5),
        xycoords='axes fraction',
        frameon=False,             # no border
        pad=0                      # no extra padding
    )
    #ax.add_artist(ab)

    # Add timestamp with minute-level precision to the bottom right corner
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    deltaX = 0.1*(ax.get_xlim()[1] - ax.get_xlim()[0])
    ax.text(x=ax.get_xlim()[0] + deltaX, y=1.025*ax.get_ylim()[1], s=timestamp, fontsize=8, color='#d67a11', ha='right', va='top')

    figure.suptitle('SBND Run 1+2 Cumulative POT')
    figure.savefig( str(PLOT_DIR) + '/livetime_pot_cumulative_run1+2.png', dpi=1000, bbox_inches='tight')
    figure.savefig( str(PLOT_DIR) + '/livetime_pot_cumulative_run1+2.pdf', dpi=1000, bbox_inches='tight')
    figure.savefig( str(PLOT_DIR) + '/livetime_pot_cumulative_run1+2_light.png', dpi=75, bbox_inches='tight')