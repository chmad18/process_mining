import pandas as pd
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.discovery.ilp import algorithm as ilp_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.end_activities.log.get import get_end_activities
from pm4py.statistics.start_activities.log.get import get_start_activities
from pm4py.visualization.petri_net import visualizer as pn_visualizer


def calculate_statistics(event_log):
    start_act_freq = get_start_activities(event_log)
    end_act_freq = get_end_activities(event_log)
    activities_durations = {}
    total_morning_duration = []
    average_wakeup_time = []
    average_breakfast_duration = []
    average_bathroom_duration = []
    average_dressing_duration = []
    average_bed_making_duration = []
    wake_up_freq = 0
    breakfast_freq = 0
    bathroom_freq = 0
    dressing_freq = 0
    go_out_freq = 0
    make_bed_freq = 0
    total_wake_up_freq = 0
    total_breakfast_freq = 0
    total_bathroom_freq = 0
    total_dressing_freq = 0
    total_go_out_freq = 0
    total_make_bed_freq = 0

    for trace in event_log:
        total_routine_time = 0
        wakeup_time = None

        for event in trace:
            act_name = event["concept:name"]

            # Increment frequency counters
            if act_name == 'Wake_up':
                wake_up_freq += 1
                total_wake_up_freq += 1
            elif act_name == 'Have_breakfast':
                breakfast_freq += 1
                total_breakfast_freq += 1
            elif act_name == 'Go_bathroom':
                bathroom_freq += 1
                total_bathroom_freq += 1
            elif act_name == 'Get_dressed':
                dressing_freq += 1
                total_dressing_freq += 1
            elif act_name == 'Go_out':
                go_out_freq += 1
                total_go_out_freq += 1
            elif act_name == 'Make_bed':
                make_bed_freq += 1
                total_make_bed_freq += 1

            activities_durations.setdefault(act_name, [])

            if 'start_timestamp' in event and 'time:timestamp' in event:
                start_timestamp = pd.to_datetime(event['start_timestamp'])
                complete_timestamp = pd.to_datetime(event['time:timestamp'])
                duration = (complete_timestamp - start_timestamp).total_seconds()
                activities_durations[act_name].append(duration)

                if act_name == 'Wake_up':
                    wakeup_time = start_timestamp
                total_routine_time += duration

            for act_name, durations in activities_durations.items():
                if act_name == 'Have_breakfast':
                    average_breakfast_duration.append(pd.Series(durations).mean())
                elif act_name == 'Go_bathroom':
                    average_bathroom_duration.append(pd.Series(durations).mean())
                elif act_name == 'Get_dressed':
                    average_dressing_duration.append(pd.Series(durations).mean())
                elif act_name == 'Make_bed':
                    average_bed_making_duration.append(pd.Series(durations).mean())

        total_morning_duration.append(total_routine_time)
        if wakeup_time:
            average_wakeup_time.append(wakeup_time)

    # Calculate enhanced statistical measures for each activity
    for act_name in activities_durations:
        durations_series = pd.Series(activities_durations[act_name])
        activities_durations[act_name] = {
            'mean': durations_series.mean(),
            'median': durations_series.median(),
            'std': durations_series.std(),
            'min': durations_series.min(),
            'max': durations_series.max()
            # Normalize by the number of traces
        }

    mean_total_morning_duration = pd.Series(total_morning_duration).mean()
    mean_wakeup_time = pd.Series(average_wakeup_time).mean()
    mean_breakfast_duration = pd.Series(average_breakfast_duration).mean()
    mean_bathroom_duration = pd.Series(average_bathroom_duration).mean()
    mean_dressing_duration = pd.Series(average_dressing_duration).mean()
    mean_bed_making_duration = pd.Series(average_bed_making_duration).mean()


    statistics = {
        'start_activities': start_act_freq,
        'end_activities': end_act_freq,
        'activities_durations': activities_durations,
        'mean_total_morning_duration': mean_total_morning_duration,
        'mean_wakeup_time': mean_wakeup_time,
        'mean_breakfast_duration': mean_breakfast_duration,
        'mean_bathroom_duration': mean_bathroom_duration,
        'mean_dressing_duration': mean_dressing_duration,
        'mean_bed_making_duration': mean_bed_making_duration,
        'wake_up_frequency': wake_up_freq / len(event_log),
        'mean_breakfast_frequency': breakfast_freq / len(event_log),
        'mean_bathroom_frequency': bathroom_freq / len(event_log),
        'mean_dressing_frequency': dressing_freq / len(event_log),
        'mean_go_out_frequency': go_out_freq / len(event_log),
        'mean_make_bed_frequency': make_bed_freq / len(event_log),
        'total_breakfast_frequency': total_breakfast_freq,
        'total_bathroom_frequency': total_bathroom_freq,
        'total_dressing_frequency': total_dressing_freq,
        'total_go_out_frequency': total_go_out_freq,
        'total_make_bed_frequency': total_make_bed_freq
    }

    return statistics


