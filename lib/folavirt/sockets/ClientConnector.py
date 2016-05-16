#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import socket
from ConfigParser import ConfigParser

class ClientConnector():
    def __init__(self):
        # Czytanie konfiguracji
        parser = ConfigParser()
        parser.readfp(open("../etc/sockets.ini"))
        self.socketpath = parser.get("folavirtd","file")
        
        # Tworzenie nowego gniazda
        self._createSocket()
        
    def getSocket(self):
        """
        Zwraca gniazdo
        
        @param void
        @return void
        """
        return self.socket    
    
    def _createSocket(self):
        """
        Tworzenie nowego gniazda, tworzenie połączenia
        
        @param void
        @return void
        """
        # Tworzenie gniazda uniksowego
        self.socket = socket.socket(socket.AF_UNIX)
        
        # Łączenie z gniazdem
        self.socket.connect(self.socketpath)
        
    def sendQuery(self, query):
        """
        Wysyłanie zapytania
        
        @param folavirt.networking.Query
        @return void
        """
        self.socket.sendall(query.getJSON())
        
    def sendQueryAndReceive(self, query):
        """
        Wysyła zapytanie i czeka na odpowiedź
        
        @param folavirt.networking.Query
        @return void
        """
        # Wysyłanie zapytania
        self.sendQuery(query)
        # Oczekiwanie na odpowiedź
        response = self.socket.recv(4096)
        
        return response