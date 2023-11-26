from filehandler import read_from_file, files_dictionary
from datadimension import get_statistics_per_trace, get_frequency_fitness, get_duration_fitness_kde #, get_duration_fitness_ChiSquared, get_frequency_fitness_kde
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import os
my_path = os.getcwd()

files_dictionary = files_dictionary()

frequency_df = pd.DataFrame()
kde_duration_df = pd.DataFrame()
chi_duration_df = pd.DataFrame()
kde_frequency_df = pd.DataFrame()

for scenario in files_dictionary:
    log_file_normal = files_dictionary[scenario]["normal"][0]
    log_normal = read_from_file(log_file_normal)
    statistics_df = get_statistics_per_trace(log_normal)

    # Get a list of all unique activities in the reference log
    all_activities = statistics_df['Activity'].unique()

    #Duration
    duration_stats = statistics_df.groupby(['TraceID', 'Activity'])['Duration'].sum().unstack(fill_value=0).reindex(columns=all_activities, fill_value=0)
    aggregated_duration_stats = duration_stats.agg(['mean', 'std', 'min', 'max', 'median'])
    expected_durations = aggregated_duration_stats.loc['mean']
    
    #Frequency
    freq_stats = statistics_df.groupby(['TraceID', 'Activity']).size().unstack(fill_value=0).reindex(columns=all_activities, fill_value=0)
    aggregated_freq_stats = freq_stats.agg(['mean', 'std', 'min', 'max', 'median'])
    expected_frequencies = aggregated_freq_stats.loc['mean']

    # Check Normal Distribution Assumption. Saves Histogram to the specified folders. The plot contains the P value and if the normal distribution is accepted or not
    alpha = 0.05
    logName = log_file_normal.removesuffix('.xes').replace('/', '\\')
    for activity in all_activities:
        s = ''
        r = ''
        statfreq, pfreq = stats.shapiro(freq_stats[activity])
        pfreq=float(format(pfreq, '.2f'))
        if pfreq > alpha:
            s = 'P Value : ' + str(pfreq) + ' Sample looks Gaussian (fail to reject H0)'
        else:
            s = 'P Value : ' + str(pfreq) + ' Sample does not look Gaussian (reject H0)'

        plt.hist(freq_stats[activity], bins=20, alpha=0.7, color='blue', edgecolor='black')
        plt.text(-5,-5, s, fontsize = 12) 
        plt.title('Frequency : ' + activity + ' ' + logName)
        freqfilename = 'DataDimension\\Results\\NormalDistributionChecks\\' + logName + '_' + activity + '_freq.png'
        plt.savefig(os.path.join(my_path, freqfilename))
        plt.close()

        statdur, pdur = stats.shapiro(freq_stats[activity])
        pdur=float(format(pdur, '.2f'))
        if pdur > alpha:
            r = 'P Value : ' + str(pdur) + ' Sample looks Gaussian (fail to reject H0)'
        else:
            r = 'P Value : ' + str(pdur) + ' Sample does not look Gaussian (reject H0)'

        plt.hist(duration_stats[activity], bins=20, alpha=0.7, color='red', edgecolor='black', label=r)
        plt.title('Duration : ' + activity + ' ' + logName)
        plt.text(-5, -5, r, fontsize = 12) 
        durfilename = 'DataDimension\\Results\\NormalDistributionChecks\\'+ logName + '_' + activity + '_duration.png'
        plt.savefig(os.path.join(my_path, durfilename))
        plt.close()


    for log_file_enriched in files_dictionary[scenario]["enriched"]:
        log_enriched = read_from_file(log_file_enriched)
        statistics_enriched_df = get_statistics_per_trace(log_enriched)

        #Frequency - Chi-Squared
        chi2_stat, p_value, fitness_value = get_frequency_fitness(statistics_enriched_df, expected_frequencies, all_activities)

        frequency_row = pd.DataFrame([
            {'Scenario' : scenario,
            'Normal Log': log_file_normal,
            'Enriched Log': log_file_enriched,
            'Fitness Value': fitness_value,
            'P Value' : p_value,
            'Chi Stat' : chi2_stat}])
        
        frequency_df = pd.concat([frequency_df, frequency_row], ignore_index=True)

        #Duration - KDE
        duration_fitness_value = get_duration_fitness_kde(statistics_enriched_df, duration_stats, all_activities, logName)
        duration_row = pd.DataFrame([
            {'Scenario' : scenario,
            'Normal Log': log_file_normal,
            'Enriched Log': log_file_enriched,
            'Fitness Value': duration_fitness_value
            }])

        kde_duration_df = pd.concat([kde_duration_df, duration_row], ignore_index=True)

        # #Frequency - KDE
        # freq_fitness_value_kde = get_frequency_fitness_kde(statistics_enriched_df, freq_stats, all_activities, logName)
        # freq_row_kde = pd.DataFrame([
        #     {'Scenario' : scenario,
        #     'Normal Log': log_file_normal,
        #     'Enriched Log': log_file_enriched,
        #     'Fitness Value': freq_fitness_value_kde
        #     }])

        # kde_frequency_df = pd.concat([kde_frequency_df, freq_row_kde], ignore_index=True)

        # #Duration - Chi-Squared
        # chi2_stat_dur, p_value_chi_dur, fitness_value_chi_dur = get_duration_fitness_ChiSquared(statistics_enriched_df, expected_durations, all_activities)

        # duration_row_chi = pd.DataFrame([
        #     {'Scenario' : scenario,
        #     'Normal Log': log_file_normal,
        #     'Enriched Log': log_file_enriched,
        #     'Fitness Value': fitness_value_chi_dur,
        #     'P Value' : p_value_chi_dur,
        #     'Chi Stat' : chi2_stat_dur}])
        
        # chi_duration_df = pd.concat([chi_duration_df, duration_row_chi], ignore_index=True)



chi_duration_df.to_excel('DataDimension/Results/ChiSquared/duration_results.xlsx')
frequency_df.to_excel('DataDimension/Results/ChiSquared/frequency_results.xlsx')
kde_duration_df.to_excel('DataDimension/Results/KDE/duration_results.xlsx')
kde_frequency_df.to_excel('DataDimension/Results/KDE/frequency_results.xlsx')