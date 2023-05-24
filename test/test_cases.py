import pm4py
from click.testing import CliRunner
import os
from glob import glob

from unittest import TestCase
from parameterized import parameterized

from src.pipeline import main

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
        ['TestEventLog1.xes', 1, 1],
        ['TestEventLog2.xes', 1, 1],
        ['TestEventLog3.xes', 1, 1]
    ])
    def test_executions(self, log_name, exp_reps, s_gen_max_eval):
        # given
        test_event_log = os.path.join('test', 'fixes', 'test_event_logs', log_name)
        runner = CliRunner()

        # when

        # noinspection PyTypeChecker
        result = runner.invoke(main, ['discover', '--file', test_event_log, '--exp_reps', exp_reps, '--s_gen_max_eval',
                                      s_gen_max_eval, '--mining_alg', 'sm3'])

        # then
        assert result.exit_code == 0
        output_path = result.output.split('\n')[-4]
        assert os.path.exists(output_path)
        assert self.load_bpmn(output_path) == 1
        assert self.load_event_log(output_path) == 1
