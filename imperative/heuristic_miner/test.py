import pm4py
from pm4py.algo.discovery.heuristics import algorithm as heuristic_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay

# Import your event log
log = xes_importer.apply('Scenario3/Scenario3/logShuffle.xes')

# Discover a process model using the Heuristic Miner
net, initial_marking, final_marking = heuristic_miner.apply(log)

# Apply token-based replay for conformance checking
replayed_traces = token_replay.apply(log, net, initial_marking, final_marking)

# Calculate fitness metric
fitness = sum(trace['trace_fitness'] for trace in replayed_traces) / len(replayed_traces)
print(fitness)
