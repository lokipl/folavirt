#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import base64
import ConfigParser

from folavirt.networking.Response import Response
from folavirt.virt.Host import Host

class VmResponse():
    def __init__(self, q):
        self.q = q
        
        parser = ConfigParser.ConfigParser()
        parser.read("../etc/folavirt.ini")
        
        self.uri = parser.get("libvirt", "uri")
        
    def getResponse(self):
        if self.q.getCommand() == 'definexml':
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand('definexml')
            
            # Odbieranie definicji maszyny
            xmldesc = base64.b64decode(self.q.getData())
            
            # Definiowanie maszyny wirtualnej
            out = Host().definexml(xmldesc)
            r.setData(out)
            
            return r
            
        if self.q.getCommand() == 'undefinebyname':
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand('undefinebyname')
            
            # Usuwanie maszyny
            Host(self.uri).undefineByName(self.q.getData())
            
            return r
        
        if self.q.getCommand() == "virsh":
            r = Response()
            r.setCommand("virsh")
            r.setData(Host(self.uri).executeVirsh(self.q.getData()))
            
            return r
        
        return None