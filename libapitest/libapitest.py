"""
File: libapitest.py 

This file is a library of common classes and functions that are used by
various APItest modules.
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
# $Id: libapitest.py,v 1.33 2005/10/04 16:29:32 wcmclen Exp $
#

#=============================================================================
# INCLUDED MODULES
#=============================================================================
import re
import md5
import string
import time
from exceptions import Exception
from xml.etree import ElementTree
import twistedTools
import libdebug
import Queue
from twisted.internet import reactor,defer
import os
import os.path
from xml.parsers.expat import ExpatError

#=============================================================================
# Exceptions
#=============================================================================
class notImplementedError(Exception):
    """ something isn't implemented yet """
    def __init__(self,msg=""):
        self.msg = msg
    def __str__(self):
        return "notImplementedError: %s"%(`self.msg`)

class filePermissionError(Exception):
    """ Called if we encounter a permission problem. """
    def __init__(self,msg=""):
        self.msg = msg
    def __str__(self):
        return "ERROR: Failed file permission check."

class apitestLoadError(Exception):
    """ """
    pass

#=============================================================================
# FUNCTIONS
#=============================================================================

#--------------------------------------
# genTimeStamp()
#--------------------------------------
def genTimeStamp():
    """ Generate a timestamp in string format YYYY-MM-DDTHH:MM:SS """
    t = time.localtime( time.time() )
    return "%04d-%02d-%02dT%02d:%02d:%02d"%(t[0],t[1],t[2],t[3],t[4],t[5])


def logMessage(msgClass, msg):
    """ Generates a log formatted message """
    msgClass  = "[%s]"%(msgClass)
    ts = genTimeStamp().replace("T"," ")      # separates the date and time with a space.
    theMsg = "%-23s  %s   %s"%(msgClass,ts,msg)
    return theMsg


#--------------------------------------
# hexdigest()
#--------------------------------------
def hexdigest(fname):
    """ Load a file and return an md5 digest. """
    md5obj = md5.new()
    try:
        f = file(fname,'rb')
    except:
        return None
    
    while True:
        d = f.read(8096)
        if d:
            md5obj.update(d)
        else:
            break
        
    return md5obj.hexdigest()


#--------------------------------------
# xmlObjToString
#--------------------------------------
def xmlObjToString(element=None):
    s = "None"
    if element != None:
        s = ""
        textBlock = False
        level = 0
        fields = re.split('(<.*?>)',ElementTree.tostring(element))
        for f in fields:
            if f[:4]=="<!--":
                s += "\n"+f+"\n"
            elif string.strip(f)=='':
                s += "\n"
            elif f[0]=="<" and f[1] != "/" and f[len(f)-2:]=="/>":
                s += " "*(2*level)+f
            elif f[0]=="<" and f[1] != "/":
                s += " "*(2*level)+f
                level += 1
            elif (f[:2]=="</" or f[len(f)-2:]=="/>") and not textBlock:
                level -= 1
                textBlock = False
                s += " "*(2*level)+f
            elif (f[:2]=="</") and textBlock==True:
                s += f
                level -= 1
                textBlock = False
            else:
                textBlock = True
                s += f
    return s

#--------------------------------------
# ANSIColor
#--------------------------------------
def ANSIcolor(color=None):
    if color==None:           return "\033[0m"
    elif color=="default":    return "\033[0m"
    elif color=="red":        return "\033[00;31m"
    elif color=="lightred":   return "\033[01;31m"
    elif color=="green":      return "\033[00;32m"
    elif color=="lightgreen": return "\033[01;32m"
    elif color=="brown":      return "\033[00;33m"
    elif color=="yellow":     return "\033[01;33m"
    elif color=="blue":       return "\033[00;34m"
    elif color=="lightblue":  return "\033[01;34m"
    elif color=="magenta":    return "\033[00;35m"
    elif color=="cyan":       return "\033[00;36m"
    elif color=="lightcyan":  return "\033[01;36m"
    elif color=="white":      return "\033[00;37m"

#--------------------------------------
# ANSIstring
#--------------------------------------
def ANSIstring(color="default", str=""):
    return "%s%s%s"%(ANSIcolor(color),str,ANSIcolor("default"))

#--------------------------------------
# xmlResultStatus
#--------------------------------------
def xmlResultStatus(element=None):
    status = 'UNKNOWN'
    if element != None:
        status = element.attrib.get('status')
    return status

#-----------------------------------
# getTestType
#-----------------------------------
def getTestType(file=None):
    """
    Returns the test type of a given XML test file.  Returns the root tag
    of the XML.  For APItest input files this will either be 'testDef' or
    'testBatch' for tests and batch files, respectively.  Returns 'UNKNOWN'
    if there is no filename argument given.
    """
    ret = 'UNKNOWN'
    if file != None:
        try:
            ret = ElementTree.parse(file).getroot().tag
        except:
            print "Error parsing %s"%(file)
    return ret


