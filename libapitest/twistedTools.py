"""
This file contains various tools and utilities for the Twisted framework 
library (http://www.twistedmatrix.com)
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


import os
import os.path
import libdebug
import systools
import string
from twisted.internet import protocol,reactor,defer
from exceptions import Exception
from elementtree import ElementTree


#--------------------------------------------------------------------
# ProcessProtocol with SpawnProcess test
#--------------------------------------------------------------------
class processHandlerBase(protocol.ProcessProtocol, libdebug.debuggable):
    """
    Base class for ProcessProtocol apps.  Extends the ProcessProtocol
    module from the Twisted Framework.

    For additional information on ProcessProtocol, refer to section 3.6
    of the Twisted Python user manual.
    """

    # --------------------------
    # Data Definitions
    # --------------------------
    stdin_args = []
    stdout  = ""
    stderr  = ""
    status  = -1
    cmd     = ""
    args    = []
    env     = {}
    wdir    = "./"
    uid     = os.getuid()
    gid     = os.getgid()
    pid     = -1
    tpid    = -1
    hasCallback = False
    theCallback = None
    type = 'cmd'

    # --------------------------
    # Constructor
    # --------------------------
    def __init__(self, stdin_args=[]):
        """
        Constructor
        """
        self.Initialize(stdin_args)


    def Initialize(self, stdin_args=[]):
        """ Initializer """
        self.stdin_args = stdin_args
        ##self.debug_on()

##
##
##    def childDataReceived(self,childFD,data):
##        self.printDebug("[->] childDataReceived")
##        self.printDebug("\tchildFD :: %s"%(`childFD`))
##        self.printDebug("\tdata    :: %s"%(`data`))
##        self.printDebug("[<-] childDataReceived")
##
##
##    def childConnectionLost(self,childFD):
##        self.printDebug("[->] childConnectionLost")
##        self.printDebug("[<-] childConnectionLost")
##
##

    def setType(self,type='cmd'):
        """ Set execution profile """
        self.type = type


    def createAndSetCallback(self, callback_target):
        """ create a deferred and a callback and set it """
        D = defer.Deferred()
        D.addCallback(callback_target)
        self.setCallback(D)
        return D


    def setCallback(self, deferred_obj):
        """ Set the callback function """
        self.hasCallback = True
        self.theCallback = deferred_obj


    def unsetCallback(self):
        """ clear the callback function """
        self.hasCallback = False
        self.theCallback = None


    def connectionMade(self):
        """ sends STDIN to process """
        self.printDebug("[->]\tconnectionMade()")
        ## send stdin buffers into app from here.
        if self.transport.pid != None:
            self.tpid = self.transport.pid
        self.printDebug("[<-]\tconnectionMade()")


    def inConnectionLost(self):
        """ Executes when the connection to STDIN is closed """
        self.printDebug("[->]\tinConnectionLost()")
        self.printDebug("[<-]\tinConnectionLost()")


    def outReceived(self, newStdout):
        """ Executes when we receive some STDOUT """
        self.printDebug("[->]\toutReceived()")
        self.printDebug("\tdata_received=[%s]"%(`newStdout`))
        self.stdout = self.stdout + newStdout
        self.printDebug("[<-]\toutReceived()")


    def outConnectionLost(self):
        """ Executes when the STDOUT connection is closed """
        self.printDebug("[->]\toutConnectionLost")
        self.printDebug("[<-]\toutConnectionLost")


    def errReceived(self, newStderr):
        """ Executes when we receive some STDERR """
        self.printDebug("[->]\terrReceived")
        self.stderr = self.stderr + newStderr
        self.printDebug("[<-]\terrReceived")
        

    def errConnectionLost(self):
        """ Executes when the STDERR connection is closed """
        self.printDebug("[->]\terrConnectionLost")
        self.printDebug("[<-]\terrConnectionLost")


    def processEnded(self, status_object):
        """ Executes when the process has ended """
        self.printDebug("[->]\tprocessHandlerBase.processEnded()")
        self.status = status_object.value.exitCode
        if hasattr(self,'postProcess'):
            if callable(self.postProcess):
                self.postProcess()
        self.printDebug("[<-]\tprocessHandlerBase.processEnded()")

    def wdirDoesNotExist(self):
        """ Called if we don't have a working directory """
        self.printDebug("[->]\tprocessHandlerBase.wdirDoesNotExist()")
        self.status = -99
        if hasattr(self, 'dirNotFound'):
            if callable(self.dirNotFound):
                self.dirNotFound()
        if hasattr(self,'postProcess'):
            if callable(self.postProcess):
                self.postProcess()
        self.printDebug("[<-]\tprocessHandlerBase.wdirDoesNotExist()")

    def getpid(self):
        """ Return the process ID of the process we're running. """
        self.printDebug("[**]\tgetpid()")
        if self.pid == None:
            return -1
        return self.pid

    def getStatus(self):
        """ Return the exit status of the process """
        self.printDebug("[**]\tgetStatus()")
        return self.status

    def getStderr(self):
        """ Return the stderr we've collected so far. """
        self.printDebug("[**]\tgetStderr()")
        return self.stderr

    def getStdout(self):
        """ Return the stdout we've collected so far. """
        self.printDebug("[**]\tgetStdout()")
        return self.stdout

    def execute(self, cmd, args=[], wdir=os.getcwd(), \
                env=os.environ, uid=os.getuid(),      \
                gid=os.getgid() ):
        """
        Launch the application.
        """
        self.printDebug("[->]\tprocessHandlerBase.execute()")
        self.cmd = cmd
        self.args= [cmd]+args
        self.env = env
        self.wdir= wdir
        self.uid = uid
        self.gid = gid
        self.uname = systools.getUNAMEfromUID(self.uid)

        if self.wdir == "":
            self.wdir = os.getcwd()

        if self.type=="cmd":
            if not os.path.exists( os.path.normpath( self.wdir+"/"+self.cmd )):
                self.wdir = ""

        ##self.debug_on()
        self.printDebug( "\tcmd  =%s"%(`self.cmd`)  )
        self.printDebug( "\targs =%s"%(`self.args`) )
        ##self.printDebug( "\tenv  =%s"%(`self.env`)  )
        self.printDebug( "\twdir =%s"%(`self.wdir`) )
        self.printDebug( "\tuid  =%s (%s)"%(`self.uid`,uid) )
        self.printDebug( "\tgid  =%s"%(`self.gid`)  )
        self.printDebug( "\tuname=%s"%(`self.uname`))
        ##self.debug_off()

        if os.path.exists(self.wdir) or self.wdir=="":

            if(self.wdir != ""):
                self.wdir = os.path.normpath(self.wdir)+"/"

            if ( (os.getgid()==0) and (os.getuid() != int(self.uid)) ):
                # can only change UID and GID if we're running with group id root.
                if self.uname != None:
                    self.cmd = "su"
                    targ = None
                    if len(self.args) > 1:
                        targ = [ self.args[0], self.wdir+self.args[1]] + self.args[2:]
                    elif len(self.args)==1:
                        targ = [ self.wdir+self.args[0] ]
                    else:
                        targ = []
                    tstr = string.join(targ)
                    self.args = ["su","-l",self.uname,"-c",tstr]
                    reactor.spawnProcess(self,self.cmd,self.args,self.env,self.wdir)
                else:
                    if hasattr(self,'userNotFound') and callable(self.userNotFound):
                        self.userNotFound()
            else:
                self.env.update( os.environ.copy() )
                reactor.spawnProcess(self,self.cmd,self.args,self.env,self.wdir)
                self.pid = self.transport.pid
                self.printDebug( "\tpid=%s"%(`self.getpid()`) )
        else:
            self.wdirDoesNotExist()
            
        self.printDebug("[<-]\tprocessHandlerBase.execute()")


# --------------------------------------------------------------------------
#  Internal Test Routine
# --------------------------------------------------------------------------
if "__main__" == __name__:
    """ For testing purposes only """
    if 1:
        tPHB = processHandlerBase()
        tPHB.Initialize()
        print "tPHB=", `tPHB`
        tPHB.debug_on()
        reactor.callLater(1,tPHB.execute,"ls",["-l","-t","-r"], "./" )
        reactor.callLater(2, reactor.stop )
        reactor.run()

        print "STDOUT=", `tPHB.getStdout()`
        print "STDERR=", `tPHB.getStderr()`
        print "STATUS=", `tPHB.getStatus()`
        print "PID   =", `tPHB.getpid()`

#EOF
