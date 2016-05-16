#!/usr/bin/env python2
# -*- encoding: utf-8

import os
import sys

class Path():
    """
    Przetwarzanie ścieżek
    """
    def __init__(self):
        # Szukanie scieżki głównej aplikacji
        path = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.folavirtpath = os.path.abspath(path + "/../")
    
    def parseValues(self, path):
        """
        Parsuje ciąg w poszukiwaniu zmiennych
        
        @param str
        @return str
        """
        p = path.replace('$APPPATH', self.folavirtpath)
        
        return p