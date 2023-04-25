# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 13:27:58 2020

@author: Manuel Camargo
"""
import json
import os
import sys

import click
import yaml
import pandas as pd

from common import SequencesGenerativeMethods as SqG
from common import SplitMinerVersion as Sm


@click.command()
@click.option('--file', default=None, required=True, type=str)
@click.option('--update_gen/--no-update_gen', default=False, required=False, type=bool)
@click.option('--update_ia_gen/--no-update_ia_gen', default=False, required=False, type=bool)
@click.option('--update_mpdf_gen/--no-update_mpdf_gen', default=False, required=False, type=bool)
@click.option('--update_times_gen/--no-update_times_gen', default=False, required=False, type=bool)
@click.option('--save_models/--no-save_models', default=True, required=False, type=bool)
@click.option('--evaluate/--no-evaluate', default=True, required=False, type=bool)
@click.option('--mining_alg', default=Sm.SM_V1, required=False, type=click.Choice(Sm().get_methods()))
@click.option('--exp_reps', default=5, required=False, type=int)
@click.option('--s_gen_repetitions', default=5, required=False, type=int)
@click.option('--s_gen_max_eval', default=30, required=False, type=int)
@click.option('--seq_gen_method', default=SqG.PROCESS_MODEL, required=False, type=click.Choice(SqG().get_methods()))
def main(file, update_gen, update_ia_gen, update_mpdf_gen, update_times_gen, save_models, evaluate, mining_alg,
         exp_reps, s_gen_repetitions, s_gen_max_eval, seq_gen_method):
    params = dict()
    params['gl'] = dict()
    params['gl']['file'] = file
    params['gl']['update_gen'] = update_gen
    params['gl']['update_ia_gen'] = update_ia_gen
    params['gl']['update_mpdf_gen'] = update_mpdf_gen
    params['gl']['update_times_gen'] = update_times_gen
    params['gl']['save_models'] = save_models
    params['gl']['evaluate'] = evaluate
    params['gl']['mining_alg'] = mining_alg
    params = read_properties(params)
    # params['gl']['sim_metric'] = 'tsd'  # Main metric
    # Additional metrics
    # params['gl']['add_metrics'] = ['day_hour_emd', 'log_mae', 'dl', 'mae']
    params['gl']['exp_reps'] = exp_reps
    # Sequences generator
    params['s_gen'] = dict()
    params['s_gen']['gen_method'] = seq_gen_method  # stochastic_process_model, test
    params['s_gen']['repetitions'] = s_gen_repetitions
    params['s_gen']['max_eval'] = s_gen_max_eval
    params['s_gen']['concurrency'] = [0.0, 1.0]
    params['s_gen']['epsilon'] = [0.0, 1.0]
    params['s_gen']['eta'] = [0.0, 1.0]
    params['s_gen']['alg_manag'] = ['replacement', 'repair']
    params['s_gen']['gate_management'] = ['discovery', 'equiprobable']

    _ensure_locations(params)
    _print_parameters(params)

    # simulator = ds.DeepSimulator(params)
    # simulator.execute_pipeline()


def _print_parameters(params):
    print("General parameters: ")
    print(pd.read_json(json.dumps(params['gl']), orient='index').rename(columns={0: 'value'}))
    print("Search space: ")
    print(pd.read_json(json.dumps(params['s_gen']), orient='index').rename(columns={0: 'value'}))


def read_properties(params):
    """ Sets the app general params"""
    properties_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'properties.yml')
    with open(properties_path, 'r') as f:
        properties = yaml.load(f, Loader=yaml.FullLoader)
    if properties is None:
        raise ValueError('Properties is empty')
    paths = {k: os.path.join(*path.split('\\')) for k, path in properties.pop('paths').items()}
    params['gl'] = {**params['gl'], **properties, **paths}
    return params


def _ensure_locations(params):
    if not os.path.exists(params['gl']['output_path']):
        os.makedirs(params['gl']['output_path'])


if __name__ == "__main__":
    main(sys.argv[1:])
