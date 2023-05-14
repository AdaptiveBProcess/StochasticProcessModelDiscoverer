import os
import warnings
from glob import glob
from unittest import TestCase

import click
import readers.bpmn_reader as br
import readers.log_reader as lr
from click.testing import CliRunner
from parameterized import parameterized
from readers.process_structure import create_process_structure
import json

from src.extraction.log_replayer_stochastic import LogReplayerS
from src.pipeline import main

warnings.filterwarnings('ignore')
"""
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
        ['Test3.xes', 1, 1],
        ['Test4.xes', 1, 1],
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
"""

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

    lrs = LogReplayerS(bpmn, model, log)
    click.echo('Dictionary output')
    click.echo(json.dumps(lrs.branching_probs))

class TestLogReplayerStochastic(TestCase):

    @parameterized.expand([
        ['Test1.xes', 'Test1.bpmn', {'node_da8afe4e-1c5e-4ba5-a508-9f881f07a296': {'node_6c6575fc-b066-4ead-b0a9-23c49a802698': 0.3,
                                                                                   'node_59d36866-e2b9-4a5b-8b72-2841af524125': 0.7},
                                     'node_f7ccd5b7-3060-42ed-b922-309b0cbba8e7': {'node_295466ee-f0ac-46e4-ab0a-14177fa2fb28': 0.33,
                                                                                   'node_b1f732ca-f378-4a71-9142-2543e5f7f050': 0.67}
                                    }],
        ['Test2.xes', 'Test2.bpmn', {'node_6f794a3a-9cd3-4e55-bc10-0147e03b1d1b': {'node_81456361-24e1-43cb-ab8b-f82bc39c3a9b': 0.38,
                                                                                   'node_ea8c4ba8-6a5b-43b6-9a63-4b490a5d3b53': 0.62},
                                     'node_7f046a69-6779-4205-a772-0f67ff90f3a2': {'node_bfeca2bd-c624-44f6-a4a3-2e336d21bc8d': 0.68,
                                                                                   'node_22c626f1-09af-477b-8536-4ceb59c4f478': 0.32}
                                    }],
        ['Test3.xes', 'Test3.bpmn', {'node_f9c804d0-6004-4c04-b459-5b3872b02b9b': {'node_8ac0beb4-f92c-48e5-89fa-2176006af76d': 0.68,
                                                                                   'node_3f2271ce-3bd2-4c97-94be-6b304392eb52': 0.32},
                                     'node_ab175215-7879-44ec-9fb8-85287b37b9f3': {'node_7d049353-4df3-423b-86f8-8464df15d52f': 0.41,
                                                                                   'node_5f50fe99-0d04-45ca-ab97-e1aae6674c07': 0.59}
                                    }],
        ['Test4.xes', 'Test4.bpmn', {'node_2e8faeff-f38c-4c4c-9ec8-881a12ca2dc4': {'node_524386d7-9aff-4cc8-96fc-a947be034de3': 0.31,
                                                                                   'node_15e412e8-45a0-456f-ac47-dd1b0143d7af': 0.69},
                                     'node_8a9c52dd-363f-485f-beff-8564681287b0': {'node_b81eacb1-7716-4e12-af48-147083c520cf': 0.59,
                                                                                   'node_a5cdafec-1253-496e-9421-35f1c8a8b194': 0.41}
                                    }]
                                                                                
    ])
    def test_log_replayer_stochastic(self, log_name, bpmn_name, ground_truths):
        log_path = os.path.join('test', 'fixes', 'test_event_logs', log_name)
        bpmn_path = os.path.join('test', 'fixes', 'test_bpmn_models', bpmn_name)

        runner = CliRunner()
        result = runner.invoke(run_log_replayer, ['--log_path', log_path, '--bpmn_path', bpmn_path],
                               prog_name="testing_log_replayer_stochastic", catch_exceptions=False)

        branching_probs = json.loads(result.output.split('Dictionary output')[-1])
        assert set(branching_probs.keys()) == set(ground_truths.keys())
        assert result.exit_code == 0
        for key in branching_probs.keys():
            result_value = branching_probs[key]
            input_value = ground_truths[key]
            assert result_value == input_value