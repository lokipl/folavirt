#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from xml.dom import minidom
from xml.etree import ElementTree

from folavirt.admin.console.BasicConsole import BasicConsole
from folavirt.console.Colors import Colors
from folavirt.console.Params import Params
from folavirt.xmlfactory.BaseDomain import BaseDomain
from folavirt.remote.Domain import Domain
from folavirt.remote.Lab import Lab
from folavirt.remote.Distributor import Distributor
from folavirt.remote.DiskManager import getDms
from folavirt.remote.DiskManager import getDmByBaseName
from folavirt.remote.Agent import getAgents
from folavirt.permissions.GraphicPasswords import GraphicPasswords

class VmConsole():
    def __init__(self):
        self.ro = None
        
        # Tworzenie maszyn
        if Params().getArg(0) == "create":
            if Params().getArg(1) == "base":
                # Tworzenie maszyny bazowej
                self.createBaseVm()
                sys.exit(0)
            if Params().getArg(1) == "snapshot":
                # Tworzenie snapshotu
                self.createSnapshotVm()
                sys.exit(0)
            
        # Usuwanie definicji maszyn
        if Params().getArg(0) == "undefine":
            # Usuwanie definicji maszyny
            self.undefine()
            sys.exit(0)
            
        # Usuwa snapshot
        if Params().getArg(0) == "undefine-snapshot":
            self.undefineSnapshot()
            sys.exit(0)
                
        if Params().getArg(0) == "dumpxml":
            # Definicja maszyny
            self.dumpxml()
            sys.exit(0)
            
        if Params().getArg(0) == "migratexml":
            # Migracja maszyny
            self.migrate()
            sys.exit(0)
    
    @staticmethod
    def printhelp(ljust1 = 37, ljust2 = 15):
        """
        Pomoc
        
        @param void
        @return void
        """
        # Przeniesione do BasicConsole
        pass
    
    def _refreshIscsi(self):
        """
        Odświeża stan iscsi na agentach
        """
        # Odświeżanie stanu iscsi         
        agents = getAgents()
                
        print(Colors.setgreen(" * ") + u"Aktualizowanie stanu pul dyskowych")
                
        # Wysyłanie żądania do każdego z hostów
        for agent in agents:
            print(Colors.setgreen(" * ") + u"Odświeżanie agenta " + Colors.setbold(agent.getHostName()))
                    
            # Odświeżanie pul dyskowych
            agent.poolSync()
    
    def createBaseVm(self):
        """
        Tworzy maszyny bazową
        
        """        
        try:
            # Parametry
            name = Params().getArg(2)       # Nazwa maszyny bazowej
            template = Params().getArg(3)
            basename = Params().getArg(4)       # Nazwa maszyny bazowej
            balance = Params().getArg(5)       # Sposób balansowania maszyn
            # Domyślny dystrybutor - equal
            if balance == "":
                balance = "round"
            
            if Params().getArg(2) == "":
                raise Exception('skladnia')
            
            # Szukanie zarządcy dyskami na którym jest baza
            try:
                dm = getDmByBaseName(basename)
            except Exception as e:
                print(Colors.setred(" * ")),
                print(str(e).decode('utf-8')) 
                sys.exit(0)
            
            # Szukanie numeru lun na którym jest baza
            lun = 1
            for base in dm.getBaseVolumes():
                if base == basename:
                    break
                lun += 1
            
            if not Params().isParameter("xml"):
                print(Colors.setgreen(" * ") + u"Generowanie definicji maszyny wirtualnej")
            # Generowanie maszyny
            basedomain = BaseDomain(name, basename, template, lun)
            
            # Sprawdzanie czy tylko wyświetlić definicję
            if Params().isParameter("xml"):
                print basedomain.getXML()
                sys.exit(0)
            
            print(Colors.setgreen(" * ") + u"Sprawdzanie czy taka maszyna jest już gdzieś zdefiniowana")
            # Sprawdzanie czy taka maszyna jest już gdzieś zdefiniowana
            agents = getAgents()
            for agent in agents:
                for vm in agent.getVmList():
                    if vm.getName() == basedomain.getName():
                        print(Colors.setred(" * ") + u"Taka maszyna jest juz zdefiniowana.")
                        sys.exit(0)
            
            # Umieszczanie maszyny
            try:
                Distributor([basedomain], balance)
            except Exception:
                sys.exit(1)
                
            # Ustawianie losowego hasła
            domain = Domain(basedomain.getName())
            try:
                domain.searchAgent()
            except Exception:
                print(Colors.setred(" * ") + u"Nie udało się poprawnie umieścić maszyny wirtualnej")
                sys.exit(1)
                
            passwd = domain.setGraphicConsoleRandomPasswd()
            print(Colors.setgreen(" * ") + u"Ustawiono hasło do konsoli graficznej na " + passwd)
            
            # Dodawanie maszyny użytkownikowi root
            domain.addOwnership("root")
            
            sys.exit(0)
        except KeyboardInterrupt:
            print(Colors.setred(" * ") + u"Niepoprawne wywołanie polecenia")
            print(Params().getScriptName() + u" create base [nazwa maszyny wirtualnej] [szablon] [wolumin bazowy]")
      
    def createSnapshotVm(self):
        template = Params().getArg(2)
        baselv = Params().getArg(3)
        size = Params().getArg(4)
        
        try:
            int(size)
        except ValueError:
            print(Colors.setred(" * ") + u"Niepoprawna wielkość snapshotu. Musi być liczbą całkowitą")
            sys.exit(0)
            
        balancer = Params().getArg(5)   
        if balancer == "":
            balancer = "round"
        
        # Tworzenie obiektu laboratorium
        lab = Lab("_hidden_vmsnapshots", baselv)  
        
        try:
            # Tworzenie snapshota
            lab.createSnapshots(1, size) 
        except Exception as e:
            print(Colors.setred(" * ") + u"Błąd. "),
            print(str(e).decode('utf-8'))
            sys.exit(0)
        
        # Tworzenie maszyn
        lab.createSnapshotMachines(template, 1, balancer)
        
    def undefineSnapshot(self):
        """
        Usuwa snapshot
        """
        name = Params().getArg(1)
        
        # Tworzenie obiektu laboratorium
        lab = Lab("_hidden_vmsnapshots")  
        
        try:
            lab.getBaselvByName(name)
        except Exception as e:
            print(Colors.setred(" * ") + u"Błąd! " + str(e).decode('utf-8'))
            sys.exit(0)
        
        lun = lab.getLunByName(name)
        lab.removeByName(name, lun)
    
    def undefine(self):
        """
        Usuwa maszynę
        
        @param void
        @return void
        """
        name = Params().getArg(1)
        if name == "":
            print(Colors.setred(" * ") + u"Nie podano nazwy maszyny wirtualnej")
            sys.exit(0)
        
        try:
            domain = BasicConsole._getDomain()
            
            if not Params().isParameter("force"):
                print(Colors.setyellow(" * ") + u"Czy na pewno chcesz usunąć definicję maszyny " + domain.name + " ? [y|n]"),
                out = raw_input()
                if out != "y":
                    print(Colors.setred(" * ") + u"Anulowano") 
                    sys.exit(0)
                                
            # Czyszczenie uprawnień
            domain.clearOwnership()
            # Usuwanie
            domain.undefine()
            
            # Usuwanie tymczasowych haseł
            GraphicPasswords().deletePassword(name)
            
            print(Colors.setgreen(" * ") + u"Usunięto maszynę wirtualną " + domain.name)
        except Exception as e:
            print(Colors.setred(" * ") + u"Błąd podczas usuwania maszyny wirtualnej. "),
            print(str(e).decode('utf-8'))
    
    def dumpxml(self):
        """
        Zwraca XML maszyny
        """
        domain = BasicConsole._getDomain()
        
        print domain.getXML()
        
    def migrate(self):
        """
        Migracja
        """        
        name = Params().getArg(1)
        agentname = Params().getArg(2)
        
        domain = Domain(name)
        # Szukanie obecnego agenta domeny, sprawdzanie czy vm istnieje
        try:
            domain.searchAgent()
        except Exception as e:
            print(Colors.setred(" * ") + u"Błąd. "),
            print(str(e))
            sys.exit(0)
        
        # Sprawdzanie czy maszyna już jest na tym agencie
        if domain.getAgent().getHostName() == agentname:
            print(Colors.setgreen(" * ") + u"Maszyna już jest na agencie " + domain.getAgent().getHostName())
            sys.exit(1)
        
        print(Colors.setgreen(" * ") + u"Rozpoczęto migrację maszyny " + name + " z agenta " + domain.getAgent().getHostName())
        
        if domain.getState() == 1:
            if Params().isParameter("force"):
                domain.destroy()
            else:
                print(Colors.setgreen(" * ") + u"Maszyna jest uruchomiona. Wyłączyć? [y|n] "),
                out = raw_input()
                if out == "y":
                    domain.destroy()
                else:
                    print(Colors.setred(" * ") + u"Anulowano")
                    sys.exit(1)
        
        agents = getAgents()
        for agent in agents:
            if agent.getHostName() == agentname:
                print(Colors.setgreen(" * ") + u"Sprawdzanie połączenia z agentem " + agentname)
                # Pingowanie agenta
                #r = agent.ping()
                r = True
                if r != False:
                    print(Colors.setgreen(" * ") + u"Definiowanie maszyny na docelowym agencie")
                    xmldesc = domain.getXML()
                    # Definiowanie maszyny na nowym hoście
                    agent.defineXML(xmldesc)
                    # Usuwanie maszyny ze starej lokalizacji
                    print(Colors.setgreen(" * ") + u"Usuwanie maszyny z poprzedniego agenta")
                    domain.undefine()
                    
                    sys.exit(0)
                else:
                    print(Colors.setred(" * ") + u"Brak połączenia z agentem.")
                    sys.exit(2)
                
                sys.exit(0)
                
        print(Colors.setred(" * ") + u"Nie znaleziono definicji agenta " + agentname)
        sys.exit(1)