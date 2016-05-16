#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import socket

from folavirt.networking.TcpClient import TcpClient

class RemoteObject():
    """
    Zdalny obiekt
    """
    def __init__(self):
        pass
    
    address = ""
    hostname = ""
    port = 7050
    
    tcp = 0
    
    def setAddress(self,address):
        self.address = address
    def getAddress(self):
        return self.address

    def setPort(self, port):
        """
        Ustawia port
        
        @param int
        @return void
        """
        self.port = port
    def getPort(self):
        return self.port
    
    def setHost(self, host):
        """
        Ustawia danę, biorąc za parametr obiekt host
        
        @param Host
        @return void
        """
        self.setAddress(host.getAddress())
        self.setPort(host.getPort())
    
    def establish(self):   
        """
        Zestawia połączenie z hostem jeśli jest taka potrzeba
        
        @param void
        @return void
        """    
        if self.tcp == 0:
            self.tcp = TcpClient()
            self.tcp.connect(self.getAddress(), self.getPort())
            
    def execute(self, q):
        """
        Wykonuje zapytanie
        
        @param void
        @return folavirt.networking.Response
        @raise exception:  Gdy nie powiodło się wykonanie zapytania
        """
        try:
            self.establish()
        except Exception:
            return -1
            
        try:
            r = self.tcp.execute(q)
            return r
        except ValueError:
            # Zamykanie połączenia
            if self.tcp != 0:
                self.quit()
            raise Exception('Zapytanie nie zostało wykonane!')
    
    def quit(self):
        """
        Zamyka połączenie
        """
        self.tcp.quit()