#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import SocketServer
import ConfigParser

from folavirt.networking.Query import Query
from folavirt.networking.Response import Response
from folavirt.disks.response.BaseResponse import BaseResponse
from folavirt.disks.response.SnapshotResponse import SnapshotResponse
from folavirt.permissions.Network import Network

class TcpRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        parser = ConfigParser.ConfigParser()
        parser.read("../etc/folavirt.ini")
        
        try:
            if parser.get("foladiskd", "log_connections") == 1:
                print("Connected from " + self.client_address[0])
        except ConfigParser.NoOptionError:
            pass
        
        if not Network().allowed(self.client_address[0]):
            self.request.sendall("denied\n")
            print("Connection denied for " + self.client_address[0])
            self.finish()
        else:
            while True:
                data = self.request.recv(1024).strip()
                if(data != ""):
                    try:
                        if parser.getint("foladiskd", "log_query") == 1:
                            print("Query: " + data)
                    except ConfigParser.NoOptionError:
                        pass
                    
                    if data == "quit":
                        self.request.sendall("bye\n")
                        self.finish()
                        return
                    
                    # Odebranie zapytania
                    q = Query()
                    try:
                        q.setFromJSON(data)
                    except ValueError:
                        print("Bad request from " + self.client_address[0])
                        self.finish()
                        return
                    
                    # Obsługa pinga
                    if q.getCommand() == "ping":
                        r = Response()
                        r.setCommand("pong")
                        self.request.sendall(r.getJSON())
                        continue
                    
                    # Zapytania o bazy woluminów
                    r = BaseResponse(q).getResponse()
                    if r != None:
                        self.request.sendall(r.getJSON())
                        continue
                    
                    # Zapytania dot. snapshotów
                    r = SnapshotResponse(q).getResponse()
                    if r != None:
                        self.request.sendall(r.getJSON())
                        continue
                    
                    # Wysłać jeśli polecenie jest niezrozumiałe
                    r = Response()
                    r.setErrorCode(1337)
                    r.setCommand("notexists")
                    self.request.sendall(r.getJSON())
                else:
                    self.finish()
                    break