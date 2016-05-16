#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import socket
from ConfigParser import ConfigParser

class ClientListener():
    def __init__(self):
        # Czytanie konfiguracji
        parser = ConfigParser()
        parser.readfp(open("../etc/sockets.ini"))
        self.socketpath = parser.get("folavirtd","file")
        
        # Tworzenie gniazda
        self._createSocket()
    
    def getSocket(self):
        """
        Zwraca gniazdo
        
        @return socket
        """
        return self.socket
        
    def _createSocket(self):
        """
        Tworzy gniazdo
        
        """
        # Tworzenie nowego gniazda uniksowego
        self.socket = socket.socket(socket.AF_UNIX)
        
        # Ustawianie opcji gniazda
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        # Powiązanie gniazda z plikiem
        self.socket.bind(self.socketpath)
        
        # Ustawianie uprawnień do gniazda
        os.chmod(self.socketpath, 0777)
        
        # Rozpoczęcie nasłuchiwania
        self.socket.listen(5)
        
    
    