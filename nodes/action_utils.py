#!/usr/bin/env python

""" Questo modulo ha lo scopo di fornire funzioni utili per la gestione delle azioni richieste.
    @action_strip:      Eliminazione spazi e inserimento maiuscole
    @action_fill:       Sostituzione spazi con underscore
    @action_synm:       Ricerca sinonimi
    @action_roll:       Wrapper
    @checkKnownAction:  Verifica se l'azione richiesta sia conosciuta o meno
    @getAction:         Estrapola l'azione conosciuta dallo yaml 
    @checkKnownMacro:   Verifica se la macro richiesta sia conosciuta o meno (offline)
    @getMacro:          Estrapola la macro richiesta con relative dipendenza (offline)
    @checkRemoteRecipe: Verifica se la macro richiesta sia presente in Roboearth
    @getRecipe:         Estrapola la macro richiesta con relative dipendenze tramite un'interrogazione
"""
import enchant
from random import choice
from colors import *

LANGUAGE = "en_GB"

lower = lambda s: s[:1].lower() + s[1:] if s else ''

def action_strip(action):
    print "+ Stripping action request..."
    action = lower(action.title().replace(" ", ""))
    return action

def action_fill(action):
    print "+ Filling action request..."
    action = action.replace(" ", "_")
    return action

def action_synm(action):
    print "+ Rerolling action request..."
    action_words = action.split()
    d = enchant.Dict(LANGUAGE)
    action_words = [choice(d.suggest(word)) for word in action_words]
    action = action_strip("".join(action_words))
    return action

""" Stampa lo status colorato """
def printlog(log, status):
    if status: 
        log += bcolors.OKGREEN
    else: 
        log += bcolors.FAIL
    log += str(status) + bcolors.ENDC
    print log

import rdflib, tempfile

STANDARD_MACRO = "manouver"
""" Una ricerca Pythonica """
def checkKnownMacro(robot_macros, requested_macro=STANDARD_MACRO, field='name'):
    keywords = [macro[field].split(" ") for macro in robot_macros]
    status = any([requested_macro in key for key in keywords])
    printlog("+ Robot knowledge about the requested macro: ", status)
    return status

""" Estrapola la risorsa richiesta dalla lista di macro """
def getMacro(robot_macros, digested_macro, field):
    try:
        index = next(index for (index, d) in enumerate(robot_macros) if (digested_macro in d[field]))
    except StopIteration:
        return None
    macro = [action for action in robot_macros[index]['dependancies'].split(" ")]
    return macro

STANDARD_ACTION = "straight"
""" Un'altra ricerca Pythonica """
def checkKnownAction(robot_actions, requested_action=STANDARD_ACTION, field='name'):
    keywords = [action[field].split(" ") for action in robot_actions]
    status = any([requested_action in key for key in keywords])
    printlog("+ Robot knowledge about the requested action: ", status)
    return status

""" Estrapola la risorsa richiesta dalla lista di azioni """
def getAction(robot_actions, digested_action, field):
    for action in robot_actions:
        if digested_action in action[field]:
            return action['name']
    try:
        index = next(index for (index, d) in enumerate(robot_actions) if (digested_action in d[field]))
    except StopIteration:
        return None
    return robot_actions[index]['name']        

ACTION_DIGEST = {
    1: action_strip,
    2: action_fill,
    3: action_synm,
}
ACTION_RESEARCH = {
    1: 'name',
    2: 'tags',
    3: 'tips',
}
""" ACTION_RESEARCH e ACTION_DIGEST massaggiano la action_request per irrobustire la validazione """
# Ritorna una nuova action_request in caso di checkKnownAction positivo
def action_roll(robot_actions, requested_action):
    for idx, key in enumerate(ACTION_RESEARCH):
        field = ACTION_RESEARCH[key]
        print
        print bcolors.OKBLUE + "+ field: " + field + bcolors.ENDC 
        for idx, key in enumerate(ACTION_DIGEST):
            digested_action = ACTION_DIGEST[key](requested_action)
            print "+ Action result: %s" % digested_action
            print "+ Done"
            status = checkKnownAction(robot_actions, digested_action, field=field)
            if status:                
                return getAction(robot_actions, digested_action, field) 
    return requested_action  