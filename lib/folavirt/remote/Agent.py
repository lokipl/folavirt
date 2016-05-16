#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import socket
import base64

from folavirt.remote.RemoteObject import RemoteObject
from folavirt.remote.Domain import Domain
from folavirt.remote.Pool import Pool
from folavirt.networking.Query import Query

def getAgents():
    """
    Zwraca listę agentów z pliku konfiguracyjnego
    """
    
    if not os.path.exists("../etc/agents"):        
        return []
    
    # Otwiera plik    
    f = open("../etc/agents")
    agentsdef = f.readlines()
      
    # Nowa lista hostów
    agents = []
    for agentdef in agentsdef:
        if agentdef[0] == "#":
            continue
            
        foo = agentdef.split()
        
        try:
            agent = Agent()
            agent.setHostName(foo[0])
            agent.setAddress(foo[1])
            agent.setPort(int(foo[2]))
            
            # Dodaje hosta do listy
            agents.append(agent)
        except IndexError:
            pass
        
    return agents

def getOnlineAgents():
    agents = []
    
    for agent in getAgents():
        response = agent.ping()
        if not response:
            continue
        
        if response == "nolibvirt":
            continue
        
        agents.append(agent)
        
    return agents

class Agent(RemoteObject):
    """
    Zdalny obiekt zarządcy
    """
    def setHostName(self,hostname):
        self.hostname = hostname
    def getHostName(self):
        return self.hostname
      
    def ping(self):
        """
        Pinguje serwer, za pomocą wewnętrznego protokołu
        
        @param void
        @return folavirt.networking.Response
        """            
        # Tworzenie zapytania
        q = Query()
        q.setCommand("ping")
        
        # wykonywanie zapytania
        try:
            response = self.execute(q)
            if response.getCommand() == "nolibvirt":
                return "nolibvirt"
        except socket.error:
            return False
        except:
            return False
        
        if response == -1:
            return False
        
        return response
    
    def defineXML(self, xmldesc):
        """
        Definiuje maszynę z podanego XMLa
        
        @param xml
        @return void
        """
        # Zestawianie połączenia z agentem
        self.establish()
        
        # Tworzenie zapytania
        q = Query()
        q.setCommand("definexml")
        q.setData(base64.b64encode(xmldesc))

        # Wykonywanie zapytania
        r = self.execute(q)
        
        return r
    
    def getVmList(self):
        """
        Zwraca listę maszyn wirtualnych
        
        @param void
        @return [domain]
        """
        # Zestawianie połączenia
        self.establish()
        
        # Tworzenie zapytania
        q = Query()
        q.setCommand("vmlist")    
        
        response = self.tcp.execute(q)
        domains = []
        for domaindata in response.getData():
            # Tworzy nowy obiekt domeny
            domain = Domain()
            domain.address = self.getAddress()
            domain.port = self.getPort()
            domain.host = self
            domain.name = domaindata['name']
            domain.state = domaindata['state']
            domains.append(domain)
            
        return domains  
    
    def getPools(self):
        """
        Zwraca pule dyskowe
        
        @param void
        @return [Pool]
        """
        # Tworzenie zapytania
        q = Query()
        q.setCommand('getpools')
        
        # Wykonywanie zapytania
        response = self.execute(q)
        
        pools = []
        # Przetwarzanie odpowiedzi na 
        for pooldef in response.getData():
            # Tworzenie obiektu puli, dodatkowo, przekazywanie połączenia
            pool = Pool(pooldef, self.tcp)
            pools.append(pool)
        
        return pools
    
    def poolAdd(self):
        """
        Aktualizuje stan pul
        """
        # Tworzenie zapytania powodującego odświeżenie listy zasobów iscsi
        q = Query()
        q.setCommand("iscsi-add")
        q.setData({})
        
        # Wykonywanei zapytania
        response = self.execute(q)
        
        return response
    
    def poolSync(self):
        """
        Usuwa nie potrzebne, dynamiczne pule
        """
        # Tworzenie zapytania
        q = Query()
        q.setCommand("iscsi-sync")
        q.setData({})
        
        # Wykonywanei zapytania
        response = self.execute(q)
        
        return response
    
    def close(self):
        """
        Zamyka połączenie z hostem
        
        @param void
        @return void
        """
        if self.tcp != 0:  
            try:          
                self.tcp.quit()
            except socket.error:
                pass
            
    def virsh(self, command):
        """
        Wykonuje polecenie virsh
        
        @param void
        @return void
        """
        q = Query()
        q.setCommand("virsh")
        q.setData(command)
        
        response = self.execute(q)
        
        return response.getData()