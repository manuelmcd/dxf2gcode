#!/usr/bin/python
# -*- coding: cp1252 -*-
#
#dxf2gcode_b02_point
#Programmers:   Christian Kohl�ffel
#               Vinzenz Schulz
#
#Distributed under the terms of the GPL (GNU Public License)
#
#dxf2gcode is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from Canvas import Oval, Arc, Line
from math import sqrt, sin, cos, atan2, radians, degrees, pi, floor, ceil, copysign
from copy import copy

#Length of the cross.
dl=1

class PointClass:
    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y
    def __str__(self):
        return ('X ->%6.3f  Y ->%6.3f' %(self.x,self.y))
        #return ('CPoints.append(PointClass(x=%6.5f, y=%6.5f))' %(self.x,self.y))
    def __cmp__(self, other) : 
        return (self.x == other.x) and (self.y == other.y)
    def __neg__(self):
        return -1.0*self
    def __add__(self, other): # add to another point
        return PointClass(self.x+other.x, self.y+other.y)
    def __sub__(self, other):
        return self + -other
    def __rmul__(self, other):
        return PointClass(other * self.x,  other * self.y)
    def __mul__(self, other):
        if type(other)==list:
            #Skalieren des Punkts
            return PointClass(x=self.x*other[0],y=self.y*other[1])
        else:
            #Skalarprodukt errechnen
            return self.x*other.x + self.y*other.y

    def unit_vector(self,Pto=None):
        diffVec=Pto-self
        l=diffVec.distance()
        return PointClass(diffVec.x/l,diffVec.y/l)
    def distance(self,other=None):
        if type(other)==type(None):
            other=PointClass(x=0.0,y=0.0)
        return sqrt(pow(self.x-other.x,2)+pow(self.y-other.y,2))
    def norm_angle(self,other=None):
        if type(other)==type(None):
            other=PointClass(x=0.0,y=0.0)
        return atan2(other.y-self.y,other.x-self.x)
    def isintol(self,other,tol):
        return (abs(self.x-other.x)<=tol) & (abs(self.y-other.y)<tol)
    def transform_to_Norm_Coord(self,other,alpha):
        xt=other.x+self.x*cos(alpha)+self.y*sin(alpha)
        yt=other.y+self.x*sin(alpha)+self.y*cos(alpha)
        return PointClass(x=xt,y=yt)
    def get_arc_point(self,ang=0,r=1):
        return PointClass(x=self.x+cos(radians(ang))*r,\
                          y=self.y+sin(radians(ang))*r)

    def Write_GCode(self,parent=None,postpro=None):
        point=self.rot_sca_abs(parent=parent)
        return postpro.rap_pos_xy(point)
    
    def plot2can(self,canvas=None,parent=None,tag=None,col='black'):
        pass
    
    def triangle_height(self,other1,other2):
        #Die 3 L�ngen des Dreiecks ausrechnen
        a=self.distance(other1)
        b=other1.distance(other2)
        c=self.distance(other2)
        return sqrt(pow(b,2)-pow((pow(c,2)+pow(b,2)-pow(a,2))/(2*c),2))  
      
    def rot_sca_abs(self,sca=None,p0=None,pb=None,rot=None,parent=None):
        if type(sca)==type(None) and type(parent)!=type(None):
            p0=parent.p0
            pb=parent.pb
            sca=parent.sca
            rot=parent.rot
            
            pc=self-pb
            rotx=(pc.x*cos(rot)+pc.y*-sin(rot))*sca[0]
            roty=(pc.x*sin(rot)+pc.y*cos(rot))*sca[1]
            p1= PointClass(x=rotx,y=roty)+p0
            
            #Rekursive Schleife falls selbst eingef�gt
            if type(parent.parent)!=type(None):
                p1=p1.rot_sca_abs(parent=parent.parent)
            
        elif type(parent)==type(None) and type(sca)==type(None):
            p0=PointClass(0,0)
            pb=PointClass(0,0)
            sca=[0,0,0]
            rot=0
            
            pc=self-pb
            rot=rot
            rotx=(pc.x*cos(rot)+pc.y*-sin(rot))*sca[0]
            roty=(pc.x*sin(rot)+pc.y*cos(rot))*sca[1]
            p1= PointClass(x=rotx,y=roty)+p0
        else:
            pc=self-pb
            rot=rot
            rotx=(pc.x*cos(rot)+pc.y*-sin(rot))*sca[0]
            roty=(pc.x*sin(rot)+pc.y*cos(rot))*sca[1]
            p1= PointClass(x=rotx,y=roty)+p0
        
        
#        print(("Self:    %s\n" %self)+\
#                ("P0:      %s\n" %p0)+\
#                ("Pb:      %s\n" %pb)+\
#                ("Pc:      %s\n" %pc)+\
#                ("rot:     %0.1f\n" %degrees(rot))+\
#                ("sca:     %s\n" %sca)+\
#                ("P1:      %s\n\n" %p1))
        
        return p1
      
