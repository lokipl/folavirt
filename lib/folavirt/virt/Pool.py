#!/usr/bin/env python2
# -*- coding: utf-8 -*-

try:
    import libvirt
except ImportError:
    print(u"! Brak modułu python-libvirt. Niektóre funkcje nie będą działać.")
    
from xml.etree import ElementTree

class Pool():
    def __init__(self, name = None, connection = None):
        self.name = name;
        self.connection = connection;
    
    def _getLibVirtConnection(self):
        """
        Zwraca połączenie z libvirtem
        """
        # Tworzy połączenie tylko raz
        if self.connection == None:
            self.connection = libvirt.open('qemu:///system')
            
        return self.connection
    
    def create(self):
        """
        Uruchamia pule
        """
        # łapanie obiektu puli dyskowej
        pool = self._getLibVirtConnection().storagePoolLookupByName(self.name)
        pool.create(0)
    
    def setName(self, name):
        """
        Ustawia nazwę puli
        
        @param Nazwa
        @return void
        """
        self.name = name
        
    def getName(self):
        """
        Zwraca nazwę puli
        
        @param void
        @return nazwa
        """
        return self.name
    
    def getAddress(self):
        """
        Zwraca adres puli
        
        @param void
        @return adres
        """
        # łapanie obiektu puli dyskowej
        pool = self._getLibVirtConnection().storagePoolLookupByName(self.name)

        # Parsowanie definicji maszyny
        poolxml = ElementTree.fromstring(pool.XMLDesc(0))
        source = poolxml.find(".//source")
        
        host = source.find(".//host")
        # Pobieranie adresu ip
        ip = host.get("name")
        
        device = source.find(".//device")
        # Pobieranie iqn
        iqn = device.get("path")
        
        return "ip-" + ip + ":3260-iscsi-" + iqn
    
    def setAutostart(self):
        """
        Ustawia automatyczne uruchamianie puli
        """
        pool = self._getLibVirtConnection().storagePoolLookupByName(self.name)
        pool.setAutostart(0)
    
    def remove(self):
        """
        Usuwa pule
        """
        # Usuwa pule
        pool = self._getLibVirtConnection().storagePoolLookupByName(self.name)
        pool.destroy()
        try:
            pool.undefine()
        except libvirt.libvirtError as e:
            print(u"Błąd" + str(e))
    
    def refresh(self):
        """
        Odświeża pule
        """
        try:
            self._getLibVirtConnection().storagePoolLookupByName(self.name).refresh(0)
            return 0
        except:
            print(u"Błąd odswiezania puli " + self.name)
            return -1
        
    def listVolumes(self):
        """
        Zwraca listę woluminów
        """
        try:
            return self._getLibVirtConnection().storagePoolLookupByName(self.name).listVolumes()
        except:
            print(u"Błąd pobierania listy woluminów z puli " + self.name)
            return []