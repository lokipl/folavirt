#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import libvirt
from xml.etree import ElementTree
from ConfigParser import ConfigParser

from folavirt.virt.Pool import Pool
from folavirt.virt.Host import Host

class ImportIscsiPool():
    """
    Zarządzanie pulami dyskowymi iscsi
    """
    def __init__(self, iscsilist, removeold = False):
        self.config = ConfigParser()
        self.config.read("../etc/folavirt.ini")
        
        # Pobieranie listy pul dyskowych
        host = Host(self.config.get("libvirt", "uri"))
        pools = host.getPools()
        self.pools = [pool.getName() for pool in pools]
        
        # Wszystkie pule jakie są dynamiczne
        self.dynamicpools = []
        # Pule dodane
        self.added = []
        
        # Przeszukiwanie listy w poszukiwaniu baz do zdefiniowania
        self.handleBases(iscsilist['base'])
        
        # Przeszukiwanie listy w poszukiwaniu snapshotów do zdefiniowania
        self.handleSnapshots(iscsilist['snapshot'])
        
        # Pule usunięte
        self.removed = []
        
        if removeold:
            # Usuwa nieużywane pule
            self.removeold(host.getPools())
        
        # Odśwież wszystkie pule
        self.refreshPools(host.getPools())
    
    connection = None
    def _getLibVirtConnection(self):
        """
        Zwraca połączenie z libvirtem
        """
        # Tworzy połączenie tylko raz
        if self.connection == None:
            self.connection = libvirt.open(self.config.get("libvirt", "uri"))
            
        return self.connection
    
    def _getPoolXml(self, name, address, iqn):
        """
        Zwraca definicję XML
        """
        # Tworzenie XML
        poolxml = ElementTree.Element('pool')
        poolxml.set('type', 'iscsi')
                
        # Nazwa
        nameelement = ElementTree.SubElement(poolxml, 'name')
        nameelement.text = name
                
        # Zródło
        source = ElementTree.SubElement(poolxml, 'source')
        host = ElementTree.SubElement(source, 'host')
        host.set('name', address)
        device = ElementTree.SubElement(source, 'device')
        device.set('path', iqn)
                
        # target
        target = ElementTree.SubElement(poolxml, 'target')
        path = ElementTree.SubElement(target, 'path')
        path.text = '/dev/disk/by-path'
        
        return ElementTree.tostring(poolxml)
    
    def handleBases(self, baselist):
        """
        Przetwarza definiowanie baz
        
        @param list
        @return void
        """
        for basedefinition in baselist:
            # Możliwa nazwa puli w lokalnym systemie
            localpoolname = "Folavirt-ISCSI-base-" + basedefinition['address'].replace('.','_') + "-" + basedefinition['iqn']
            self.dynamicpools.append(localpoolname)
            
            # Czy jest taka pula
            if not (localpoolname in self.pools):
                # generowanie  definicji XML
                poolxml = self._getPoolXml(localpoolname, basedefinition['address'], basedefinition['iqn'])
                
                # Dodawanie puli
                try:
                    self._getLibVirtConnection().storagePoolCreateXML(poolxml, libvirt.VIR_STORAGE_POOL_BUILD_NEW)
                    pool = Pool(localpoolname, self._getLibVirtConnection())
                
                    self.added.append(localpoolname)
                except:
                    pass
            else:
                # Odświeżanie puli
                pool = Pool(localpoolname, self.connection)
                pool.refresh()
        
    def handleSnapshots(self, snapshotlist):  
        """
        Przetwarza definiowanie snapshotów
        
        @param list
        @return void
        """      
        for snapshotdefinition in snapshotlist:
            # Nazwa puli w lokalnym systemie
            localpoolname = "Folavirt-ISCSI-snapshot-" + snapshotdefinition['address'].replace('.','_') + "-" + snapshotdefinition['iqn']
            self.dynamicpools.append(localpoolname)
            
            # Czy jest taka pula
            if not (localpoolname in self.pools):
                # generowanie definicji XML
                poolxml = self._getPoolXml(localpoolname, snapshotdefinition['address'], snapshotdefinition['iqn'])
                
                # Dodawanie puli do zarządcy
                try:
                    self._getLibVirtConnection().storagePoolCreateXML(poolxml, libvirt.VIR_STORAGE_POOL_BUILD_NEW)
                    pool = Pool(localpoolname, self._getLibVirtConnection())
                    
                    self.added.append(localpoolname)
                except:
                    pass
            else:
                # Odświeżanie puli
                pool = Pool(localpoolname, self.connection)
                pool.refresh()
    
    def removeold(self, pools):
        """
        Usuwa nieużywane pule
        
        @param lista puli
        @return void
        """
        # Szukanie pul do usuniecia
        for pool in pools:
            # Przeglądanie tylko pul z nazwą Folavirt-*
            if pool.getName().startswith("Folavirt-"):
                if not pool.getName() in self.dynamicpools:
                    # Dodawanie do tablicy usuniętych
                    self.removed.append(pool.getName())
                    # Usuwanie puli
                    pool.remove()
                
    def refreshPools(self, pools):
        """
        Odświeża wszystkie pule
        
        @param void
        @return void
        """
        for pool in pools:
            pool.refresh()
        