#=============================================================================
#=============================================================================
# CLASSES
#=============================================================================
#=============================================================================


#=============================================================================
#-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-
#
#  ###### ###### ###### ######    ##  ## ##  ## #####  ##     ######
#    ##   ##     ##       ##      ##  ## ### ## ##  ## ##     ##  ##
#    ##   ####   ######   ##   ## ###### ## ### ##  ## ##     ######
#    ##   ##         ##   ##      ##  ## ##  ## ##  ## ##     ## ##
#    ##   ###### ######   ##      ##  ## ##  ## #####  ###### ##  ##
#
#-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-
#=============================================================================
#
#=============================================================================
# testHandlerBase
#=============================================================================
class testHandlerBase(libdebug.debuggable):
    """
    This is the base class for test handlers.
    Forms the backbone for the test driver.  This class is inherited into
    testHandler where specific tests are defined.
    """
    
    # -------------------------
    #  Local Data Definitions
    # -------------------------
    options       = None
    isRunning     = False
    constructorOK = False            # T iff used right constructor
    preparedOK    = False            # T iff test is prepared
    testFileOK    = False            # T iff test file loaded
    hasCallback   = False            # T iff the callback is assigned
    timeoutFlag   = False            # T iff we killed the test b/c of timeout
    theCallback   = None
    testFileName  = None             # Test file name
    xmlFileTree   = None
    xmlFileRoot   = None
    xmlTestRoot   = None
    testType      = None
    actual        = {}
    expect        = {}
    expectFile    = []
    matchData     = {}
    matchCount    = 0
    matchedOK     = False
    preDelay      = 0.0
    postDelay     = 0.0
    iterDelay     = 0.0
    minPctMatch   = 100.0
    maxPctMatch   = 100.0
    match         = "YES"
    repCount      = 1
    repDone       = 0
    onMismatch    = 'CONTINUE'
    status        = 'DNE'
    hasXmlOutputTree = False
    xmlResultTree = None
    theTestData   = None
    WDIR          = None	   # Working directory (default is same as TSDIR)
    TSDIR         = None	   # Test Script Directory

    
    # -------------------------
    def __init__(self, db=None):
        """
        Default Constructor.  This should NOT be overridden.
        """
        ##print "[->]\ttestHandlerBase.__init__()"
        self.constructorOK = True
        self.Initialize()
        self.db = db
        self.db_runid = None
        self.db_batchid = None
        ##print "[<-]\ttestHandlerBase.__init__()"

    # -------------------------
    def Initialize(self):
        """ 
        Initializer.  Called at the end of __init__.
        This function should be overridden, not __init__.
        """
        self.printDebug("[->]\ttestHandlerBase.Initialize()")
        self.printDebug("[<-]\ttestHandlerBase.Initialize()")

    # -------------------------
    def setOptions(self, options=None):
        """
        Set local copy of command line options from getopt
        """
        self.options = options

    # -------------------------
    def prepare(self, testFileName=None):
        """
        Prepare the test (load it, etc)
        """
        self.printDebug("[->]\ttestHandlerBase.prepare()")
        self.preparedOK = False
        self.reset()
        self.load(testFileName)
        if self.testFileOK == True:
            self.preparedOK = True
        self.printDebug("[<-]\ttestHandlerBase.prepare()")

    # -------------------------
    def prepared(self):
        if self.preparedOK == True and self.testFileOK==True:
            return True
        else:
            return False

    # -------------------------
    def reset(self):
        """
        Reset the data structure.  Do some cleanup and erasing
        of old data after the test is finished to prevent any
        spillover.
        """
        self.printDebug("[->]\ttestHandlerBase.reset()")
        self.actual.clear()
        self.expect.clear()
        self.expectFile    = []
        self.testType      = None
        self.xmlFileTree   = None
        self.xmlFileRoot   = None
        self.xmlTestRoot   = None
        self.xmlResultTree = None
        self.hasXmlOutputTree = False
        self.isRunning = False
        self.timeoutFlag = False
        self.printDebug("[<-]\ttestHandlerBase.reset()")

    #-------------------------
    def set_timeoutFlag(self):
        """ Set the timeoutFlag to True. """
        self.timeoutFlag = True
        self.xmlResultTree.attrib['timeoutFlag'] = "YES"

    #-------------------------
    def unset_timeoutFlag(self):
        """ Set the timeoutFlag to False. """
        self.timeoutFlag = False
        self.xmlResultTree.attrib['timeoutFlag'] = "NO"

    #-------------------------
    def get_timeoutFlag(self):
        """ Return the timeoutFlag (T/F) """
        return self.timeoutFlag

    # ------------------------
    def delCallback(self):
        """ remove the callback """
        self.printDebug("[  ]\ttestHandlerBase.delCallback()")
        self.hasCallback = False
        del self.theCallback  ; self.theCallback= None

    # ------------------------
    def setXmlOutputTree(self, element):
        """ """
        self.hasXmlOutputTree = True
        self.xmlResultTree = element

    def getXmlOutputTree(self):
        """ return the XML Output Tree. """
        return self.xmlResultTree


    # -------------------------
    def load(self, testFileName=None):
        """
        load the test file and process it. 
        """
        self.printDebug("[->]\ttestHandlerBase.load(%s)"%(`testFileName`))
        self.testFileOK = False
        if testFileName:
            self.testFileName = testFileName
            
            if not os.access(self.testFileName, os.F_OK|os.R_OK):
                return False
            
            try:
                self.xmlFileTree  = ElementTree.parse(self.testFileName)
            except ExpatError,e:
                print "Error parsing '%s' in libapitest.load().\n====> %s" % \
                                (self.testFileName, e)
                return False

            self.xmlFileRoot  = self.xmlFileTree.getroot()
            self.xmlTestRoot  = self.xmlFileRoot.find('test')
            self.testType     = self.xmlTestRoot.attrib.get('type',None)
            self.repCount     = self.xmlTestRoot.attrib.get('repCount','1')
            self.repCount     = int(self.repCount)
            self.minPctMatch  = self.xmlTestRoot.attrib.get('minPctMatch','100.0')
            self.minPctMatch  = float(self.minPctMatch)
            self.maxPctMatch  = self.xmlTestRoot.attrib.get('maxPctMatch','100.0')
            self.maxPctMatch  = float(self.maxPctMatch)
            self.match        = self.xmlTestRoot.attrib.get('match','YES')
            self.match        = self.match.upper()
            self.preDelay     = self.xmlTestRoot.attrib.get('preDelay','0.0')
            self.preDelay     = float(self.preDelay)
            self.postDelay    = self.xmlTestRoot.attrib.get('postDelay','0.0')
            self.postDelay    = float(self.postDelay)
            self.iterDelay    = self.xmlTestRoot.attrib.get('iterDelay','0.0')
            self.iterDelay    = float(self.iterDelay)
            self.onMismatch   = self.xmlTestRoot.attrib.get('onMismatch','CONTINUE')
            self.onMismatch   = self.onMismatch.upper()
            self.timeout      = self.xmlTestRoot.attrib.get('timeout','0.0')
            self.timeout      = float(self.timeout)
            
            # setting ranges based on self.match
            ##print self.match
            if self.match == "YES": 
                self.minPctMatch = 100.0
                self.maxPctMatch = 100.0
            else:
                self.minPctMatch = 0.0
                self.maxPctMatch = 0.0

            # look for output buffer data in the apt file.
            outputElt = self.xmlTestRoot.findall('output')
            for ielem in outputElt:
                name = ielem.attrib.get('name')
                fmt  = ielem.attrib.get('format','literal')
                buf  = ielem.text
                if buf == None:
                    buf = ""
                self.expect[name] = (fmt,buf)

            # look for output file data in the apt file. (outputFile)
            outputFileElt = self.xmlTestRoot.findall('outputFile')
            for ielem in outputFileElt:
                control = ielem.attrib.get('control',None)
                output  = ielem.attrib.get('output',None)
                cleanup = ielem.attrib.get('cleanup',"YES")
                self.expectFile.append( (control,output,cleanup) )

            self.hasXmlOutputTree = True
            self.xmlResultTree = ElementTree.Element("testResult", \
                                           filename=self.testFileName, \
                                           status=self.status, \
                                           md5sum=hexdigest(self.testFileName),\
                                           pctMatchMin=str(self.minPctMatch),\
                                           pctMatchMax=str(self.maxPctMatch),\
                                           match=str(self.match) )
            
            
            # Insert shortDescription from test file into test result text.
            SD = self.xmlFileTree.find("shortDescription")
            if SD != None:
                if SD.text != None:
                    desc = SD.text
                    if desc != None:
                        desc = string.lstrip(desc)
                        if desc != "":
                            bSD = ElementTree.SubElement(
                                        self.xmlResultTree,'shortDescription')
                            bSD.text = desc
                            #print bSD.__dict__
                            
            self.unset_timeoutFlag()
            self.xmlResultTree.attrib['timeoutTime'] = str(self.timeout)
            self.testFileOK   = True

        ## ========================================================
        #  MySQL Stuff BEGIN
        #
        if self.options and self.options.has_key("sqldb") and \
           self.options["sqldb"] and self.db.connected:
            
            from db_mysql import apitestdb
            fname = os.path.abspath(self.testFileName)
            query = ""
            if self.db_batchid == None:
                query="""
                    INSERT INTO `results` (`RUNID`,`FNAME`,`STATUS`,`TYPE`,`TIMEOUT`)
                    VALUES (%d,'%s','%s','TEST',%f)
                    """ % (self.db_runid,fname,'RUNNING',self.timeout)
            else:
                query="""
                    INSERT INTO `results` (`RUNID`,`PID`,`FNAME`,`STATUS`,`TYPE`,`TIMEOUT`)
                    VALUES (%d,%d,'%s','%s','TEST',%f)
                    """ % (self.db_runid,self.db_batchid,fname,
                           'RUNNING',self.timeout)
            self.db.execute(query)
            self.db_testid = self.db.getMaxID('results')
        #
        #  MySQL Stuff END
        ## ========================================================
        
        self.printDebug("[<-]\ttestHandlerBase.load()")


    # -------------------------
    # testHandlerBase.execute()
    def execute(self):
        """
        run the test.
        """
        self.printDebug("[->]\ttestHandlerBase.execute()")
        self.printDebug("\t  testType = %s"%(self.testType))

        self.TSDIR = os.path.dirname(self.testFileName)

        if self.TSDIR != "": 
            self.TSDIR = os.path.normpath(self.TSDIR+"/")

        self.WDIR = self.TSDIR

        self.xmlResultTree.attrib['timeStart']=genTimeStamp()

        # Put info into xmlResultTree regarding testID,batchID, and runID
        self.status  = 'RUNNING'
        self.batchID = None
        self.runID   = None
        self.testID  = None
        self.testID  = self.WB.TD.addTest(self.xmlResultTree)

        self.xmlResultTree.attrib["testID"] = str(self.testID)
        self.xmlResultTree.attrib['status'] = self.status
        
        self.batchID = self.WB.TD.B.currentID
        if (self.batchID != -1) and (self.batchID != None):
            self.xmlResultTree.attrib["pBatchID"] = str(self.batchID)

        self.runID = self.WB.TD.R.currentID
        if(self.runID != -1):
            self.xmlResultTree.attrib["runID"] = str(self.runID)

        execFuncName = "do_"+self.testType
        self.printDebug("\t  execFunc = %s"%(execFuncName))
        if not hasattr(self, execFuncName):
            print "\tERROR: function %s does not exist!"%(execFuncName)

        # else:
        #  WCM: need to insert predelay sleep.  Must be nonblocking
        #       probably via reactor.callLater and break up execute()
        #       into pieces.
        else:
            execFunc = getattr(self, execFuncName)

            killFuncName = "kill_"+self.testType
            if hasattr(self, killFuncName) and self.timeout>0.0:
                killFunc = getattr(self, killFuncName)
                reactor.callLater(self.timeout, killFunc)

            for irep in range(self.repDone, self.repCount):
                self.printDebug('\t  irep = %d'%(irep))
                self.isRunning = True
                execFunc()
                
        self.printDebug("[<-]\ttestHandlerBase.execute()")


    # -------------------------
    def validate(self):
        """
        Validate the returned results.
        * sets matchData with details
        * sets self.matchedOK flag
        * sets self.status flag too
        """
        self.printDebug("[->]\ttestHandlerBase.validate()")
        self.printDebug('\t\tACTUAL: %s'%(`self.actual`))
        self.printDebug('\t\tEXPECT: %s'%(`self.expect`))
        self.matchedOK = True
        
        for k in self.expect.keys():
            expect_type = self.expect[k][0]
            self.printDebug("\tvalidating :: %s"%(`k`))
            if self.actual.has_key(k):
                self.actual[k] = str(self.actual[k])
                if expect_type == 'regexp':
                    rmatch = re.compile(self.expect[k][1],re.M|re.S)
                    if rmatch.match(self.actual[k]): 
                        self.matchData[k] = True
                    else:
                        self.matchData[k] = False
                        self.matchedOK = False
                elif expect_type == 'literal':
                    if str(self.expect[k][1]) == str(self.actual[k]):
                        self.matchData[k] = True
                    else:
                        self.matchData[k] = False
                        self.matchedOK = False
            else:
                self.matchData[k] = False
                self.matchedOK = False
                self.actual[k] = None
                
            # dump the results into the XML tree
            matchtxt="NO"
            if self.matchData[k]:
                matchtxt = "YES"
            xmlOutput = ElementTree.SubElement(self.xmlResultTree,\
                                               'output',matched=matchtxt,\
                                               name=k,format=self.expect[k][0])
            
            a=ElementTree.SubElement(xmlOutput,'actual').text=str(self.actual[k])
            
            e=ElementTree.SubElement(xmlOutput,'expect').text=str(self.expect[k][1])
            
            #############
            #
            # MySQL BEGIN
            #
            if self.options and self.options.has_key("sqldb") and \
               self.options["sqldb"] and self.db.connected:
                
                from db_mysql import apitestdb
                query = """
                INSERT INTO `resultdata` (`resultid`,`match`,`type`,`format`,`expect`,`actual`)
                VALUES (%d,%d,'%s','%s','%s','%s')
                """ % (self.db_testid,self.matchData[k],k,expect_type, 
                       self.expect[k][1],self.actual[k] )
                self.db.execute(query)
            #
            # MySQL END
            #
            ###############

        if self.actual.has_key("ERROR") and not self.expect.has_key("ERROR"):
            self.matchedOK = False
            xmlOutput = ElementTree.SubElement(self.xmlResultTree, \
                                               'output',matched="NO", \
                                               name="ERROR",format="literal")
            ElementTree.SubElement(xmlOutput,'actual').text=str(self.actual["ERROR"])
            ElementTree.SubElement(xmlOutput,'expect').text=""

        # check reference file if we have one
        # This might not be the best way to try and check a file for
        # correctness though.
        # (may be experimental code... don't remember.  Need to verify)
        for ifile in self.expectFile:
            controlFile = ifile[0]
            outputFile  = ifile[1]
            cleanup     = re.match("^YES$",ifile[2].upper()) != None
            #print "Validating file: %s <=> %s [cleanup=%s]"%(ifile[0],ifile[1],ifile[2])
            controlExists = os.path.exists(controlFile)
            outputExists  = os.path.exists(outputFile)
            if controlExists and outputExists:
                iline = 1
                try:
                    cfp = open(controlFile,"r")
                    ofp = open(outputFile,"r")

                    close(cfp)
                    close(ofp)
                except:
                    # print " internal error: libapitest.py, problem openining files."
                    pass
            else:
                self.matchedOK = False
                for i in [(controlExists,controlFile),(outputExists,outputFile)]:
                    if i[0] == False:
                        xmlOutput = ElementTree.SubElement(self.xmlResultTree, \
                                    'output',matched="NO", name="ERROR", format="literal")
                    ElementTree.SubElement(xmlOutput,'actual').text="File not be found!"
                    ElementTree.SubElement(xmlOutput,'expect').text=i[1]
         

        if self.matchedOK:
            self.matchCount += 1
            
        self.printDebug('\tmatchedOK   = %s'%(self.matchedOK))
        self.printDebug('\tmatchData   = %s'%(`self.matchData`))
        self.printDebug('\tmatch       = %s'%(self.match))
        self.printDebug('\tmatchCount  = %s'%(`self.matchCount`))
        self.printDebug('\trep data    = %s / %s'%(self.repDone,self.repCount))
        # for right now, we're not iterating a test... 
        self.printDebug("[<-]\ttestHandlerBase.validate()")
        return True


    # -------------------
    def createCallback(self):
        """
        Create the deferred object for a function and set the appropriate callback.
        Return the deferred object.
        """
        D = defer.Deferred()
        D.addCallback(self.procReturned)
        return(D)


    # -------------------------
    def procReturned(self, result):
        """
        Returned from the test.  Save the result and move on to validation.
        """
        self.printDebug('[->]\ttestHandlerBase.procReturned()')
        self.isRunning = False
        self.unsetRunningFlag()
        self.xmlResultTree.attrib['timeStop']=genTimeStamp()
        self.repDone += 1
        self.actual = result
        self.validate()
        self.done()
        # execute the callback
        self.doCallback()
        self.printDebug('[<-]\ttestHandlerBase.procReturned()')


    # --------------------------
    def done(self):
        """
        Final routine called when a process has completed and reporting
        is finalized.
        """
        self.printDebug("[->]\ttestHandlerBase.done()")
        self.pctMatch = (self.matchCount/float(self.repCount))*100.0
        if self.repDone > 0:
            if self.timeoutFlag:
                self.status = "TIMEDOUT"
            elif self.pctMatch > self.maxPctMatch or self.pctMatch < self.minPctMatch:
                self.printDebug('\tTest FAILED')
                self.status = 'FAIL'
            else:
                self.status = 'PASS'
        self.xmlResultTree.attrib['pctMatch'] = str(self.pctMatch)
        self.xmlResultTree.attrib['status']= self.status

        # Dump the original Test Script into the output XML as a comment.
        testFileString = xmlObjToString(self.xmlFileTree.getroot())
        testFileString = string.replace(testFileString, "--", "-")
        orig = ElementTree.Comment(testFileString)
        self.xmlResultTree._children.append(orig)

        # if command line: print out message indicating test status
        # colorize it too!
        if(self.options['cmdLine']==True):
            msgStr = ""
            statusColor = "yellow"
            if   self.status == "PASS":  statusColor = "green"
            elif self.status == "FAIL":  statusColor = "red"
            statusStr = "%s"%(ANSIstring(statusColor,self.status))
            print logMessage(statusStr, self.testFileName)

        # cleanup if the cleanup handler exists
        cleanupFuncName = "cleanup_"+self.testType
        if hasattr(self,cleanupFuncName):
            cleanupFunc = getattr(self,cleanupFuncName)
            cleanupFunc()
        self.saveResultData()
        self.reset()
        self.printDebug("[<-]\ttestHandlerBase.done()")


    # -------------------------
    def saveResultData(self):
        """
        Save Result Data
        """
        # Save the output to a File if we are requested to!
        if( self.options and self.options["transient"]==0 ):
            fileName = string.join(self.WB.currentORoot,"/") 
            fileName += "/t%d."%(self.testID)
            fileName += os.path.splitext(os.path.basename(self.testFileName))[0]
            fileName += ".out"
            fileName = os.path.normpath(fileName)
            FP = open(fileName,"w")
            FP.write( xmlObjToString(self.xmlResultTree) )
            FP.close()
        ################
        #
        # MySQL Test Code BEGIN
        #
        if self.options and self.options["sqldb"] and self.db.connected:
            from db_mysql import apitestdb
            query = """
                    UPDATE `results` SET `TFINISH`=CURRENT_TIMESTAMP,`STATUS`='%s'
                    WHERE ID=%s
                    """ % (self.status, self.db_testid)
            self.db.execute(query)
        #
        # MySQL Test Code END
        #
        ################
        
        return True


    # -------------------------
    def setCallback(self, theCallback):
        """
        Set the callback.
        """
        self.printDebug("[->]\ttestHandlerBase.setCallback()")
        self.theCallback = theCallback
        self.hasCallback = True
        self.printDebug("[<-]\ttestHandlerBase.setCallback()")


    # -------------------------
    def unsetCallback(self):
        """
        Remove the callback.
        """
        self.printDebug("[->]\ttestHandlerBase.unsetCallback()")
        self.theCallback = None
        self.hasCallback = False
        self.printDebug("[<-]\ttestHandlerBase.unsetCallback()")


    # -------------------------
    def doCallback(self):
        """
        If a callback has been assigned ... stick it into the reactor's 
        scheduler.
        """
        self.printDebug("[->]\ttestHandlerBase.doCallback()")
        if self.hasCallback:
            reactor.callLater(0, self.theCallback.callback, self.status)
        reactor.callLater(0,self.delCallback)
        self.printDebug("[<-]\ttestHandlerBase.doCallback()")

        
    # -------------------------
    def setRunningFlag(self, data):
        self.WB.running[0] = True
        self.WB.running[1] = data

        
    # -------------------------
    def unsetRunningFlag(self):
        self.WB.running[0] = False
        self.WB.running[1] = None

        
    # -------------------------
    def do_None(self):
        """
        do_None - placeholder handler (example)
        """
        self.printDebug("[->]\ttestHandlerBase.do_None()")
        self.printDebug("[<-]\ttestHandlerBase.do_None()")


