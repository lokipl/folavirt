#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import SocketServer
import ConfigParser

from folavirt.virt.Host import Host
from folavirt.networking.Query import Query
from folavirt.networking.Response import Response
from folavirt.permissions.Network import Network

# Odpowiedzi agenta
from folavirt.agent.response.DomainResponses import DomainResponses
from folavirt.agent.response.PoolResponses import PoolResponses
from folavirt.agent.response.IscsiResponses import IscsiResponses
from folavirt.agent.response.VmResponse import VmResponse
from folavirt.agent.response.OwnershipResponse import OwnershipResponse

class TcpRequestHandler(SocketServer.BaseRequestHandler):
    def domainslist(self, uri):
        host = Host(uri)
        if host.libvirtTest():
            return host.getDomains()
        else:
            return []
        
    def handle(self):
        """
        Obsługa nowego połączenia
        """
        
        # Parsowanie pliku konfiguracyjnego
        parser = ConfigParser.ConfigParser()
        parser.read("../etc/folavirt.ini")
        
        # Logowanie nowego połączenia
        try:
            if parser.get("folavirtd", "log_connections") == 1:
                print("Connected from " + self.client_address[0])
        except ConfigParser.NoOptionError:
            pass

        # Sprawdzanie dostępu
        if not Network().allowed(self.client_address[0]):
            self.request.sendall("denied\n")
            print("Connection denied for " + self.client_address[0])
            self.finish()
        else:
            while True:
                # Oczekiwanie na dane
                data = self.request.recv(16384).strip()
                if(data != ""):
                    # Logowanie zapytań
                    try:
                        if parser.getint("folavirtd", "log_query") == 1:
                            print("Query: " + data)
                    except ConfigParser.NoOptionError:
                        pass
                    
                    # Czy wysłano koniec połączenia
                    if data == "quit":
                        self.request.sendall("bye\n")
                        self.finish()
                        return
    
                    q = Query()
                    try:
                        q.setFromJSON(data)
                    except ValueError:
                        print("Bad request from " + self.client_address[0])
                        self.finish()
                        return
                    
                    # Prawa do domen
                    r = OwnershipResponse(q).getResponse()
                    if r != None:
                        self.request.sendall(r.getJSON())
                        continue
                                    
                    # Domeny
                    domains = DomainResponses(q)
                    r = domains.getResponse()
                    if r != None:
                        self.request.sendall(r.getJSON())
                        continue
                    
                    # Pule dyskowe
                    pools = PoolResponses(q)
                    r = pools.getResponse()
                    if r != None:
                        self.request.sendall(r.getJSON())
                        continue
                    
                    # Iscsi
                    iscsis = IscsiResponses(q)
                    r = iscsis.getResponse()
                    if r != None:
                        self.request.sendall(r.getJSON())
                        continue
                    
                    # Zarządzanie maszynami wirtualnymi
                    vms = VmResponse(q)
                    r = vms.getResponse()
                    if r != None:
                        self.request.sendall(r.getJSON())
                        continue
                    
                    # Lista domen
                    if q.getCommand() == "vmlist":
                        r = Response()
                        r.setCommand("vmlist")
                        r.setData(self.domainslist(parser.get("libvirt", "uri")))
                        self.request.sendall(r.getJSON())
                        continue
                    
                    # Ping
                    if q.getCommand() == "ping":
                        host = Host(parser.get("libvirt", "uri"))
                        r = Response()
                        if host.libvirtTest():
                            r.setCommand("pong")
                            self.request.sendall(r.getJSON())
                            continue
                        else:
                            r = Response()
                            r.setCommand("nolibvirt")
                            self.request.sendall(r.getJSON())
                            continue
                    
                    r = Response()
                    r.setErrorCode(1337)
                    r.setCommand("notexists")
                    self.request.sendall(r.getJSON())
                else:
                    self.finish()
                    break