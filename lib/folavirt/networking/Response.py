#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json

class Response():
    def __init__(self, command = "", data = {}):
        self.command = command
        self.data = data
    
    errorcode = 0
    data = {}
    command = ""
    
    def setErrorCode(self, code):
        self.errorcode = code
    
    def getErrorCode(self):
        return self.errorcode
        
    def setData(self, array):
        self.data = array
        
    def getData(self):
        return self.data
        
    def setCommand(self, command):
        self.command = command
        
    def getCommand(self):
        return self.command
    
    def getJSON(self):
        retarray = {}
        retarray['errorcode'] = self.errorcode
        retarray['data'] = self.data
        retarray['command'] = self.command
        
        return json.dumps(retarray)
    
    def setFromJSON(self, jsondata):
        retarray = json.loads(jsondata)
        
        self.errorcode = retarray['errorcode']
        self.data = retarray['data']
        self.command = retarray['command']
    