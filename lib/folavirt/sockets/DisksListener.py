#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import socket
from ConfigParser import ConfigParser

from folavirt.console.Path import Path

class DisksListener():
    def __init__(self):
        parser = ConfigParser()
        parser.readfp(open("../etc/folavirt.ini"))
        self.socketpath = parser.get("foladiskd","file")

    def create(self):
        # Pobiera ścieżkę do gniazda, parsuje w poszukiwaniu zmiennych
        socketpath = Path().parseValues(self.socketpath)
        
        # Usuwanie gniazda jeśli istnieje
        if os.path.exists(socketpath):
            os.remove(socketpath)
        
        # Utworzenie uniksowego gniazda
        self.socket = socket.socket(socket.AF_UNIX)
        # Opcje gniazda
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # Ścieżka do gniazda
        self.socket.bind(socketpath)
        # Ustawienie uprawnień
        os.chmod(socketpath, 0777)
        
        self.socket.listen(5)
        
    def getSocket(self):
        return self.socket