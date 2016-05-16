#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import SocketServer

class TcpListenerThreaded(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass
