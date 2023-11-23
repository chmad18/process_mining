# import pm4py
# from pm4py.objects.log.importer.xes import importer as xes_importer
# from graphviz import Digraph
#
# # Step 1: Parse the Event Log
# def parse_event_log(log_path):
#     log = xes_importer.apply(log_path)
#     return log
#
# def identify_at_most_one_relations(trace):
#     # Initialize a dictionary to count occurrences of each activity in the trace
#     activity_count = {}
#
#     # Iterate through each event in the trace
#     for event in trace:
#         # Get the activity name from the event
#         activity_name = event["concept:name"]
#
#         # Increment the count for this activity
#         if activity_name in activity_count:
#             activity_count[activity_name] += 1
#         else:
#             activity_count[activity_name] = 1
#
#     # Identify activities that occur at most once
#     at_most_one_activities = {activity for activity, count in activity_count.items() if count <= 1}
#
#     return at_most_one_activities
#
# def identify_response_relations(trace):
#     response_relations = set()
#     seen_activities = set()
#
#     # Iterate through each event in the trace
#     for event in trace:
#         current_activity = event["concept:name"]
#
#         # For each seen activity, add a (seen_activity, current_activity) pair to the relations
#         for seen_activity in seen_activities:
#             if seen_activity != current_activity:
#                 response_relations.add((seen_activity, current_activity))
#
#         # Mark the current activity as seen
#         seen_activities.add(current_activity)
#
#     return response_relations
#
# def identify_precedence_relations(trace):
#     precedence_relations = set()
#     seen_activities = set()
#
#     # Iterate through each event in the trace
#     for event in trace:
#         current_activity = event["concept:name"]
#
#         # For each seen activity, check if it precedes the current activity
#         for seen_activity in seen_activities:
#             if seen_activity != current_activity:
#                 precedence_relations.add((seen_activity, current_activity))
#
#         # Mark the current activity as seen
#         seen_activities.add(current_activity)
#
#     return precedence_relations
#
#
# def identify_alternate_precedence_relations(trace):
#     alternate_precedence_relations = set()
#     activity_occurrences = {}
#
#     # Iterate through each event in the trace
#     for event in trace:
#         current_activity = event["concept:name"]
#
#         # Update the occurrence count for the current activity
#         activity_occurrences[current_activity] = activity_occurrences.get(current_activity, 0) + 1
#
#         # Check if the current activity has occurred exactly once before
#         for activity, count in activity_occurrences.items():
#             if activity != current_activity and count == 1:
#                 alternate_precedence_relations.add((activity, current_activity))
#
#     return alternate_precedence_relations
#
# def identify_chain_precedence_relations(trace):
#     chain_precedence_relations = set()
#     previous_activity = None
#
#     # Iterate through each event in the trace
#     for event in trace:
#         current_activity = event["concept:name"]
#
#         # If there was a previous activity, check if it precedes the current activity
#         if previous_activity is not None:
#             chain_precedence_relations.add((previous_activity, current_activity))
#
#         # Update the previous activity to the current one
#         previous_activity = current_activity
#
#     return chain_precedence_relations
#
#
# def identify_not_chain_succession_relations(trace):
#     not_chain_succession_relations = set()
#     previous_activity = None
#
#     # Iterate through each event in the trace
#     for event in trace:
#         current_activity = event["concept:name"]
#
#         # If there was a previous activity, add the relation if it's not a direct succession
#         if previous_activity is not None and previous_activity != current_activity:
#             not_chain_succession_relations.add((previous_activity, current_activity))
#
#         # Update the previous activity to the current one
#         previous_activity = current_activity
#
#     return not_chain_succession_relations
#
#
# def identify_not_coexistence_relations(log):
#     not_coexistence_relations = set()
#     all_activities = set()
#
#     # First, gather all unique activities across the log
#     for trace in log:
#         for event in trace:
#             all_activities.add(event["concept:name"])
#
#     # Initialize potential co-existence pairs based on all activities
#     potential_coexistence = {(a, b) for a in all_activities for b in all_activities if a != b}
#
#     # Iterate through each trace to remove pairs that co-exist
#     for trace in log:
#         activities_in_trace = set(event["concept:name"] for event in trace)
#
#         # Remove any pair from potential coexistence if both activities are in the trace
#         potential_coexistence -= {(a, b) for a in activities_in_trace for b in activities_in_trace if a != b}
#
#     # What remains in potential_coexistence are the not coexistence relations
#     not_coexistence_relations = potential_coexistence
#
#     return not_coexistence_relations
#
#
#
# # Step 2: Identify Relation Patterns
# def identify_relation_patterns(log):
#     # Initialize dictionaries to hold relations
#     at_most_one_relations = set()
#     response_relations = set()
#     precedence_relations = set()
#     alternate_precedence_relations = set()
#     chain_precedence_relations = set()
#     not_chain_succession_relations = set()
#     not_coexistence_relations = set()
#
#     # Iterate over the log to identify patterns
#     for trace in log:
#         # Identify AtMostOne relations
#         # ... (logic to find activities that occur at most once in the trace)
#         at_most_one_relations_in_trace = identify_at_most_one_relations(trace)
#         at_most_one_relations = at_most_one_relations.union(at_most_one_relations_in_trace)
#
#         # Identify Response relations
#         # ... (logic to find all pairs of (a, b) where b follows a)
#         response_relations_in_trace = identify_response_relations(trace)
#         response_relations = response_relations.union(response_relations_in_trace)
#
#         # Identify Precedence relations
#         # ... (logic to find all pairs of (a, b) where a precedes b)
#         precedence_relations_in_trace = identify_precedence_relations(trace)
#         precedence_relations = precedence_relations.union(precedence_relations_in_trace)
#
#         # Identify AlternatePrecedence relations
#         # ... (logic to find pairs where a occurs exactly once before b)
#         alternate_precedence_relations_in_trace = identify_alternate_precedence_relations(trace)
#         alternate_precedence_relations = alternate_precedence_relations.union(alternate_precedence_relations_in_trace)
#
#         # Identify ChainPrecedence relations
#         # ... (logic to find pairs where a occurs immediately before b)
#         chain_precedence_relations_in_trace = identify_chain_precedence_relations(trace)
#         chain_precedence_relations = chain_precedence_relations.union(chain_precedence_relations_in_trace)
#
#         # Identify NotChainSuccession relations
#         # ... (logic to find pairs where b does not occur immediately after a)
#         not_chain_succession_relations_in_trace = identify_not_chain_succession_relations(trace)
#         not_chain_succession_relations = not_chain_succession_relations.union(not_chain_succession_relations_in_trace)
#
#         # Identify NotCoExistence relations
#         # ... (logic to find pairs of activities that never co-occur in the same trace)
#         not_coexistence_relations = identify_not_coexistence_relations(log)
#
#     # Combine all relations into a single data structure
#     relation_patterns = {
#         'at_most_one': at_most_one_relations,
#         'response': response_relations,
#         'precedence': precedence_relations,
#         'alternate_precedence': alternate_precedence_relations,
#         'chain_precedence': chain_precedence_relations,
#         'not_chain_succession': not_chain_succession_relations,
#         'not_coexistence': not_coexistence_relations
#     }
#
#     return relation_patterns
#
# # Step 3: Construct Initial DCR Graph
# def construct_dcr_graph():
#     dcr_graph = {
#         'activities': set(),
#         'relations': {
#             'at_most_one': set(),
#             'response': set(),
#             'precedence': set(),
#             'alternate_precedence': set(),
#             'chain_precedence': set(),
#             'not_chain_succession': set(),
#             'not_coexistence': set()
#         },
#         'marking': {
#             'executed': set(),
#             'pending': set(),
#             'included': set(),
#             'excluded': set()
#         }
#     }
#     return dcr_graph
#
# # Step 4: Add Relations to DCR Graph
# def add_relations_to_dcr_graph(dcr_graph, relation_patterns):
#     # Add activities to the DCR graph
#     for relation_type, relations in relation_patterns.items():
#         for relation in relations:
#             # Each relation is a tuple of (activity_a, activity_b)
#             activity_a, activity_b = relation
#
#             # Add the activities to the graph's activities set
#             dcr_graph['activities'].add(activity_a)
#             dcr_graph['activities'].add(activity_b)
#
#             # Add the relation to the appropriate type in the graph
#             if relation_type in dcr_graph['relations']:
#                 dcr_graph['relations'][relation_type].add(relation)
#
#     # Additionally, you can set initial markings for the activities
#     # For instance, initially, all activities can be included and not executed
#     dcr_graph['marking']['included'] = dcr_graph['activities'].copy()
#     # The sets for 'executed', 'pending', and 'excluded' can remain empty initially
#     # These will be used in the dynamic behavior of the DCR graph
#
#     return dcr_graph
#
# def apply_transitive_reduction(relations, relation_type):
#     # Placeholder function for applying transitive reduction to a set of relations
#     # The implementation will vary based on the semantics of each relation type
#     # Here, you need to implement the specific logic to remove redundant relations
#     # This could involve graph algorithms and specific rules based on DCR semantics
#     reduced_relations = set(relations)  # Currently, it just returns the same set
#     return reduced_relations
#
# # Step 5: Remove Redundant Relations
# def remove_redundant_relations(dcr_graph):
#     # For each type of relation, apply transitive reduction
#     for relation_type, relations in dcr_graph['relations'].items():
#         # Implement the logic for transitive reduction based on the type of relation
#         # This is a placeholder for the specific logic
#         reduced_relations = apply_transitive_reduction(relations, relation_type)
#
#         # Update the relations in the DCR graph
#         dcr_graph['relations'][relation_type] = reduced_relations
#
#     return dcr_graph
#
# # Step 6: Discover Additional Conditions
# def discover_additional_conditions(dcr_graph, log):
#     # Iterate through each trace in the log
#     for trace in log:
#         # Simulate the execution of the trace on the DCR graph
#         for event in trace:
#             current_activity = event["concept:name"]
#
#             # Check if the current activity's execution is allowed based on the DCR graph's state
#             # and update the graph's state accordingly
#             is_allowed, dcr_graph = is_execution_allowed(dcr_graph, current_activity)
#
#             # If the activity's execution is not allowed, then we may have identified a missing condition
#             if not is_allowed:
#                 # Logic to identify and add the missing condition relation
#                 # This might involve checking which conditions could have allowed this activity
#                 # and updating the DCR graph accordingly
#                 dcr_graph = add_missing_condition(dcr_graph, current_activity)
#
#     return dcr_graph
#
#
# def is_execution_allowed(dcr_graph, activity):
#     updated_dcr_graph = dcr_graph.copy()
#     # Check if the activity is included in the graph
#     if activity not in dcr_graph['marking']['included']:
#         return False, dcr_graph  # Activity is not included, hence not allowed
#
#     # Check for Precedence relations - activity is allowed if all its predecessors have been executed
#     for (predecessor, successor) in dcr_graph['relations']['precedence']:
#         if successor == activity and predecessor not in dcr_graph['marking']['executed']:
#             return False, dcr_graph  # A predecessor has not been executed, hence not allowed
#
#     # Check for Response relations - if the activity has been executed,
#     # then all its response activities should be included
#     for (a, b) in dcr_graph['relations']['response']:
#         if a == activity:
#             updated_dcr_graph['marking']['included'].add(b)
#
#     # Check for ChainPrecedence relations - the activity is allowed if it's
#     # immediately preceded by its chain predecessor
#     for (predecessor, successor) in dcr_graph['relations']['chain_precedence']:
#         if successor == activity and (predecessor not in dcr_graph['marking']['executed'] or
#                                       dcr_graph['marking']['executed'][-1] != predecessor):
#             return False, dcr_graph  # Chain predecessor not immediately executed before, hence not allowed
#
#     # Check for AtMostOne relations - the activity is allowed if it has not been executed yet
#     if activity in dcr_graph['relations']['at_most_one'] and activity in dcr_graph['marking']['executed']:
#         return False, dcr_graph
#
#     # Check for AlternatePrecedence relations - the activity is allowed if its alternate predecessor
#     # has occurred exactly once before it
#     for (predecessor, successor) in dcr_graph['relations']['alternate_precedence']:
#         if successor == activity and dcr_graph['marking']['executed'].count(predecessor) != 1:
#             return False, dcr_graph
#
#     # Check for NotChainSuccession relations - the activity is allowed if it's not immediately
#     # followed by a specific other activity
#     for (a, b) in dcr_graph['relations']['not_chain_succession']:
#         if a == dcr_graph['marking']['executed'][-1] and b == activity:
#             return False, dcr_graph
#
#     # Check for NotCoExistence relations - the activity is allowed if it and its non-coexistent
#     # activity have not both been executed
#     for (a, b) in dcr_graph['relations']['not_coexistence']:
#         if (a == activity and b in dcr_graph['marking']['executed']) or \
#                 (b == activity and a in dcr_graph['marking']['executed']):
#             return False, dcr_graph
#
#     # Update the graph's state if the activity is executed
#     # For example, mark the activity as executed
#     updated_dcr_graph['marking']['executed'].add(activity)
#
#     # Update pending activities based on response relations
#     for (a, b) in updated_dcr_graph['relations']['response']:
#         if a == activity:
#             updated_dcr_graph['marking']['pending'].add(b)
#
#     # Update included or excluded activities based on other relations
#     # For example, for AtMostOne relations, if an activity is executed, exclude it from future execution
#     if activity in updated_dcr_graph['relations']['at_most_one']:
#         updated_dcr_graph['marking']['excluded'].add(activity)
#
#     # Additional logic for other relations like chain_precedence, alternate_precedence, etc.
#     # For example, executing an activity might include or exclude other activities based on these relations
#
#     return True, updated_dcr_graph
#
#
# def add_missing_condition(dcr_graph, activity):
#     updated_dcr_graph = dcr_graph.copy()
#
#     # Identify potential missing condition activities
#     potential_missing_conditions = identify_potential_missing_conditions(updated_dcr_graph, activity)
#
#     # Add the identified missing condition relations to the DCR graph
#     for missing_condition in potential_missing_conditions:
#         updated_dcr_graph['relations']['condition'].add((missing_condition, activity))
#
#     return updated_dcr_graph
#
# def identify_potential_missing_conditions(dcr_graph, activity):
#     potential_conditions = set()
#
#     # Check against all other activities to identify potential missing conditions
#     for other_activity in dcr_graph['activities']:
#         if other_activity != activity and is_condition_missing(dcr_graph, other_activity, activity):
#             potential_conditions.add(other_activity)
#
#     return potential_conditions
#
#
# def is_condition_missing(dcr_graph, potential_condition, activity):
#     # If "Sleep" is the first activity, it should not have a predecessor
#     if activity == "Sleep" and not dcr_graph['marking']['executed']:
#         return False
#
#     # If the activity is "Bathroom" or "Get Up", it requires "Sleep" to have happened
#     if activity in ["Bathroom", "Get Up"] and "Sleep" not in dcr_graph['marking']['executed']:
#         return True
#
#     # "Sleep" should not directly follow "Get Up"
#     if activity == "Sleep" and potential_condition == "Get Up":
#         return True
#
#     # "Bathroom" should only be followed by "Sleep"
#     if activity == "Sleep" and potential_condition == "Bathroom":
#         return False
#
#     # "Bathroom" should not be followed by "Get Up"
#     if activity == "Get Up" and potential_condition == "Bathroom":
#         return True
#
#     # "Get Up" should be the last activity, no activity should follow "Get Up"
#     if activity == "Get Up" and dcr_graph['marking']['executed']:
#         return True
#
#     return False
#
#
# def some_complex_check(dcr_graph, potential_condition, activity):
#     # Check if executing the potential_condition would allow the activity
#     # based on the process model's logic
#
#     # If the activity is "Bathroom" and the potential condition is "Sleep",
#     # check if "Sleep" executed would allow "Bathroom"
#     if activity == "Bathroom" and potential_condition == "Sleep":
#         # Allow "Bathroom" if it follows "Sleep"
#         return True
#
#     # If the activity is "Get Up" and the potential condition is "Sleep",
#     # check if "Sleep" executed would allow "Get Up"
#     if activity == "Get Up" and potential_condition == "Sleep":
#         # Allow "Get Up" if it follows "Sleep"
#         return True
#
#     # If the activity is "Sleep" and the potential condition is "Bathroom",
#     # check if "Bathroom" executed would allow "Sleep"
#     if activity == "Sleep" and potential_condition == "Bathroom":
#         # Allow "Sleep" if it follows "Bathroom"
#         return True
#
#     # If the activity is "Sleep" and the potential condition is "Get Up",
#     # "Sleep" should not directly follow "Get Up"
#     if activity == "Sleep" and potential_condition == "Get Up":
#         return False
#
#     # Default case if none of the specific conditions are met
#     return False
#
#
#
#
#
# # Step 7: Finalize DCR Graph
# def finalize_dcr_graph(dcr_graph):
#     # Perform final transitive reduction
#     dcr_graph = apply_final_transitive_reduction(dcr_graph)
#
#     # Perform any other necessary refinements
#     # This might include checking for inconsistencies, removing redundant activities,
#     # or ensuring the graph adheres to certain constraints specific to your process
#     dcr_graph = perform_other_refinements(dcr_graph)
#
#     return dcr_graph
#
# def apply_final_transitive_reduction(dcr_graph):
#     # Placeholder for transitive reduction logic
#     # This should iterate over the relations in the graph and remove redundant ones
#     for relation_type, relations in dcr_graph['relations'].items():
#         # Apply specific logic for transitive reduction based on relation type
#         dcr_graph['relations'][relation_type] = reduce_relations(relations)
#
#     return dcr_graph
#
# def reduce_relations(relations):
#     reduced_relations = set(relations)
#
#     # Iterate through each pair of relations to find transitive relations
#     for relation1 in relations:
#         for relation2 in relations:
#             # Check if there's a transitive relation (e.g., A -> B and B -> C implies A -> C)
#             if relation1[1] == relation2[0]:  # relation1 ends where relation2 starts
#                 transitive_relation = (relation1[0], relation2[1])
#                 # If the transitive relation exists in the set, it's redundant and can be removed
#                 if transitive_relation in reduced_relations:
#                     reduced_relations.remove(transitive_relation)
#
#     return reduced_relations
#
#
# def perform_other_refinements(dcr_graph):
#     # Remove activities that are never executed or included
#     executed_or_included = dcr_graph['marking']['executed'].union(dcr_graph['marking']['included'])
#     dcr_graph['activities'] = {activity for activity in dcr_graph['activities'] if activity in executed_or_included}
#
#     # Ensure logical sequence of activities
#     if ("Get Up", "Sleep") in dcr_graph['relations']['precedence']:
#         dcr_graph['relations']['precedence'].remove(("Get Up", "Sleep"))
#
#     # Check for unreachable activities
#     # Example: If "Bathroom" is always preceded by "Sleep", ensure "Sleep" is not excluded
#     if any(("Sleep", act) in dcr_graph['relations']['precedence'] for act in dcr_graph['activities']):
#         dcr_graph['marking']['included'].add("Sleep")
#
#     # Validate activity frequency
#     # Example: Ensure "Get Up" only occurs once
#     if dcr_graph['marking']['executed'].count("Get Up") > 1:
#         dcr_graph['marking']['excluded'].add("Get Up")
#
#     # ... (any other specific refinements)
#
#     return dcr_graph
#
#
# def visualize_dcr_graph_with_graphviz(dcr_graph):
#     dot = Digraph(comment='DCR Graph')
#
#     # Add nodes (activities)
#     for activity in dcr_graph['activities']:
#         dot.node(activity, activity)
#
#     # Add edges (relations)
#     for relation_type, relations in dcr_graph['relations'].items():
#         for (source, target) in relations:
#             dot.edge(source, target, label=relation_type)
#
#     # Render the graph to a file (e.g., in PDF format)
#     dot.render('dcr_graph_output', format='pdf', view=True)
#
# # Main execution
# if __name__ == "__main__":
#     log_path = "../imperative/inductive_miner/Scenario1/Scenario1/logNormal.xes"
#     log = parse_event_log(log_path)
#     relation_patterns = identify_relation_patterns(log)
#     dcr_graph = construct_dcr_graph()
#     add_relations_to_dcr_graph(dcr_graph, relation_patterns)
#     remove_redundant_relations(dcr_graph)
#     discover_additional_conditions(dcr_graph, log)
#     finalize_dcr_graph(dcr_graph)
#     visualize_dcr_graph_with_graphviz(dcr_graph)