# ========================================================================
# class mystack
# ========================================================================
class mystack(libdebug.debuggable):
    """
    Implements a simple stack via a list. 
    """
    def __init__(self):
        self.data = []

    def __str__(self):
        return `self.data`

    def __len__(self):
        return len(self.data)

    def push(self, item):
        self.data.append(item)
        
    def pop(self):
        return self.data.pop()
    
    def top(self):
        """
        Get the item that is on the top of the stack, but do not
        pop it from the stack.
        """
        if len(self.data) > 0:
            return self.data[len(self.data)-1]
        else:
            return None

    def clear(self):
        self.data = []
        

# ========================================================================
# class dbtable
# ========================================================================
class dbtable(libdebug.debuggable):
    """
    Superclass for a database table.
    """
    def __init__(self):
        self.nextID    = 0
        self.currentID = -1
        self.data      = {}

    def append(self, data):
        id = self.nextID
        self.nextID += 1
        self.data[id] = data
        self.currentID = id
        return id

    def __getitem__(self, idx):
        return self.data[idx]

    def __delitem__(self, id):
        if self.data.has_key(id):
            self.data.__delitem__(id)

    def __str__(self):
        s  = "-----------------------\n"
        s += "nextID    = %s\n"%(`self.nextID`)
        s += "currentID = %s\n"%(`self.currentID`)
        s += "data      = %s\n"%(`self.data`)
        return s

