#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys

from xml.etree import ElementTree

from folavirt.remote.Agent import getAgents
from folavirt.console.Colors import Colors

class SnapshotDomain():
    """
    Tworzenie definicji domeny
    """
    def __init__(self, template, basename, i):
        self.template = template     # Nazwa szablonu
        self.basename = basename     # Wolumin bazowy
        self.i = i                   # LUN
        
        self.xml = None              # XML
        
        self.agentname = ""          # Nazwa agenta na którym umieszczono host
        self.agentsnapshotid = 0     # ID na agencie
        
    def getName(self):
        """
        Generuje nazwę wirtualnej maszyny
        
        @param void
        @return nazwa
        """
        # Sprawdzanie czy wygenerowano XML
        if self.xml == None:
            # Generowanie XML
            self.getXML()
            
        # Szukanie znacznika name
        xmlet = ElementTree.fromstring(self.xml)
        name = xmlet.find('.//name')
        
        return name.text
        
    def _getSourceDev(self):
        """
        Generuje nazwę dysku
        
        @param void
        @return nazwa
        @raise gdy nie znaleziono woluminu bazowego
        """
        # Usuwanie z listy nie działających agentów
        agents = getAgents()
        for agent in agents:
            response = agent.ping()
            if not response:
                agents.remove(agent)
            if response == "nolibvirt":
                agents.remove(agent)
        
        # Wybieranie pierwszego agenta z listy
        agent = agents[0]
        
        address = None
            
        for pool in agent.getPools():
            # Szukanie puli ze snapshotami
            if pool.getType() == 'dynamic-snapshot':
                # Szukanie definicji zbioru dysków
                splitted = pool.getName().split(':')
                if len(splitted) == 2:
                    # Szukanie nazwy woluminu bazowego
                    splitted = splitted[1].split("snapshots_")
                    if len(splitted) == 2:
                        if splitted[1] == self.basename:
                            address = pool.getIscsiAddress()
                            break
        
        # Sprawdzanie czy znaleziono adres
        if address == None:
            raise Exception("Nie znaleziono woluminu bazowego")
        
        address = address + '-lun-' + str(self.i)
        
        return address
        
    def getXML(self):
        """
        Zwraca XML definiujący maszynę wirtualną stworzoną ze snapshota
        
        @param void
        @return string
        """
        # Wczytanie szablonu
        if not os.path.exists('../etc/templates/' + self.template):
            if os.path.exists('../etc/templates/' + self.template + '.xml'):
                self.template += '.xml'
            else:
                print(Colors.setred(" * ") + u"Nie ma takiego szablonu")
                sys.exit(0)
        
        f = open('../etc/templates/' + self.template)
        xmldef = f.read()
        xmldef = str(xmldef)
        
        # Parsowanie zmiennych
        xmldef = xmldef.replace('$LUN', str(self.i))
        xmldef = xmldef.replace('$HEXLUN', str(hex(int(self.i)))[2:])
        xmldef = xmldef.replace('$BASELV', self.basename)
        xmldef = xmldef.replace('$SOURCEDEV', self._getSourceDev())
        xmldef = xmldef.replace('$AGENTSEQUENCE', str(self.agentsnapshotid))
        xmldef = xmldef.replace('$HEXAGENTSEQUENCE', str(hex(int(self.agentsnapshotid)))[2:])
        
        self.xml = xmldef
        
        return xmldef