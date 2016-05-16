#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
from xml.dom import minidom

from folavirt.console.Colors import Colors
from folavirt.remote.DiskManager import getDms

class BaseDomain():
    def __init__(self, name, basename, template, lun):
        self.name = name
        self.basename = basename
        self.template = template
        self.lun = lun
    
    def getName(self):
        """
        Zwraca nazwę maszyny
        """
        basedomainxml = self.getXML()

        xmldesc = minidom.parseString(basedomainxml)
        nametag = xmldesc.getElementsByTagName("name");
  
        return nametag[0].firstChild.data
    
    def _getSourceDev(self):
        """
        Zwraca bazową pulę
        """
        # Szukanie bazy
        dms = getDms()
        for dm in dms:
            for basevolume in dm.getBaseVolumes():
                if basevolume == self.basename:
                    # Brać z tego woluminu
                    return dm.getBaseDiskSourceDev() + "-lun-" + str(self.lun)
    
    def getXML(self):
        """
        Zwraca definicję maszyny wirtualnej
        """        
        if not os.path.exists('../etc/templates/' + self.template):
            if os.path.exists('../etc/templates/' + self.template + '.xml'):
                self.template += '.xml'
            else:
                print(Colors.setred(" * ") + u"Nie ma takiego szablonu")
                sys.exit(0)
        
        # Wczytanie szablonu
        f = open('../etc/templates/' + self.template)
        xmldef = f.read()
        xmldef = str(xmldef)
        
        xmldef = xmldef.replace('$HEXLUN', "00")
        xmldef = xmldef.replace('$NAME', str(self.name))
        xmldef = xmldef.replace('$LUN', str(self.lun))
        xmldef = xmldef.replace('$BASELV', self.basename)
        xmldef = xmldef.replace('$SOURCEDEV', self._getSourceDev())
        
        return xmldef