# ========================================================================
# class tblRunList
# ========================================================================
class tblRunList(dbtable):
    def __init__(self):
        dbtable.__init__(self)
        self.idstk = mystack()

    def newRow(self):
        self.append( ([],[], genTimeStamp()) )
        self.idstk.push(self.currentID)
        return self.currentID

    def addTestID(self, runID, testID):
        self.data[runID][0].append(testID)
        
    def addBatchID(self, runID, batchID):
        self.data[runID][1].append(batchID)

    def popCurrentID(self):
        self.idstk.pop()
        self.currentID = self.idstk.top()

    def clearCurrentID(self):
        self.idstk.clear()

    def getTestList(self,runID):
        return self.data[runID][0]

    def getBatchList(self,runID):
        return self.data[runID][1]

    def getRunIDs(self):
        return self.data.keys()

    def __str__(self):
        s = "tblRunList\n"
        s+= dbtable.__str__(self)
        s+= "idstack   = "+str(self.idstk)+"\n"
        return s


# ========================================================================
# class tblBatchList
# ========================================================================
class tblBatchList(dbtable):
    def __init__(self):
        dbtable.__init__(self)
        self.idstk = mystack()
        
    def newRow(self,runID,batch,parentBatchID=None):
        # testList, batchList, RunID
        self.append( ([],[],runID,batch,parentBatchID) )
        self.idstk.push(self.currentID)
        return self.currentID

    def addTestID(self,batchID,testID):
        self.data[batchID][0].append(testID)
        
    def addSubBatchID(self,batchID,subBatchID):
        self.data[batchID][1].append(subBatchID)

    def popCurrentID(self):
        self.idstk.pop()
        self.currentID = self.idstk.top()

    def clearCurrentID(self):
        self.idstk.clear()

    def getRunID(self,ID):
        if self.data.has_key(ID):
            return self.data[ID][2]
        else:
            return None

    def getTestList(self,ID):
        if self.data.has_key(ID):
            return self.data[ID][0]
        else:
            return None

    def getSubBatchList(self,ID):
        if self.data.has_key(ID):
            return self.data[ID][1]
        else:
            return None

    def __str__(self):
        s = "tblBatchList\n"
        s+= dbtable.__str__(self)
        return s


