#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import re
import sys

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class Params():
    """
    Przetwarzanie parametrów
    
    @see Singleton
    """
    def __init__(self):
        self.parseArgv()
        
    def parseArgv(self):
        """
        Parsuje argumenty
        
        @param void
        @return void
        """
        self.script = sys.argv[0]
        self.args = []
        self.parameters = []
            
        for arg in sys.argv[1:]:
            if re.search('^[a-zA-Z0-9/]', arg):
                self.args.append(arg)
                continue
            if re.search('^--',arg):
                self.parameters.append(arg)
                continue
            
    def getArg(self, number):
        """
        Zwraca argument
        
        @param id
        @return wartość
        """
        if (number+1) > len(self.args):
            return ""
        
        return self.args[number]
    
    def getAllArgsFrom(self, number):
        """
        Zwraca wszystkie argumenty rozpoczynając od
        
        @param id
        @return wartość
        """
        if (number+1) > len(self.args):
            return ""
        
        return " ".join(self.args[number:])
    
    def getArgList(self, number):
        """
        Zwraca tablicę podargumentów
        """
        # Sprawdzanie czy po przecinku są argumenty
        splitted = self.getArg(number).split(',')
        
        return splitted
    
    def getArgNumberList(self, number):
        """
        Zwraca argument jako określenie zakresu liczb
        
        @param id
        @return []
        """
        numbers = []
        
        # Sprawdzanie jest zwykłą cyfrą
        try:
            number = int(self.getArg(number))
            numbers.append(number)
        except ValueError:
            pass
            
        # Sprawdzanie czy jest zakresem
        splitted = self.getArg(number).split("-")
        if len(splitted) == 2:
            numbers += range(int(splitted[0]), int(splitted[1])+1)
    
        # Sprawdzanie czy są listą
        splitted = self.getArg(number).split(",")
        if len(splitted) >= 2:
            for split in splitted:
                numbers.append(split)
    
        return numbers
    
    def isParameter(self, name):
        """
        Sprawdza czy został dodany parametr
        
        @param nazwa
        @return Bool
        """
        if "--"+name in self.parameters:
            return True
        
        return False
    
    def argLen(self):
        """
        Zwraca ilość argumentów
        
        @param void
        @return int
        """
        return len(self.args)
    
    def getScriptName(self):
        """
        Zwraca nazwę skryptu
        
        @param void
        @return nazwa
        """
        return os.path.basename(self.script)
    
    def setStdoutToNull(self):
        """
        Sprawdza czy ustawiono parametr silent i gdy tak, ustawia domyślne wyjście na dev null
        """
        if self.isParameter("silent"):
            devnull = open('/dev/null','w')
            sys.stdout = devnull