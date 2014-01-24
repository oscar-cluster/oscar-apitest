""" 
Job Manager class 
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
# $Id: jobManager.py,v 1.28 2005/10/04 16:29:32 wcmclen Exp $
#

import re
import os
import os.path
import Queue
import string
from time import sleep

# APItest modules
import libdebug
import libapitest
import testHandler
import digraph

# Twisted modules
from twisted.internet import protocol
from twisted.internet import reactor,defer

# ElementTree modules
from elementtree import ElementTree

from xml.parsers.expat import ExpatError

# KLUDGE ALERT!
if not os.path.__dict__.has_key('sep'): 
    os.path.sep = '/'

    
# --- genBaseTestResult() ---
def genBaseTestResult(task):
    xml = ElementTree.Element("testResult", \
                              filename=task, \
                              md5sum=libapitest.hexdigest(task))
    return xml


# --- genBaseBatchResult() ---
def genBaseBatchResult(task):
    xml = ElementTree.Element("batchResult", \
                              filename=task, \
                              md5sum=libapitest.hexdigest(task))
    return xml



# ====================================================================
# class jobManagerBase
# ====================================================================
class jobManagerBase(libdebug.debuggable):
    """
    base class for job manager
    """
    options      = None
    pollDelay    = 1.0
    _isBusy      = False
    _continue    = False
    _theCallback = None

    def Initialize(self, options, db=None):
        self.options = options
        self.db = db
        self.db_batchid = None
        self.db_runid   = None
        ### MySQL : get runid
        if self.options and self.options["sqldb"] and self.db.connected:
            self.db_runid = self.db.getMaxID('runs')
        ### MySQL : get runid

    def start(self):
        """ start up the poller """
        self.printDebug("[->]\tjobManagerBase.start(%s)"%(`self`))
        self._continue = True
        reactor.callLater(0, self.poll)
        self.printDebug("[<-]\tjobManagerBase.start()")

    def stop(self):
        """ shut down the poller """
        self.printDebug("[->]\tjobManagerBase.stop(%s)"%(`self`))
        self._continue = False
        self.printDebug("[<-]\tjobManagerBase.stop()")


    def poll(self):
        """ poll for some work """
        self.printDebug("[->]\tjobManagerBase.poll()")
        if self._continue:
            if self.query():
                self.do_task()
            else:
                reactor.callLater(self.pollDelay,self.poll)
        self.printDebug("[<-]\tjobManagerBase.poll()")

    def do_task(self,doexec=True):
        """ execute the task if we had one """
        self.printDebug("[->]\tjobManagerBase.do_task()")
        self.isBusy_on()
        self._theCallback = defer.Deferred()
        self._theCallback.addCallback(self.task_done)
        if doexec:
            self.Execute()
        self.printDebug("[<-]\tjobManagerBase.do_task()")

    def task_done(self,status):
        """ task returned """
        self.printDebug("[->]\tjobManagerBase.task_done(%s)"%(`status`))
        self.Finish(status)
        self.isBusy_off()
        reactor.callLater(0.01,self.poll)
        self.printDebug("[<-]\tjobManagerBase.task_done()")

    def getCallback(self):
        return self._theCallback

    def setPollDelay(self, pollDelay=1.0):
        """
        set the poll delay timer (seconds).  Defaults to 1.0 sec.
        """
        self.printDebug("[  ]\tjobManagerBase.setPollDelay(%s)"%(`pollDelay`))
        self.pollDelay = pollDelay

    def isBusy_on(self):  self._isBusy = True
    def isBusy_off(self): self._isBusy = False
    def isBusy(self):     return self._isBusy

    def query(self):
        """
        Return T/F if there is or is not work to be done.
        This MUST be overrided by the child object.
        Raises notImplementedError if not.
        """
        raise libapitest.notImplementedError
    
    def Execute(self):
        """
        Called by do_task.
        This MUST be overrided by the child object.
        Raises notImplementedError if not.
        """
        raise libapitest.notImplementedError

    def Finish(self, status):
        """
        Called by task_done to execute cleanup code for a given task.
        Does nothing if not overrided by teh child object.
        """
        pass




#============================================================================
#-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-
#
#      ## ###### #####  ##   ##  ####  ##  ##  ####  ###### ###### ######
#      ## ##  ## ##  #  ### ### ##  ## ### ## ##  ## ##     ##     ##  ##
#      ## ##  ## ###### ## # ## ###### ## ### ###### ## ### ####   ######
#  ##  ## ##  ## ##   # ##   ## ##  ## ##  ## ##  ## ##  ## ##     ## ##
#  ###### ###### ###### ##   ## ##  ## ##  ## ##  ## ###### ###### ##  ##
#
#-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-
#============================================================================
#
#============================================================================
# class jobManager
#============================================================================
class jobManager(jobManagerBase):
    workQueue = Queue.Queue()


    # Initialize:: overrides the base initialize.
    def Initialize(self, options, db=None):
        self.options = options
        self.db = db
        self.db_batchid = None
        self.db_runid   = None

    # --- jobManager.clear()
    def clear(self):
        """ clear out the workQueue """
        while not self.workQueue.empty():
            self.workQueue.get()
        
    # --- jobManager.query()
    def query(self):
        """ true if there's work to do """
        self.printDebug("[->]\tjobManager.query(%s)"%(`self`))

        # Shutdown if we're running from the command line and are done.
        if(self.options['cmdLine'] == True and self.WB.workList.empty()):
            self._continue = False
            reactor.callLater(1.0, reactor.stop)
        
        while not self.WB.workList.empty():
            task = self.WB.workList.get()
            self.workQueue.put(task)
        self.printDebug("[<-]\tjobManager.query()")
        return not self.workQueue.empty()

    # --- jobManager.Execute() ---
    def Execute(self):
        """ Called at Top-level for each batch or test """
        self.printDebug("[->]\tjobManager.Execute()")
        task = self.workQueue.get()

        #### MySQL Stuff Begin
        if self.options and self.options["sqldb"] and self.db.connected:
            self.db_runid = self.db.getMaxID('runs')
        #### MySQL Stuff End
        
        if re.match(".*\.apt$",task):
            tH = testHandler.testHandler(self.db)
            tH.setOptions(self.options)
            tH.WB         = self.WB
            tH.db_runid   = self.db_runid
            tH.db_batchid = self.db_batchid
            if self.get_debug(): tH.debug_on()
            tH.setCallback( self.getCallback() )
            tH.prepare(task)
            if True == tH.prepared():
                tH.execute()
            else:
                # will need to do the callback here
                reactor.callLater(0.0, tH.doCallback)
                pass
        elif re.match(".*\.apb$",task):
            tB = batchHandler()
            tB.clear()
            tB.Initialize(self.options, self.db)
            tB.WB = self.WB
            if self.get_debug(): tB.debug_on()
            try:
                tB.loadBatchFile(task)
            except ExpatError,msg:
                print "ERROR: Loading `%s` failed!  [%s]"%(task,msg)
                reactor.callLater(0.1, tB.doCallback)
            tB.setCallback(self.getCallback())
            tB.start()
            
        self.printDebug("[<-]\tjobManager.Execute()")