# ========================================================================
# class tblTestList
# ========================================================================
class tblTestList(dbtable):
    """
    Class for storing a TEST's data in the database.
    Extends dbtable.
    """
    def __init__(self):
        dbtable.__init__(self)

    def addData(self, data):
        testID = self.append( None )
        self.data[testID] = data
        return testID


# ========================================================================
# class testDataType
# ========================================================================
class testDataType(libdebug.debuggable):
    """
    testDataType stores the test results database information as well as
    controls adding/removing entries to and from it.  It tracks if we're
    in a batch file or not for recursive batch file execution, etc.
    """
    def __init__(self):
        self.R = tblRunList()
        self.B = tblBatchList()
        self.T = tblTestList()

    def newRun(self):
        self.exitRun()
        return self.R.newRow()
        
    def addBatch(self,batch):
        oldBatchID = None
        rootLevel = False
        if self.B.idstk.top() == None:
            rootLevel = True
        else:
            oldBatchID = self.B.currentID
        batchID= self.B.newRow(self.R.currentID,batch,oldBatchID)
        if rootLevel:
            self.R.addBatchID(self.R.currentID, self.B.currentID)
        else:
            self.B.addSubBatchID(oldBatchID, self.B.currentID)
        return batchID

    def exitBatch(self):
        self.B.popCurrentID()

    def exitRun(self):
        self.B.clearCurrentID()
        self.R.clearCurrentID()

    def addTest(self, test):
        newID = self.T.addData(test)
        if self.B.idstk.top() != None:
            self.B.addTestID(self.B.currentID,self.T.currentID)
        else:
            self.R.addTestID(self.R.currentID,self.T.currentID)
        return newID

    def getRunIDs(self):
        return self.R.getRunIDs()

    def getRun(self,ID):
        if self.hasRun(ID):
            return self.R.data[ID]
        else:
            return None

    def hasRun(self,ID):
        return self.R.data.has_key(ID)

    def getTestsByRun(self,ID):
        if self.R.data.has_key(ID):
            return self.R.getTestList(ID)
        else: return None

    def getBatchesByRun(self,ID):
        if self.R.data.has_key(ID):
            return self.R.getBatchList(ID)
        else:
            return None

    def getTestsByBatch(self,ID):
        return self.B.getTestList(ID)
    
    def getSubBatchesByBatch(self,ID):
        return self.B.getSubBatchList(ID)
    
    def getRunIDByBatch(self,ID):
        return self.B.getRunID(ID)

    def hasTest(self,ID):
        return self.T.data.has_key(ID)

    def getTest(self,ID):
        if self.hasTest(ID):
            return self.T.data[ID]
        else:
            return None

    def hasBatch(self,ID):
        return self.B.data.has_key(ID)
    
    def getBatch(self,ID):
        if self.hasBatch(ID):
            return self.B.data[ID]
        else:
            return None

    def sumBatchTree(self,batchID):
        subBatchIDs = self.B[batchID][1]
        batchXML    = self.B[batchID][3]
        summaryXML  = batchXML.find('summary')
        nFail  = int(summaryXML.attrib.get('nFail', 0))
        nPass  = int(summaryXML.attrib.get('nPass', 0))
        nTotal = int(summaryXML.attrib.get('nTotal',0))
        for i in subBatchIDs:
            (nT,nP,nF) = self.sumBatchTree(i)
            nFail  += nF
            nTotal += nT
            nPass  += nP
        return(nTotal,nPass,nFail)

    def __str__(self):
        s = str(self.R)+"\n"
        s+= str(self.B)+"\n"
        s+= str(self.T)
        return s



