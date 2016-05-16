#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import socket

from folavirt.networking.Response import Response

class TcpClient():
    def __init__(self):
        pass
    
    def connect(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((address, port))
        except socket.error:
            raise Exception("Error while connecting to remote " + address + ":" + str(port))
        
    def write(self, message):
        # Wysyła tekst do gniazda
        self.socket.sendall(message)
    
    def execute(self, query):
        """
        Wykonuje zapytania i oczekuje na odpowiedź. Zwraca odpowiedź
        
        @param Query
        @return Response
        """
        # Zapisuje dane do gniazda
        self.write(query.getJSON())

        data = ""
        while True:
            data += self.socket.recv(16384)
            
            try:
                json.loads(data)
                break
            except:
                pass
        
        # Tworzy obiekt odpowiedzi
        r = Response()
        r.setFromJSON(data)
        
        # Zwraca odpowiedź
        return r
        
    def quit(self):
        """
        Kończy połączenie
        
        @param void
        @return void
        """
        # Wysyła do obiorcy polecenie quit
        self.write("quit")
        # Zamyka gniazdo
        self.socket.close()