class PointsClass:
    #Initialisieren der Klasse
    def __init__(self,point_nr=0, geo_nr=0,Layer_Nr=None,be=[],en=[],be_cp=[],en_cp=[]):
        self.point_nr=point_nr
        self.geo_nr=geo_nr
        self.Layer_Nr=Layer_Nr
        self.be=be
        self.en=en
        self.be_cp=be_cp
        self.en_cp=en_cp
        
    
    #Wie die Klasse ausgegeben wird.
    def __str__(self):
        # how to print the object
        return '\npoint_nr ->'+str(self.point_nr)+'\ngeo_nr ->'+str(self.geo_nr) \
               +'\nLayer_Nr ->'+str(self.Layer_Nr)\
               +'\nbe ->'+str(self.be)+'\nen ->'+str(self.en)\
               +'\nbe_cp ->'+str(self.be_cp)+'\nen_cp ->'+str(self.en_cp)

class ContourClass:
    #Initialisieren der Klasse
    def __init__(self,cont_nr=0,closed=0,order=[],length=0):
        self.cont_nr=cont_nr
        self.closed=closed
        self.order=order
        self.length=length

    #Komplettes umdrehen der Kontur
    def reverse(self):
        self.order.reverse()
        for i in range(len(self.order)):
            if self.order[i][1]==0:
                self.order[i][1]=1
            else:
                self.order[i][1]=0
        return

    #Ist die klasse geschlossen wenn ja dann 1 zur�ck geben
    def is_contour_closed(self):

        #Immer nur die Letzte �berpr�fen da diese neu ist        
        for j in range(len(self.order)-1):
            if self.order[-1][0]==self.order[j][0]:
                if j==0:
                    self.closed=1
                    return self.closed
                else:
                    self.closed=2
                    return self.closed
        return self.closed


    #Ist die klasse geschlossen wenn ja dann 1 zur�ck geben
    def remove_other_closed_contour(self):
        for i in range(len(self.order)):
            for j in range(i+1,len(self.order)):
                #print '\ni: '+str(i)+'j: '+str(j)
                if self.order[i][0]==self.order[j][0]:
                    self.order=self.order[0:i]
                    break
        return 
    #Berechnen der Zusammengesetzen Kontur L�nge
    def calc_length(self,geos=None):        
        #Falls die beste geschlossen ist und erste Geo == Letze dann entfernen
        if (self.closed==1) & (len(self.order)>1):
            if self.order[0]==self.order[-1]:
                del(self.order[-1])

        self.length=0
        for i in range(len(self.order)):
            self.length+=geos[self.order[i][0]].length
        return


    
#===============================================================================
#    def analyse_and_opt(self,geos=None):
#        #Errechnen der L�nge
#        self.calc_length(geos)
#        
#        #Optimierung f�r geschlossene Konturen
#        if self.closed==1:
#            summe=0
#            #Berechnung der Fl�ch nach Gau�-Elling Positive Wert bedeutet CW
#            #negativer Wert bedeutet CCW geschlossenes Polygon
#            geo_point_l, dummy=geos[self.order[-1][0]].get_start_end_points(self.order[-1][1])            
#            for geo_order_nr in range(len(self.order)):
#                geo_point, dummy=geos[self.order[geo_order_nr][0]].get_start_end_points(self.order[geo_order_nr][1])
#                summe+=(geo_point_l.x*geo_point.y-geo_point.x*geo_point_l.y)/2
#                geo_point_l=geo_point
#            if summe>0.0:
#                self.reverse()
# 
#            #Suchen des kleinsten Startpunkts von unten Links X zuerst (Muss neue Schleife sein!)
#            min_point=geo_point_l
#            min_point_nr=None
#            for geo_order_nr in range(len(self.order)):
#                geo_point, dummy=geos[self.order[geo_order_nr][0]].get_start_end_points(self.order[geo_order_nr][1])
#                #Geringster Abstand nach unten Unten Links
#                if (min_point.x+min_point.y)>=(geo_point.x+geo_point.y):
#                    min_point=geo_point
#                    min_point_nr=geo_order_nr
#            #Kontur so anordnen das neuer Startpunkt am Anfang liegt
#            self.set_new_startpoint(min_point_nr)
#            
#        #Optimierung f�r offene Konturen
#        else:
#            geo_spoint, dummy=geos[self.order[0][0]].get_start_end_points(self.order[0][1])
#            geo_epoint, dummy=geos[self.order[0][0]].get_start_end_points(not(self.order[0][1]))
#            if (geo_spoint.x+geo_spoint.y)>=(geo_epoint.x+geo_epoint.y):
#                self.reverse()
#===============================================================================


    #Neuen Startpunkt an den Anfang stellen
    def set_new_startpoint(self,st_p):
        self.order=self.order[st_p:len(self.order)]+self.order[0:st_p]
        
    #Wie die Klasse ausgegeben wird.
    def __str__(self):
        # how to print the object
        return '\ncont_nr ->'+str(self.cont_nr)+'\nclosed ->'+str(self.closed) \
               +'\norder ->'+str(self.order)+'\nlength ->'+str(self.length)