#==========================================================================
#\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/
#
#   ##    ## ##  ## ## ###### ###### #####  ######  ####  ###### #####
#   ##    ## ##  ## ##   ##   ##     ##  #  ##  ## ##  ## ##  ## ##  ##
#   ## ## ## ###### ##   ##   ####   ###### ##  ## ###### ###### ##  ##
#   ## ## ## ##  ## ##   ##   ##     ##  ## ##  ## ##  ## ## ##  ##  ##
#   ######## ##  ## ##   ##   ###### ###### ###### ##  ## ##  ## #####
#
#/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\
#==========================================================================
        
#==========================================================================
# class extendable
#==========================================================================
class extendable:
    """
    Base class that makes other classes more easily extendable dynamically
    """
    def additem(self, dataMemberName, dataMemberData):
        try:
            setattr(self, dataMemberName, dataMemberData)
        except:
            print "Error in extendable, could not set attribte"

    def delitem(self, dataMemberName):
        if hasattr(self, dataMemberName):
            victim = getattr(self, dataMemberName)
            del victim

    def getitem(self, dataMemberName):
        item = None
        if hasattr(self, dataMemberName):
            item = getattr(self, dataMemberName)
        return item

    def display(self):
        for k in self.__dict__.keys():
            print "  %14s::\t%s"%(`k`,`getattr(self,k)`)



