# -*- coding: utf-8 -*-

############################################################################
#   
#   Copyright (C) 2015
#    Christian Kohlöffel
#    Vinzenz Schulz
#    Jean-Paul Schouwstra
#    Robert Lichtenberger
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

from Core.Point import Point
from Core.EntitieContent import EntitieContentClass

import logging
from Gui.EntryExitMoveBase import EntryExitMoveBase
logger = logging.getLogger('Gui.InlineMove')

from PyQt4 import QtCore

# Length of the cross.
dl = 0.2
DEBUG = 1

class InlineMove(EntryExitMoveBase):
    def __init__(self, startp, angle,
                 pencolor=QtCore.Qt.green,
                 shape=None, parent=None, isStartMove=True):
        self.isStartMove = isStartMove
        super(InlineMove, self).__init__(startp, angle, pencolor, shape, parent)

    def do_make_start_moves(self):
        # BaseEntitie created to add the StartMoves etc. This Entitie must not
        # be offset or rotated etc.
        BaseEntitie = EntitieContentClass(Nr=-1, Name='BaseEntitie',
                                          parent=None,
                                          children=[],
                                          p0=Point(x=0.0, y=0.0),
                                          pb=Point(x=0.0, y=0.0),
                                          sca=[1, 1, 1],
                                          rot=0.0)
        
        self.parent = BaseEntitie        
        
        if (self.shape.cut_cor == 41 or self.shape.cut_cor == 42):
            if (self.isStartMove):
                move = self.shape.geos[-1].fragment(False, self.shape.LayerContent.start_radius)
            else:
                move = self.shape.geos[0].fragment(True, self.shape.LayerContent.start_radius)
                
            if self.isStartMove:
                startPoint, dummy = move.get_start_end_points(0, self.parent)
                self.geos.append(startPoint)                    
                self.geos.append(move)
            else:
                self.geos.append(move)
        else:
            self.geos.append(self.startp)                    
    
