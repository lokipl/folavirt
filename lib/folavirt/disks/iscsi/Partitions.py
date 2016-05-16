#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import commands
import socket

from folavirt.console.Colors import Colors
from folavirt.utils.TableCreator import TableCreator
from folavirt.utils.Database import Database
from folavirt.disks.iscsi.Base import Base
from folavirt.sockets.DisksUpdater import DisksUpdater

class Partitions():
    def __init__(self):
        self.tablename = "basedisks"
        TableCreator().createBaseDisksTableIfNeeded(self.tablename)
        self.database = Database()
    
    def attachBase(self, vg, name):
        """
        Dodaje wolumin do bazy danych
        """
        # Dodawanie maszyny bazowej do bazy danych
        query = "INSERT INTO " + self.database.getPrefix() + self.tablename + "(vgname, baselv, host) "
        query += "VALUES('" + vg + "', '" + name + "', '" + socket.gethostname() + "');"
        
        # Wykonywanie zapytania
        self.database.getCursor().execute(query)
        self.database.commit()
        
    
    def createBase(self, vg, name, size):
        """
        Tworzy obraz dysku maszyny bazowej
        
        @param Grupa woluminowa
        @param Nazwa
        @param Wielkość (w GB)
        """
        size = str(size)
        
        # Sprawdzanie czy podano jednostki, jeśli nie, dodawanie gigabajtów
        if size[-1:].isdigit():
            size += "G"
        
        # Polecenie 
        command = "lvcreate -L "+str(size) + "G -n " + name + " " + vg
        # Wykonanie polecenia
        (status, output) = commands.getstatusoutput(command)
        if (status == 0):                        
            # Dodaje bazę do mysql
            self.attachBase(vg, name)
            
            # Uaktualnienie Aavahi
            try:
                DisksUpdater().sendUpdate()
            except Exception:
                print(Colors.setred(" * ") + u"Błąd podczas odświeżania Avahi.")

            return True
        else:
            print(Colors.setred(" * ") + u"Tworzenie systemu bazowego nie powiodło się na poziomie tworzenia partycji")
            print(Colors.setred(" * ") + u"Komenda: ".ljust(12) + command)
            print(Colors.setred(" * ") + u"Komunikat: ".ljust(12) + output)
            
            return False

    def detachBase(self, vg, name):
        """
        Usuwa obraz dysku bazowego z bazy danych
        
        @param Grupa woluminowa
        @param Nazwa
        """
        # Sprawdza czy istnieje taki wolumin
        if not name in [volume.getName() for volume in self.getBaseList(vg)]:
            return False
        
        # Usuwanie bazy z bazy danych
        query = "DELETE FROM " + self.database.getPrefix() + self.tablename + " WHERE vgname = '" + vg + "' AND baselv = '" + name + "' AND host = '" + socket.gethostname() + "' LIMIT 1"
        self.database.getCursor().execute(query)
        self.database.commit()
        
        return True

    def removeBase(self, vg, name):
        """
        Usuwa obraz dysku bazowego
        
        @param Grupa woluminowa
        @param Nazwa
        """                    
        # Usuwanie z LVM
        (status, output) = commands.getstatusoutput("lvremove -f /dev/" + vg + "/" + name)
        if status == 0:
            # Uaktualnienie Avahi
            try:
                DisksUpdater().sendUpdate()
            except Exception:
                print(Colors.setred(" * ") + u"Błąd podczas odświeżania Avahi. Sprawdź czy foladiskd jest uruchomiony.")
                sys.exit(-2)
            return True
        else:
            print(Colors.setred(" * ") + u"Nie udało się usunąć woliminu z LVM")
            print(Colors.setred(" * ") + "Output: " + output)
            return False

    def getBaseList(self, vg = None):
        """
        Zwraca listę dysków bazowych
        
        @param void
        @return 
        """        
        # Pobiera listę baz z bazy danych
        query = "SELECT vgname, baselv FROM " + self.database.getPrefix() + self.tablename + " WHERE host = '" + socket.gethostname() + "'"
        if (vg != None):
            query += " AND vgname = '" + vg + "'"
            
        # Wykonywanie zapytania
        self.database.getCursor().execute(query)
        
        volumes = []
        # Tworzenie listy baz
        for record in self.database.getCursor().fetchall():
            volumes.append(Base(record[0], record[1]))
            
        return volumes
    
    def getBaseByName(self, name):
        """
        Szuka bazy na podstawie nazwy
        
        @param nazwa
        @return void
        @raise gdy nie znaleziono bazy
        """
        # Pobiera listę baz
        baselist = self.getBaseList()
        for base in baselist:
            if base.getName() == name:
                return base
            
        raise Exception('Nie można znaleźć bazy')