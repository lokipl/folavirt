#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
from folavirt.console.Colors import Colors
from ConfigParser import ConfigParser

try:
    import MySQLdb
except ImportError:
    pass

class Database():
    """
    To są wartości domyślne, konfiguracja jest w etc
    """
    host = "127.0.0.1"
    port = "3306"
    db = "folavirt"
    user = "folavirt"
    password = "folavirt"
    prefix = "folavirt_"
    
    cursor = None
    
    def __init__(self):        
        config = ConfigParser()
        try:
            config.readfp(open('../etc/folavirt.ini'))
        except IOError:
            print Colors.red + " * " + Colors.nocolor + "Brak pliku konfiguracyjnego bazy danych"
            sys.exit(1)
        
        self.host = config.get('database','host')
        self.port = config.getint('database','port')
        self.db = config.get('database','db')
        self.user = config.get('database','user')
        self.password = config.get('database','passwd')
        self.prefix = config.get('database','prefix')
       
    def getPrefix(self):
        """ Zwraca prefix tabel baz danych """
        return self.prefix
       
    def getCursor(self):
        """ Zwraca kursor bazy danych """
        if self.cursor == None:
            self.database = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.db)
            self.cursor = self.database.cursor()    
        
        return self.cursor
    
    def commit(self):
        self.database.commit()
