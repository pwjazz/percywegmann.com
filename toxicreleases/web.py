# Copyright 2012, Percy Wegmann

# This file defines the web-based back-end for triexplore.py

import os
import cherrypy
from cherrypy import tools
from model import Model, ALL

class TriExplorerWeb(object):
    _cp_config = {'tools.staticdir.on' : True,
                  'tools.staticdir.dir' : os.path.abspath(os.path.dirname(__file__)) + '/web',
                  'tools.staticdir.index' : 'index.html'}
    
    def __init__(self):
        self.model = Model()
    
    # Serves up a list of chemicals, which happen to be sorted in descending order by frequency
    @cherrypy.expose
    @tools.json_out()
    def chemicals(self):
        return self.model.chemicals
        
    # Note - I use CherryPy's json_out without knowing it very well.  Hopefully it streams the results
    # rather than building a complete JSON structure in memory.
    @cherrypy.expose
    @tools.json_out()
    def incidents(self, **kwargs):
        chemical = kwargs.get('chemical', ALL)
        perCapita = self.parseBool(kwargs.get('perCapita', 'False'))
        return self.model.incidentsByFipsCodeForChemical(chemical, perCapita)
    
    @cherrypy.expose
    @tools.json_out()
    def poundsReleased(self, **kwargs):
        chemical = kwargs.get('chemical', ALL)
        perCapita = self.parseBool(kwargs.get('perCapita', 'False'))
        return self.model.poundsReleasedByFipsCodeForChemical(chemical, perCapita)
    
    # Utility for parsing a string from the web into a boolean
    def parseBool(self, string):
        return string and string.lower() in ['true', '1', 't', 'y', 'yes']

def run(port):
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = port 
    cherrypy.quickstart(TriExplorerWeb())