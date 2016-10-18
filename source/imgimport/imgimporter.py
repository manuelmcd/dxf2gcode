# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division

############################################################################
#
#   Copyright (C) 2008-2015
#    Christian Kohlöffel
#    Jean-Paul Schouwstra
#
#   This file is part of DXF2GCODE.
#
#   DXF2GCODE is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   DXF2GCODE is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with DXF2GCODE.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################

from __future__ import absolute_import

from copy import deepcopy, copy
import logging

from core.point import Point
from core.linegeo import LineGeo


import globals.globals as g

from globals.six import text_type
import globals.constants as c
if c.PYQT5notPYQT4:
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5 import QtCore
else:
    from PyQt4.QtGui import QMessageBox
    from PyQt4 import QtCore

logger = logging.getLogger("ImgImport.ImgImport")


class ReadIMG(QtCore.QObject):
    # Initialise the class
    def __init__(self, filename=None):
        QtCore.QObject.__init__(self)

        self.update_tool_values()

        sections_pos = self.Get_Sections_pos()
        self.layers = self.Read_Layers()
        self.blocks = self.Read_Blocks()
        self.entities = self.Read_Entities()


    def tr(self, string_to_translate):
        """
        Translate a string using the QCoreApplication translation framework
        @param: string_to_translate: a unicode string
        @return: the translated unicode string if it was possible to translate
        """
        return text_type(QtCore.QCoreApplication.translate('ReadDXF',
                                                           string_to_translate))





   

    # Search the TABLES section of the sections within this include LAYERS ???
    def Read_Layers(self):
        """
        Read_Layers()
        """

        layers.append(LayerClass(len(layers)))
        layers[-1].name = "Default Layer"

        return layers

  
    def Read_Blocks(self, blocks_pos):
        """
        Read_Blocks() - Read the block geometries
        """
        blocks = BlocksClass([])
        return blocks

    def Read_Entities(self, sections):
        """
        Read_Entities() - Read the entities geometries
        """
        for section_nr in range(len(sections)):
            if sections[section_nr - 1].name.startswith("ENTITIES"):
                # g.logger.logger.info("Reading Entities", 1)
                entities = EntitiesClass(0, 'Entities', [])
                entities.geo = self.Get_Geo()


    def Get_Geo(self):
        """
        Get_Geo() - Read the geometries of Blocks and Entities
        """
        geos = []
        geo.append(LineGeo(Ps=Ps, Pe=Pe))

class LayerClass:
    def __init__(self, Nr=0, name=''):
        self.Nr = Nr
        self.name = name

    def __str__(self):
        # how to print the object
        return 'Nr ->' + str(self.Nr) + '\nName ->' + self.name

    def __len__(self):
        return self.__len__

class EntitiesClass:
    def __init__(self, Nr=0, Name='', geo=[], cont=[]):
        self.Nr = Nr
        self.Name = Name
        self.basep = Point(x=0.0, y=0.0)
        self.geo = geo
        self.cont = cont

    def __str__(self):
        # how to print the object
        return "\nNr:      %s" % self.Nr +\
               "\nName:    %s" % self.Name +\
               "\nBasep:   %s" % self.basep +\
               "\nNumber of Geometries: %i" % len(self.geo) +\
               "\nNumber of Contours:   %i" % len(self.cont)

    def __len__(self):
        return self.__len__

    # Gibt einen List mit den Benutzten Layers des Blocks oder Entities zur�ck
    # Is a List back to results with the use of block layer or Entities ???
    def get_used_layers(self):
        used_layers = []
        for i in range(len(self.geo)):
            if (self.geo[i].Layer_Nr in used_layers) == 0:
                used_layers.append(self.geo[i].Layer_Nr)
        return used_layers
    # Gibt die Anzahl der Inserts in den Entities zur�ck
    # Returns the number of inserts back into the Entities ???

    def get_insert_nr(self):
        insert_nr = 0
        for i in range(len(self.geo)):
            if "Insert" in self.geo[i].Typ:
                insert_nr += 1
        return insert_nr

class BlocksClass:
    def __init__(self, Entities=[]):
        self.Entities = Entities

    def __str__(self):
        # how to print the object
        s = 'Blocks:\nNumber of Blocks ->' + str(len(self.Entities))
        for entitie in self.Entities:
            s += str(entitie)
        return s
