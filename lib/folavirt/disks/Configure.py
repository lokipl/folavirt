#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import socket

from folavirt.utils.TableCreator import TableCreator
from folavirt.utils.Database import Database

class Configure():
    def __init__(self):
        # Nazwa tabeli przechowującej woluminy logiczne
        self.tablename = 'volumegroups';
        # Tworzy tabelę jeśli nie ma w bazie danych
        TableCreator().createVolumeGroupsTableIfNeeded(self.tablename)
        self.database = Database()
        
    def addVolumeGroup(self, vgname):
        """
        Dodawanie woluminu logicznego do systemu
        
        @param Wolumin logiczny
        """
        query = "INSERT INTO " + self.database.getPrefix() + self.tablename + "(vgname, host) VALUES('" + vgname + "', '" + socket.gethostname()  + "')"
        
        self.database.getCursor().execute(query)
        self.database.commit()
    
    def deleteVolumeGroup(self, vgname):
        """
        Usuwanie woluminu logicznego z systemu
        
        @param Wolumin logiczny
        """
        
        query = "DELETE FROM " + self.database.getPrefix() + self.tablename + " WHERE vgname='" + vgname + "' AND host = '" + socket.gethostname() + "';"
        
        self.database.getCursor().execute(query)
        self.database.commit()
        
    def getVolumeGroupList(self):
        """
        Zwraca listę woluminów logicznych
        
        @param void
        @return Lista
        """
        query = "SELECT vgname FROM " + self.database.getPrefix() + self.tablename + " WHERE host = '" + socket.gethostname() + "';"
        
        self.database.getCursor().execute(query)
        result = self.database.getCursor().fetchall()
        
        return [x[0] for x in result]