#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from folavirt.console.Colors import Colors
from folavirt.console.Params import Params
from folavirt.disks.Configure import Configure
from folavirt.disks.iscsi.Partitions import Partitions
from folavirt.disks.iscsi.Snapshot import Snapshot
from folavirt.disks.iscsi.Snapshots import Snapshots
from folavirt.disks.iscsi.Tgt import Tgt
from folavirt.disks.iscsi.Base import Base

class SnapshotConsole():
    def __init__(self):
        if Params().argLen() >= 1:
            if Params().getArg(0) == "snapshot":
                if Params().argLen() >= 2:
                    if Params().getArg(1) == "create":
                        self.snapshotCreate()
                        sys.exit(0)
                    if Params().getArg(1) == "list":
                        self.snapshotList()
                        sys.exit(0)
                    if Params().getArg(1) == "remove":
                        self.snapshotRemove()
                        sys.exit(0)
                    if Params().getArg(1) == "removeall":
                        self.snapshotRemoveAll()
                        sys.exit(0)
                    if Params().getArg(1) == "attach":
                        self.attach()
                        sys.exit(0)
                    if Params().getArg(1) == "detach":
                        self.detach()
                        sys.exit(0)
                
                # Jeśli nie wpadło w żadne podpolecenie, wyświetl helpa tylko dla tej grupy
                self.printhelp()
                sys.exit(0)
    
    @staticmethod
    def printhelp(ljust1 = 37, ljust2 = 15):
        """
        Pomoc dotycząca tworzenia snapshotów
        
        @param void
        @return void
        """
        print("\n " + u"Zarządzanie snapshotami")
        print("  " + Colors.setbold("snapshot attach $VG $LV $DEV".ljust(ljust1)) + u"dodaje istniejący już snapshot do bazy danych")
        print("  " + Colors.setbold("snapshot create $VG $LV $S [$C]".ljust(ljust1)) + u"tworzy snapshot")
        print("  " + Colors.setbold("snapshot detach $VG $LV $DEV".ljust(ljust1)) + u"usuwa snapshot z bazy danych")
        print("  " + Colors.setbold("snapshot list".ljust(ljust1)) + u"lista snapshotów")
        print("  " + Colors.setbold("snapshot remove $DEV".ljust(ljust1)) + u"usuwanie snapshotów")
        print("  " + Colors.setbold("snapshot removeall $VG [$LV]".ljust(ljust1)) + u"usuwa wszystkie snapshoty przypisane do grupy woluminowej [i bazy]")
                        
    def snapshotCreate(self):
        """
        Tworzenie snapshotów
        
        @param void
        @return void
        """
        # Polecenie wymaga 6 lub 7 parametrów
        if Params().argLen() == 5 or Params().argLen() == 6:
            # Pobieranie listy maszyn bazowych
            vg = Params().getArg(2)
            base = Params().getArg(3)
            size = Params().getArg(4)
            
            # Sprawdzanie czy istnieje taka baza
            if base in [x.getName() for x in Partitions().getBaseList(vg)]:
                print(Colors.setgreen(" * ") + u"Tworzenie snapshotów")
                count = 1
                
                # Obsługa ilości snapshotów
                if Params().argLen() == 6:
                    count = int(Params().getArg(5))
                    
                # Tworzenie obiektu bazy
                base = Base(vg,base)
                
                # Tworzenie snapshotów
                for _i in range(count):
                    Snapshots().createFromBase(base, size)
            else:
                print (Colors.red + " * " + Colors.nocolor + u"Nie ma takiej maszyny bazowej")
                sys.exit(2)
        else:
            print(Colors.setred(" * ") + u"Błąd składni.")
            print(Colors.setred(" * ") + Params().getScriptName() + u" snapshot create \"Grupa woluminów logicznych\" \"Nazwa bazy\" \"wielkość w GB\" [ilość]")
            sys.exit(1)
        
        # Uaktualnianie konfiguracji tgt
        Tgt().writeConfig()
    
    def snapshotList(self):
        """
        Wypisuje listę snapshotów
        
        @param void
        @return void
        """
        print(Colors.setbold(u"Grupa woluminowa".ljust(20) + "Baza".ljust(20) + u"Urządzenie"))
        
        for snapshot in Snapshots().getList():
            print(snapshot.getVolumeGroup().ljust(20) + snapshot.getBase().getName().ljust(20) + snapshot.getDevice())
         
    def snapshotRemove(self):
        """
        Usuwanie snapshota
        
        @param void
        @return void
        """
        if Params().argLen() == 3:
            device = Params().getArg(2)
            try:
                snapshot = Snapshots().getSnapshotByDevice(device)
                snapshot.remove()
            except Exception as e:
                print(Colors.setred(" * ")),
                print(str(e).decode("utf8", "ignore"))
                
            sys.exit(0)
        else:
            print(Colors.setred(" * ") + "Niepoprawna ilość parametrów")
      
    def snapshotRemoveAll(self):
        """
        Usuwa wszystkie snapshoty stworzone z jakiejś bazy lub w grupie woluminowej
        
        @param void
        @return void
        """
        snapshots = []
        if Params().argLen() == 3:
            # Usuwanie z całej grupy woluminów
            vg = Params().getArg(2)
            if not vg in Configure().getVolumeGroupList():
                print(Colors.setred(" * ") + u"Użyta grupa woluminowa nie istnieje")
                sys.exit(-1)
            
            for base in Partitions().getBaseList(vg):
                for snapshot in base.getSnapshots():
                    snapshots.append(snapshot)
        if Params().argLen() == 4:
            vg = Params().getArg(2)
            basename = Params().getArg(3)
            
            if not vg in Configure().getVolumeGroupList():
                print(Colors.setred(" * ") + u"Użyta grupa woluminowa nie istnieje")
                sys.exit(-1)
                
            if not basename in [x.getName() for x in Partitions().getBaseList(vg)]:
                print(Colors.setred(" * ") + u"Użyty wolumin bazowy nie istnieje")
                sys.exit(-1)
            
            # Baza (grupa woluminowa, baza)
            base = Base(Params().getArg(2), Params().getArg(3))
            for snapshot in base.getSnapshots():
                snapshots.append(snapshot)
            
        if len(snapshots) == 0:
            sys.exit(0)

        print(Colors.setgreen(" * ") + u"Zostaną usunięte następujące snapshoty:")
                    
        # Wypisywanie listy snapshotów
        for snapshot in snapshots:
            print(Colors.setyellow(" * ") + " - " + snapshot.getDevice())
            
        print(Colors.setyellow(" * ") + u"Czy chcesz kontynuować? "), 
        result = raw_input("[y|n] ")
        # Jeśli potwierdzono, usuwanie snapshotów
        if result == "y":
            for snapshot in snapshots:
                snapshot.remove()
        else:
            print(Colors.setyellow(" * ") + "Anulowano")        
            
        sys.exit(0)
        
    def attach(self):
        """
        Dodaje istniejacy snapshot do bazy danych
        """
        vg = Params().getArg(2)
        basename = Params().getArg(3)
        dev = Params().getArg(4)
        
        base = Base(vg, basename)
        
        print(Colors.setgreen(" * ") + u"Dodawanie snapshota do bazy danych")
        Snapshots().attach(base, dev.split('/')[-1])
        
    def detach(self):
        """
        Usuwa snapshot z bazy danych
        """
        vg = Params().getArg(2)
        basename = Params().getArg(3)
        dev = Params().getArg(4)
        
        print(Colors.setgreen(" * ") + u"Usuwanie snapshotu z bazy danych")
        Snapshot(vg, basename, dev).detach()