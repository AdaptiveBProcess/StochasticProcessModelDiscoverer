# -*- coding: utf-8 -*-
"""
@author: Manuel Camargo
"""
import copy
import itertools
import os
import shutil
import subprocess
from abc import ABCMeta, abstractmethod
from operator import itemgetter
from pathlib import Path
from xml.dom import minidom

import pandas as pd
import readers.log_reader as lr
import utils.support as sup

import structure_optimizer as so
from common import LogAttributes as La
from common import SequencesGenerativeMethods as SqM
from common import split_log


class SeqGeneratorFabric:

    @classmethod
    def get_generator(cls, method):
        if method == SqM.PROCESS_MODEL:
            return StochasticProcessModelGenerator
        elif method == SqM.TEST:
            return OriginalSequencesGenerator
        else:
            raise ValueError('Nonexistent sequences generator')


class SeqGenerator(metaclass=ABCMeta):
    """
    Generator base class
    """

    def __init__(self, parameters):
        """constructor"""
        self.parameters = parameters
        self.is_safe = True
        self.model_metadata = dict()
        self.gen_seqs = None
        self.log = None
        self.model_path = None

    @abstractmethod
    def generate(self, num_inst, exp_reps):
        pass

    @abstractmethod
    def clean_time_stamps(self):
        pass

    def _read_inputs(self, **_kwargs) -> None:
        # Event log reading
        self.log = lr.LogReader(self.parameters['file'], self.parameters['read_options'])
        # Time splitting 80-20
        self._split_timeline(0.8, self.parameters['read_options']['one_timestamp'])

    @staticmethod
    def sort_log(log):
        log = sorted(log.to_dict('records'), key=lambda x: x[La.CASE_ID])
        for key, group in itertools.groupby(log, key=lambda x: x[La.CASE_ID]):
            events = list(group)
            events = sorted(events, key=itemgetter(La.START_TIME))
            length = len(events)
            for i in range(0, len(events)):
                events[i]['pos_trace'] = i + 1
                events[i]['trace_len'] = length
        log = pd.DataFrame.from_records(log)
        log.sort_values(by=La.START_TIME, ascending=True, inplace=True)
        return log

    def _split_timeline(self, size: float, one_ts: bool) -> None:
        """
        Split an event log dataframe by time to perform split-validation.
        preferred method time splitting removing incomplete traces.
        If the testing set is smaller than the 10% of the log size
        the second method is sort by traces start and split taking the whole
        traces no matter if they are contained in the timeframe or not

        Parameters
        ----------
        size : float, validation percentage.
        one_ts : bool, Support only one timestamp.
        """
        key = 'end_timestamp' if one_ts else 'start_timestamp'
        # Split log data
        train, test = split_log(self.log, one_ts, size)
        self.log_test = (test.sort_values(key, ascending=True).reset_index(drop=True))
        print('Number of instances in test log: {}'.format(len(self.log_test[La.CASE_ID].drop_duplicates())))
        self.log_train = copy.deepcopy(self.log)
        self.log_train.set_data(train.sort_values(key, ascending=True).reset_index(drop=True).to_dict('records'))
        print('Number of instances in train log: {}'.format(
            len(train.sort_values(key, ascending=True).reset_index(drop=True)[La.CASE_ID].drop_duplicates())))


class StochasticProcessModelGenerator(SeqGenerator):

    def discover_model(self, search_space, s_gen_max_eval, exp_reps):
        self._read_inputs()
        structure_optimizer = so.StructureOptimizer(self.parameters, search_space, copy.deepcopy(self.log_train))
        structure_optimizer.execute_trials(s_gen_max_eval, exp_reps)
        # Print results
        print(structure_optimizer.best_output, structure_optimizer.best_parms,
              structure_optimizer.best_similarity, sep='\n')
        # clean output folder
        # shutil.rmtree(structure_optimizer.temp_output)

    def generate(self, num_inst, exp_reps):
        self.model_path = self.parameters['file']
        # update model parameters
        self._modify_simulation_model(self.model_path, num_inst)
        temp_path = self._temp_path_creation(self.parameters['output_path'])
        # generate instances
        for rep_num in range(0, exp_reps):
            sim_log = self._execute_simulator(self.parameters['bimp_path'], temp_path, self.model_path)
            # order by Case ID and add position in the trace
            self.gen_seqs = self._rename_sim_log(sim_log)
            # remove simulated log
            self.clean_time_stamps()
            # save sequences
            self.gen_seqs.to_csv(os.path.join(temp_path, sup.file_id('SEQ_')), index=False)

    def _rename_sim_log(self, sim_log):
        sim_log_df = pd.read_csv(sim_log)
        sim_log_df = self.sort_log(sim_log_df)
        sim_log_df[La.CASE_ID] = sim_log_df[La.CASE_ID] + 1
        sim_log_df[La.CASE_ID] = sim_log_df[La.CASE_ID].astype('string')
        sim_log_df[La.CASE_ID] = f"Case{sim_log_df[La.CASE_ID]}"
        os.remove(sim_log)
        return sim_log_df

    def clean_time_stamps(self):
        self.gen_seqs.drop(columns=[La.START_TIME, La.END_TIME], inplace=True)

    @staticmethod
    def _temp_path_creation(output_files) -> Path:
        # Paths redefinition
        temp_path = os.path.join(output_files, sup.folder_id())
        # Output folder creation
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        return Path(temp_path)

    @staticmethod
    def _modify_simulation_model(model, num_inst):
        """Modifies the number of instances of the BIMP simulation model
        to be equal to the number of instances in the testing log"""
        my_doc = minidom.parse(model)
        items = my_doc.getElementsByTagName('qbp:processSimulationInfo')
        items[0].attributes['processInstances'].value = str(num_inst)
        with open(model, 'wb') as f:
            f.write(my_doc.toxml().encode('utf-8'))
        f.close()

    @staticmethod
    def _execute_simulator(bimp_path, temp_path, model):
        sim_log = os.path.join(temp_path, sup.file_id('SIM_'))
        args = ['java', '-jar', bimp_path, model, '-csv', sim_log]
        subprocess.run(args, check=True, stdout=subprocess.PIPE)
        return sim_log


class OriginalSequencesGenerator(SeqGenerator):

    def generate(self, log, exp_reps):
        sequences = log.copy(deep=True)
        sequences = sequences[[La.CASE_ID, La.ACTIVITY, La.RESOURCE, La.START_TIME]]
        replacements = {case_name: f'Case{idx + 1}' for idx, case_name in enumerate(sequences[La.CASE_ID].unique())}
        sequences.replace({La.CASE_ID: replacements}, inplace=True)
        sequences = self.sort_log(sequences)
        self.gen_seqs = (sequences.rename(columns={La.RESOURCE: 'resource'}).sort_values([La.CASE_ID, 'pos_trace']))

    def clean_time_stamps(self):
        self.gen_seqs.drop(columns=La.START_TIME)
