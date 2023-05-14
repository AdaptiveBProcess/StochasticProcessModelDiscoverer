import networkx as nx
import pandas as pd
import itertools

import warnings
warnings.filterwarnings('ignore')

from tqdm import tqdm

class LogReplayerS:
    def __init__(self, bpmn, model, log) -> None:
        self.model = model
        self.log = log
        self.bpmn = bpmn
        self.m_data = pd.DataFrame.from_dict(dict(model.nodes.data()),
                                             orient='index')
        self.index_ac = self.m_data['name'].to_dict()
        self.df_log = pd.DataFrame([item for sublist in self.log.get_traces() for item in sublist])
        self.index_id = self.m_data['id'].to_dict()
        self.ac_index = {self.index_ac[key]:key for key in self.index_ac}
        self.find_branches()
        self.count_branc_cases()

    def find_branches(self):
        branch_nodes = []
        for node in self.model.nodes():
            out_edges = list(self.model.out_edges(node))
            in_edges = list(self.model.in_edges(node))
            if len(out_edges) > 1:
                path = [(in_edges[0][0], x[1]) for x in out_edges]
                branch_nodes += path

        self.branch_nodes = [(self.index_ac[x[0]], self.index_ac[x[1]]) for x in branch_nodes]

    @staticmethod
    def evaluate_condition(activities, nodes):
        second_index = 0
        for activity in activities:
            if activity == nodes[second_index]:
                second_index += 1
                if second_index == len(nodes):
                    return 1
        return 0
    
    def count_branc_cases(self):
        print('Counting branch cases...')
        branching_probs_idx = {}
        self.df_log = self.df_log.sort_values(by=['caseid', 'start_timestamp'])
        cases = self.df_log.groupby('caseid')['task'].apply(list).to_dict()
        for case in tqdm(cases.keys()):
            seq = cases[case]
            for branch in self.branch_nodes:
                branching_probs_idx[branch] = branching_probs_idx.get(branch, 0) + self.evaluate_condition(seq, branch)

        branching_probs_idx = {(self.ac_index[key[0]], self.ac_index[key[1]]):value for key, value in branching_probs_idx.items()}

        branching_probs = {}
        for key in branching_probs_idx.keys():
            gate = list(self.model.out_edges(key[0]))[0][1]
            branching_probs[self.index_id[gate]] = {self.index_id[k[1]]:v for k, v in branching_probs_idx.items() if k[0] == key[0]}

        namespace = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
        sequence_flows = self.bpmn.root.findall('.//bpmn:sequenceFlow', namespace)

        new_branching_probs = {}
        for key in branching_probs.keys():
            branchings = {}
            for sequence_flow in sequence_flows:
                id_branch = sequence_flow.get('id')
                source_ref = sequence_flow.get('targetRef')
                for task_id in branching_probs[key].keys():
                    if task_id == source_ref:
                        branchings[id_branch] = round(branching_probs[key][task_id]/sum(branching_probs[key].values()), 2)
            new_branching_probs[key] = branchings
        
        self.branching_probs = new_branching_probs