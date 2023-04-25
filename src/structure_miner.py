# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 20:47:09 2020

@author: Manuel Camargo
"""

import os
import platform as pl
import subprocess

import readers.bpmn_reader as br
import readers.process_structure as gph

import conformance_checking as chk
from common import SplitMinerVersion as smv


class StructureMiner:

    def __init__(self, settings, log):
        """constructor"""
        self.log = log
        self.is_safe = True
        self.settings = settings

    def execute_pipeline(self) -> None:
        self._mining_structure()
        self._evaluate_alignment()

    def _mining_structure(self) -> None:
        miner = self._get_miner(self.settings['mining_alg'])
        miner(self.settings)

    def _get_miner(self, miner):
        if miner == smv.SM_V1:
            return self._sm1_miner
        elif miner == smv.SM_V2:
            return self._sm2_miner
        elif miner == smv.SM_V3:
            return self._sm3_miner
        else:
            raise ValueError(miner)

    @staticmethod
    def _sm2_miner(settings):
        print(" -- Mining Process Structure with sm2--")
        # Event log file_name
        file_name = settings['file'].split('.')[0]
        input_route = os.path.join(settings['output'], file_name + '.xes')
        sep = ';' if pl.system().lower() == 'windows' else ':'
        # Mining structure definition
        args = ['java']
        if pl.system().lower() != 'windows':
            args.append('-Xmx2G')
        args.extend(['-cp',
                     (settings['sm2_path'] + sep + os.path.join('external_tools', 'splitminer2', 'lib', '*')),
                     'au.edu.unimelb.services.ServiceProvider',
                     'SM2',
                     input_route,
                     os.path.join(settings['output'], file_name),
                     str(settings['concurrency'])])
        subprocess.call(args)

    @staticmethod
    def _sm1_miner(settings) -> None:
        print(" -- Mining Process Structure with sm1--")
        # Event log file_name
        file_name = settings['file'].split('.')[0]
        input_route = os.path.join(settings['output'], file_name + '.xes')
        # Mining structure definition
        args = ['java', '-jar', settings['sm1_path'],
                str(settings['epsilon']), str(settings['eta']),
                input_route,
                os.path.join(settings['output'], file_name)]
        subprocess.call(args)

    @staticmethod
    def _sm3_miner(settings) -> None:
        print(" -- Mining Process Structure with sm3--")
        # Event log file_name
        file_name = settings['file'].split('.')[0]
        input_route = os.path.join(settings['output'], file_name + '.xes')
        sep = ';' if pl.system().lower() == 'windows' else ':'
        # Mining structure definition
        args = ['java']
        if pl.system().lower() != 'windows':
            args.extend(['-Xmx2G', '-Xss8G'])
        args.extend(['-cp',
                     (settings['sm3_path'] + sep + os.path.join('external_tools', 'splitminer3', 'lib', '*')),
                     'au.edu.unimelb.services.ServiceProvider',
                     'SMD',
                     str(settings['epsilon']), str(settings['eta']),
                     'false', 'false', 'false',
                     input_route,
                     os.path.join(settings['output'], file_name)])
        subprocess.call(args)

    def _evaluate_alignment(self) -> None:
        # load bpmn model
        self.bpmn = br.BpmnReader(os.path.join( self.settings['output'], self.settings['file'].split('.')[0] + '.bpmn'))
        self.process_graph = gph.create_process_structure(self.bpmn)
        # Evaluate alignment
        chk.evaluate_alignment(self.process_graph, self.log, self.settings)
