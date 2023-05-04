from dataclasses import dataclass
from typing import List

import pandas as pd
from readers.log_splitter import LogSplitter

import random
import math
import os
import utils.support as sup

@dataclass
class FileExtensions:
    BPMN: str = '.bpmn'
    XES: str = '.xes'
    CSV: str = '.csv'
    JSON: str = '.json'


@dataclass
class LogAttributes:
    CASE_ID: str = 'caseid'
    ACTIVITY: str = 'task'
    START_TIME: str = 'start_timestamp'
    END_TIME: str = 'end_timestamp'
    RESOURCE: str = 'user'
    ROLE: str = 'role'
    TIMESTAMP: str = 'timestamp'


@dataclass
class SequencesGenerativeMethods:
    PROCESS_MODEL: str = 'stochastic_process_model'
    TEST: str = 'test'

    def get_methods(self) -> List[str]:
        return list(self.__dict__.values())


@dataclass
class SplitMinerVersion:
    SM_V1: str = 'sm1'
    SM_V2: str = 'sm2'
    SM_V3: str = 'sm3'

    def get_methods(self) -> List[str]:
        return list(self.__dict__.values())


def split_log(log, one_ts, size):
    splitter = LogSplitter(log.data)
    train, validation = splitter.split_log('timeline_contained', size, one_ts)
    total_events = len(log.data)
    # Check size and change time splitting method if necessary
    if len(validation) < int(total_events * 0.1):
        train, validation = splitter.split_log('timeline_trace', size, one_ts)
    # Set splits
    validation = pd.DataFrame(validation)
    train = pd.DataFrame(train)
    return train, validation

def _sample_log(train):

    def sample_size(p_size, c_level, c_interval):
        """
        p_size : population size.
        c_level : confidence level.
        c_interval : confidence interval.
        """
        c_level_constant = {50: .67, 68: .99, 90: 1.64, 95: 1.96, 99: 2.57}
        Z = 0.0
        p = 0.5
        e = c_interval / 100.0
        N = p_size
        n_0 = 0.0
        n = 0.0
        # DEVIATIONS FOR THAT CONFIDENCE LEVEL
        Z = c_level_constant[c_level]
        # CALC SAMPLE SIZE
        n_0 = ((Z ** 2) * p * (1 - p)) / (e ** 2)
        # ADJUST SAMPLE SIZE FOR FINITE POPULATION
        n = n_0 / (1 + ((n_0 - 1) / float(N)))
        return int(math.ceil(n))  # THE SAMPLE SIZE

    cases = list(train.caseid.unique())
    if len(cases) > 1000:
        sample_sz = sample_size(len(cases), 95.0, 3.0)
        scases = random.sample(cases, sample_sz)
        train = train[train.caseid.isin(scases)]
    return train

def _save_times(times, settings, temp_output):
    if times:
        times = [{**{'output': settings['output']}, **times}]
        log_file = os.path.join(temp_output, 'execution_times.csv')
        if not os.path.exists(log_file):
            open(log_file, 'w').close()
        if os.path.getsize(log_file) > 0:
            sup.create_csv_file(times, log_file, mode='a')
        else:
            sup.create_csv_file_header(times, log_file)
