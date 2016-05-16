#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from folavirt.console.Colors import Colors
from folavirt.console.Params import Params
from folavirt.disks.Configure import Configure
from folavirt.disks.iscsi.Tgt import Tgt
from folavirt.disks.iscsi.Base import Base
from folavirt.disks.iscsi.Partitions import Partitions
from folavirt.disks.iscsi.Snapshots import Snapshots

class LvConsole():
    def __init__(self):
        if Params().argLen() >= 1:
            # Tworzenie bazowych dysków
            if Params().getArg(0) == "lv":
                if Params().argLen() >= 2:
                    if Params().getArg(1) == "create":
                        self.baseCreate()
                        sys.exit(0)
                    if Params().getArg(1) == "list":
                        self.baseList()
                        sys.exit(0)
                    if Params().getArg(1) == "remove":
                        self.baseRemove()
                        sys.exit(0)
                    if Params().getArg(1) == "help":
                        self.baseHelp()
                        sys.exit(0)
                    if Params().getArg(1) == "attach":
                        self.attach()
                        sys.exit(0)
                    if Params().getArg(1) == "detach":
                        self.detach()
                        sys.exit(0)
                
                # Wyświetlanie helpa
                self.printhelp()
                sys.exit(0)
    
    @staticmethod
    def printhelp(ljust1 = 27, ljust2 = 15):
        """
        Pomoc dotycząca tworzenia maszyn bazowych
        
        @param void
        @return void
        """
        print("\n " + u"Zarządzanie woluminami bazowymi")
        print("  " + Colors.setbold("lv attach $VG $LV".ljust(ljust1)) + u"dodaje do folavirt wolumin bazowy, bez jego tworzenia")
        print("  " + Colors.setbold("lv create $VG $LV".ljust(ljust1)) + u"tworzy wolumin bazowy")
        print("  " + Colors.setbold("lv detach $VG $LV".ljust(ljust1)) + u"usuwa wolumin bazowy z folavirt, nie usuwa go")
        print("  " + Colors.setbold("lv list".ljust(ljust1)) + u"lista woluminów bazowych")
        print("  " + Colors.setbold("lv remove $VG $LV".ljust(ljust1)) + u"usuwa wolumin bazowy")
                       
    def baseCreate(self):
        """
        Parsowanie poleceń tworzenia bazy
        
        @param void
        @return void
        """
        # Sprawdzenie poprawnej ilości parametrów
        if Params().argLen() != 5:
            print(Colors.setred(" * ") + u"Błąd! Niepoprawne użycie polecenia\n")
            print(u"Poprawne użycie polecenia")
            print(Params().getScriptName() + u" lv create <nazwa grupy woluminów> <nazwa woluminu bazowego> <ilość gigabajtów>")
            sys.exit(1)     
        
        # Ustawianie parametrów
        vg = Params().getArg(2)
        name = Params().getArg(3)
        size = Params().getArg(4)
            
        # Sprawdzanie czy istnieje taki wolumin logiczny w zarządzaniu
        baselist = Configure().getVolumeGroupList()
        if not vg in baselist:
            print(Colors.setred(" * ") + u"Użyta grupa woluminowa nie istnieje")
            sys.exit(-1)
            
        # Sprawdzanie czy taka baza już istnieje
        if name in [x.getName() for x in Partitions().getBaseList(vg)]:
            print(Colors.setred(" * ") + u"Taka partycja bazowa już istnieje")
            sys.exit(1)
            
        # Tworzenie partycji bazowej
        ret = Partitions().createBase(vg, name, size)
        if not ret:
            sys.exit(1)
        
        print(Colors.setgreen(" * ") + u"Utworzono wolumin logiczny")
           
        # Odświeżanie konfiguracji Tgt
        Tgt().writeConfig()
           
        sys.exit(0)
    
    def baseRemove(self):
        """
        Usuwanie dysku bazowego
        
        @param void
        @return void
        """
        if Params().argLen() == 4:
            # Pobieranie parametrów
            vg = Params().getArg(2)
            name = Params().getArg(3)
            
            # Sprawdzanie czy istnieje taki wolumin logiczny w zarządzaniu
            baselist = Configure().getVolumeGroupList()
            if not vg in baselist:
                print(Colors.setred(" * ") + u"Użyta grupa woluminowa nie istnieje")
                sys.exit(-1)
            
            # Usuwanie snapshotów
            base = Base(vg, name)
            for snapshot in base.getSnapshots():
                print(Colors.setgreen(" * ") + u"Usuwanie snapshotu " + snapshot.getDevice())
                snapshot.remove()
            
            # Najpierw usuwanie z bazy danych  
            result = Partitions().detachBase(vg, name)
            if not result:
                print(Colors.setred(" * ") + u"Nie ma takiego woluminu")
                sys.exit(1)
            print(Colors.setgreen(" * ") + u"Usunięto wolumin z bazy danych")
            
            # Odświeżenie konfiguracji TGT, zwolnienie urządzenia
            Tgt().writeConfig()
            
            # Usuwanie
            result = Partitions().removeBase(vg, name)
            if not result:
                sys.exit(2)
            
            print(Colors.setgreen(" * ") + u"Poprawnie usunięto wolumin z LVM")
        else:
            print(u"Poprawne użycie polecenia:")
            print(Params().getScriptName() + u" baselv remove [Nazwa grupy woluminów] [Nazwa maszyny bazowej]")
         
    def baseList(self):
        """
        Wyświetlanie listy maszyn bazowych
        
        @param void
        @return void
        """
        lvlist = Partitions().getBaseList()
        
        if len(lvlist) >= 1:
            print(Colors.setbold("Grupa woluminowa".ljust(20) + "Nazwa".ljust(20)))
    
            # Wyświetlanie tabeli z listą woluminów
            for volume in lvlist:
                print(str(volume.getVolumeGroup()).ljust(20) + str(volume.getName()).ljust(20))
        else:
            print(Colors.setred(" * ") + u"Lokalnie żadna grupa woluminowa nie została przyłaczona")
                  
        sys.exit(0)
        
    def _attachdetachParams(self):
        vg = Params().getArg(2)
        name = Params().getArg(3)
        
        if Params().getArg(2) == "":
            print(Colors.setred(" * ") + u"Nie podano grupy woluminowej")
            sys.exit(0)
            
        if Params().getArg(3) == "":
            print(Colors.setred(" * ") + u"Nie podano nazwy woluminu")
            sys.exit(0)
            
        return {'vg':vg, 'name': name}
    
    def attach(self):
        """
        Dodaje wolumin do bazy danych
        """
        p = self._attachdetachParams()
        
        if p['name'] in [base.getName() for base in Partitions().getBaseList() if base.getVolumeGroup() == p['vg']]:
            print(Colors.setred(" * ") + u"Taki wolumin logiczny istnieje już w bazie danych")
            sys.exit(0)
        
        print(Colors.setgreen(" * ") + u"Dodawanie woluminu do bazy danych")
        Partitions().attachBase(p['vg'], p['name'])
        
        # Odświeżanie konfiguracji Tgt
        Tgt().writeConfig()
        
    def detach(self):
        """
        Usuwa wolumin z bazy danych
        """
        p = self._attachdetachParams()
            
        if not p['name'] in [base.getName() for base in Partitions().getBaseList() if base.getVolumeGroup() == p['vg']]:
            print(Colors.setred(" * ") + u"Nie ma takiego woluminu bazowego")
            sys.exit(0)
            
        base = Base(p['vg'], p['name'])
        for snapshot in base.getSnapshots():
            print(Colors.setgreen(" * ") + u"Usuwanie snapshotu " + snapshot.getDevice() + u" z bazy danych")
            snapshot.detach()
            
        print(Colors.setgreen(" * ") + u"Usuwanie woluminu z bazy danych")
        Partitions().detachBase(p['vg'], p['name'])
        
        # Odświeżanie konfiguracji Tgt
        Tgt().writeConfig()
        
        sys.exit(0)
        