def process_discovery_and_visualization(event_log, file_name):
    # Apply the Heuristics Miner algorithm
    net, initial_marking, final_marking = ilp_miner.apply(event_log)

    # Visualize the Petri Net
    gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters={
        pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png"
    })
    gviz2 = pn_visualizer.apply(net, initial_marking, final_marking, parameters={
        pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png",
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
log_files = ['Scenario3/logNormal.xes', 'Scenario3/logShuffle.xes']

# Dictionary to hold the results for comparison
results = []

# Process each event log
for log_file in log_files:
    # Load the event log
    log = xes_importer.apply(log_file)

    reference_model_log = xes_importer.apply('Scenario3/logNormal.xes')
    reference_net, reference_initial_marking, reference_final_marking = ilp_miner.apply(reference_model_log)

    visual_file_name = f"results/{log_file.split('.')[0].split('/')[1]}_petri_net.png"
    process_discovery_and_visualization(log, visual_file_name)

    # Discover a process model using the Heuristics Miner
    net, initial_marking, final_marking = ilp_miner.apply(log)

    # Calculate fitness and statistics
    fitness = calculate_fitness(log, reference_net, reference_initial_marking, reference_final_marking)
    statistics = calculate_statistics(log)

    # Store the results for this log
    results.append({
        'log_file': log_file,
        'fitness': fitness,
        'mean_duration': {act: data['mean'] for act, data in statistics['activities_durations'].items()},
        'median_duration': {act: data['median'] for act, data in statistics['activities_durations'].items()},
        'min_duration': {act: data['min'] for act, data in statistics['activities_durations'].items()},
        'max_duration': {act: data['max'] for act, data in statistics['activities_durations'].items()},
        'mean_total_morning_duration': statistics['mean_total_morning_duration'],
        'mean_wakeup_time': statistics['mean_wakeup_time'],
        'mean_breakfast_duration': statistics['mean_breakfast_duration'],
        'mean_bathroom_duration': statistics['mean_bathroom_duration'],
        'mean_dressing_duration': statistics['mean_dressing_duration'],
        'wake_up_frequency': statistics['wake_up_frequency'],
        'mean_breakfast_frequency': statistics['mean_breakfast_frequency'],
        'mean_bathroom_frequency': statistics['mean_bathroom_frequency'],
        'mean_dressing_frequency': statistics['mean_dressing_frequency'],
        'mean_go_out_frequency': statistics['mean_go_out_frequency'],
        'mean_make_bed_frequency': statistics['mean_make_bed_frequency'],
        'total_breakfast_frequency': statistics['total_breakfast_frequency'],
        'total_bathroom_frequency': statistics['total_bathroom_frequency'],
        'total_dressing_frequency': statistics['total_dressing_frequency'],
        'total_go_out_frequency': statistics['total_go_out_frequency'],
        'total_make_bed_frequency': statistics['total_make_bed_frequency']
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
df_results.to_csv('results/actual_statistics.csv', index=False)

# Optionally, print out the DataFrame
print(df_results)


def compare_statistics_to_expected_and_save(actual_file_path, expected_file_path, output_file_path):
    # Read the CSV files into DataFrames
    actual_df = pd.read_csv(actual_file_path)
    expected_df = pd.read_csv(expected_file_path)

    # Assuming the first row of expected_df contains the expected results
    expected_stats = expected_df.iloc[0]

    # Dictionary to hold comparison results for each log
    all_comparisons = {}

    # Iterate through each row in actual_df for comparison
    for index, actual_row in actual_df.iterrows():
        log_file = actual_row['log_file']
        comparison_results = {}

        # Iterate through each column for comparison
        for column in actual_row.index:
            if column in expected_stats.index and column not in ['log_file', 'fitness']:
                actual_value = actual_row[column]
                expected_value = expected_stats[column]

                if isinstance(actual_value, str) and isinstance(expected_value, str):
                    try:
                        # Convert strings to datetime objects
                        actual_date = pd.to_datetime(actual_value)
                        expected_date = pd.to_datetime(expected_value)

                        # Calculate the difference in a specific unit (e.g., seconds, minutes)
                        diff = (actual_date - expected_date).total_seconds()
                        abs_diff = abs(diff)
                        percent_diff = 0  # or other logic as needed

                    except ValueError:
                        # Handle the case where the conversion fails
                        diff = 9999
                        percent_diff = 0.99  # or other logic as needed
                        abs_diff = 9999
                # elif isinstance(actual_value, float) and isinstance(expected_value, float):
                #     # Calculate absolute and percentage difference for non-date values
                #     diff = actual_value - expected_value
                #     abs_diff = abs(diff)
                #     percent_diff = (abs_diff / expected_value) * 100 if expected_value != 0 else float('inf')
                else:
                    diff = actual_value - expected_value
                    abs_diff = abs(diff)
                    percent_diff = (abs_diff / expected_value) * 100 if expected_value != 0 else float('inf')

                comparison_results[column] = {
                    'difference': diff,
                    'absolute_difference': abs_diff,
                    'percentage_difference': percent_diff
                }

        all_comparisons[log_file] = comparison_results

    # Convert the comparisons dictionary to a DataFrame
    comparison_df = pd.DataFrame.from_dict({(i,j): all_comparisons[i][j]
                                            for i in all_comparisons.keys()
                                            for j in all_comparisons[i].keys()},
                                           orient='index')

    # Save the DataFrame to a CSV file
    comparison_df.to_csv(output_file_path)


# Example usage:
compare_statistics_to_expected_and_save('results/actual_statistics.csv',
                                        'results/expected_statistics.csv',
                                        '../../../comparison_results/scenario3_ilp_comparison_analysis.csv')

print()




