import pandas as pd
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.discovery.ilp import algorithm as ilp_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.end_activities.log.get import get_end_activities
from pm4py.statistics.start_activities.log.get import get_start_activities
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from scipy import stats


def calculate_statistics(event_log):
    start_act_freq = get_start_activities(event_log)
    end_act_freq = get_end_activities(event_log)
    activities_durations = {}
    total_night_sleep_times = []
    total_night_bathroom_times = []
    bathroom_frequency_per_night = []
    sleep_frequency_per_night = []

    for trace in event_log:
        total_sleep_time = 0
        total_bathroom_time = 0
        bathroom_count = 0
        sleep_count = 0

        for event in trace:
            act_name = event["concept:name"]
            activities_durations.setdefault(act_name, [])

            if 'start_timestamp' in event and 'time:timestamp' in event:
                start_timestamp = pd.to_datetime(event['start_timestamp'])
                complete_timestamp = pd.to_datetime(event['time:timestamp'])
                duration = (complete_timestamp - start_timestamp).total_seconds()
                activities_durations[act_name].append(duration)

                if act_name == 'Sleep':
                    total_sleep_time += duration
                    sleep_count += 1
                elif act_name == 'Bathroom':
                    total_bathroom_time += duration
                    bathroom_count += 1

        total_night_sleep_times.append(total_sleep_time)
        total_night_bathroom_times.append(total_bathroom_time)
        bathroom_frequency_per_night.append(bathroom_count)
        sleep_frequency_per_night.append(sleep_count)

    # Calculate enhanced statistical measures for each activity
    for act_name in activities_durations:
        durations_series = pd.Series(activities_durations[act_name])
        activities_durations[act_name] = {
            'mean': durations_series.mean(),
            'median': durations_series.median(),
            'std': durations_series.std(),
            'min': durations_series.min(),
            'max': durations_series.max()
        }

    mean_total_night_sleep_time = pd.Series(total_night_sleep_times).mean()
    mean_total_night_bathroom_time = pd.Series(total_night_bathroom_times).mean()
    mean_bathroom_frequency = pd.Series(bathroom_frequency_per_night).mean()
    mean_sleep_frequency = pd.Series(sleep_frequency_per_night).mean()

    statistics = {
        'start_activities': start_act_freq,
        'end_activities': end_act_freq,
        'activities_durations': activities_durations,
        'mean_total_night_sleep_time': mean_total_night_sleep_time,
        'mean_total_night_bathroom_time': mean_total_night_bathroom_time,
        'mean_bathroom_frequency_per_night': mean_bathroom_frequency,
        'mean_sleep_frequency_per_night': mean_sleep_frequency
    }

    return statistics

def process_discovery_and_visualization(event_log, file_name):
    # Apply the ilp Miner algorithm
    net, initial_marking, final_marking = ilp_miner.apply(event_log)

    # Visualize the Petri Net
    gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters={
        pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png"
    })

    # Save the Petri Net visualization to a file
    pn_visualizer.save(gviz, file_name)

def calculate_fitness(event_log, net, initial_marking, final_marking):
    # Use token replay to calculate fitness
    replayed_traces = token_replay.apply(event_log, net, initial_marking, final_marking)
    # Calculate and return the average fitness from the replayed traces
    fitness = sum(trace['trace_fitness'] for trace in replayed_traces) / len(replayed_traces)
    return fitness

# List of log file paths
log_files = ['Scenario1/logNormal.xes']

# Dictionary to hold the results for comparison
results = []

# Process each event log
for log_file in log_files:
    # Load the event log
    log = xes_importer.apply(log_file)

    visual_file_name = f"results/{log_file.split('.')[0].split('/')[1]}_petri_net.png"
    process_discovery_and_visualization(log, visual_file_name)

    # Discover a process model using the ilp Miner
    net, initial_marking, final_marking = ilp_miner.apply(log)

    # Calculate fitness and statistics
    fitness = calculate_fitness(log, net, initial_marking, final_marking)
    statistics = calculate_statistics(log)

    # Store the results for this log
    results.append({
        'log_file': log_file,
        'fitness': fitness,
        'mean_duration': {act: data['mean'] for act, data in statistics['activities_durations'].items()},
        'median_duration': {act: data['median'] for act, data in statistics['activities_durations'].items()},
        'min_duration': {act: data['min'] for act, data in statistics['activities_durations'].items()},
        'max_duration': {act: data['max'] for act, data in statistics['activities_durations'].items()},
        'mean_total_night_sleep_time': statistics['mean_total_night_sleep_time'],
        'mean_total_night_bathroom_time': statistics['mean_total_night_bathroom_time'],
        'mean_bathroom_frequency_per_night': statistics['mean_bathroom_frequency_per_night'],
        'mean_sleep_frequency_per_night': statistics['mean_sleep_frequency_per_night'],
    })


def expand_dict_column(data, column_name):
    expanded_data = []
    for entry in data:
        expanded_entry = entry.copy()
        dict_values = expanded_entry.pop(column_name, {})
        for key, value in dict_values.items():
            expanded_entry[f"{column_name}_{key}"] = value
        expanded_data.append(expanded_entry)
    return expanded_data


# Expanding the dictionary columns in the results list
columns_to_expand = ['mean_duration', 'median_duration', 'min_duration', 'max_duration']
for column in columns_to_expand:
    results = expand_dict_column(results, column)

# Convert the expanded results to a DataFrame
df_results = pd.DataFrame(results)

# Save the DataFrame to a CSV file
df_results.to_csv('results/expected_statistics.csv', index=False)


def compare_statistics_to_expected(actual_statistics, expected_statistics):
    comparison_results = {}

    # Iterate through each key in actual statistics
    for key, actual_value in actual_statistics.items():
        if key in expected_statistics:
            expected_value = expected_statistics[key]

            # Assuming normal distribution, use a statistical test (e.g., t-test) for comparison
            # Note: This is a simplification, and you should ensure the distribution assumptions are valid
            t_stat, p_value = stats.ttest_ind_from_stats(
                mean1=actual_value['mean'], std1=actual_value['std'], nobs1=actual_value['count'],
                mean2=expected_value['mean'], std2=expected_value['std'], nobs2=expected_value['count']
            )

            comparison_results[key] = {
                't_statistic': t_stat,
                'p_value': p_value
            }

    return comparison_results
