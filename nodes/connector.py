#!/usr/bin/env python

""" Questo script si connette e interfaccia al server di Roboearth:
    1) Sottomette una query semantica, tramite POST data
    2) Estrapola l'action recipe dal risultato json
    3) Effettua il parsing della risorsa OWL tramite rdflib
    4) Ritorna la sequenza della subazioni ordinate

    @extra requests: gestisce la connessione POST
    @extra rdflib:   effettua parsing della risorsa OWL
    @extra json:     codifica e decodifica risorse json
"""

import rdflib, requests, json, sys, os
from requests.exceptions import RequestException

DEFAULT_QUERY = "manouver"

def get_subactions(g, ordering=True):
    result = []
    reset_n = {
                True: 0,
                False: 1
              }
    n = reset_n[ordering]
    action = ""    
    for subj, pred, obj in g:
        if ordering:
            if "#Annotation" in pred:
                n = [x for x in obj if x.isdigit()][0]
        if "#someValuesFrom" in pred:
            action = obj.split("#")[1] 
        if n != 0 and action != "":
            t = n, action
            n = reset_n[ordering]
            action = ""
            result.append(t)
    result.sort()
    return result  


def connect_to_roboearth(query=DEFAULT_QUERY):
    print "+ Connecting to roboearh..."
    url = "http://api.roboearth.org/api/recipe"
    query_wrapper = "SELECT source FROM CONTEXT source {x} rdfs:label {L} where L LIKE \"*%s*\"" % query
    print query_wrapper 
    payload = { "query" : query_wrapper }
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        r.raise_for_status()
    except RequestException:
        print "+ We noticed the following error: %s. Exiting." % r.status_code
        return None

    print "+ Data received, parsing the rdf..."

    recipe = r.json[0]['recipes'][0]['recipe']

    g = rdflib.Graph()
    g.parse(data=recipe, format="application/rdf+xml")
    s = g.serialize(format='n3')
    result = get_subactions(g, "owl:Annotation" in s)
    print "Done."
    return [r[1] for r in result]

if __name__ == "__main__":
    LOG_PATH = "/home/flavio/Tesi-Magistrale/app/Recipes/log"
    if len(sys.argv) > 1:
        result = connect_to_roboearth(sys.argv[1])
    else:
        result = connect_to_roboearth()
    f = open(LOG_PATH, 'w') # Debug
    for t in result:
        f.write(str(t))
        f.write("\n")
    f.close()