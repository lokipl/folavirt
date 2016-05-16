#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from folavirt.remote.RemoteObject import RemoteObject
from folavirt.networking.Query import Query

class Pool(RemoteObject):
    def __init__(self, name = None, tcp = None):
        self.name = name

        if tcp != None:
            self.tcp = tcp   
        
    def getIscsiAddress(self):
        """
        Zwraca adres
        """
        # Tworzenie zapytania
        q = Query('getpooladdress', self.name)
        
        # Wykonywanie zapytania
        r = self.execute(q)
        
        return r.getData()
        
    def getVolumes(self):
        """
        Zwraca listę pul
        """
        # Zapytanie
        q = Query('getpoolvolumes', self.name)
        r = self.execute(q)
        
        return r.getData()
        
    def getType(self):
        """
        Zwraca typ
        """
        splitted = self.name.split("-")
        
        # Pula dynamiczna
        if splitted[0] == "Folavirt":
            if splitted[2] == "base":
                return "dynamic-base"
            if splitted[2] == "snapshot":
                return "dynamic-snapshot"
            
            return "dynamic"
        else:
            return "static"
        
    def getName(self):
        """
        Zwraca nazwę puli
        """
        return self.name