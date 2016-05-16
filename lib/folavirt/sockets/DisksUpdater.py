#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import socket

from ConfigParser import ConfigParser

from folavirt.console.Path import Path

class DisksUpdater():
    def __init__(self):
        parser = ConfigParser()
        parser.readfp(open("../etc/folavirt.ini"))
        self.socketpath = parser.get("foladiskd","file")
        
        self.connect()
        
    def connect(self):
        """
        łączy się z gniazdem
        """
        self.socket = socket.socket(socket.AF_UNIX)
        # Parsuje w poszukiwaniu zmiennych
        socketpath = Path().parseValues(self.socketpath)
        self.socket.connect(socketpath)
        self.socket.settimeout(3)
        
    def getSocket(self):
        """
        Zwraca gniazdo
        
        @param void
        @return socket
        """
        return self.socket

    def sendUpdate(self):
        # Wysłanie komunikatu o aktualizacji avahi
        self.getSocket().sendall("UPDATE")