#==========================================================================
# class whiteboard
#==========================================================================
class whiteboard(libdebug.debuggable):
    """
    A whiteboard that is linked into all data structures, facilitates
    easy passing of data around.
    """
    def __init__(self):
        self.workList  = Queue.Queue()
        self.running = [False, (-1,"")]
        self.TD = testDataType()

    def clearWorkList(self):
        self.jobMan.clear()
        while not self.workList.empty():
            self.workList.get()
        del self.running
        self.running = [False, (-1,"")]

    def clearTestData(self):
        pass

    def clear(self):
        # clear the workQueue
        self.clearWorkList()
        self.clearTestData()


def getTimestampByRunID(runID,whiteBoard):
    if runID in whiteBoard.TD.R.data:
        return(whiteBoard.TD.R.data[runID][2])
    else:
        return(None)


def makeOutputDir(WB, runID):
    retVal = True
    ts = getTimestampByRunID(runID,WB)
    ts = string.replace(ts, ":","-")
    ts = string.replace(ts, "T",".")
    WB.currentORoot.append("run."+ts)
    theOutputPath = os.path.normpath(string.join(WB.currentORoot,"/"))
    ##print string.join(WB.currentORoot,"/")
    
    try:
        os.makedirs( theOutputPath )
    except:
        print "Failed to make directory '%s'!"%( theOutputPath )
        retVal = False
    return retVal


#======================================================================
#=====================================================================
#                      S C R I P T    T E S T S
#=====================================================================
#======================================================================

# ----------------------------------
# cmd_cb - callback tester
# ----------------------------------
def cmd_cb(result):
    """ Internal Testing Routine """
    print "[->]\tEntering test callback!"
    for k in result.keys():
        print "%s=\t%s"%(k, `result[k]`)

if "__main__" == __name__:
    """ For testing purposes only """
    
    pass


# EOF
