from filehandler import read_from_file, files_dictionary
from datadimension import get_statistics_per_trace, get_kde_models, get_activity_stats
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import poisson
import numpy as np
from scipy.stats import chisquare
import pandas as pd


files_dictionary = files_dictionary()

frequency_df = pd.DataFrame()

for scenario in files_dictionary:
    log_file_normal = files_dictionary[scenario]["normal"][0]
    log_normal = read_from_file(log_file_normal)
    statistics_df = get_statistics_per_trace(log_normal)

    # Get a list of all unique activities
    all_activities = statistics_df['Activity'].unique()
    # Group by TraceID and Activity, then count the frequency of each activity per trace
    activity_frequency_per_trace = statistics_df.groupby(['TraceID', 'Activity']).size().unstack(fill_value=0)
    # Fill in zeros for activities not mentioned in each trace
    activity_frequency_filled = activity_frequency_per_trace.reindex(columns=all_activities, fill_value=0)

    # Calculating the frequency of each activity per trace
    frequency_per_trace = statistics_df.groupby(['TraceID', 'Activity']).size().reset_index(name='Frequency')

    # Calculate aggregated statistics
    aggregated_stats = activity_frequency_filled.agg(['mean', 'std', 'min', 'max', 'median'])

    # Extract mean frequencies as expected frequencies
    expected_frequencies = aggregated_stats.loc['mean']

    for log_file_enriched in files_dictionary[scenario]["enriched"]:
        log_enriched = read_from_file(log_file_enriched)
        statistics_enriched_df = get_statistics_per_trace(log_enriched)
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

        new_row_df = pd.DataFrame([
            {'Scenario' : scenario,
            'Normal Log': log_file_normal,
            'Enriched Log': log_file_enriched,
            'Fitness Value': fitness_value,
            'P Value' : p_value_average,
            'Chi Stat' : chi2_stat_average}])
        
        frequency_df = pd.concat([frequency_df, new_row_df], ignore_index=True)

frequency_df.to_excel('DataDimension/Results/frequency_results.xlsx')