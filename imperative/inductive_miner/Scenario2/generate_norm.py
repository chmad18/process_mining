from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.statistics.start_activities.log.get import get_start_activities
from pm4py.statistics.end_activities.log.get import get_end_activities
from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from scipy import stats


def calculate_statistics(event_log):
    start_act_freq = get_start_activities(event_log)
    end_act_freq = get_end_activities(event_log)
    activities_durations = {}
    total_eating_duration = []
    eating_absence_frequency = 0
    average_lunch_start_time = []
    average_dinner_start_time = []

    for trace in event_log:
        total_eat_time = 0
        lunch_time = None
        dinner_time = None

        for event in trace:
            act_name = event["concept:name"]
            activities_durations.setdefault(act_name, [])

            if 'start_timestamp' in event and 'time:timestamp' in event:
                start_timestamp = pd.to_datetime(event['start_timestamp'])
                complete_timestamp = pd.to_datetime(event['time:timestamp'])
                duration = (complete_timestamp - start_timestamp).total_seconds()
                activities_durations[act_name].append(duration)

                if act_name == 'Eat':
                    total_eat_time += duration
                    if start_timestamp.hour <= 15:  # Assuming lunch
                        lunch_time = start_timestamp
                    else:  # Assuming dinner
                        dinner_time = start_timestamp

        total_eating_duration.append(total_eat_time)
        if lunch_time:
            average_lunch_start_time.append(lunch_time)
        else:
            eating_absence_frequency += 1  # Lunch was skipped
        if dinner_time:
            average_dinner_start_time.append(dinner_time)
        else:
            eating_absence_frequency += 1  # Dinner was skipped

    # Calculate enhanced statistical measures for each activity
    # ... (same as your existing code)
    for act_name in activities_durations:
        durations_series = pd.Series(activities_durations[act_name])
        activities_durations[act_name] = {
            'mean': durations_series.mean(),
            'median': durations_series.median(),
            'std': durations_series.std(),
            'min': durations_series.min(),
            'max': durations_series.max()
        }

    mean_total_eating_duration = pd.Series(total_eating_duration).mean()
    mean_lunch_start_time = pd.Series(average_lunch_start_time).mean()
    mean_dinner_start_time = pd.Series(average_dinner_start_time).mean()

    statistics = {
        'start_activities': start_act_freq,
        'end_activities': end_act_freq,
        'activities_durations': activities_durations,
        'mean_total_eating_duration': mean_total_eating_duration,
        'eating_absence_frequency': eating_absence_frequency,
        'mean_lunch_start_time': mean_lunch_start_time,
        'mean_dinner_start_time': mean_dinner_start_time
    }

    return statistics

def process_discovery_and_visualization(event_log, file_name):
    # Apply the Inductive Miner algorithm
    process_tree = inductive_miner.apply(event_log)

    # Convert the ProcessTree to a Petri Net
    net, initial_marking, final_marking = pt_converter.apply(process_tree)

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
log_files = ['Scenario2/logNormal.xes']

# Dictionary to hold the results for comparison
results = []

# Process each event log
for log_file in log_files:
    # Load the event log
    log = xes_importer.apply(log_file)

    visual_file_name = f"results/{log_file.split('.')[0].split('/')[1]}_petri_net.png"
    process_discovery_and_visualization(log, visual_file_name)

    # Discover a process model using the Inductive Miner
    process_tree = inductive_miner.apply(log)
    net, initial_marking, final_marking = pt_converter.apply(process_tree)

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
        'mean_total_eating_duration': statistics['mean_total_eating_duration'],
        'eating_absence_frequency': statistics['eating_absence_frequency'],
        'mean_lunch_start_time': statistics['mean_lunch_start_time'],
        'mean_dinner_start_time': statistics['mean_dinner_start_time']
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

# Optionally, print out the DataFrame
print(df_results)


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
