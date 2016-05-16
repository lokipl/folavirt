#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys

from folavirt.remote.RemoteObject import RemoteObject
from folavirt.networking.Query import Query
from folavirt.console.Colors import Colors

def getDms():
    """
    Zwraca listę zarządców dyskami z pliku konfiguracyjnego
    
    @param void
    @return list
    """
    if not os.path.exists("../etc/disks"):
        print(Colors.setred(" * ") + u"Nie skonfigurowano zarządców dysków")
        sys.exit(1)
    
    f = open("../etc/disks")
    
    if not os.path.exists("../etc/disks"):
        return False
    
    dms = []
    diskdefs = f.readlines()
    for diskdef in diskdefs:
        if diskdef[0] == "#":
            continue
        
        # dzielenie ciągu na definicje
        elements = diskdef.split()
        
        try:
            # Tworzenie obiektu managera dysków
            dm = DiskManager()
            dm.address = elements[1]
            dm.name = elements[0]
            dm.port = int(elements[2])
        
            # Dodawanie do listy
            dms.append(dm)
        except IndexError:
            pass
    
    return dms

def getDmByBaseName(baselv):
    """
    Szuka zarządcy dysków na którym jest podana baza
    """
    dms = getDms()
    for dm in dms:
        if not dm.ping():
            print(Colors.setred(" * ") + u"Brak połączenia z zarządcą dysków " + dm.getName())
            continue
        
        for base in dm.getBaseVolumes():
            if base == baselv:
                return dm
            
    raise Exception(u"Nie znaleziono takiego woluminu bazowego")

class DiskManager(RemoteObject):
    def __init__(self):
        self.name = ""
    
    def getName(self):
        """
        Zwraca nazwę
        
        """
        return self.name
    
    def ping(self):
        """
        Wysyła ping
        """
        # Tworzenie zapytania
        q = Query("ping")
        
        try:
            r = self.execute(q)
            if r.getCommand() == "pong":
                return True
        except:
            return False
        
        return False
    
    def getBaseIqn(self):
        """
        Zwraca puli bazowej
        """
        # Tworzenie zapytania
        q = Query("getbaseiqn")
        
        # Wykonywanie zapytania
        r = self.execute(q)
        
        return r.getData()
    
    def getBaseDiskSourceDev(self):
        """
        Zwraca adres do zasobu iscsi do wykorzystania w definicji bazowej maszyny wirutalnej
        
        @param 
        @return str
        """
        return "ip-" + self.getAddress() + ":3260-iscsi-" + self.getBaseIqn()
    
    def getBaseVolumes(self):
        """
        Zwraca woluminy bazowe dostępne na tym zarządcy dyskami
        """
        # Tworzenie zapytania
        q = Query("getbasevolumes")

        # Wykonywanie zapytania
        r = self.execute(q)
        
        return r.getData()
    
    def removeSnapshot(self, baselv, lun):
        """
        Usuwanie snapshotu na podstawie nazwy woluminu 
        """
        # Tworzenie zapytania
        q = Query("removeparticualsnapshot", {'baselv': baselv, 'lun': lun})
        # Wykonanie zapytania
        r = self.execute(q)
        
        return r
    
    def removeSnapshotByBase(self, baselv):
        """
        Usuwa wszystkie snapshoty odnośnie bazy
        
        @param Nazwa bazy
        @return Ile usunięto
        """
        # Tworzenie zapytania
        q = Query()
        q.setCommand("removebasesnapshot")
        q.setData(baselv)
        
        # Wykonywanie zapytania
        r = self.execute(q)
        
        return r.getData()
    
    def createSnapshot(self, baselv, size = 2):
        """
        Tworzy snapshot
        
        @param Nazwa bazy
        @param Wielkość w GB
        @return void
        """
        # Tworzenie zapytania
        q = Query()
        q.setCommand("createsnapshot")
        q.setData({'base':baselv, 'size': size})
        
        # Wykonywanie zapytania
        r = self.execute(q)
        
        if r.getErrorCode() == 1:
            return False
        if r.getErrorCode() == 0:
            return True