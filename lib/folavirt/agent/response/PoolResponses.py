#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from folavirt.networking.Response import Response
from folavirt.virt.Host import Host
from folavirt.virt.Pool import Pool

class PoolResponses():
    def __init__(self, q):
        self.q = q
        self.uri = 'qemu:///system'
        
    def getResponse(self):
        # Lista puli dyskowych
        if self.q.getCommand() == "getpools":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("getpools")
            
            # Host
            host = Host(self.uri)
            # Pobieranie pul
            r.setData([pool.getName() for pool in host.getPools()])
            
            return r
        
        # Lista woluminów w puli dyskowej
        if self.q.getCommand() == "getpoolvolumes":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand('getpoolvolumes')
            
            # Pobieranie listy woluminów
            pool = Pool(self.q.getData())
            r.setData(pool.listVolumes());
            
            return r
        
        # Adres ip puli
        if self.q.getCommand() == "getpooladdress":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("getpooladdress")
            
            # Pobieranie adresu ip
            pool = Pool(self.q.getData())
            r.setData(pool.getAddress())
        
            return r
        return None