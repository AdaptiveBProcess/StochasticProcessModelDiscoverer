# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 13:27:58 2020

@author: Manuel Camargo
"""
import os
import sys

import click
import yaml

from common import SequencesGenerativeMethods as SqG
from common import SplitMinerVersion as Sm
from seq_generator import SeqGeneratorFabric


@click.group()
def main():
    # This is a main group which includes other commands specified below.
    pass


@main.command('discover')
@click.option('--file', default=None, required=True, type=str)
@click.option('--evaluate/--no-evaluate', default=True, required=False, type=bool)
@click.option('--mining_alg', default=Sm.SM_V1, required=False, type=click.Choice(Sm().get_methods()))
@click.option('--exp_reps', default=5, required=False, type=int)
@click.option('--s_gen_max_eval', default=30, required=False, type=int)
@click.option('--discovery_method', default='simulation', required=False, type=str)

def discover_model(file, evaluate, mining_alg, exp_reps, s_gen_max_eval, discovery_method):
    params = {'file': file, 'evaluate': evaluate, 'mining_alg': mining_alg, 'discovery_method':discovery_method}
    params = read_properties(params)
    # Sequences generator
    search_space = dict()
    search_space['concurrency'] = [0.0, 1.0]
    search_space['epsilon'] = [0.0, 1.0]
    search_space['eta'] = [0.0, 1.0]
    search_space['alg_manag'] = ['replacement', 'repair']
    search_space['gate_management'] = ['discovery', 'equiprobable']

    _ensure_locations(params)

    seq_generator_class = SeqGeneratorFabric.get_generator(SqG.PROCESS_MODEL)
    seq_generator = seq_generator_class(params)
    seq_generator.discover_model(search_space, s_gen_max_eval, exp_reps)


@main.command('generate')
@click.option('--generative_model', default=None, required=True, type=str)
@click.option('--evaluate/--no-evaluate', default=True, required=False, type=bool)
@click.option('--num_inst', default=5, required=True, type=int)
@click.option('--exp_reps', default=5, required=False, type=int)

def generate_sequences(generative_model, evaluate, num_inst, exp_reps):
    params = {'file': generative_model, 'evaluate': evaluate, 'mining_alg': None}
    params = read_properties(params)
    seq_generator_class = SeqGeneratorFabric.get_generator(SqG.PROCESS_MODEL)
    seq_generator = seq_generator_class(params)
    seq_generator.generate(num_inst, exp_reps)


def read_properties(params):
    """ Sets the app general params"""
    properties_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'properties.yml')
    with open(properties_path, 'r') as f:
        properties = yaml.load(f, Loader=yaml.FullLoader)
    if properties is None:
        raise ValueError('Properties is empty')
    paths = {k: os.path.join(*path.split('\\')) for k, path in properties.pop('paths').items()}
    params = {**params, **properties, **paths}
    return params


def _ensure_locations(params):
    if not os.path.exists(params['output_path']):
        os.makedirs(params['output_path'])


if __name__ == "__main__":
    main(sys.argv[1:])
