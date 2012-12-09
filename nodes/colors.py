#!/usr/bin/env python

""" Questo script attiva la stampa di font colorato
    @color OKBLUE: blu
    @color OKGREEN verde
    @color WARNING giallo
    @color FAIL rosso
    @color ENDC bianco
"""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''