#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json

class Query():
    """
    Zapytanie
    
    @author: michal
    @group folavirt.networking: 
    """
    def __init__(self, command = "", array = {}):
        self.command = command
        self.array = array
    
    command = ""
    array = {}
    
    def setCommand(self, command):
        """
        Ustawia polecenie
        
        @param Polecenie
        """
        self.command = command
    
    def getCommand(self):
        """
        Zwraca polecenie
        
        @param void
        @return Polecenie
        """
        return self.command
    
    def setData(self, array):
        self.array = array
      
    def getData(self):
        return self.array
        
    def getJSON(self):
        retarray = {}
        retarray['command'] = self.command
        retarray['data'] = self.array
        
        return json.dumps(retarray)

    def setFromJSON(self, jsondata):
        retarray = json.loads(jsondata)
        
        self.command = retarray['command']
        self.array = retarray['data']
