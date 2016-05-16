#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from folavirt.console.Colors import Colors
from folavirt.utils.Database import Database
from folavirt.utils.TableCreator import TableCreator
from folavirt.xmlfactory.SnapshotDomain import SnapshotDomain
from folavirt.remote.Distributor import Distributor
from folavirt.remote.Agent import getAgents
from folavirt.remote.DiskManager import getDmByBaseName
from folavirt.remote.Domain import Domain

class Lab():
    tablename = "laboratory"
    
    """
    Laboratorium
    """
    def __init__(self, name, basename = None):
        self.name = name
        self.basename = basename
        
        # Baza danych
        TableCreator().createLaboratoryTableIfNeed(self.tablename)
        self.database = Database()
        
        # Pełna nazwa tabeli
        self.tablename = self.database.getPrefix() + self.tablename
    
    @staticmethod
    def getLabs():
        """
        Zwraca wszystkie laboratoria
        """
        # Baza danych
        Lab.tablename = "laboratory"
        TableCreator().createLaboratoryTableIfNeed(Lab.tablename)
        database = Database()
        # Pełna nazwa tabeli
        tablename = database.getPrefix() + Lab.tablename
        
        # Zapytanie
        query = "SELECT lab, baselv FROM " + tablename + " GROUP BY lab"
        # Wykonywanie zapytania
        database.getCursor().execute(query)
        
        labs = []
        # Parsowanie wyniku
        for result in database.getCursor().fetchall():
            if not str(result[0]).startswith("_hidden"):
                labs.append(Lab(result[0], result[1]))
        
        return labs

    def _getLastLunInDb(self):
        """
        Zwraca ostatni lun dla danej bazy
        """
        # Zapytanie o najwyższy lun w bazie
        query = "SELECT baselv, max(lun) FROM " + self.tablename + " WHERE baselv = '" + self.basename + "' GROUP BY baselv"
        self.database.getCursor().execute(query)
        try:
            result = self.database.getCursor().fetchall()[0]
            lastlun = int(result[1])
        except IndexError:
            # Brak ostatniego zapisu
            return 0
        
        return lastlun
        
    def _getMaxIdTable(self):
        """
        Zwraca tablę z maksymalnymi id na hostach
        """
        query = "SELECT max(idonhost), agent FROM "+self.tablename+" WHERE lab = '" + self.name + "' GROUP BY baselv, agent HAVING max(idonhost)"
        self.database.getCursor().execute(query)
        results = self.database.getCursor().fetchall()
        # Tworzenie tabeli
        maxidonhosts = {}
        agents = getAgents()
        for agent in agents:
            maxidonhosts[agent.getHostName()] = 0
            
        for result in results:
            maxidonhosts[result[1]] = result[0]
            
        return maxidonhosts
      
    def _refreshAgents(self):
        # Odświeżanie stanu iscsi         
        agents = getAgents()
                
        print(Colors.setgreen(" * ") + u"Aktualizowanie stanu puli dyskowej")
                
        # Wysyłanie żądania do każdego z hostów
        for agent in agents:
            print(Colors.setgreen(" * ") + u"Odświeżanie agenta " + Colors.setbold(agent.getHostName()))
                    
            # Odświeżanie pul dyskowych
            try:
                agent.poolSync()
            except:
                print(Colors.setred(" * ") + u"Błąd odświeżania agenta " + Colors.setbold(agent.getHostName()))
        
    def createSnapshots(self, count, size):
        """
        Tworzy snapshoty
        """
        size = str(size)
        
        # Sprawdzanie czy podano jednostki, jeśli nie, dodawanie gigabajtów
        if size[-1:].isdigit():
            size += "G"
        
        # Skanowanie w poszukiwaniu takiego dm gdzie jest dana baza
        dm = getDmByBaseName(self.basename)
        
        print(Colors.setgreen(" * ") + u"Tworzenie snapshotowanych woluminów ...")
        for i in range(count):
            # Tworzenie snapshotu
            result = dm.createSnapshot(self.basename, size)
            if result:
                print(Colors.setgreen(" * ") + u"Utworzono snapshot. " + str(i+1) + "/" + str(count))
            else:
                print(Colors.setred(" * ") + u"Błąd podczas tworzenia snapshotu. " + str(i+1) + "/" + str(count)),
                print(u"Kontynuować? [y|n]"),
                out = raw_input()
                if out != "y":
                    print(Colors.setred(" * ") + "Koniec")
                    sys.exit(1)
                # Tworzenie z liczbą snapshotów ile się dało utworzyć
                count = i
         
        self._refreshAgents()
                
        return count
        
    def createSnapshotMachines(self, template, count, balancer):
        """
        Tworzy snapshotowane maszyny wirtualne
        
        @param Template
        @param Ilość
        @param Balancer
        @return void
        """
        # Pobieranie ostatniego numeru Lun
        lastlun = self._getLastLunInDb()
        
        # Zapytanie o najwyższy przyznany id na każdym z hostów
        maxidonhosts = self._getMaxIdTable()
           
        self.snapshots = []
        for _ in range(count):
            lastlun += 1
            self.snapshots.append(SnapshotDomain(template, self.basename, lastlun))
           
        # Wykonywanie dystrybucji maszyn
        distributor = Distributor(self.snapshots, balancer, maxidonhosts)
        self.snapshots = distributor.xmlfactories    # Pobieranie zaktualizowanej listy snapshotów
        
        for snapshot in self.snapshots:
            # Zapytanie, dodające informację o snapshocie.
            query = "INSERT INTO " + self.tablename +" (lab, baselv, name, agent, lun, idonhost) "
            query += "VALUES('" + self.name + "', '" + self.basename + "', '" + snapshot.getName() + "',"
            query += "'"+snapshot.agentname+"' , "+str(snapshot.i)+", "+str(snapshot.agentsnapshotid)+")"
            
            # Wykonywanie zapytania
            self.database.getCursor().execute(query)
        
        # Zapisanie tranzakcji
        self.database.commit()
        
    def setPermissions(self, userlist):
        """
        Ustawia dostęp do snapshotów
        
        @param []
        @return void
        """
        for i in range(len(self.snapshots)):
            domain = Domain(self.snapshots[i].getName())
            domain.searchAgent()
            
            # Ustawienie losowego hasła
            passwd = domain.setGraphicConsoleRandomPasswd()
            print(Colors.setgreen(" * ") + u"Ustawiono hasło do konsoli graficznej na " + passwd)
            
            # Dodawanie uprawnień użytkownikowi
            domain.addOwnership(userlist[i])
            print(Colors.setgreen(" * ") + u"Przypisano maszynę " + self.snapshots[i].getName() + u" użytkownikowi " + userlist[i])
    
    def getDomains(self):
        """
        Zwraca wszystkie domeny
        """
        query = "SELECT name FROM " + self.tablename + " WHERE lab = '" + self.name + "'"
        self.database.getCursor().execute(query)
        
        domains = []
        for result in self.database.getCursor().fetchall():
            domains.append(Domain(result[0]))
            
        return domains
       
    def getBaselvByName(self, name):
        # Odpytywanie bazy danych o domeny w tym laboratorium
        query = "SELECT baselv FROM " + self.tablename + " WHERE lab = '" + self.name + "' AND name = '" + name + "'"
        self.database.getCursor().execute(query)
        
        try:
            self.basename = self.database.getCursor().fetchone()[0]
            return self.basename
        except TypeError:
            raise Exception(u"Nie ma takiego snapshotu")  
        
    def getLunByName(self, name):
        # Odpytywanie bazy danych o domeny w tym laboratorium
        query = "SELECT lun FROM " + self.tablename + " WHERE lab = '" + self.name + "' AND name = '" + name + "'"
        self.database.getCursor().execute(query)
        
        return self.database.getCursor().fetchone()[0]
          
    def removeByName(self, name, lun):
        print(Colors.setgreen(" * ") + u"Usuwanie maszyny wirtualnej " + name)
        domain = Domain(name)
        try:
            domain.searchAgent()
            domain.clearOwnership()
            domain.undefine()
        except Exception as e:
            print(Colors.setred(" * ") + u"Błąd: "),
            print(str(e).decode("utf8", "ignore"))
        
        # Usuwanie snapshotów u zarządcy dyskami
        print(Colors.setgreen(" * ") + u"Usuwanie snapshotu nr " + str(lun) + u" bazy " + self.basename)
        
        # Zarządca dyskami
        dm = getDmByBaseName(self.basename)  
        
        try:
            dm.removeSnapshot(self.basename, lun)
        except Exception as e:
            print(Colors.setred(" * ") + u"Błąd: "),
            print(str(e).decode("utf8", "ignore"))
          
        # Usuwanie domeny z laboratorium
        query = "DELETE FROM " + self.tablename + " WHERE lab = '" + self.name + "' AND name = '" + name + "'"
        self.database.getCursor().execute(query)
        self.database.commit()
          
    def remove(self):
        """
        Usuwanie laboratorium
        """        
        # Szukanie bazy
        lab = [x for x in self.getLabs() if x.name == self.name]
        if lab == []:
            print(Colors.setred(" * ") + u"Nie ma takiego laboratorium")
            sys.exit(0)
            
        self.basename = lab[0].basename
        
        # Zarządca dyskami
        try:
            dm = getDmByBaseName(self.basename)
        except Exception as e:
            print(Colors.setred(" * ") + str(e).decode('utf-8'))
            sys.exit(1)
        
        # Odpytywanie bazy danych o domeny w tym laboratorium
        query = "SELECT name, lun FROM " + self.tablename + " WHERE lab = '" + self.name + "'"
        self.database.getCursor().execute(query)

        for result in self.database.getCursor().fetchall():            
            # Usuwanie domeny z nadzorcy
            print(Colors.setgreen(" * ") + u"Usuwanie maszyny wirtualnej " + result[0])
            domain = Domain(result[0])
            try:
                domain.searchAgent()
                domain.clearOwnership()
                domain.undefine()
            except Exception as e:
                print(Colors.setred(" * ") + u"Błąd: "),
                print(str(e).decode("utf8", "ignore"))
            
            # Usuwanie snapshotów u zarządcy dyskami
            print(Colors.setgreen(" * ") + u"Usuwanie snapshotu nr " + str(result[1]) + u" bazy " + self.basename)
            try:
                dm.removeSnapshot(self.basename, result[1])
            except Exception as e:
                print(Colors.setred(" * ") + u"Błąd: "),
                print(str(e).decode("utf8", "ignore"))
            
            # Usuwanie domeny z laboratorium
            query = "DELETE FROM " + self.tablename + " WHERE lab = '" + self.name + "' AND name = '" + result[0] + "'"
            self.database.getCursor().execute(query)
            self.database.commit()
        
        # Odświeżanie pul agentów
        self._refreshAgents()
       
    def removeFromDatabase(self):
        query = "DELETE FROM " + self.tablename + " WHERE lab = '" + self.name + "'"
        self.database.getCursor().execute(query)
        self.database.commit()