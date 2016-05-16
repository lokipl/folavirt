#!/usr/bin/env python2
# -*- coding: utf-8 -*-

try:
    import ipaddr
except ImportError:
    print(u"Brak modułu python-ipaddr")
    import sys
    sys.exit(0)
    
from ConfigParser import ConfigParser

class Network():
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("../etc/folavirt.ini")
        
        self.networkaddress = self.config.get("folavirt", "network")
        self.network = ipaddr.IPv4Network(self.networkaddress)
        self.localnetwork = ipaddr.IPv4Network("127.0.0.1/8")
        
    def contains(self, address):
        ip = ipaddr.IPv4Address(address)
        
        return self.network.Contains(ip)
    
    def allowed(self, address):
        ip = ipaddr.IPv4Address(address)
        
        if self.localnetwork.Contains(ip):
            return True
        
        if self.network.Contains(ip):
            return True
        
        return False