class ArcGeo:
    def __init__(self,Pa=None,Pe=None,O=None,r=1,s_ang=None,e_ang=None,dir=1):
        self.type="ArcGeo"
        self.Pa=Pa
        self.Pe=Pe
        self.O=O
        self.r=abs(r)
        self.s_ang=s_ang
        self.e_ang=e_ang
        self.BB=[]
        self.col='Black'
        
       
        # Kreismittelpunkt bestimmen wenn Pa,Pe,r,und dir bekannt
        if type(self.O)==type(None):
           
            if (type(Pa)!=type(None)) and (type(Pe)!=type(None)) and (type(dir)!=type(None)):
               
                arc=self.Pe.norm_angle(Pa)-pi/2
                Ve=Pe-Pa
                m=(sqrt(pow(Ve.x, 2)+pow(Ve.y, 2)))/2
                lo=sqrt(pow(r, 2)-pow(m, 2))
                if dir<0:
                    d=-1
                else:
                    d=1
                self.O=Pa+0.5*Ve
                self.O.y+=lo*sin(arc)*d
                self.O.x+=lo*cos(arc)*d
                
              
        # Falls nicht �bergeben Mittelpunkt ausrechnen  
            elif (type(self.s_ang)!=type(None)) and (type(self.e_ang)!=type(None)):
                self.O.x=self.Pa.x-r*cos(self.s_ang)
                self.O.y=self.Pa.y-r*sin(self.s_ang)
            else:
                print('Fehlende Angabe f�r Kreis')

        #Falls nicht �bergeben dann Anfangs- und Endwinkel ausrechen            
        if type(self.s_ang)==type(None):
            self.s_ang=self.O.norm_angle(Pa)
            
        if type(self.e_ang)==type(None):
            self.e_ang=self.O.norm_angle(Pe)
        
        #Aus dem Vorzeichen von dir den extend ausrechnen
        self.ext=self.e_ang-self.s_ang
        if dir>0.0:
            self.ext=self.ext%(-2*pi)
            self.ext-=floor(self.ext/(2*pi))*(2*pi)
        else:
            self.ext=self.ext%(-2*pi)
            self.ext+=ceil(self.ext/(2*pi))*(2*pi)

        #Falls es ein Kreis ist Umfang 2pi einsetzen        
        if self.ext==0.0:
            self.ext=2*pi
                   
        
        self.length=self.r*abs(self.ext)

    def __str__(self):
        """ 
        Standard method to print the object
        @return: A string
        """ 
        return ("\nArcGeo")+\
               ("\nPa : %s; s_ang: %0.5f" %(self.Pa,self.s_ang))+\
               ("\nPe : %s; e_ang: %0.5f" %(self.Pe,self.e_ang))+\
               ("\nO  : %s; r: %0.3f" %(self.O,self.r))+\
               ("\nBB : %s" %self.BB)+\
               ("\next  : %0.5f; length: %0.5f" %(self.ext,self.length))

    
    def dif_ang(self, P1, P2, dir):
        """
        Calculated the angle of extend based on the 3 given points. Center Point,
        P1 and P2.
        @param P1: the start point of the arc 
        @param P2: the end point of the arc
        @param dir: the direction of the arc
        @return: Returns the angle between -2* pi and 2 *pi for the arc extend
        """ 
        sa=self.O.norm_angle(P1)
       
        if(sa<0):
            sa+=2*pi
        
        ea=self.O.norm_angle(P2)
        if(ea<0):
            ea+=2*pi
        
        if(dir>0):     # GU
            if(sa>ea):
                ang=(2*pi-sa+ea)
            else:
                ang=(ea-sa)
        else:
            if(ea>sa):
                ang=(sa+2*pi-ea)
            else:
                ang=(sa-ea)
        
        return(ang)        
        
    def reverse(self):
        """ 
        Reverses the direction of the arc (switch direction).
        """ 
        Pa=self.Pa
        Pe=self.Pe
        ext=self.ext
        s_ang=self.e_ang
        e_ang=self.s_ang
        
        self.Pa=Pe
        self.Pe=Pa
        self.ext=ext*-1
        self.s_ang=s_ang
        self.e_ang=e_ang
        
    def make_abs_geo(self,parent=None,reverse=0):
        """
        Generates the absolut geometry based on the geometry self and the
        parent. If reverse 1 is given the geometry may be reversed.
        @param parent: The parent of the geometry (EntitieContentClass)
        @param reverse: If 1 the geometry direction will be switched.
        @return: A new ArcGeoClass will be returned.
        """ 
        Pa=self.Pa.rot_sca_abs(parent=parent)
        Pe=self.Pe.rot_sca_abs(parent=parent)
        O=self.O.rot_sca_abs(parent=parent)
        r=self.scaleR(self.r,parent)
        dir=copysign(1,self.ext)
        #s_ang=self.rot_angle(self.s_ang,parent)
        #e_ang=self.rot_angle(self.e_ang,parent)
        abs_geo=ArcGeo(Pa=Pa,Pe=Pe,O=O,r=r,dir=dir)
        if reverse:
            abs_geo.reverse()
        return abs_geo
    
    def calc_bounding_box(self):
        """
        Calculated the BoundingBox of the geometry and saves it into self.BB
        """
        
        Pa=PointClass(x=self.O.x-self.r,y=self.O.y-self.r)
        Pe=PointClass(x=self.O.x+self.r,y=self.O.y+self.r)
        
        #Do the calculation only for arcs have positiv extend => switch angles
        if self.ext>=0:
            s_ang=self.s_ang
            e_ang=self.e_ang
        elif self.ext<0:
            s_ang=self.e_ang
            e_ang=self.s_ang
                 
        #If the positive X Axis is crossed
        if not(self.wrap(s_ang,0)>=self.wrap(e_ang,1)):
            Pe.x=max(self.Pa.x,self.Pe.x)

        #If the positive Y Axis is crossed 
        if not(self.wrap(s_ang-pi/2,0)>=self.wrap(e_ang-pi/2,1)):
            Pe.y=max(self.Pa.y,self.Pe.y)

        #If the negative X Axis is crossed
        if not(self.wrap(s_ang-pi,0)>=self.wrap(e_ang-pi,1)):
            Pa.x=min(self.Pa.x,self.Pe.x)

        #If the negative Y is crossed 
        if not(self.wrap(s_ang-1.5*pi,0)>=self.wrap(e_ang-1.5*pi,1)):
            Pa.y=min(self.Pa.y,self.Pe.y)
       
        self.BB=BoundingBoxClass(Pa=Pa,Pe=Pe)
        
    def wrap(self,angle,isend=0):
        """
        Wrapes the given angle into a range between 0 and 2pi
        @param angle: The angle to be wraped
        @param isend: If the angle is the end angle or start angle, this makes a
        difference at 0 or 2pi.
        @return: Returns the angle between 0 and 2 *pi
        """ 
        wrap_angle=angle%(2*pi)
        if isend and wrap_angle==0.0:
            wrap_angle+=2*pi
        elif wrap_angle==2*pi:
            wrap_angle-=2*pi
            
        return wrap_angle
    
    
    def plot2can(self,canvas=None,tag=None,col='black',plotoption=0):
        """
        Plots the geometry of self into the defined canvas. Arcs will be ploted
        as line segments.
        @param canvas: The canvas instance to plot in
        @param tag: the number of the parent shape
        @param col: The color in which the shape shall be ploted
        @param plotoption: Additional option for Debug print use
        @return: Returns the hdl or hdls of the ploted objects.
        """
                        
        x=[]; y=[]; hdl=[]
        #Alle 10 Grad ein Segment => 120 Segmente f�r einen Kreis !!
        segments=int((abs(degrees(self.ext))//2)+1)
        
        for i in range(segments+1):
            
            ang=self.s_ang+i*self.ext/segments
            p_cur=PointClass(x=(self.O.x+cos(ang)*abs(self.r)),\
                       y=(self.O.y+sin(ang)*abs(self.r)))
                    
            x.append(p_cur.x)
            y.append(p_cur.y)
            
            if i>=1:
                hdl.append(Line(canvas,x[i-1],-y[i-1],x[i],-y[i],tag=tag,fill=col))       
               
        if plotoption:
            hdl.append(Line(canvas,self.Pa.x-dl,-self.Pa.y-dl,
                            self.Pa.x+dl,-self.Pa.y+dl,tag=tag,fill=col))
            hdl.append(Line(canvas,self.Pa.x+dl,-self.Pa.y-dl,
                            self.Pa.x-dl,-self.Pa.y+dl,tag=tag,fill=col))
            hdl.append(Line(canvas,self.Pe.x-dl,-self.Pe.y-dl,
                            self.Pe.x+dl,-self.Pe.y+dl,tag=tag,fill=col))
            hdl.append(Line(canvas,self.Pe.x+dl,-self.Pe.y-dl,
                            self.Pe.x-dl,-self.Pe.y+dl,tag=tag,fill=col))
            
        self.BB.plot2can(canvas=canvas,tag=tag,col='red',hdl=hdl)
         
        return hdl  

    def get_start_end_points(self,direction):
        """
        Returns the start/end point and its direction
        @param direction: 0 to return start point and 1 to return end point
        @return: a list of point and angle Returns the hdl or hdls of the ploted objects.
        """
        if not(direction):
            point=self.Pa
            angle=degrees(self.s_ang)+90*self.ext/abs(self.ext)
        elif direction:
            point=self.Pe
            angle=degrees(self.e_ang)-90*self.ext/abs(self.ext)
        return point,angle
    
   
    def rot_angle(self,angle,parent):
        """
        Rotates the given angle based on the rotations given in its parents.
        @param angle: The angle which shall be rotated
        @param parent: The parent Entitie (Instance: EntitieContentClass)
        @return: The rotated angle.
        """

        #Rekursive Schleife falls mehrfach verschachtelt.
        if type(parent)!=type(None):
            angle=angle+degrees(parent.rot)
            angle=self.rot_angle(angle,parent.parent)
                
        return angle
    
    def scaleR(self,sR,parent):
        """
        Scales the radius based on the scale given in its parents. This is done
        recursively.
        @param sR: The radius which shall be scaled
        @param parent: The parent Entitie (Instance: EntitieContentClass)
        @return: The scaled radius
        """
        
        #Rekursive Schleife falls mehrfach verschachtelt.
        if type(parent)!=type(None):
            sR=sR*parent.sca[0]
            sR=self.scaleR(sR,parent.parent)
                
        return sR

    def Write_GCode(self,postpro=None):
        """
        Writes the GCODE for a ARC.
        """
       
        #If the radius of the element is bigger then the max. radius export
        #the element as an line.
        if self.r>postpro.max_arc_radius:
            string=postpro.lin_pol_xy(self.Pa,self.Pe)
        else:
            if (self.ext>0):
                string=postpro.lin_pol_arc("ccw",self.Pa,self.Pe,
                                           self.s_ang,self.e_ang,
                                           self.r,self.O,self.O-self.Pa)
                
            elif (self.ext<0) and postpro.export_ccw_arcs_only:
                string=postpro.lin_pol_arc("ccw",self.Pe,self.Pa,
                                           self.e_ang,self.s_ang,
                                           self.r,self.O,self.O-self.Pe)
            else:
                string=postpro.lin_pol_arc("cw",self.Pa,self.Pe,
                                           self.s_ang,self.e_ang,
                                           self.r,self.O,self.O-self.Pa)
        return string  


    
class LineGeo:
    def __init__(self,Pa,Pe):
        self.type="LineGeo"
        self.Pa=Pa
        self.Pe=Pe
        self.BB=[]
        self.col='Black'
        self.length=self.Pa.distance(self.Pe)
        Va=PointClass(0.0,0.0)
         
        Ve=self.Pe-self.Pa            # Richtungsabh�ngiger Normalenvektor
        if (abs(Ve.x)>abs(Ve.y)):
            if(Ve.x>0):
                Va.y=-1
            else:
                Va.y=1
            if(Ve.y!=0):
                Va.x=-Ve.y*Va.y/Ve.x
            else:
                Va.x=0;
        else:
            if(Ve.y>0):
                Va.x=1
            else:
                Va.x=-1
            if(Ve.y!=0):
                Va.y=-Ve.x*Va.x/Ve.y
            else:
                Va.y=0
            
        betrag=Va.distance()
               
        self.nve=1/betrag*Va
        self.nva=self.nve
       
        
    def __str__(self):
        """ 
        Standard method to print the object
        @return: A string
        """ 
        return ("\nLineGeo")+\
               ("\nPa : %s" %self.Pa)+\
               ("\nPe : %s" %self.Pe)+\
               ("\nBB : %s" %self.BB)+\
               ("\nlength: %0.5f" %self.length)        

    def reverse(self):
        """ 
        Reverses the direction of the arc (switch direction).
        """ 
        Pa=self.Pa
        Pe=self.Pe
        
        self.Pa=Pe
        self.Pe=Pa
   
    def make_abs_geo(self,parent=None,reverse=0):
        """
        Generates the absolut geometry based on the geometry self and the
        parent. If reverse 1 is given the geometry may be reversed.
        @param parent: The parent of the geometry (EntitieContentClass)
        @param reverse: If 1 the geometry direction will be switched.
        @return: A new LineGeoClass will be returned.
        """ 
        Pa=self.Pa.rot_sca_abs(parent=parent)
        Pe=self.Pe.rot_sca_abs(parent=parent)
        abs_geo=LineGeo(Pa=Pa,Pe=Pe)
        if reverse:
            abs_geo.reverse()
        return abs_geo
    
    def calc_bounding_box(self):
        """
        Calculated the BoundingBox of the geometry and saves it into self.BB
        """
        Pa=PointClass(x=min(self.Pa.x,self.Pe.x),y=min(self.Pa.y,self.Pe.y))
        Pe=PointClass(x=max(self.Pa.x,self.Pe.x),y=max(self.Pa.y,self.Pe.y))
        
        self.BB=BoundingBoxClass(Pa=Pa,Pe=Pe)
        
    def plot2can(self,canvas=None,tag=None,col='black',plotoption=0):
        """
        Plots the geometry of self into the defined canvas.
        @param canvas: The canvas instance to plot in
        @param tag: the number of the parent shape
        @param col: The color in which the shape shall be ploted
        @param plotoption: Additional option for Debug print use
        @return: Returns the hdl or hdls of the ploted objects.
        """
        
        hdl=[]

        hdl.append(Line(canvas,self.Pa.x,-self.Pa.y,
                        self.Pe.x,-self.Pe.y,tag=tag,fill=col))
        
        if plotoption:
            hdl.append(Line(canvas,self.Pa.x-dl,-self.Pa.y-dl,
                            self.Pa.x+dl,-self.Pa.y+dl,tag=tag,fill=col))
            hdl.append(Line(canvas,self.Pa.x+dl,-self.Pa.y-dl,
                            self.Pa.x-dl,-self.Pa.y+dl,tag=tag,fill=col))
            hdl.append(Line(canvas,self.Pe.x-dl,-self.Pe.y-dl,
                            self.Pe.x+dl,-self.Pe.y+dl,tag=tag,fill=col))
            hdl.append(Line(canvas,self.Pe.x+dl,-self.Pe.y-dl,
                            self.Pe.x-dl,-self.Pe.y+dl,tag=tag,fill=col))
            
        self.BB.plot2can(canvas=canvas,tag=tag,col='red',hdl=hdl)
            
        return hdl

    def get_start_end_points(self,direction):
        """
        Returns the start/end point and its direction
        @param direction: 0 to return start point and 1 to return end point
        @return: a list of point and angle 
        """
        if not(direction):
            punkt=self.Pa
            angle=degrees(self.Pa.norm_angle(self.Pe))
        elif direction:
            punkt=self.Pe
            angle=degrees(self.Pe.norm_angle(self.Pa))
        return punkt, angle
    
    def CheckIntersectLineLine(selfL2):
       
    
        print('check line/line')
        dx1=self.Pe.x-self.Pa.x
        dy1=self.Pe.y-self.Pa.y
        
        dx2=L2.Pe.x-L2.Pa.x
        dy2=L2.Pe.y-L2.Pa.y

        dax=L1.Pa.x-L2.Pa.x
        day=L1.Pa.y-L2.Pa.y

        if dx1==0 and dy1==0:
            return
        if dx2==0 and dy2==0:
            return
        
        print dx1
        print dy1
        print dx2
        print dy2
        
        
        if(abs(dx2)>=abs(dy2)):
            n=(day-dax*dy2/dx2)/(dx1*dy2/dx2 -dy1)
            u=(dax+n*dx1)/dx2
            self.P1=PointClass(x=L1.Pa.x+n*dx1,
                               y=L1.Pa.y+n*dy1)
            self.v1=n
            self.v2=u
            
        else:
            print dy1*dx2/dy2 -dx1
           
            n=(dax-day*dx2/dy2)/(dy1*dx2/dy2 -dx1)
            u=(day+n*dy1)/dy2
            self.P1=PointClass(x=L1.Pa.x+n*dx1,
                               y=L1.Pa.y+n*dy1)
            self.v1=n
            self.v2=u
            
        self.num=1
        
        if 0.00001<self.v1 and self.v1<0.9999:
            self.ISPstatus1a='between'             
        elif 0.9999<self.v1 and self.v1<1.00001:
            self.ISPstatus1a='at_end'
        elif -0.00001<self.v1 and self.v1<0.00001:
            self.ISPstatus1a='at_start'    
        elif self.v1>1.00001:
            self.ISPstatus1a='above'
        else:
            self.ISPstatus1a='under'
            
        if 0.00001<self.v2 and self.v2<0.9999:
            self.ISPstatus1b='between'             
        elif 0.9999<self.v2 and self.v2<1.00001:
            self.ISPstatus1b='at_end'
        elif -0.00001<self.v2 and self.v2<0.00001:
            self.ISPstatus1b='at_start'    
        elif self.v2>1.00001:
            self.ISPstatus1b='above'
        else:
            self.ISPstatus1b='under'    
            
            
        
        print ('num,x1,y1,x2,y2',self.num,self.P1.x,self.P1.y,self.P2.x,self.P2.y)
        print ('st1a,st2a,st1b,st2b,v1,v2',self.ISPstatus1a,self.ISPstatus2a,self.ISPstatus1b,self.ISPstatus2b, self.v1,self.v2, )

        return 
    
    
    def Write_GCode(self,postpro=None):
        return postpro.lin_pol_xy(self.Pa,self.Pe)

    def distance2point(self,point):
        try:
            AE=self.Pa.distance(self.Pe)
            AP=self.Pa.distance(point)
            EP=self.Pe.distance(point)
            AEPA=(AE+AP+EP)/2
            return abs(2*sqrt(abs(AEPA*(AEPA-AE)*(AEPA-AP)*(AEPA-EP)))/AE)
        except:
            return 1e10
            
class BoundingBoxClass:
    """ 
    Bounding Box Class. This is the standard class which provides all std. 
    Bounding Box methods.
    """ 
    def __init__(self,Pa=PointClass(0,0),Pe=PointClass(0,0),hdl=[]):
        """ 
        Standard method to initialize the class
        """ 
        self.Pa=Pa
        self.Pe=Pe
        
    def __str__(self):
        """ 
        Standard method to print the object
        @return: A string
        """ 
        s= ("\nPa : %s" %(self.Pa))+\
           ("\nPe : %s" %(self.Pe))
        return s
    
    def joinBB(self,other):
        """
        Joins two Bounding Box Classes and returns the new one
        @param other: The 2nd Bounding Box
        @return: Returns the joined Bounding Box Class
        """
        
        if type(self.Pa)==type(None) or type(self.Pe)==type(None):
            return BoundingBoxClass(copy(other.Pa),copy(other.Pe))
        
        xmin=min(self.Pa.x,other.Pa.x)
        xmax=max(self.Pe.x,other.Pe.x)
        ymin=min(self.Pa.y,other.Pa.y)
        ymax=max(self.Pe.y,other.Pe.y)
        
        return BoundingBoxClass(Pa=PointClass(xmin,ymin),Pe=PointClass(xmax,ymax))
    
    def hasintersection(self,other=None,tol=0.0):
        """
        Checks if the two bounding boxes have an intersection
        @param other: The 2nd Bounding Box
        @return: Returns true or false
        """        
        x_inter_pos=(self.Pe.x-tol > other.Pa.x) and (self.Pa.x + tol<other.Pe.x)
        y_inter_pos=(self.Pe.y-tol > other.Pa.y) and (self.Pa.y + tol<other.Pe.y)
     
        return x_inter_pos and y_inter_pos
     
    def plot2can(self,canvas=None,tag=None,col='red',hdl=[]):
        """
        Plots the geometry of self into the defined canvas.
        @param canvas: The canvas instance to plot in
        @param tag: the number of the parent shape
        @param col: The color in which the shape shall be ploted
        @param hdl: The existing hdls where to append the additional ones
        @return: Returns the hdl or hdls of the ploted objects.
        """
        hdl.append(Line(canvas,
                        self.Pa.x,-self.Pa.y,self.Pe.x,-self.Pa.y,tag=tag,fill=col))
        hdl.append(Line(canvas,
                        self.Pe.x,-self.Pa.y,self.Pe.x,-self.Pe.y,tag=tag,fill=col))
        hdl.append(Line(canvas,
                        self.Pe.x,-self.Pe.y,self.Pa.x,-self.Pe.y,tag=tag,fill=col))
        hdl.append(Line(canvas,
                        self.Pa.x,-self.Pe.y,self.Pa.x,-self.Pa.y,tag=tag,fill=col))
        return hdl
       



class BiarcClass:
    def __init__(self,Pa=[],tan_a=[],Pb=[],tan_b=[],min_r=5e-4):
        min_len=1e-9        #Min Abstand f�r doppelten Punkt
        min_alpha=1e-4      #Winkel ab welchem Gerade angenommen wird inr rad
        max_r=5e3           #Max Radius ab welchem Gerade angenommen wird (5m)
        min_r=min_r         #Min Radius ab welchem nichts gemacht wird
        
        self.Pa=Pa
        self.tan_a=tan_a
        self.Pb=Pb
        self.tan_b=tan_b
        self.l=0.0
        self.shape=None
        self.geos=[]
        self.k=0.0

        #Errechnen der Winkel, L�nge und Shape
        norm_angle,self.l=self.calc_normal(self.Pa,self.Pb)

        alpha,beta,self.teta,self.shape=self.calc_diff_angles(norm_angle,\
                                                              self.tan_a,\
                                                              self.tan_b,\
                                                              min_alpha)
        
        if(self.l<min_len):
            self.shape="Zero"
            pass
        
            
        elif(self.shape=="LineGeo"):
            #Erstellen der Geometrie
            self.shape="LineGeo"
            self.geos.append(LineGeo(self.Pa,self.Pb))
        else:
            #Berechnen der Radien, Mittelpunkte, Zwichenpunkt            
            r1, r2=self.calc_r1_r2(self.l,alpha,beta,self.teta)
            
            if (abs(r1)>max_r)or(abs(r2)>max_r):
                #Erstellen der Geometrie
                self.shape="LineGeo"
                self.geos.append(LineGeo(self.Pa,self.Pb))
                return
            
            elif (abs(r1)<min_r)or(abs(r2)<min_r):
                self.shape="Zero"
                return
          
            O1, O2, k =self.calc_O1_O2_k(r1,r2,self.tan_a,self.teta)
            
            #Berechnen der Start und End- Angles f�r das drucken
            s_ang1,e_ang1=self.calc_s_e_ang(self.Pa,O1,k)
            s_ang2,e_ang2=self.calc_s_e_ang(k,O2,self.Pb)

            #Berechnen der Richtung und der Extend
            dir_ang1=(tan_a-s_ang1)%(-2*pi)
            dir_ang1-=ceil(dir_ang1/(pi))*(2*pi)

            dir_ang2=(tan_b-e_ang2)%(-2*pi)
            dir_ang2-=ceil(dir_ang2/(pi))*(2*pi)
            
            
            #Erstellen der Geometrien          
            self.geos.append(ArcGeo(Pa=self.Pa,Pe=k,O=O1,r=r1,\
                                    s_ang=s_ang1,e_ang=e_ang1,dir=dir_ang1))
            self.geos.append(ArcGeo(Pa=k,Pe=self.Pb,O=O2,r=r2,\
                                    s_ang=s_ang2,e_ang=e_ang2,dir=dir_ang2)) 

    def calc_O1_O2_k(self,r1,r2,tan_a,teta):
        #print("r1: %0.3f, r2: %0.3f, tan_a: %0.3f, teta: %0.3f" %(r1,r2,tan_a,teta))
        #print("N1: x: %0.3f, y: %0.3f" %(-sin(tan_a), cos(tan_a)))
        #print("V: x: %0.3f, y: %0.3f" %(-sin(teta+tan_a),cos(teta+tan_a)))

        O1=PointClass(x=self.Pa.x-r1*sin(tan_a),\
                      y=self.Pa.y+r1*cos(tan_a))
        k=PointClass(x=self.Pa.x+r1*(-sin(tan_a)+sin(teta+tan_a)),\
                     y=self.Pa.y+r1*(cos(tan_a)-cos(tan_a+teta)))
        O2=PointClass(x=k.x+r2*(-sin(teta+tan_a)),\
                      y=k.y+r2*(cos(teta+tan_a)))
        return O1, O2, k

    def calc_normal(self,Pa,Pb):
        norm_angle=Pa.norm_angle(Pb)
        l=Pa.distance(Pb)
        return norm_angle, l        

    def calc_diff_angles(self,norm_angle,tan_a,tan_b,min_alpha):
        #print("Norm angle: %0.3f, tan_a: %0.3f, tan_b %0.3f" %(norm_angle,tan_a,tan_b))
        alpha=(norm_angle-tan_a)   
        beta=(tan_b-norm_angle)
        alpha,beta= self.limit_angles(alpha,beta)

        if alpha*beta>0.0:
            shape="C-shaped"
            teta=alpha
        elif abs(alpha-beta)<min_alpha:
            shape="LineGeo"
            teta=alpha
        else:
            shape="S-shaped"
            teta=(3*alpha-beta)/2
            
        return alpha, beta, teta, shape    

    def limit_angles(self,alpha,beta):
        #print("limit_angles: alpha: %s, beta: %s" %(alpha,beta))
        if (alpha<-pi):
            alpha += 2*pi
        if (alpha>pi):
            alpha -= 2*pi
        if (beta<-pi):
            beta += 2*pi
        if (beta>pi):
            beta -= 2*pi
        while (alpha-beta)>pi:
            alpha=alpha-2*pi
        while (alpha-beta)<-pi:
            alpha=alpha+2*pi
        #print("   -->>       alpha: %s, beta: %s" %(alpha,beta))         
        return alpha,beta
            
    def calc_r1_r2(self,l,alpha,beta,teta):
        #print("alpha: %s, beta: %s, teta: %s" %(alpha,beta,teta))
        r1=(l/(2*sin((alpha+beta)/2))*sin((beta-alpha+teta)/2)/sin(teta/2))
        r2=(l/(2*sin((alpha+beta)/2))*sin((2*alpha-teta)/2)/sin((alpha+beta-teta)/2))
        return r1, r2
    
    def calc_s_e_ang(self,P1,O,P2):
        s_ang=O.norm_angle(P1)
        e_ang=O.norm_angle(P2)
        return s_ang, e_ang
    
    def get_biarc_fitting_error(self,Pt):
        #Abfrage in welchem Kreissegment der Punkt liegt:
        w1=self.geos[0].O.norm_angle(Pt)
        if (w1>=min([self.geos[0].s_ang,self.geos[0].e_ang]))and\
           (w1<=max([self.geos[0].s_ang,self.geos[0].e_ang])):
            diff=self.geos[0].O.distance(Pt)-abs(self.geos[0].r)
        else:
            diff=self.geos[1].O.distance(Pt)-abs(self.geos[1].r)
        return abs(diff)
            
    def __str__(self):
        s= ("\nBiarc Shape: %s" %(self.shape))+\
           ("\nPa : %s; Tangent: %0.3f" %(self.Pa,self.tan_a))+\
           ("\nPb : %s; Tangent: %0.3f" %(self.Pb,self.tan_b))+\
           ("\nteta: %0.3f, l: %0.3f" %(self.teta,self.l))
        for geo in self.geos:
            s+=str(geo)
        return s