import pandas as pd
from scipy.stats import gaussian_kde
from filehandler import debugger_is_active
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chisquare
import pandas as pd
import os
my_path = os.getcwd()

def get_duration_fitness_kde(statistics_enriched_df, statistics_reference_df, all_activities, fileName):
    kde_models = {}
    for activity in all_activities:
        data = statistics_reference_df[activity].tolist()
        kde_model = gaussian_kde(data)
        kde_models[activity] = kde_model
        # Plotting the KDE for the reference model
        values = np.linspace(min(data), max(data), 1000)
        densities = kde_model(values)

        plt.figure()
        plt.plot(values, densities, label=f'KDE of {activity}')
        plt.title(f'KDE for Activity: {activity}')
        plt.xlabel('Duration')
        plt.ylabel('Density')
        plt.legend()
        enrichedFileName = 'DataDimension\\Results\\KDE\\Plots\\'+ fileName + '_' + activity + '_duration.png'
        plt.savefig(os.path.join(my_path, enrichedFileName))
        plt.close()

    fitness_scores = {}
    for trace_id, trace_data in statistics_enriched_df.groupby('TraceID'):
        trace_fitness = []
        for activity in all_activities:
            if activity in trace_data['Activity'].values:
                test_data = trace_data[trace_data['Activity'] == activity]['Duration']
                
                # Check if test data is not empty
                if not test_data.empty:
                    original_data = statistics_reference_df[activity].tolist()
                    # Evaluate probability densities
                    kde_model = kde_models[activity]
                    densities = kde_model(test_data)

                    # Normalize the densities
                    normalized_densities = densities / max(kde_model(np.linspace(min(original_data), max(original_data), 1000)))

                    # Example fitness calculation (can be modified)
                    trace_fitness.append(np.mean(normalized_densities))
        
    # Normalize and aggregate score for each trace
    fitness_scores[trace_id] = np.mean(trace_fitness) if trace_fitness else 0

    # Overall fitness score for the test log
    overall_fitness = np.mean(list(fitness_scores.values()))

    return overall_fitness

# def get_frequency_fitness_kde(statistics_enriched_df, statistics_reference_df, all_activities):
#     freq_stats = statistics_enriched_df.groupby(['TraceID', 'Activity']).size().unstack(fill_value=0).reindex(columns=all_activities, fill_value=0)
#     kde_models = {}
#     activities_to_skip = []
#     for activity in all_activities:
#         data = freq_stats[activity].tolist()
#         if(len(set(data))==1):
#             activities_to_skip.append(activity)
#             continue
#         kde_model = gaussian_kde(data)
#         kde_models[activity] = kde_model

#     fitness_scores = {}
#     for trace_id, trace_data in freq_stats.groupby('TraceID'):
#         trace_fitness = []
#         for activity in all_activities:
#             if activity in activities_to_skip:
#                 continue
#             test_data = trace_data[activity]
#             # Check if test data is not empty
#             if not test_data.empty:
#                 original_data = freq_stats[activity].tolist()
#                 # Evaluate probability densities
#                 kde_model = kde_models[activity]
#                 densities = kde_model(test_data)

#                 # Normalize the densities
#                 normalized_densities = densities / max(kde_model(np.linspace(min(original_data), max(original_data), 1000)))

#                 # Example fitness calculation (can be modified)
#                 trace_fitness.append(np.mean(normalized_densities))
        
#     # Normalize and aggregate score for each trace
#     fitness_scores[trace_id] = np.mean(trace_fitness) if trace_fitness else 0

#     # Overall fitness score for the test log
#     overall_fitness = np.mean(list(fitness_scores.values()))

#     return overall_fitness