#============================================================================
#-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-\/-
#
#  #####   ####  ###### ###### ##  ##    ##  ## ##  ## #####  ##     ######
#  ##  #  ##  ##   ##   ##     ##  ##    ##  ## ### ## ##  ## ##     ##  ##
#  ###### ######   ##   ##     ###### ## ###### ## ### ##  ## ##     ######
#  ##  ## ##  ##   ##   ##     ##  ##    ##  ## ##  ## ##  ## ##     ## ##
#  ###### ##  ##   ##   ###### ##  ##    ##  ## ##  ## #####  ###### ##  ##
#
#-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-/\-
#============================================================================
#
# ===========================================================================
# class batchHandler
# ===========================================================================
class batchHandler(jobManagerBase):
    """
    Controls the execution of a batch script.  Extends jobManagerBase
    and maintains its own scheduler / polling loop.
    """


    # ------------------------------
    def __init__(self):
        self.printDebug("[->] batchHandler.__init__()")
        self.db_parent_batchid = None
        self.runID = None
        self.parentTask  = ""
        self.currentTask = ""
        self.status = "DNE"
        self.hasRun = False
        self.hasCallback = False
        self.theCallback = None
        self.batchFileName = ""
        self.batchFilePath = ""
        self.batchFileTree = None
        self.testQueue = Queue.Queue()
        self.testGraph = digraph.digraph()
        ##self.debug_on()
        self.printDebug("[<-] batchHandler.__init__()")
    

    # ------------------------------
    def setCallback(self, CB):
        self.printDebug("[->]\tbatchHandler.setCallback(%s)"%(`CB`))
        self.theCallback = CB
        self.hasCallback = True

        
    # ------------------------------
    def delCallback(self):
        self.printDebug("[->]\tbatchHandler.delCallback()")
        del self.theCallback
        self.theCallback = None
        self.hasCallback = False

        
    # ------------------------------
    def doCallback(self):
        self.printDebug("[->]\tbatchHandler.doCallback()")
        if self.hasCallback:
            reactor.callLater(0,self.theCallback.callback,self.status)
        self.printDebug("[<-]\tbatchHandler.doCallback()")

        
    # ------------------------------
    def setWhiteboard(self, WB):
        """ set the whiteboard pointer. """
        self.printDebug("[->]\tbatchHandler.setWhiteBoard(%s)"%(`WB`))
        self.WB = WB

        
    # ------------------------------
    def loadBatchFile(self, fileName):
        """ load the batchFile """
        self.printDebug("[->]\tbatchHandler.loadBatchFile(%s)"%(fileName))
        self.hasRun        = False
        self.batchFileName = fileName
        self.batchFilePath = os.path.split(fileName)[0]
        self.testGraph.clear()
        self.testGraph.set_name(self.batchFileName)
        if not os.path.exists(self.batchFileName):
            print "Error encountered in '%s'"%(self.parentTask)
            print "\tCould not locate file '%s'\n"%(self.batchFileName)
        try:
            self.batchFileTree = ElementTree.parse(self.batchFileName)
        except:
            print "Could not parse '%s'.\n"%(self.batchFileName)


        ##########
        #
        # MySQL Test Code :: loadBatchFile
        #
        if self.options and self.options["sqldb"] and self.db.connected:
            from db_mysql import apitestdb
            fname = os.path.abspath(self.batchFileName)
            if self.db_parent_batchid == None:
                query="""
                      INSERT INTO `results` (`RUNID`,`FNAME`,`STATUS`,`TYPE`,`TIMEOUT`)
                      VALUES (%d,'%s','%s','BATCH',0.0)
                      """ % (self.db_runid,fname,'RUNNING')
            else:
                query="""
                      INSERT INTO `results` (`RUNID`,`PID`,`FNAME`,`STATUS`,
                                             `TYPE`,`TIMEOUT`)
                      VALUES (%d,%d,'%s','RUNNING','BATCH',0.0)
                      """ % (self.db_runid,self.db_parent_batchid,fname)
            self.db.execute(query)
            self.db_batchid = self.db.getMaxID("results")
        #
        # MySQL Test Code END
        #
        ##########

            
        batchFileTreeRoot = self.batchFileTree.getroot()

        self.xmlroot = ElementTree.Element("batchResult", \
                              filename=self.batchFileName, \
                              status="", \
                              md5sum=libapitest.hexdigest(self.batchFileName),
                              timeStart=libapitest.genTimeStamp() )

        xmlOutputSummary = ElementTree.SubElement(self.xmlroot,'summary', \
                              nPass='0',nFail='0',nTotal='0')

        self.batchID = self.WB.TD.addBatch(self.xmlroot)
        #self.xmlroot.attrib['batchID']=str(self.batchID)

        parentBatchID = self.WB.TD.B.data[ self.batchID ][4]
        if parentBatchID != None:
            self.xmlroot.attrib['pBatchID'] = str(parentBatchID)

        self.runID = self.WB.TD.R.currentID
        self.xmlroot.attrib['runID']=str(self.runID)
       
        # Insert shortDescription from batch file into result text.
        SD = batchFileTreeRoot.find("shortDescription")
        if SD != None:
            if SD.text != None:
                desc = SD.text
                if desc != None:
                    desc = string.lstrip(desc)
                    if desc != "":
                        bSD = ElementTree.SubElement(self.xmlroot,'shortDescription')
                        bSD.text = desc
    
        
        ## Load <test> Elements from Batch File. 
        #
        #  mustPass : determines if this test must pass for the batch file
        #             to PASS.
        #  mustPass = TRUE : (DEFAULT) Test must pass for the batch file to pass.
        #  mustPass = FALSE: Test is not considered in passing/failing a batch file.
        #
        mustPassDefault = "TRUE"
        statusDefault   = "PASS"

        # User can change default behaviour of mustPass by using
        # <parameter key="mustPass" value={true|false} /> 
        # anywhere in the batch file.
        for iParam in batchFileTreeRoot.findall('parameter'):
            key   = iParam.attrib.get('key',None)
            value = iParam.attrib.get('value',mustPassDefault)
            value = string.upper(value)
            if key=='mustPass' and value in ("TRUE","FALSE"):
                mustPassDefault = value

        for iTest in batchFileTreeRoot.findall('test'):
            tname= iTest.attrib.get('name','__noname__')
            if not self.batchFilePath == '':
                tname = self.batchFilePath+"/"+tname
            mustPass = iTest.attrib.get('mustPass',mustPassDefault)
            
            self.printDebug("\ttname    = %s"%tname)
            self.printDebug("\tmustPass = %s"%mustPass)

            self.testGraph.add_vertex(tname,["DNE",mustPass])
            
        ## Iterate over dependencies, parent name and child name
        ## (pname,cname) get __noname__ if left out.
        ## status defaults to PASS.
        ## Load <dep> Elements from Batch file.
        for iDep in batchFileTreeRoot.findall('dep'):
            pname = iDep.attrib.get('parent','__noname__')
            cname = iDep.attrib.get('child','__noname__')
            status= iDep.attrib.get('status',statusDefault) 
            
            if self.batchFilePath != "":
                pname = self.batchFilePath+"/"+pname
                cname = self.batchFilePath+"/"+cname

            if not self.testGraph.has_vertex(pname):
                self.testGraph.add_vertex(pname,["DNE",mustPassDefault])
            if not self.testGraph.has_vertex(cname):
                self.testGraph.add_vertex(cname,["DNE",mustPassDefault])
                
            self.testGraph.add_edge(pname,cname,[status])

        testOrder = self.testGraph.topological_sort()

        self.clearQueue()
        for iTest in testOrder:
            self.testQueue.put(iTest)
        self.printDebug("\ttestQueue.queue = %s"%(`self.testQueue.queue`))
        self.printDebug("\ttestGraph.vertex_list = %s"%self.testGraph.vertex_list())
        return 0


    # ------------------------------
    def clear(self):
        """ clear out the handler """
        self.printDebug("[->]\tbatchHandler.clear()")
        self.hasRun = False
        self.clearQueue()


    # ------------------------------
    def clearQueue(self):
        """ empty the queue """
        self.printDebug("[->]\tbatchHandler.clearQueue()")
        while not self.testQueue.empty():
            self.testQueue.get()

    
    # ------------------------------
    def query(self):
        """ query """
        self.printDebug("[->]\tbatchHandler.query()")

        if self.testQueue.empty() and self.hasRun:
            reactor.callLater(0,self.done)
        return not self.testQueue.empty()

    
    # ------------------------------
    def Execute(self):
        """ Executes tests/batches called from within a batch """

        self.printDebug("[->]\tbatchHandler.Execute()")
        self.hasRun      = True
        self.currentTask = self.testQueue.get()
        self.xmlchild    = None

        currentTaskData = self.testGraph.get_vertex_data(self.currentTask)

        self.printDebug("\tcurrentTask      = %s"%self.currentTask)
        self.printDebug("\tcurrentTask.Data = %s"%currentTaskData)
        
        # Increment the nTotal count for both batch and test files
        xmlsummary = self.xmlroot.find('summary')
        nTotal = int(xmlsummary.attrib.get('nTotal',0))
        nTotal += 1
        xmlsummary.attrib['nTotal'] = str(nTotal)

        # Check dependencies for the next test, verify that the actual and
        # expected values match up correctly.
        # if <dep status=ANY>     : dependency passes regardless of parent
        # if <dep status=MUSTRUN> : dependency passes IFF the parent 
        #			    test ran to completion.
        # if <dep>                : status= left out means child always runs
        #			    after the parent ran (or tried to run).
        # if <dep status="PASS">  : (DEFAULT) parent must run and PASS
        # if <dep status="FAIL">  : parent must run and FAIL.
        depList    = self.testGraph.get_eid_list_by_dest( self.currentTask )
        passDep    = True
        failedDeps = []
        passedDeps = []
        depElts    = []
        for idep in depList:
            source     = self.testGraph.get_edge_source(idep)
            sourceData = self.testGraph.get_vertex_data(source)
            expect     = self.testGraph.get_edge_data(idep)[0]

            self.printDebug("\tdep.source     = %s"%source)
            self.printDebug("\tdep.sourceData = %s"%sourceData)
            self.printDebug("\tdep.expect     = %s"%expect)
            
            if re.match(".*\.apt$|.*\.apb$",source):
                depElt = ElementTree.Element("dep")
                depElt.attrib['parent']=source
                depElt.attrib['expect']=expect
                depElt.attrib['actual']=sourceData[0]
                depElts.append(depElt)
                
                if expect == "ANY" or sourceData[0]==expect:
                    passedDeps.append( (source,expect,sourceData[0]) )
                    pass
                elif expect=="MUSTRUN" and sourceData[0] in ("PASS","FAIL"):
                    passedDeps.append( (source,expect,sourceData[0]) )
                    pass
                else:
                    failedDeps.append( (source,expect,sourceData[0]) )
                    passDep = False
                    
        if passDep:
            if re.match(".*\.apt$",self.currentTask):
                self.xmlchild = ElementTree.SubElement(self.xmlroot,'child')
                self.xmlchild.attrib['file']   = self.currentTask
                self.xmlchild.attrib['status'] = "UNKNOWN"
                tH = testHandler.testHandler(self.db)
                tH.setOptions(self.options)
                tH.WB = self.WB
                tH.db_runid   = self.db_runid
                tH.db_batchid = self.db_batchid
                tH.setCallback(self.getCallback())
                tH.prepare(self.currentTask)   # --< put a guard here?
                if tH.preparedOK==True:
                    # The test file was prepared successfully.
                    tH.execute()
                    element=tH.getXmlOutputTree()
                    self.xmlchild.attrib["testID"] = element.attrib["testID"]
                    for idep in depElts:
                        element.append(idep)
                else:
                    # The test file had a problem and failed to be prepared.
                    reactor.callLater(0, self.poll)  # jumpstart the poller

            elif re.match(".*\.apb$",self.currentTask):
                self.xmlchild = ElementTree.SubElement(self.xmlroot,'child')
                self.xmlchild.attrib['file']  =self.currentTask
                self.xmlchild.attrib['status']="BATCH"
                tB = batchHandler()
                tB.clear()
                tB.Initialize(self.options,self.db)
                tB.WB = self.WB
                if self.get_debug(): tB.debug_on()
                try:
                    tB.db_parent_batchid = self.db_batchid
                    tB.parentTask = self.batchFileName
                    tB.loadBatchFile(self.currentTask)
                    tB.setCallback( self.getCallback() )
                    self.xmlchild.attrib['batchID'] = str(tB.batchID)
                    tB.start()
                except:
                    reactor.callLater(0,self.poll)   # jumpstart the poller :)
                    
        # DEPENDENCY FAILED
        elif not passDep:
            if re.match(".*\.apb$",self.currentTask):
                
                #######################
                # MySQL Adding FAILDEP database
                #
                if self.options and self.options["sqldb"] and self.db.connected:
                    from db_mysql import apitestdb
                    fname = os.path.abspath(self.currentTask)
                    query = """
                        INSERT INTO `results` (`RUNID`,`PID`,`FNAME`,
                                               `STATUS`,`TYPE`,`TFINISH`,`TIMEOUT`)
                        VALUES (%d,%d,'%s','FAILDEP','BATCH',CURRENT_TIMESTAMP,0.0)
                        """ % (self.db_runid,self.db_batchid,fname)
                    self.db.execute(query)
                    db_testid = self.db.getMaxID('results')
                    query = """
                            INSERT INTO `dependencies` (`RESULTID`,`EXPECT`,`ACTUAL`,`PARENT_FILE`)
                            VALUES """
                    i = 0
                    ndeps = len(passedDeps)+len(failedDeps)
                    for dep in passedDeps:
                        query += "(%d,'%s','%s','%s')" % (db_testid,dep[1],dep[2],dep[0])
                        if i < ndeps-1:
                            query += ","
                        i+=1;
                    for dep in failedDeps:
                        query += "(%d,'%s','%s','%s')" % (db_testid,dep[1],dep[2],dep[0])
                        if i < ndeps-1:
                            query += ","
                        i+=1;
                    self.db.execute(query)
                #
                # END MySQL Entry
                #########################
                
                self.status = "DNE"
                self.xmlchild = ElementTree.SubElement(self.xmlroot,'child')
                self.xmlchild.attrib['file']   = self.currentTask
                self.xmlchild.attrib['status'] = "FAILDEP"
                element = genBaseBatchResult(self.currentTask)
                element.attrib['ID'] = ""
                element.attrib['pBatchID']  = str(self.batchID)
                element.attrib['status']    = "FAILDEP"
                element.attrib['timeStart'] = libapitest.genTimeStamp()
                element.attrib['timeStop']  = libapitest.genTimeStamp()
                summaryElt = ElementTree.SubElement(element,"summary")
                summaryElt.attrib['nFail']  = "0"
                summaryElt.attrib['nPass']  = "0"
                summaryElt.attrib['nTotal'] = "0"
                for idep in depElts:
                    element.append(idep)
                id   = self.WB.TD.B.nextID
                file = os.path.splitext(os.path.split(self.currentTask)[1])[0]
                file = string.join( \
                        self.WB.currentORoot+["t%d.%s.out"%(id,file)],os.path.sep)
                try:
                    # write results output file
                    if(self.options["transient"]==0):
                        file = os.path.normpath(file)
                        file = os.path.abspath(file)
                        ofp  = open(file,"w")
                        ofp.write(libapitest.xmlObjToString(element))
                        ofp.close()
                    else:
                        pass
                except:
                    print "[100]\tUnable to open file %s for write."%(file)
                self.WB.TD.addBatch(element)
                self.WB.TD.exitBatch()
                
            if re.match(".*\.apt$",self.currentTask):
                
                ####################
                # MySQL Adding FAILDEP to database
                #
                if self.options and self.options["sqldb"]:
                    from db_mysql import apitestdb
                    fname = os.path.abspath(self.currentTask)
                    query = """
                        INSERT INTO `results` (`RUNID`,`PID`,`FNAME`,
                                               `STATUS`,`TYPE`,`TFINISH`,`TIMEOUT`)
                        VALUES (%d,%d,'%s','FAILDEP','TEST',CURRENT_TIMESTAMP,0.0)
                        """ % (self.db_runid,self.db_batchid,fname)
                    self.db.execute(query)
                    db_testid = self.db.getMaxID('results')
                    query = """
                            INSERT INTO `dependencies` (`RESULTID`,`EXPECT`,`ACTUAL`,`PARENT_FILE`)
                            VALUES """
                    i = 0
                    ndeps = len(passedDeps)+len(failedDeps)
                    for dep in passedDeps:
                        query += "(%d,'%s','%s','%s')" % (db_testid,dep[1],dep[2],dep[0])
                        if i < ndeps-1:
                            query += ","
                        i+=1;
                    for dep in failedDeps:
                        query += "(%d,'%s','%s','%s')" % (db_testid,dep[1],dep[2],dep[0])
                        if i < ndeps-1:
                            query += ","
                        i+=1;
                    self.db.execute(query)
                #
                # END MySQL
                ####################
                
                self.status = 'DNE'
                self.xmlchild = ElementTree.SubElement(self.xmlroot,'child')
                self.xmlchild.attrib['file']   = self.currentTask
                self.xmlchild.attrib['status'] = "FAILDEP"
                self.xmlchild.attrib['ID']     = str(self.WB.TD.T.nextID)
                
                element = genBaseTestResult(self.currentTask)
                element.attrib['ID']        = str(self.WB.TD.T.nextID)
                element.attrib['pBatchID']  = str(self.batchID)
                element.attrib['status']    = "FAILDEP"
                element.attrib['timeStart'] = libapitest.genTimeStamp()
                element.attrib['timeStop']  = libapitest.genTimeStamp()

                for idep in depElts:
                    element.append(idep)

                id = self.WB.TD.T.nextID
                file = os.path.splitext(os.path.split(self.currentTask)[1])[0]
                file = string.join( \
                        self.WB.currentORoot+["t%d.%s.out"%(id,file)],os.path.sep)
                try:
                    # write results output file
                    if(self.options["transient"]==0):
                        file = os.path.normpath(file)
                        file = os.path.abspath(file)
                        ofp = open(file,"w")
                        ofp.write( libapitest.xmlObjToString(element) )
                        ofp.close()
                    else:
                        pass
                except:
                    print "[100]\tUnable to open file %s for write."%(file)
                self.WB.TD.addTest(element)

            # summary stuff for FAILDEP stuff
            xmlsummary = self.xmlroot.find('summary')
            nFail = int(xmlsummary.attrib.get('nFail',0))
            nFail += 1
            xmlsummary.attrib['nFail'] = str(nFail)

            if not self.options.subCommand or self.options.subCommand !="httpd":
                failStr = 'FAILDEP'
                failStr = libapitest.ANSIstring('red',failStr)
                message  = "%s failed dependency(s).'" % (self.currentTask)
                
