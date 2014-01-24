"""
Useful debugging tools.
"""
#############################################################################
#
#     This Cplant(TM) source code is the property of Sandia National
#     Laboratories.
#
#     This Cplant(TM) source code is copyrighted by Sandia National
#     Laboratories.
#
#     The redistribution of this Cplant(TM) source code is subject to the
#     terms of the GNU Lesser General Public License
#     (see cit/LGPL or http://www.gnu.org/licenses/lgpl.html)
#
#     Cplant(TM) Copyright 1998, 1999, 2000, 2001, 2002 Sandia Corporation.
#     Under the terms of Contract DE-AC04-94AL85000, there is a non-exclusive
#     license for use of this work by or on behalf of the US Government.
#     Export of this program may require a license from the United States
#     Government.
#
#############################################################################

#===========================================================================
# class debuggable
#===========================================================================
class debuggable:
    """ 
    A class that defines a debug flag and come associated methods
    for turning debugging on/off and printing a message if debugging
    is toggled on.  Mainly this class is inherited by other classes
    to give them convenient debugging capabilities.
    """
    debug = False
    def __init__(self):  self.debug = False
    def debug_on(self):  self.debug = True
    def debug_off(self): self.debug = False
    def get_debug(self): return self.debug
    def printDebug(self, msg):
        if self.debug:
            print msg
