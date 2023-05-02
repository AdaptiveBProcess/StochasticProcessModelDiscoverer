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
        if len(bpmn_files) == 0:
            print('BPMN file does not exist.')
        else:
            print(e)
        return 0

def load_event_log(output_path):
    event_log_files = [x for x in glob(os.path.join(output_path, '*.xes'))]
    try:
        event_log = pm4py.read_xes(event_log_files[0])
        return 1
    except Exception as e:
        if len(event_log_files) == 0:
            print('Event log file does not exist.')
        else:
            print(e)
        return 0
    
logs_name = ['TestEventLog3.xes']

for log_name in logs_name:
    #try:
    
    test_event_log = os.path.join('..', 'input_files', 'test_event_logs', log_name) 
    runner = CliRunner()
    result = runner.invoke(main, ['discover', '--file', test_event_log])

    if result.exit_code == 0:
        output_path = result.output.split('\n')[-4]
        assert result.exit_code == 0
        assert os.path.exists(output_path)
        assert load_bpmn(output_path) == 1
        assert load_event_log(output_path) == 1
    else:
        print('Execution failed')
        print(result.output)
