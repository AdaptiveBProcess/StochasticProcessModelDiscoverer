import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import itertools

import warnings
warnings.filterwarnings('ignore')


class LogReplayerS:
    def __init__(self, bpmn, model, log) -> None:
        self.model = model
        self.log = log
        self.bpmn = bpmn
        self.m_data = pd.DataFrame.from_dict(dict(model.nodes.data()),
                                             orient='index')
        self.index_ac = self.m_data['name'].to_dict()
        
        self.df_log = pd.DataFrame([item for sublist in log.get_traces() for item in sublist])
        self.index_ac = self.m_data['name'].to_dict()
        self.index_id = self.m_data['id'].to_dict()
        self.ac_index = {self.index_ac[key]:key for key in self.index_ac}
        self.find_branches()
        self.count_branc_cases()

    def find_branches(self):
        self.branch_nodes = []
        for node in self.model.nodes():
            out_edges = list(self.model.out_edges(node))
            in_edges = list(self.model.in_edges(node))
            if len(out_edges) > 1:
                path = [(in_edges[0][0], x[1]) for x in out_edges]
                self.branch_nodes += path

    @staticmethod
    def evaluate_condition(df_case, ac_index, act_path):
        df_case.is_copy = False
        df_case.loc[:, 'rank'] = df_case.groupby('caseid')['start_timestamp'].rank().astype(int).values
        df_case = df_case.sort_values(by='rank')
        u_tasks = [x for x in df_case['task'].drop_duplicates()]
        
        G = nx.DiGraph()
        for task in [ac_index[x] for x in u_tasks]:
            G.add_node(task)

        tasks = [ac_index[x] for x in list(df_case['task'])]
        if list(df_case['rank']) == list(set(list(df_case['rank']))):
            order = [(x[0], x[1]) for x in [(a, b) for a, b in zip(tasks[:-1], tasks[1:])]]
        else:
            order = []
            for i in range(1, len(df_case['rank'])):
                c_task = list(df_case[df_case['rank']==i]['task'])
                n_task = list(df_case[df_case['rank']==i+1]['task'])
                order += [(x[0], x[1]) for x in list(itertools.product(c_task, n_task))]

        G.add_edges_from(order)
        cond = 1 if nx.is_simple_path(G, act_path) else 0
        return cond
    
    def count_branc_cases(self):
        branching_probs_idx = {}
        for case in self.df_log['caseid'].drop_duplicates():
            df_case = self.df_log[self.df_log['caseid']==case]
            for branch in self.branch_nodes:
                branching_probs_idx[branch] = branching_probs_idx.get(branch, 0) + self.evaluate_condition(df_case, self.ac_index, branch)

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
                source_ref = sequence_flow.get('sourceRef')
                for task_id in branching_probs[key].keys():
                    if task_id == source_ref:
                        branchings[id_branch] = branching_probs[key][task_id]/sum(branching_probs[key].values())
            new_branching_probs[key] = branchings
        
        self.branching_probs = new_branching_probs