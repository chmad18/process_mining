from Declare4Py.D4PyEventLog import D4PyEventLog
from Declare4Py.ProcessModels.LTLModel import LTLModel
from ltlf2dfa.parser.ltlf import LTLfParser
from Declare4Py.D4PyEventLog import D4PyEventLog
from Declare4Py.ProcessModels.LTLModel import LTLModel
from Declare4Py.ProcessMiningTasks.ConformanceChecking.LTLAnalyzer import LTLAnalyzer
from logaut import ltl2dfa
from pylogics.parsers import parse_ltl


formula = parse_ltl("F(a)")
dfa = ltl2dfa(formula, backend="lydia")

event_log: D4PyEventLog = D4PyEventLog(case_name="case:concept:name")
event_log.parse_xes_log("../imperative/inductive_miner/Scenario1/Scenario1/logNormal.xes")

model = LTLModel()
model.parse_from_string("F(CRP)")

analyzer = LTLAnalyzer(event_log, model)
conf_check_res_df = analyzer.run(jobs=2)
print(conf_check_res_df)