def get_duration_fitness_ChiSquared(statistics_df, expected_durations, all_activities):
    # Group by TraceID and Activity, then count the frequency of each activity per trace
    test_activity_duration_per_trace = statistics_df.groupby(['TraceID', 'Activity'])['Duration'].sum().unstack(fill_value=0).reindex(columns=all_activities, fill_value=0)

    p_values = []
    chi2_stat_values = []

    for trace_id, trace_data in test_activity_duration_per_trace.iterrows():
        trace_observed_durations = []
        trace_expected_durations = []
        for activity in all_activities:
            dur = trace_data.get(activity, 0)
            trace_observed_durations.append(dur)

            expected_dur = expected_durations.get(activity)
            trace_expected_durations.append(expected_dur)

        # Convert to numpy arrays to ensure sums match
        trace_observed_durations = np.array(trace_observed_durations)
        trace_expected_durations = np.array(trace_expected_durations)

        if trace_observed_durations.sum() > 0:
            scale_factor = trace_observed_durations.sum() / trace_expected_durations.sum()
            scaled_expected_durations = trace_expected_durations * scale_factor

            # Perform Chi-Squared Test
            chi2_stat, p_value = chisquare(f_obs=trace_observed_durations, f_exp=scaled_expected_durations)

            normalized_chi2_stat = chi2_stat / sum(trace_expected_durations)
            chi2_stat_values.append(normalized_chi2_stat)
            p_values.append(p_value)
            # Store or use the chi2_stat and p_value as needed
        else:
            chi2_stat_values.append(0)
            p_values.append(0)

    chi2_stat_average = sum(chi2_stat_values) / len(chi2_stat_values)
    p_value_average = sum(p_values) / len(p_values)
    fitness_value = (1 - chi2_stat_average) * p_value_average    

    return chi2_stat_average, p_value_average, fitness_value



def get_frequency_fitness(statistics_enriched_df, expected_frequencies, all_activities):
    # Group by TraceID and Activity, then count the frequency of each activity per trace
    test_activity_frequency_per_trace = statistics_enriched_df.groupby(['TraceID', 'Activity']).size().unstack(fill_value=0)
    # Fill in zeros for activities not mentioned in each trace
    test_activity_frequency_filled = test_activity_frequency_per_trace.reindex(columns=all_activities, fill_value=0)

    p_values = []
    chi2_stat_values = []

    for trace_id, trace_data in test_activity_frequency_filled.iterrows():
        trace_observed_frequencies = []
        trace_expected_frequencies = []
        for activity in all_activities:
            freq = trace_data.get(activity, 0)
            trace_observed_frequencies.append(freq)


            expected_freq = expected_frequencies.get(activity)
            trace_expected_frequencies.append(expected_freq)

        # Convert to numpy arrays to ensure sums match
        trace_observed_frequencies = np.array(trace_observed_frequencies)
        trace_expected_frequencies = np.array(trace_expected_frequencies)

        if trace_observed_frequencies.sum() > 0:
            scale_factor = trace_observed_frequencies.sum() / trace_expected_frequencies.sum()
            scaled_expected_frequencies = trace_expected_frequencies * scale_factor

            # Perform Chi-Squared Test
            chi2_stat, p_value = chisquare(f_obs=trace_observed_frequencies, f_exp=scaled_expected_frequencies)

            normalized_chi2_stat = chi2_stat / sum(trace_expected_frequencies)
            chi2_stat_values.append(normalized_chi2_stat)
            p_values.append(p_value)
            # Store or use the chi2_stat and p_value as needed
        else:
            chi2_stat_values.append(0)
            p_values.append(0)

    chi2_stat_average = sum(chi2_stat_values) / len(chi2_stat_values)
    p_value_average = sum(p_values) / len(p_values)
    fitness_value = (1 - chi2_stat_average) * p_value_average    

    return chi2_stat_average, p_value_average, fitness_value

def calculate_duration(start, stop):
    return (stop - start).total_seconds() / 60  # Duration in minutes


def get_statistics_per_trace(log):
     # Lists to store data
    caseIDs = []
    activities = []
    frequencies = []
    durations = []
    abseluteTimes = []

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
                frequencies.append(1)

    # Create a DataFrame
    statistics_df = pd.DataFrame({
        'TraceID': caseIDs,
        'Activity': activities,
        'Duration': durations,
        'AbseluteTimes': abseluteTimes,
        'Frequency' : frequencies
    })

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

    # if debugger_is_active():
    #     print(statistics_df)

    return statistics_df