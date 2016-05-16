#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
from ConfigParser import ConfigParser

from folavirt.console.Colors import Colors
from folavirt.console.Params import Params

from folavirt.networking.AvahiDiscover import AvahiDiscover
from folavirt.remote.Agent import getAgents
from folavirt.permissions.Network import Network

class AgentConsole():
    """
    Obsługa poleceń konsoli do obsługi hostów
    """
    def __init__(self):
        if Params().getArg(0) == "agent":
            if Params().getArg(1) == "discover":
                self.discover()
                sys.exit(0)
            
            if Params().getArg(1) == "list":
                self.list()
                sys.exit(0)
                            
            if Params().getArg(1) == "pool":
                self.pool()
                sys.exit(0)
            
            self.printhelp()
            sys.exit(0)
    
    @staticmethod
    def printhelp(ljust1 = 35, ljust2 = 15):
        """
        Wypisywanie helpa
        
        @static
        @param void
        @return void
        """
        print("\n " + u"Zarządzanie agentami")
        print("  " + Colors.setbold("agent discover [--dry-run]".ljust(ljust1)) + u"wyszukiwanie agentów [bez aktualizacji etc/agents]")
        print("  " + Colors.setbold("agent list".ljust(ljust1)) + u"wypisywanie listy dostępnych agentów wg etc/agents, ")
        print("  " + "".ljust(ljust1) + u"tj. serwerów maszyn wirtualnych z uruchomionymi demonami folavirtd")
        print("  " + Colors.setbold("agent pool add".ljust(ljust1)) + u"dodaje nowe pule dyskowe")
        print("  " + Colors.setbold("agent pool list [$A]".ljust(ljust1)) + u"wyświetlanie zasobów dyskowych")
        print("  " + Colors.setbold("agent pool sync [$A]".ljust(ljust1)) + u"synchronizuje pule dyskowe ze stanem foladiskd")
     
    def discover(self):
        """
        Szukanie hostów przez Avahi
        """        
        # Uruchomienie przeszukiwania
        discover = AvahiDiscover()
        
        parser = ConfigParser()
        parser.read('../etc/folavirt.ini')
        
        try:
            seconds = parser.getint("console", "avahi_timeout")
        except:
            seconds = 3
        
        # Odczekanie 3 sekund
        time.sleep(seconds)
        
        #print(Colors.setbold(u"\nLista znalezionych agentów\n"))
        # Tylko wyświetlanie?ś
        if not Params().isParameter("dry-run"):
            # Otwieranie pliku do zapisu
            f = open("../etc/agents", "w+")
            
            f.write("# Wygenerowano " + str(datetime.datetime.now()) + "\n")
            f.write("# <Nazwa agenta> <Adres IP> <Port>\n")
        
        agents = discover.getHosts()
        
        agents = sorted(agents, key=lambda agent:agent.hostname.lower())
        
        print(Colors.setbold("Nazwa".ljust(25) + "Adres".ljust(20) + "Port".ljust(11) + "Status"))
        for agent in agents:
            # Sprawdzanie czy jest to host należący do sieci
            if Network().contains(agent.getAddress()):
                # Wypisywanie na konsoli informacji o znalezionym hoście
                print(agent.getHostName().ljust(25) + agent.getAddress().ljust(20) + str(agent.getPort()).ljust(10)),
                
                response = agent.ping()
                if response == False:
                    print(Colors.setred(u"nie działa"))
                else:
                    if response == "nolibvirt":
                        print(Colors.setyellow(u"działa - bez libvirtd"))
                    else:
                        print(Colors.setgreen(u"działa"))
                    agent.close()
                
                # Dodawanie linijki definicji hosta
                if not Params().isParameter("dry-run"):
                    f.write(agent.getHostName() + "\t" + agent.getAddress() + "\t" + str(agent.getPort()) + "\n")

        # Koniec skanowania
        discover.kill()
    
    def list(self):
        """
        Wyświetla listę dostępnych agentów
        """
        if not os.path.exists("../etc/agents"): 
            print(Colors.setred(" * ") + u"Brak konfiguracji agentów. Wykonaj najpierw " + Colors.setbold(u"agent discover"))
            sys.exit(0)
        
        agents = getAgents()
        
        print(Colors.setbold("Nazwa".ljust(25) + "Adres".ljust(20) + "Port".ljust(11) + "Status"))

        for agent in agents:
            print(agent.getHostName().ljust(25) + agent.getAddress().ljust(20) + str(agent.getPort()).ljust(10)),
            
            response = agent.ping()
            if response:
                if response == "nolibvirt":
                    print(Colors.setyellow(u"działa - bez libvirtd"))
                else:
                    print(Colors.setgreen(u"działa"))
                    agent.close() 
            else:
                print(Colors.setred(u"nie działa"))
            
    def pool(self):
        """
        Obsługa iscsi w hostach
        """
        if Params().argLen() > 2:
            # Jeśli wydano polecenie "agent iscsi update"
            if Params().getArg(2) == "add":
                # Lista agentów
                agents = getAgents()

                # Wysyłanie żądania do każdego z hostów
                for agent in agents:
                    if agent.ping():
                        print(Colors.setgreen(" * ") + u"Aktualizowanie stanu puli dyskowych na " + Colors.setbold(agent.getHostName()))
                    
                        agent.poolAdd()
                    else:
                        print(Colors.setred(" * ") + u"Pominięcie aktualizacji stanu puli dyskowych na " + Colors.setbold(agent.getHostName()))
                
                # Koniec
                sys.exit(0)
            
            if Params().getArg(2) == "sync":
                # Lista agentów
                agents = getAgents()
                
                # Wysyłanie żądania do każdego z agentów
                for agent in agents:
                    if Params().getArg(3) != "":
                        if Params().getArg(3) != agent.getHostName():
                            continue
                    
                    if agent.ping():
                        print(Colors.setgreen(" * ") + u"Aktualizowanie stanu puli dyskowych na " + Colors.setbold(agent.getHostName()))
                        
                        # Pobieranie nowych
                        try:
                            result = agent.poolSync()
                        except:
                            print(Colors.setred(" * ") + u"Błąd, sprawdź log na agencie " + Colors.setbold(agent.getHostName()))
                            continue
                        
                        try:
                            for added in result.getData()['added']:
                                print(Colors.setyellow(" * ") + "+ " + added)
                            for removed in result.getData()['removed']:
                                print(Colors.setyellow(" * ") + "- " + removed)
                        except:
                            pass
                    else:
                        print(Colors.setred(" * ") + u"Pominięcie aktualizacji stanu puli dyskowych na " + Colors.setbold(agent.getHostName()))
                        
                sys.exit(0)
                
            if Params().getArg(2) == "list":
                # Pobranie listy wszystkich hostów
                agents = getAgents()
                
                for agent in agents:
                    response = agent.ping()
                    
                    if response:
                        if response == "nolibvirt":
                            continue
                            
                        if Params().getArg(3) != "":
                            if Params().getArg(3) != agent.getHostName():
                                continue
                        
                        print (Colors.bold + agent.getHostName() + Colors.nobold)
                        pools = agent.getPools()
                        if pools != None:
                            for pool in agent.getPools():
                                print pool.getName()
                        print("")
                    else:
                        print(Colors.setred(" * ") + u"Agent " + agent.getHostName() + u" nie odpowiada")
        
                sys.exit(0)
                
        self.printhelp()
