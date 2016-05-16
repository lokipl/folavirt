#!/usr/bin/env python2
# -*- coding: utf-8 -*-

try:
    import libvirt
except ImportError:
    print(u"! Brak modułu python-libvirt. Niektóre funkcje nie będą działać.")
    
from xml.dom import minidom
from xml.etree import ElementTree

class Statuses():
    DOMAIN_NOSTATE     = 0
    DOMAIN_RUNNING     = 1
    DOMAIN_BLOCKED     = 2
    DOMAIN_PAUSED      = 3 
    DOMAIN_SHUTDOWN    = 4
    DOMAIN_SHUTOFF     = 5
    DOMAIN_CRASHED     = 6
    DOMAIN_PMSUSPENDED = 7
    DOMAIN_LAST        = 8
    DOMAIN_DONTEXIST   = 20

class Domain():
    def __init__(self, uri = None, name = None):
        if uri != None:
            self.setName(name)
        if name != None:
            self.setUri(uri)
    
    name = -1
    """
    Ustawia nazwę domeny, tylko pole
    """
    def setName(self, name):
        self.name = name
    
    def getName(self):
        """
        Zwraca nazwę domeny
        
        @param void
        @return Nazwa
        """
        return self.name
    
    uri = -1
    """
    Ustawia uri maszyny, tylko pole
    """
    def setUri(self, uri):
        self.uri = uri
    """
    Zwraca uri maszyny
    """
    def getUri(self):
        return self.uri
    
    def getState(self):
        """
        Zwraca status domeny
        """
        try:
            connection = libvirt.open(self.getUri())
        except:
            return 21
        try:
            domain = connection.lookupByName(self.getName())
        except:
            return 20
        state = domain.state(0)[0]
        return state
    
    def destroy(self):
        """
        Zatrzymuje domenę
        """
        if self.getState() == 0 or self.getState() == 5:
            return -1
        else:
            connection = libvirt.open(self.getUri())
            domain = connection.lookupByName(self.getName())
            domain.destroy()
            connection.close()
            return 0
        
    def create(self):
        """
        Uruchamia domenę
        
        @param void
        @return void
        """
        if self.getState() == 1:
            return -1
        else:
            connection = libvirt.open(self.getUri())
            domain = connection.lookupByName(self.getName())
            try:
                domain.create()
            except libvirt.libvirtError as e:
                return str(e)
                
            connection.close()
            return 0
    
    # Usypia domenę
    def suspend(self):
        connection = libvirt.open(self.getUri())
        domain = connection.lookupByName(self.getName())
        try:
            domain.suspend()
        except:
            return 1
        connection.close()
        return 0
    
    # Wznawia domenę
    def resume(self):
        connection = libvirt.open(self.getUri())
        domain = connection.lookupByName(self.getName())
        domain.resume()
        connection.close()
        return 0
    
    # Resetuje domenę
    def reset(self):
        connection = libvirt.open(self.getUri())
        domain = connection.lookupByName(self.getName())
        try:
            domain.reset(0)
        except:
            return 1
        connection.close()
        return 0
    
    def dumpXML(self):
        """
        Zwraca definicję XML maszyny
        """
        connection = libvirt.open(self.getUri())
        domain = connection.lookupByName(self.getName())
        
        # Zwraca definicję
        return domain.XMLDesc(0)
    
    def getGraphicConsoleOptions(self):
        """
        Zwraca ustawienia konsoli graficznej
        
        @param void
        @return {port, type}
        """
        # Połączenie z nadzorcą
        connection = libvirt.open(self.getUri())
        domain = connection.lookupByName(self.getName())
        
        # Parsowanie definicji maszyny
        xmltree = minidom.parseString(domain.XMLDesc(0))
        graphics = xmltree.getElementsByTagName("graphics")[0]
        
        # Zwracanie portu i typu
        return {'port' : graphics.getAttribute('port'), 'type' : graphics.getAttribute('type'), 'listen': graphics.getAttribute('listen') }
    
    def setGraphicConsoleListen(self, address):
        """
        Ustawia adres na jakim ma słuchać VNC
        
        @param Adres
        @return void
        """        
        # Połączenie z nadzorcą
        connection = libvirt.open(self.getUri())
        domain = connection.lookupByName(self.getName())
        
        # Parsowanie definicji maszyny
        xmldesc = ElementTree.fromstring(domain.XMLDesc(0))
        originaldesc = ElementTree.tostring(xmldesc)
        
        # Usuwanie definicji domeny
        domain.undefine()
        
        # Zmiana adresu nasłuchiwania
        graphicelement = xmldesc.find('.//graphics')
        graphicelement.set('listen', address)
        # Zmiana obiektu listen
        listenelement = graphicelement.find('.//listen')
        listenelement.set('address', address)
        
        # Ponowne tworzenie maszyny wirtualnej
        try:
            connection.defineXML(ElementTree.tostring(xmldesc))
        except libvirt.libvirtError:
            connection.defineXML(originaldesc)
    
    def setGraphicConsolePasswd(self,passwd):
        """
        Ustawia hasło do konsoli VNC
        
        @param Hasło
        @return void
        """
        connection = libvirt.open(self.getUri())
        domain = connection.lookupByName(self.getName())
        try:
            domain.destroy()
            started = 1
        except:
            pass
            started = 0
        xmldesc = domain.XMLDesc(0)
        domain.undefine()

        xmltree = minidom.parseString(xmldesc)
        graphicstag = xmltree.getElementsByTagName("graphics")[0]
        graphicstag.setAttribute('passwd',passwd)
        
        connection.defineXML(xmltree.toxml())
        
        if started == 1:
            connection = libvirt.open(self.getUri())
            domain = connection.lookupByName(self.getName())
            domain.create()
        return 0