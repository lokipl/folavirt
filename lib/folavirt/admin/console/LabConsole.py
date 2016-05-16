#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys

from folavirt.console.Colors import Colors
from folavirt.console.Params import Params
from folavirt.remote.Lab import Lab
from folavirt.remote.DiskManager import getDms
from folavirt.remote.Agent import getAgents

class LabConsole():
    def __init__(self):
        if Params().getArg(0) == "lab":
            if Params().getArg(1) == "list":
                self.lablist()
                sys.exit(0)
            
            if Params().getArg(1) == "create":
                self.labcreate()
                sys.exit(0)
                
            if Params().getArg(1) == "remove":
                self.labremove()
                sys.exit(0)
            
            self.printhelp()
            sys.exit(0)
    
    @staticmethod
    def printhelp(ljust1 = 37, ljust2 = 15):
        print("\n " + u"Laboratorium")
        print("  " + Colors.setbold("lab create $L $T $B $U $S [$D]".ljust(ljust1)) + u"tworzenie laboratorium")
        print("  " + Colors.setbold("lab list".ljust(ljust1)) + u"lista laboratoriów")
        print("  " + Colors.setbold("lab remove $L [--force]".ljust(ljust1)) + u"usuwanie laboratorium [bez pytania o potwierdzenie]")
        
    def lablist(self):
        """
        Lista laboratoriów
        """
        labs = Lab.getLabs()
        
        # wyświetlanie tylko wtedy gdy jest jakieś laboratorium
        if len(labs) > 0:
            print(Colors.setbold(u"Nazwa".ljust(20) + u"Baza".ljust(20) + u"Ilość".ljust(10)))
            
            for lab in labs:
                print lab.name.ljust(20) + lab.basename.ljust(20) + str(len(lab.getDomains())).ljust(10)
     
    def _testForAgents(self):
        agents = []
        for agent in getAgents():
            if agent.ping():
                agents.append(agent)
               
        if len(agents) == 0:
            print(Colors.setred(" * ") + u"Nie znaleziono działającego agenta.")
            sys.exit(0)
        
    def labcreate(self):
        """
        Tworzenie laboratorium
        """
        # Parsowanie parametrów
        name = Params().getArg(2)           # Nazwa laboratorium
        baselv = Params().getArg(4)         # Baza woluminowa
        template = Params().getArg(3)       # Nazwa szablonu
        size = Params().getArg(6)           # Wielkość snapshotu
        balancer = Params().getArg(7)       # Balancer
        if balancer == "":
            balancer = "equal"
        
        if name == "":
            print(Colors.setred(" * ") + u"Nie podano nazwy laboratorium")
            sys.exit(0)
            
        if baselv == "":
            print(Colors.setred(" * ") + u"Nie podano nazwy woluminu bazowego")
            sys.exit(0)
        
        # Sprawdzanie czy taki szablon istnieje
        if not (os.path.exists("../etc/templates/" + template) or os.path.exists("../etc/templates/" + template + ".xml")):
            print(Colors.setred(" * ") + u"Nie ma takiego szablonu")
            sys.exit(0)
             
        self._testForAgents()
                
        # Parsowanie listy użytkowników
        userslist = []
        # Obsługa ewentualnej ścieżki
        path = Params().getArg(5)
        try:
            if path[0] != "/":
                path = os.getenv("PWD", "") + "/" + path
        except IndexError:
            print(Colors.setred(" * ") + u"Nie podano poprawnej nazwy szablonu")
            sys.exit(0)
        
        if os.path.exists(path):
            f = open(path)
            for line in f.readlines():
                if line == "":
                    continue
                
                userslist.append(line.strip())
        else:
            userslist = Params().getArgList(5)
        
        lab = Lab(name, baselv)
        
        try:
            lab.createSnapshots(len(userslist), size)
        except Exception as e:
            print(Colors.setred(" * ") + u"Błąd! "),
            print(str(e).decode('utf-8'))
            sys.exit(0)
        
        lab.createSnapshotMachines(template, len(userslist), balancer)
        lab.setPermissions(userslist)
        
    def labremove(self):
        """
        Usuwanie laboratorium
        """
        name = Params().getArg(2)       # Nazwa laboratorium
        if name == "":
            print(Colors.setred(" * ") + "Nie podano nazwy laboratorium")
            sys.exit(0)
        
        dms = getDms()
        if len(dms) == 0:
            print(Colors.setred(" * ") + u"Brak konfiguracji zarządców dysków. Wykonaj najpierw " + Colors.setbold(u"disk discover"))
            sys.exit(0)
        
        lab = Lab(name)
        
        if Params().isParameter("clean"):
            lab.removeFromDatabase()
            print(Colors.setgreen(" * ") + u"Usunięto laboratorium z bazy danych")
            sys.exit(0)
        
        if not Params().isParameter("force"):
            print(Colors.setyellow(" * ") + u"Czy chcesz usunąć laboratorium " + name + " ? [y|n] "),
            out = raw_input()
            if out != "y":
                print(Colors.setred(" * ") + "Anulowano")
                sys.exit(1)
        
        lab.remove()
        