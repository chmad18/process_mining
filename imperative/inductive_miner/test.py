import pm4py
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.objects.conversion.process_tree import converter as pt_converter

# Import your event log
log = xes_importer.apply('Scenario2/Scenario2/logNormal.xes')
log2 = xes_importer.apply('Scenario2/Scenario2/logAbsence.xes')

# Discover a process model using the Inductive Miner
process_tree = inductive_miner.apply(log)
net, initial_marking, final_marking = pt_converter.apply(process_tree)


# Apply token-based replay for conformance checking
replayed_traces = token_replay.apply(log2, net, initial_marking, final_marking)

# Calculate fitness metric
fitness = sum(trace['trace_fitness'] for trace in replayed_traces) / len(replayed_traces)
print("Inductive Miner Fitness:", fitness)
