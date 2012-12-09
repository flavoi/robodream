#!/usr/bin/env python

""" Gestore comunicazioni, validazione e risolutore delle dipendenze.
    @channel  'action_request':   ascolto richiesta azione
    @channel  'action_response':  scrittura messaggi validazione
    @channel  'action_manager':   inoltro azione al robot driver
    @channel  'manager_response': conferma di eseguita azione 
    @database 'roboearth':       comunicazione tramite API con il core di Roboearth (http://api.roboearth.org) 
"""

import roslib; roslib.load_manifest('Dream')
import rospy
import yaml, sys, os
from std_msgs.msg import String
from Dream.srv import *
from action_utils import *
from colors import *
from connector import connect_to_roboearth

MANAGER_SYNC = 0 
ACTION_SYNC = 1
TRYALS = 3;

""" Sblocca l'esecuzione delle azioni in coda """
def managerCallback(data):
    global ACTION_SYNC
    global MANAGER_SYNC
    if MANAGER_SYNC == 0:
        print "+ Manager ack received"
        ACTION_SYNC = 1
        MANAGER_SYNC = 1
    return

def mainCallback(data):
    global ACTION_SYNC 
    global MANAGER_SYNC
    response = "None"
    while ACTION_SYNC == 0:
        print "+ Waiting ACTION_SYNC"
        print MANAGER_SYNC
        rospy.sleep(1)
    print
    rospy.loginfo(rospy.get_name() + "\n+ Requested action: %s", data.data)
    requested_action = str(data.data)
    status = checkKnownAction(robot_actions, requested_action)
    if not status:
        requested_action = action_roll(robot_actions, requested_action)
    found_action = getAction(robot_actions, requested_action, field='name')
    if found_action is not None:
        print "+ Action found: " + bcolors.OKGREEN + str(found_action) + bcolors.ENDC
        response = found_action
    else:
        print 
        print bcolors.HEADER + "+ Initializing remote request" + bcolors.ENDC
        macro = connect_to_roboearth(requested_action)
        if macro is not None:
            print macro
            for action in macro:
                data.data = action
                mainCallback(data)
            sys.exit(0)
    if status: 
        ACTION_SYNC = 0
    print "+ Forwarding action request... "
    MANAGER_SYNC = 0
    pub = rospy.Publisher('action_response', String)
    for i in range(0, TRYALS):
        pub.publish(response)
        rospy.sleep(1)

# 
def handle_action_request(data):
    print "+ handle action request"
    return mindResponse(data.data)

""" Inizializzazione del nodo e apertura messaggi """
def dream():
    rospy.init_node('mind', anonymous=True)
    rospy.Subscriber("manager_response", String, managerCallback)
    rospy.Subscriber("action_request", String, mainCallback)
    s = rospy.Service('dream_server', mind, handle_action_request)
    print "\nDream server has started.\n-------------------------\n"
    rospy.spin()

INPUT_OPTIONS = {
    "-i": "robot_actions",
    "-r": "roboearth_connector ",
}
if __name__ == '__main__':
    try:
        """ Lettura parametri in ingresso
            @flag "-i": azioni conosciute dal robot (yaml)
            @flag "-d": macro azioni da eseguire, simulazione
            @flag "-r": utilizza connessione con roboearth
        """
        robot_data = {}
        if "-i" in sys.argv:
            for option, name in INPUT_OPTIONS.iteritems():
                if option in sys.argv:
                    print "+ Loading %s, %s" % (option, name)
                    index = sys.argv.index(option)
                    if option == "-i":
                        filepath = str(sys.argv[index+1])
                        fileExtension = os.path.splitext(filepath)[1]
                        stream = open(filepath, 'r')
                        if fileExtension == '.yaml':
                            robot_data[name] = yaml.load(stream)[name]
                        else:
                            print fileExtension
                            sys.exit(0)
        else:
            raise IndexError
        robot_actions = robot_data["robot_actions"]
        dream()
    except rospy.ROSInterruptException: pass
    except IndexError: print "Wrong parameters, please reboot the service."