import os
import warnings
from glob import glob
from unittest import TestCase

import click
import pm4py
import readers.bpmn_reader as br
import readers.log_reader as lr
from click.testing import CliRunner
from parameterized import parameterized
from readers.process_structure import create_process_structure

from src.extraction.log_replayer_stochastic import LogReplayerS
from src.pipeline import main

warnings.filterwarnings('ignore')


class TestLogReader(TestCase):

    @staticmethod
    def load_bpmn(output_path):
        bpmn_files = [x for x in glob(os.path.join(output_path, '*.bpmn'))]
        try:
            pm4py.read_bpmn(bpmn_files[0])
            return 1
        except Exception as e:
            if len(bpmn_files) == 0:
                print('BPMN file does not exist.')
            else:
                print(e)
            return 0

    @staticmethod
    def load_event_log(output_path):
        event_log_files = [x for x in glob(os.path.join(output_path, '*.xes'))]
        try:
            pm4py.read_xes(event_log_files[0])
            return 1
        except Exception as e:
            if len(event_log_files) == 0:
                print('Event log file does not exist.')
            else:
                print(e)
            return 0

    @parameterized.expand([
        ['Test1.xes', 1, 1],
        ['Test2.xes', 1, 1],
        ['Test3.xes', 1, 1]
    ])
    def test_executions(self, log_name, exp_reps, s_gen_max_eval):

        test_event_log = os.path.join('test', 'fixes', 'test_event_logs', log_name)
        runner = CliRunner()

        # noinspection PyTypeChecker
        result = runner.invoke(main, ['discover', '--file', test_event_log, '--exp_reps', exp_reps, '--s_gen_max_eval',
                                      s_gen_max_eval],
                               prog_name="testing_log_replayer")

        assert result.exit_code == 0
        output_path = result.output.split('\n')[-4]
        assert os.path.exists(output_path)
        assert self.load_bpmn(output_path) == 1
        assert self.load_event_log(output_path) == 1


@click.command()
@click.option('--log_path', default=None, required=True, type=str)
@click.option('--bpmn_path', default=None, required=True, type=str)
def run_log_replayer(log_path, bpmn_path):
    settings = dict()
    settings['timeformat'] = "%Y-%m-%dT%H:%M:%S.%f"
    settings['column_names'] = {'Case ID': 'caseid',
                                'Activity': 'task',
                                'lifecycle:transition': 'event_type',
                                'Resource': 'user'}
    settings['one_timestamp'] = False
    settings['filter_d_attrib'] = True

    log = lr.LogReader(log_path, settings)
    bpmn = br.BpmnReader(bpmn_path)
    model = create_process_structure(bpmn)

    LogReplayerS(bpmn, model, log)


class TestLogReplayerStochastic(TestCase):

    @parameterized.expand([
        ['Test1.xes', 'Test1.bpmn'],
        ['Test2.xes', 'Test2.bpmn'],
        ['Test3.xes', 'Test3.bpmn']
    ])
    def test_log_replayer_stochastic(self, log_name, bpmn_name):
        log_path = os.path.join('test', 'fixes', 'test_event_logs', log_name)
        bpmn_path = os.path.join('test', 'fixes', 'test_bpmn_models', bpmn_name)

        runner = CliRunner()
        result = runner.invoke(run_log_replayer, ['--log_path', log_path, '--bpmn_path', bpmn_path],
                               prog_name="testing_log_replayer_stochastic")

        assert result.exit_code == 0
