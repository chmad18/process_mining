import pandas as pd
from scipy.stats import gaussian_kde
from filehandler import debugger_is_active



def calculate_duration(start, stop):
    return (stop - start).total_seconds() / 60  # Duration in minutes


def get_statistics_per_trace(log):
     # Lists to store data
    caseIDs = []
    activities = []
    frequencies = []
    durations = []
    abseluteTimes = []
    statistics = {}

    for caseID in log:
        trace = log[caseID]
        for event in trace:
            activity = event['activity']
            
            if activity:
                # Duration dimension in minutes
                duration = calculate_duration(event['start_timestamp'], event['complete_time'])
                abseluteTime = event['time:timestamp']
                caseIDs.append(caseID)
                activities.append(activity)
                durations.append(duration)
                abseluteTimes.append(abseluteTime)
                # durations_per_trace[activity] = durations_per_trace.get(activity, 0) + duration

        # # Append data for this trace to the lists
        # for activity, frequency in freq_per_trace.items():
        #     caseIDs.append(caseID)
        #     activities.append(activity)
        #     frequencies.append(frequency)
        #     durations.append(durations_per_trace[activity])

    # Create a DataFrame
    statistics_df = pd.DataFrame({
        'TraceID': caseIDs,
        'Activity': activities,
        'Duration': durations,
        'AbseluteTimes': abseluteTimes
    })

    # statistics_df['Frequency'] = pd.to_numeric(statistics_df['Frequency'], errors='coerce')
    # statistics_df['Duration'] = pd.to_numeric(statistics_df['Duration'], errors='coerce')

    if debugger_is_active():
        print(statistics_df.head())

    return statistics_df
    
def get_kde_models(statistics_df):
    # Create KDEs for both frequency and duration for each activity
    kde_models_duration = {}

    for activity in statistics_df['Activity'].unique():
        # Duration KDE
        duration_data = statistics_df[statistics_df['Activity'] == activity]['Duration'].dropna()
        kde_duration = gaussian_kde(duration_data)
        kde_models_duration[activity] = kde_duration

    return kde_models_duration

def get_activity_stats(statistics_df):
    
    statistics_df.groupby('Activity').agg({
        'Frequency': ['mean', 'std', 'median', 'min', 'max'],
        'Duration': ['mean', 'std', 'median', 'min', 'max']
    })

    if debugger_is_active():
        print(statistics_df)

    return statistics_df