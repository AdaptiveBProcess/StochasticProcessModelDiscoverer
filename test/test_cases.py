import pm4py
from click.testing import CliRunner
import os
from glob import glob

from unittest import TestCase
from parameterized import parameterized

from src.pipeline import main

class TestLogReader(TestCase):

    @parameterized.expand([
        ['TestEventLog1.xes', 1, 1],
        ['TestEventLog2.xes', 1, 1],
        ['TestEventLog3.xes', 1, 1]
    ])

    @staticmethod
    def load_bpmn(self, output_path):
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

    def load_event_log(self, output_path):
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
    
    def test_executions(self, log_name, exp_reps, s_gen_max_eval):

        test_event_log = os.path.join('input_files', 'test_event_logs', log_name) 
        runner = CliRunner()
        result = runner.invoke(main, ['discover', '--file', test_event_log, '--exp_reps', exp_reps, '--s_gen_max_eval', s_gen_max_eval])

        if result.exit_code == 0:
            output_path = result.output.split('\n')[-4]
            assert result.exit_code == 0
            assert os.path.exists(output_path)
            assert self.load_bpmn(output_path) == 1
            assert self.load_event_log(output_path) == 1
        else:
            print('Execution failed')
            print(result.output)
