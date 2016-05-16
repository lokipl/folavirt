#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import commands
import socket
import sys
import os

from folavirt.console.Colors import Colors

class Snapshot():
    def __init__(self, vgname = None, basename = None, device = None):
        if vgname != None:
            self.vgname = vgname
        if basename != None:
            self.basename = basename
        if device != None:
            self.device = device
       
    def setDeviceByLun(self, lun):
        """
        Ustawia nazwę urządzenia na podstawie lun
        """
        if lun < 1:
            raise Exception('Niepoprawny numer lun')
        
        self.device = self.basename + "_Snapshot_" + str(lun - 1)
            
    def getVolumeGroup(self):
        """
        Zwraca nazwę grupy woluminowej
        
        @param void
        @return Grupa woluminowa
        """
        return self.vgname
    
    def getBase(self):
        """
        Zwraca maszynę bazową
        
        @param void
        @return Nazwa maszyny bazowej
        """
        from folavirt.disks.iscsi.Base import Base
        return Base(self.getVolumeGroup(), self.basename)
    
    def getDevice(self):
        """
        Zwraca ścieżkę urządzenia blokowego
        
        @param void
        @return Urządzenie blokowe
        """
        return "/dev/" + self.getVolumeGroup() + "/" + self.device
    
    def detach(self):
        # Usuwanie z bazy danych
        from folavirt.utils.Database import Database
        database = Database()
        query = "DELETE FROM " + database.getPrefix() + "snapshots WHERE host = '" + socket.gethostname() +"' "
        query += "AND device = '" + self.device + "' AND baselv = '" + self.getBase().getName() + "' "
        query += "AND vgname = '" + self.getVolumeGroup() + "' LIMIT 1"
        
        database.getCursor().execute(query)
        database.commit()
    
    def remove(self):
        """
        Usuwanie snapshota
        
        @param void
        @return void
        """            
        # Usuwanie z bazy danych
        self.detach()
        
        print(Colors.setgreen(" * ") + u"Usunięto snapshot z bazy danych")
        
        # Usuwanie z tgt
        from folavirt.disks.iscsi.Tgt import Tgt
        Tgt().writeConfig()
        
        # Usuwanie urządzenia blokowego
        (status, output) = commands.getstatusoutput("lvremove -f " + self.getDevice())
        if status == 0:
            print(Colors.setgreen(" * ") + u"Usunięto urządzenie blokowe " + self.getDevice())
        else:
            print(Colors.setred(" * ") + u"Błąd podczas usuwania urządzenia blokowego " + self.getDevice())
            print(Colors.setred(" * ") + "Output: "),
            print(str(output).decode("utf8", "ignore"))
            
            if os.path.exists(self.getDevice()):
                from folavirt.utils.Database import Database
                database = Database()
                
                query = "INSERT INTO " + database.getPrefix() + "snapshots(vgname, baselv, host, device) "
                query += "VALUES('" + self.getVolumeGroup() + "', '" + self.getBase().getName() + "', '" + socket.gethostname() + "', '" + self.device + "')"
                
                database.getCursor().execute(query)
                database.commit()
            else:
                print(Colors.setyellow(" * ") + u"Nie ma takiego urządzenia blokowego. Usuwanie z bazy danych")            
        