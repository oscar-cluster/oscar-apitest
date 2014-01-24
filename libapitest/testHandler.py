"""
Test Handler class
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

#
# $Id: testHandler.py,v 1.24 2005/04/12 23:51:08 wcmclen Exp $
#

import systools
import libdebug
import libapitest
import twistedTools
import os
import os.path
import string
from exceptions import OSError
from signal import SIGTERM
from twisted.internet import reactor,defer


#===========================================================================
# cmdHandler
#===========================================================================
class cmdHandler(twistedTools.processHandlerBase):
    """
    Extends processHandlerBase.

    Handles the actual launching of a test and executing the callback
    with the appropriate data in place for a validator.

    NOTE: User must assign a callback via setCallback() prior to calling
    execute()
    """
    def postProcess(self):
        self.printDebug("[->]\tcmdHandler.postProcess")
        if self.hasCallback:
            result = {}
            result['stdout'] = self.stdout
            result['stderr'] = self.stderr
            result['status'] = self.status
            ##if self.ERROR != None:
            ##    result['ERROR'] = self.ERROR
            reactor.callLater(0, self.theCallback.callback, result)
        else: 
            pass


#===========================================================================
# testHandler
#===========================================================================
class testHandler(libapitest.testHandlerBase):
    """
    Implementations of specific test handlers.  The infrastructure is contained
    within testHandlerBase.

    For a test type, we only need functions named as:

      do_<type>(self)
      cleanup_<type>(self)
      kill_<type>(self)

    The do_<type> function should be non-blocking and use callbacks if the task
    might execute for a while.  Once the task has returned with a result,
    it should invoke a callback with the deferred object returned using
    createCallback() and a dictionary of results where the keys match the
    XML attribute 'name' in the <output> elements from the test scripts.

    ie:
        result = {}
        result['key'] = 'some text string to test'
        reactor.callLater(0, createCallback(), result)
    
    """
    #-------------------------
    def __init__(self, db=None):
        libapitest.testHandlerBase.__init__(self, db)
    
    #-------------------------
    def Initialize(self, db=None):
        """ 
        Initializer.  Called at the end of __init__.
        This function should be overridden, not __init__.
        """
        self.printDebug("[->]\ttestHandler.Initialize()")
        self.db = db
        self.printDebug("[<-]\ttestHandler.Initialize()")
        return True


    #--------------------------------------------------------------------------
    # U T I L I T Y    M E T H O D S
    #--------------------------------------------------------------------------

    # ----------------------------------
    def utilSetUIDandGID(self,xmlCmdObj):
        """
        Sets UID/GID for scripts and commands, given the XML Command object.
        Returns the tuple: (UNAME,UID,GNAME,GID)
        """
        # Get the specified uid/gid/uname/gname from the XML
        theUID      = xmlCmdObj.attrib.get("uid",os.getuid() )
        theGID      = xmlCmdObj.attrib.get("gid",None)
        theUNAME    = xmlCmdObj.attrib.get("uname",None)
        theGNAME    = xmlCmdObj.attrib.get("gname",None)
        
        # Get the actual uid and gid from the system.
        actualUID   = os.getuid()
        actualGID   = os.getgid()
        
        # process uname if we got one and it's different from 
        # the actual uname.
        actualUNAME = systools.getUNAMEfromUID(actualUID);
       
        if theUNAME == None and theUID != None:
            theUNAME = systools.getUNAMEfromUID(theUID)

        if(actualUNAME == theUNAME):
            theGID   = None
            theGNAME = None
            theUNAME = None
        else:
            theGID   = None
            theGNAME = None
            theUID   = systools.getUIDfromUNAME(theUNAME)
            
        return (theUNAME,theUID,theGNAME,theGID)



#============================================================================
#-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-
#
#       ###### ##   ## #####       ##  ## ##  ## #####  ##     ######
#       ##     ### ### ##  ##      ##  ## ### ## ##  ## ##     ##  ##
#       ##     ## # ## ##  ##  ##  ###### ## ### ##  ## ##     ######
#       ##     ##   ## ##  ##      ##  ## ##  ## ##  ## ##     ## ##
#       ###### ##   ## #####       ##  ## ##  ## #####  ###### ##  ##
#
#-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-
#============================================================================
#
#--------------------------------------------------------------------------
# cmd test handler methods
#--------------------------------------------------------------------------
    def do_cmd(self):
        """
        Specific Handler instance for command line tests.
        """
        self.printDebug('[->]\ttestHandler.do_cmd()')
        theShell   = ""
        theCommand = ""
        arguments  = []
        stdin      = []

        ##xmlTestRoot = self.xmlFileRoot.find('test')
        xmlCommand  = self.xmlTestRoot.find('command')
        theCommand  = xmlCommand.text
        theShell    = xmlCommand.attrib.get('shell','csh')
        self.WDIR   = xmlCommand.attrib.get('wdir',self.TSDIR)

        # verify that the wdir/cmd *actually* exist.
        if not os.path.exists( os.path.normpath( self.WDIR+"/"+theCommand )):
            self.WDIR = ""
            
        (theUNAME,theUID,theGNAME,theGID) = self.utilSetUIDandGID(xmlCommand)
        
        self.xmlResultTree.attrib['uname'] = str(theUNAME)
        self.xmlResultTree.attrib['uid'] = str(theUID)
        
        newEnviron = {}
        xmlInputList = self.xmlTestRoot.findall('input')
        
        for inputElt in xmlInputList:
            
            if inputElt.attrib.get('name',None) == "argument" and \
                   inputElt.attrib.get('format','literal') == "literal":
                arguments.append(inputElt.text)
            elif inputElt.attrib.get('name',None) == "stdin" and \
                     inputElt.attrib.get('format','literal')=='literal' and \
                     inputElt.text != None:
                stdin.append(inputElt.text)
            elif inputElt.attrib.get('name',None) == "envvar":
                key   = inputElt.attrib.get('key',None)
                value = inputElt.text
                newEnviron[key]=value
                
        ##self.debug_on()
        ##self.printDebug("\ttestFileName =\t%s"%(`self.testFileName`))
        ##self.printDebug("\tWDIR       =\t%s"%(`self.WDIR`))
        ##self.printDebug("\tTSDIR      =\t%s"%(`self.TSDIR`))
        ##self.printDebug("\ttheCommand =\t%s"%(`theCommand`))
        ##self.printDebug("\ttheShell   =\t%s"%(`theShell`))
        ##self.printDebug("\targuments  =\t%s"%(`arguments`))
        ##self.printDebug("\tstdin      =\t%s"%(`stdin`))
        ##self.printDebug("\tnew envvar =\t%s"%(`newEnviron`)) 
        ##self.printDebug("\ttheUID     =\t%s"%(`theUID`))
        ##self.printDebug("\ttheGID     =\t%s"%(`theGID`))
        ##self.debug_off()

        (F_exists,F_exec,F_path) = systools.searchPathForExecutable(theCommand)

        ret = {}
        if theUID != None and F_exists and F_exec:
            self.tCMD = cmdHandler()
            self.tCMD.setType('cmd')
            if self.get_debug(): self.tCMD.debug_on()
            self.tCMD.setCallback( self.createCallback() )
            self.tCMD.execute(theCommand,arguments,self.WDIR,newEnviron,theUID,theGID)
            self.pid = self.tCMD.getpid()
            self.setRunningFlag( (self.pid,self.testFileName) )
        else:
            ret['ERROR'] = ""
            if theUID==None:
                ret['ERROR'] += "Could not find user \"%s\".\n"%(theUNAME)
            if not F_exists:
                ret['ERROR'] += "Could not locate the file \"%s\".\n"%(theCommand)
            if not F_exec:
                ret['ERROR'] += "The file \"%s\" is not executable!\n"%(theCommand)
            reactor.callLater(0,self.procReturned,ret)
            
        self.printDebug('[<-]\ttestHandler.do_cmd()')


    # -------------------
    def cleanup_cmd(self):
        """
        Specific handler instance for cleaning up a command
        """
        pass


    # --------------------
    def kill_cmd(self):
        """
        """
        if self.isRunning:
            pid = self.tCMD.getpid() 
            try:
                os.kill(pid, SIGTERM)
                self.set_timeoutFlag()
            except OSError, msg:
                print "Could not kill process (%d) with signal (%d)"%(pid,SIGTERM)
                print "\tmsg:\"%s\""%(msg)


    #--------------------------------------------------------------------------
    # script test handler methods
    #--------------------------------------------------------------------------
    def do_script(self):
        """
        Specific handler instance for running a script.
        """
        self.printDebug('[->]\ttestHandler.do_script()')
        self.theScriptFileName = None
        theShell   = ""
        scriptOK   = False
        arguments  = []
        stdin      = []
        
        ##xmlTestRoot   = self.xmlFileRoot.find('test')
        xmlCommand    = self.xmlTestRoot.find('command')
        self.WDIR     = xmlCommand.attrib.get("wdir",self.TSDIR)
        theShell      = xmlCommand.attrib.get("interpreter","csh")
        theScriptBody = xmlCommand.text

#	print xmlCommand.__dict__
#	print theScriptBody
#	print libapitest.xmlObjToString(xmlCommand)

        (theUNAME,theUID,theGNAME,theGID) = self.utilSetUIDandGID(xmlCommand)

        # save uid / gid information to the output entry.
        self.xmlResultTree.attrib['uname'] = str(theUNAME)
        self.xmlResultTree.attrib['uid'] = str(theUID)

        # set up script name
        theScriptName = "apitest_"
        theScriptName += os.path.splitext(os.path.basename(self.testFileName))[0]+".sh"

        # set the stdin and arguments data
        newEnviron = {}
        xmlInputList = self.xmlTestRoot.findall('input')
        arguments.append(theScriptName)
        for inputElt in xmlInputList:
            if inputElt.attrib.get('name',None) == "argument" and \
                   inputElt.attrib.get('format','literal') == "literal":
                arguments.append(inputElt.text)
            elif inputElt.attrib.get('name',None) == "stdin" and \
                     inputElt.attrib.get('format','literal')=='literal' and \
                     inputElt.text != None:
                stdin.append(inputElt.text)
            elif inputElt.attrib.get('name',None) == "envvar":
                key   = inputElt.attrib.get('key',None)
                value = inputElt.text
                newEnviron[key]=value

        if self.WDIR == "":
            self.WDIR = "./"

        # write the script
        if os.path.exists(self.WDIR):
            wdirOK = True
            out_file = open(self.WDIR+'/'+theScriptName,"w")
            out_file.write(theScriptBody)
            out_file.close()
            self.theScriptFileName = self.WDIR+'/'+theScriptName
            scriptOK = True

        # generate the command to run
        theCommand = theShell

        # lots of debugging
        self.printDebug("\tself.WDIR     =\t%s"%(`self.WDIR`))
        self.printDebug("\tself.TSDIR    =\t%s"%(`self.TSDIR`))
        self.printDebug("\ttheScriptName =\t%s"%(`theScriptName`))
        self.printDebug("\ttheScriptBody =\t%s"%(`theScriptBody`))
        self.printDebug("\ttheShell      =\t%s"%(`theShell`))
        self.printDebug("\targuments     =\t%s"%(`arguments`))
        self.printDebug("\tstdin         =\t%s"%(`stdin`))
        self.printDebug("\ttheCommand    =\t%s"%(`theCommand`))

        if scriptOK:
            if theUID != None:
                tCMD = cmdHandler()
                tCMD.setType('script')
                if self.get_debug(): tCMD.debug_on()
                tCMD.setCallback( self.createCallback() )
                tCMD.execute(theCommand,arguments,self.WDIR,newEnviron,theUID)
                self.pid = tCMD.getpid()
                self.setRunningFlag( (self.pid,self.testFileName) )
            else:
                ret = {}
                ret['ERROR'] = "Could not find user \"%s\""%(theUNAME)
                reactor.callLater(0,self.procReturned,ret)
        
        self.printDebug('[<-]\ttestHandler.do_script()')

    # --------------------
    def cleanup_script(self):
        """
        cleanup handler for scripts.
        """
        self.printDebug('[->]\ttestHandler.cleanup_script()')
        if (not self.get_debug()) and \
               self.theScriptFileName and \
               os.path.exists(self.theScriptFileName) and \
               os.path.isfile(self.theScriptFileName):
            os.remove(self.theScriptFileName)
            pass
        self.printDebug('[<-]\ttestHandler.cleanup_script()')

    # --------------------
    def kill_script(self):
        """
        Kills a script test and sets the timeout flag.
        """
        if self.isRunning:
            try:
                os.kill(self.pid, SIGTERM)
                self.set_timeoutFlag()
            except OSError, msg:
                print "Could not kill process (%d) with signal (%d)"%(self.pid,SIGTERM)
                print "\tmsg:\"%s\""%(msg)



    #--------------------------------------------------------------------------
    # sss test handler methods
    #--------------------------------------------------------------------------
    def do_sss(self):
        """
        SSS test.
        """
        ret = {}
        sendbuf = ""
        destination = ""

        try:
            from sss.ssslib import comm_lib, ConnectError
        except:
            print "IMPORT ERROR: Could not import sss.ssslib modules!"
            reactor.callLater(0, self.procReturned, ret)
            return()

        comm=comm_lib()
        destination = self.xmlTestRoot.attrib.get("destination",None)
        if None == destination or destination=="":
            ret['ERROR'] = "attribute'destination' = %s in <test>"%(destination)
            reactor.callLater(0,self.procReturned, ret)
            return()
        
        try:
            handle=comm.ClientInit(destination)
        except ConnectError, msg:
            ret['ERROR'] = "Error connecting to '%s': %s"%(destination,msg)
            reactor.callLater(0, self.procReturned, ret)
            return()
        
        xmlInputList = self.xmlTestRoot.findall('input')
        for inputElt in xmlInputList:
            if inputElt.attrib.get('name',None) == "sendbuf" and \
               inputElt.attrib.get('format','literal') == "literal":
                sendbuf += inputElt.text

        comm.SendMessage(handle,sendbuf)

        # If no <output> elements exist, don't try to receive anything.
        if( len( self.xmlTestRoot.findall('output') ) ):
            response = comm.RecvMessage(handle)
            ret['recvbuf'] = response

        comm.ClientClose(handle)
        reactor.callLater(0, self.procReturned, ret)
        return()
 

    # --------------------  
    def kill_sss(self):
        """
        Kill handler for SSS tests.
        """
        pass     

    
    # --------------------
    def cleanup_sss(self):
        """
        Cleanup handler for SSS tests.
        """
        pass

    #--------------------------------------------------------------------------
    # http test handler methods
    #--------------------------------------------------------------------------
    def do_http(self):
        """
        http test.
        """
        ret = {}
        reactor.callLater(0, self.procReturned, ret)

    
    # --------------------
    def cleanup_http(self):
        """
        Cleanup handler for http tests.
        """
        pass


    # --------------------
    def kill_http(self):
        """
        Kill handler for an http type test.
        """
        pass


    #--------------------------------------------------------------------------
    # http test handler methods
    #--------------------------------------------------------------------------
    def do_tcpip(self):
        """
        tcpip test.
        """
        ret = {}
        reactor.callLater(0, self.procReturned, ret)

    
    # --------------------
    def cleanup_tcpip(self):
        """
        Cleanup handler for tcpip tests.
        """
        pass



#===========================================================================
# For Testing / Debugging (this main will not show up in normal execution)
# to access, execute $>python thisfile.py
#===========================================================================
def __cb__(result=None):
    print "[->]\t__cb__()"
    print "\t%s"%(`result`)
    print "[<-]\t__cb__()"


if __name__ == "__main__":
    print "testing testHandler.py... "
    
    print "\tuname = ", getUnameFromUID( 27030 )
     
    ##reactor.callLater(10, reactor.stop)
    ##reactor.run()

# EOF
