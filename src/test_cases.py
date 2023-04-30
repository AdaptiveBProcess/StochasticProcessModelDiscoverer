import pm4py
from click.testing import CliRunner
import os
from pipeline import main
from glob import glob

def load_bpmn(output_path):
    bpmn_files = [x for x in glob(os.path.join(output_path, '*.bpmn'))]
    try:
        bpmn = pm4py.read_bpmn(bpmn_files[0])
        return 1
    except Exception as e:
        print(e)
        return 0

def load_event_log(output_path):
    event_log_files = [x for x in glob(os.path.join(output_path, '*.xes'))]
    try:
        event_log = pm4py.read_xes(event_log_files[0])
        return 1
    except Exception as e:
        print(e)
        return 0
    
runner = CliRunner()
test_event_logs = [r'..\input_files\test_event_logs\TestEventLog1.xes',
                   r'..\input_files\test_event_logs\TestEventLog2.xes',
                   r'..\input_files\test_event_logs\TestEventLog3.xes']

for test_event_log in test_event_logs:
    try:
        result = runner.invoke(main, ['discover', '--file', test_event_log])
        output_path = result.output.split('\n')[-4]
        assert result.exit_code == 0
        assert os.path.exists(output_path)
        assert load_bpmn(output_path) == 1
        assert load_event_log(output_path) == 1
    except Exception as e:
        print(e)    