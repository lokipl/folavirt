#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import socket
import commands

from folavirt.utils.TableCreator import TableCreator
from folavirt.utils.Database import Database
from folavirt.console.Colors import Colors
from folavirt.disks.iscsi.Snapshot import Snapshot

class Snapshots():
    def __init__(self, vgname = None, basename = None, device = None):
        # Nazwa tabeli w bazie danych
        self.tablename = "snapshots"
        self.database = Database()
        
        self.vgname = vgname
        self.basename = basename
        self.device = device
        
        # Tworzenie tabeli snapshotów jeśli jest taka potrzeba
        TableCreator().createSnapshotTableIfNeed(self.tablename)
    
    def getList(self):
        """
        Zwraca liste snapshotów
        
        @param void
        @return Lista obiektów folavirt.disks.iscsi.Snapshot
        """
        query = "SELECT vgname, baselv, device FROM " + self.database.getPrefix() + self.tablename + " WHERE host = '" + socket.gethostname() + "' ORDER BY baselv,device"
        self.database.getCursor().execute(query)
        
        snapshots = []
        # Tworzenie z wyniku zapytania listy obiektów 
        for row in self.database.getCursor().fetchall():
            snapshots.append(Snapshot(row[0], row[1], row[2]))
            
        return snapshots
    
    def attach(self, base, dev):
        # Zapis snapshota do bazy danych
        query = "INSERT INTO " + self.database.getPrefix() + self.tablename + "(vgname, baselv, host, device) "
        query += "VALUES('" + base.getVolumeGroup() + "', '" + base.getName() + "', '" + socket.gethostname() + "', '" + dev + "')"
        
        self.database.getCursor().execute(query)
        self.database.commit()
    
    def createFromBase(self, base, size):
        """
        Tworzy snapshot
        
        @param Baza
        @param Wielkość snapshotu
        @return void
        """
        size = str(size)
        
        # Sprawdzanie czy podano jednostki, jeśli nie, dodawanie gigabajtów
        if size[-1:].isdigit():
            size += "G"        
        
        number = base.getLastSnapshotNumber()
        # Nazwa urządzenia blokowego
        devicename = base.getName() + "_Snapshot_" + str(number)
        
        # Komenda do tworzenia snapshota
        command = "lvcreate -L " + str(size) + "G -s -n " + devicename + " " + base.getDevice()  
  
        # Wykonywanie snapshota  
        (status, output) = commands.getstatusoutput(command)
        if status == 0:
            # Jeśli się powiodło
            print(Colors.setgreen(" * ") + u"Utworzono urządzenie blokowe " + devicename)
            
            # Zapis snapshota do bazy danych
            query = "INSERT INTO " + self.database.getPrefix() + self.tablename + "(vgname, baselv, host, device) "
            query += "VALUES('" + base.getVolumeGroup() + "', '" + base.getName() + "', '" + socket.gethostname() + "', '" + devicename + "')"
            
            self.database.getCursor().execute(query)
            self.database.commit()
            
            return True
        else:
            # Komunikat o błędzie
            print(Colors.setred(" * ") + u"Utworzenie urządzenia blokowego nie powiodło się")
            print(Colors.setred(" * ") + output)
            return False
    
    def getSnapshotByDevice(self, device):
        """
        Zwraca obiekt snapshota szukają go w bazie po urządzeniu blokowym
        
        @param Urządzenie blokowe
        @return void
        @raise exception: Gdy nie znaleziono snapshota 
        """
        vg = device.split("/")[2]
        dev = device.split("/")[3]
        
        query = "SELECT vgname, baselv, device FROM " + self.database.getPrefix() + self.tablename + " WHERE device = '" + dev + "' AND vgname = '" + vg + "' AND host = '" + socket.gethostname() + "';"
        self.database.getCursor().execute(query)
        
        result = self.database.getCursor().fetchall()
        try:
            return Snapshot(result[0][0], result[0][1], result[0][2])
        except IndexError:
            # Nie znaleziono takiego snapshota
            raise Exception('Nie znaleziono snapshota w bazie danych')
        
        
