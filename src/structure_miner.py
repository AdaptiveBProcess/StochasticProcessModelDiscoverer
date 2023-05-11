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
from common import SplitMinerVersion as SmV
from common import FileExtensions as Fe


class StructureMiner:

    def __init__(self, settings, log):
        """constructor"""
        self.log = log
        self.is_safe = True
        self.settings = settings
        self.file_name = os.path.basename(self.settings['file']).split('.')[0]
        self.xes_file = os.path.join(settings['output'], self.file_name + Fe.XES)
        self.bpmn_file = os.path.join(self.settings['output'], self.file_name + Fe.BPMN)

    def execute_pipeline(self) -> None:
        self._mining_structure()
        self._evaluate_alignment()

    def _mining_structure(self) -> None:
        miner = self._get_miner(self.settings['mining_alg'])
        miner()

    def _get_miner(self, miner):
        if miner == SmV.SM_V1:
            return self._sm1_miner
        elif miner == SmV.SM_V2:
            return self._sm2_miner
        elif miner == SmV.SM_V3:
            return self._sm3_miner
        else:
            raise ValueError(miner)

    def _sm2_miner(self) -> None:
        print(" -- Mining Process Structure with sm2--")
        # Event log file_name
        sep = ';' if pl.system().lower() == 'windows' else ':'
        # Mining structure definition
        args = ['java']
        if pl.system().lower() != 'windows':
            args.append('-Xmx2G')
        args.extend(['-cp',
                     (self.settings['sm2_path'] + sep + os.path.join('external_tools', 'splitminer2', 'lib', '*')),
                     'au.edu.unimelb.services.ServiceProvider',
                     'SM2',
                     self.xes_file,
                     os.path.join(self.settings['output'], self.file_name),
                     str(self.settings['concurrency'])])

        subprocess.call(args)

    def _sm1_miner(self) -> None:
        print(" -- Mining Process Structure with sm1--")
        # Event log file_name
        # Mining structure definition
        args = ['java', '-jar', self.settings['sm1_path'],
                str(self.settings['epsilon']), str(self.settings['eta']),
                self.xes_file,
                os.path.join(self.settings['output'], self.file_name)]

        subprocess.call(args)

    def _sm3_miner(self) -> None:
        print(" -- Mining Process Structure with sm3--")
        # Event log file_name
        sep = ';' if pl.system().lower() == 'windows' else ':'
        # Mining structure definition
        args = ['java']
        if pl.system().lower() != 'windows':
            args.extend(['-Xmx2G', '-Xss8G'])
        args.extend(['-cp',
                     (self.settings['sm3_path'] + sep + os.path.join('external_tools', 'splitminer3', 'lib', '*')),
                     'au.edu.unimelb.services.ServiceProvider',
                     'SMD',
                     str(self.settings['epsilon']), str(self.settings['eta']),
                     'false', 'false', 'false',
                     self.xes_file,
                     os.path.join(self.settings['output'], self.file_name)])

        subprocess.call(args)

    def _evaluate_alignment(self) -> None:
        # load bpmn model
        self.bpmn = br.BpmnReader(self.bpmn_file)
        
        self.process_graph = gph.create_process_structure(self.bpmn)
        # Evaluate alignment
        chk.evaluate_alignment(self.process_graph, self.log, self.settings)