#		print libapitest.logMessage(failStr,'[%s] failed dependency(s).'% \
#		                            (self.currentTask))
            
                for idep in failedDeps:
                    message += "\n%sPREREQ: '%s'\n%sExpected: %s, Actual: %s" % \
                               (38*" ",idep[0],38*" ",idep[1],idep[2])
                print libapitest.logMessage(failStr,message)
            reactor.callLater(0,self.poll)   # jumpstart the poller :)
            #self.task_done("FAILDEP")


    #--------------------
    def Finish(self, status):
        """ The test finished (called for everything within a batch) """
        if self.testGraph.has_vertex(self.currentTask):
            vData = self.testGraph.get_vertex_data(self.currentTask)
            vData[0] = status  # set the test status in testGraph
            
            xmlsummary = self.xmlroot.find('summary')
            nPass  = int(xmlsummary.attrib.get('nPass',0))
            nFail  = int(xmlsummary.attrib.get('nFail',0))
            if   status == "PASS":     nPass += 1
            elif status == "FAIL":     nFail += 1
            elif status == "TIMEDOUT": nFail += 1
            xmlsummary.attrib['nPass']  = str(nPass)
            xmlsummary.attrib['nFail']  = str(nFail)

            if self.xmlchild != None:
                self.xmlchild.attrib['status']=status
            self.xmlchild = None


    #--------------------
    def done(self):
        """ Called when the batch itself is done. """
        self.printDebug("[->]\tbatchHandler.done()")

        self.printDebug("\ttestQueue.queue = %s"%(`self.testQueue.queue`))
        self.printDebug("\ttestGraph.vertex_list = %s"%self.testGraph.vertex_list())

        # verify batch file status
        self.status = "PASS"
        for vi in self.testGraph.vertex_list():
            (viStatus,viMustPass) = self.testGraph.get_vertex_data(vi)
            viStatus   = viStatus.upper()
            viMustPass = viMustPass.upper()
            
            if viMustPass == "TRUE":
                self.printDebug("\t\t\tCHECK MUSTPASS")
                if not viStatus == "PASS":
                    self.status = "FAIL"
        
        self.xmlroot.attrib['status'] = self.status

        # print out the message to the console
        if(self.options['cmdLine']==True):
            msgStr = ""
            statusColor = "yellow"
            if   self.status == "PASS":  statusColor = "green"
            elif self.status == "FAIL":  statusColor = "red"
            statusStr = "%s"%(libapitest.ANSIstring(statusColor,self.status))
            print libapitest.logMessage(statusStr, self.batchFileName)

        self.saveResultData()
        self.WB.TD.exitBatch()
        self.stop()


    def saveResultData(self):
        # Save the output to a File if we are requested to!
        if( self.options and self.options["transient"]==0 ):
            fileName = string.join(self.WB.currentORoot,os.path.sep) 
            fileName += "/b%d."%(self.batchID)
            fileName += os.path.splitext(os.path.basename(self.batchFileName))[0]
            fileName += ".out"
            fileName = os.path.normpath(fileName)
            FP = open(fileName,"w")
            FP.write( libapitest.xmlObjToString(self.xmlroot) )
            FP.close()

        #####
        #
        # MySQL Test Code BEGIN
        #
        if self.options and self.options["sqldb"] and self.db.connected:
            from db_mysql import apitestdb
            query = """
                    UPDATE `results` SET `TFINISH`=CURRENT_TIMESTAMP,`STATUS`='%s'
                    WHERE ID=%s
                    """%(self.status,self.db_batchid)
            self.db.execute(query)
        #
        # MySQL Test Code END
        #
        ##########
        
        self.doCallback()
        self.printDebug("[<-]\tbatchHandler.done()")



# ====================================================================
# =  Test main() ...                                                 =
# ====================================================================
if __name__ == "__main__":
    """ for testing purposes... """

    jobMan = jobManager()
    jobMan.setPollDelay()
    jobMan.start()
    jobMan.debug_on()

    reactor.callLater( 5, jobMan.setPollDelay, .25)
    reactor.callLater( 8, jobMan.setPollDelay, 1.0)
    reactor.callLater(10, jobMan.stop)
    reactor.callLater(15, reactor.stop)
    reactor.run()

# EOF #
