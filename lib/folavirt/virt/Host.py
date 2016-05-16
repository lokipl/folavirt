#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import commands
try:
    import libvirt
except ImportError:
    pass

from folavirt.virt.Pool import Pool
from folavirt.virt.Domain import Domain

class Host():
    """
    Host wirtualizacyjny
    Domyślne uri - kvm => qemu:///system
    """
    def __init__(self, uri = 'qemu:///system'):
        self.uri = uri
    
    def libvirtTest(self):
        try:
            libvirt.open(self.uri)
            return True
        except:
            return False
    
    def executeVirsh(self, command):
        command = command.replace(";","")
        c = commands.getoutput("virsh -c " + self.uri + " " + command)
        return c        
    
    def undefineByName(self, name):
        """
        Usuwa maszynę wirtualną na podstawie jej nazwy
        
        @param nazwa
        @return void
        """
        # Połączenie z libvirtem
        connection = libvirt.open(self.uri)
        
        # Zwraca obiekt domeny
        domain = connection.lookupByName(name)
        
        # Zatrzymuje domenę
        try:
            domain.destroy()
        except:
            pass
        
        # Usuwa definicję domeny
        domain.undefine()
    
    def getDomains(self):
        """
        Zwraca listę domen
        """
        # Połączenie z libvirtem
        connection = libvirt.open(self.uri)
        
        # Pobranie zdefiniowanych domen
        domainnames = connection.listDefinedDomains()
        
        domains = []
        for domainid in domainnames:
            dom = connection.lookupByName(domainid)
            domain = Domain(self.uri, dom.name())
            
            domarray = {}
            domarray['name'] = domain.getName()
            domarray['state'] = domain.getState()
            
            domains.append(domarray)
        
        # Pobranie pozostałych domen
        domainids = connection.listDomainsID()
        for domainid in domainids:
            dom = connection.lookupByID(domainid)
            domain = Domain(self.uri, dom.name())
            
            domarray = {}
            domarray['name'] = domain.getName()
            domarray['state'] = domain.getState()
            
            domains.append(domarray)
        
        return domains
    
    def definexml(self, xmldesc):
        """
        Definiuje maszynę wirtualną
        
        @param xml
        @return void
        """
        # Połączenie z libvirtem
        connection = libvirt.open(self.uri)
        
        # Definicja maszyny
        try:
            connection.defineXML(xmldesc)
            return 0
        except libvirt.libvirtError as e:
            return str(e)
    
    def getPools(self):
        """
        Zwraca pule dyskowe
        """
        # Połaczenie z libvirt
        connection= libvirt.open(self.uri)
        
        pools = []
        # Pobranie zdefiniowanych pul, m.in nieuruchomione pule
        for poolname in connection.listDefinedStoragePools():
            pool = Pool()
            pool.setName(poolname)
            
            pools.append(pool)
            
        # Pobieranie z listy pul
        for poolname in connection.listStoragePools():
            pool = Pool()
            pool.setName(poolname)
            
            pools.append(pool)
            
        return pools