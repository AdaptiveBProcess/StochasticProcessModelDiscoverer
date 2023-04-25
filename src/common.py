from dataclasses import dataclass
from typing import List

import pandas as pd
from readers.log_splitter import LogSplitter


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
