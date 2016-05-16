#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from ConfigParser import ConfigParser

from folavirt.remote.Agent import getAgents,Agent
from folavirt.console.Colors import Colors
from folavirt.console.Params import Params

class Distributor():
    """
    Dystrybucja maszyn wirtualnych pomiędzy hostami
    """
    def __init__(self, xmlfactories, method = "equal", idonhosttable = None):
        self.xmlfactories = xmlfactories
        self.method = method
        self.idonhosttable = idonhosttable
        
        if self.method == "equal":
            self.equalDistrib()
            return
            
        if self.method == "round":
            self.roundDistrib()
            return
            
        if self.method == "agent":
            self.agentDistrib()
            return
        
        self.agentDistrib()
     
    def _getAgents(self):
        # Pobieranie listy agentów
        agents = getAgents()
        
        # Szukanie nieaktywnych agentów
        for agent in agents:
            response = agent.ping()
            if not response:
                print(Colors.setred(" * ") + u"Agent " + agent.getHostName() + u" nie odpowiada. Pomijanie.")
                agents.remove(agent)
            else:
                if response == "nolibvirt":
                    print(Colors.setred(" * ") + u"Agent " + agent.getHostName() + u" nie posiada usług libvirtd. Pomijanie.")
                    agents.remove(agent)
     
        # Jeśli brak agentów
        if len(agents) == 0:
            print(Colors.setred(" * ") + u"Nie ma żadnego działającego agenta.")
            sys.exit(5)
     
        return agents
     
    def _placeOnHost(self, xmlfactory, agent):
        """
        Umieszcza maszynę na hoście
        """
        # Czy podano tabelę z licznością hostów na poszczególnych agentach
        if self.idonhosttable != None:
            try:
                self.idonhosttable[agent.getHostName()] += 1
            except KeyError:
                self.idonhosttable[agent.getHostName()] = 1
            
            # Przypsianie wartości do fabryki
            xmlfactory.agentname = agent.getHostName()
            xmlfactory.agentsnapshotid = self.idonhosttable[agent.getHostName()]
        
        print(Colors.setgreen(" * ") + u"Umieszczanie " + xmlfactory.getName() + u" na " + agent.getHostName())
        # Umieszczanie
        out = agent.defineXML(xmlfactory.getXML())        
        if out.getData() != 0:
            print(Colors.setred(" * ") + u"Błąd podczas definiowania maszyny: " + out.getData())
            raise Exception(out.getData())
            
    def equalDistrib(self):
        """
        Rozkładanie po równo na każdy z zarządców
        
        @param void
        @return void
        """
        print(Colors.setgreen(" * ") + u"Rozpoczęto umieszczanie maszyn według algorytmu \"equal\"")
        
        # Pobieranie liczby agentów
        agents = self._getAgents()
        
        for i in range(len(self.xmlfactories)):
            # Obliczanie na którego agenta wrzucić snapshot
            which = i % len(agents)
            
            # Umieszczanie maszyny
            self._placeOnHost(self.xmlfactories[i], agents[which])
    
    def roundDistrib(self):
        """
        Rozkładanie tak, żeby na każdym było po równo
        
        @param void
        @return void
        """
        print(Colors.setgreen(" * ") + u"Rozpoczęto umieszczanie maszyn według algorytmu \"round\"")
        
        # Pobieranie liczby agentów
        agents = self._getAgents()  
        
        vmlen = []
        for agent in agents:
            vm = {'agent':agent, 'count':len(agent.getVmList())}
            vmlen.append(vm)
        
        for i in range(len(self.xmlfactories)):
            # Szukanie agenta z najmniejszą liczbą maszyn
            idx = vmlen.index(min(vmlen, key=lambda x:x['count']))
            
            # Umieszczanie maszyny
            self._placeOnHost(self.xmlfactories[i], vmlen[idx]['agent'])
            
            vmlen[idx]['count'] += 1
                    
    def agentDistrib(self):
        """
        Rozkładanie na konkretny host
        
        @param void
        @return void
        """
        # Ostatni parametr musi być nazwą hosta
        agentname = Params().getArg(Params().argLen() - 1)
        # Lista agentów
        agents = self._getAgents()
        # Wybrany agent
        agent = None
        
        for a in agents:
            if a.getHostName() == agentname:
                agent = a
                break
        
        # Gdy nie znaleziono próbuj połączyć się z hotem lokalnym
        if agent == None:
            # Obiekt agenta
            agent = Agent()
            agent.hostname = "localhost"
            agent.address = "127.0.0.1"
              
            # Odczyt portu z konfiguracji
            config = ConfigParser()
            config.read("../etc/folavirt.ini")
            agent.port = int(config.get("folavirtd", "port"))
        
            # Pingowanie agenta
            if not agent.ping():
                print(Colors.setred(" * ") + u"Nie ma agenta na lokalnym porcie.")
                sys.exit(0)
        
        # Umieszczanie na agencie
        for i in range(len(self.xmlfactories)):
            self._placeOnHost(self.xmlfactories[i], agent)
        