"""
Classes that handle generation of webpages for APItest
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
# $Id: httpHandler_css.py,v 1.21 2005/06/01 00:06:38 wcmclen Exp $
#############################################################################
import re, string, os.path
from sys import exit
from os import getcwd, makedirs
from twisted.web import resource
from twisted.internet import reactor
from xml.etree import ElementTree
from xml.parsers.expat import ExpatError
import stylesheets, htmltools, libapitest, libdebug
from htmltools import genCheckBox,genHRuleTable,genSubmitButton,genSubmitTextButton
from htmltools import genResetButton,genTitlebar

# Kludge:
if not os.path.__dict__.has_key('sep'): 
    os.path.sep = '/'
    
def genPopupButton(name,label,url,width,height):
    html  = "<INPUT TYPE=\"button\" VALUE=\"%s\" NAME=\"btn%s\" "%(label,name)
    html += "onclick=\"window.open('%s','popup',"%(url)
    html += "'width=%d, height=%d, scrollbars=yes'); return false\">\n"%(width,height)
    return html

def genViewResultSrcButton(testID):
    html = genPopupButton("viewSource","View Result Source",
                          "showxml?testID=%d"%(testID),700,600);
    return html

def genShowTestButton(filename):
    html = genPopupButton("ShowTest", "View Test",
                          "showtestsummary?fileName=%s"%(filename),700,600)
    return html
   
def genShutdownButton():
    html = ""
    html += "<INPUT TYPE=\"button\" value=\"Shutdown\" name=\"btnShutdown\" "
    html += "onclick=\"window.location='shutdown'\">\n"
    return html


def str_cmp_desc(st1,st2):
    if st1<st2:   return 1
    elif st1>st2: return -1
    else:         return 0

# =======================================
def genTestResultTableFromElement(testID,element):
    html  = ""
    html += "<table id='output'>\n"
    html += "<caption>Test Information</caption>\n"
    html += "<tr><td>File Name</td>"
    html += "<td>%s</td></tr>\n"%(element.attrib.get('filename'))
    html += "<tr><td>Status</td>"
    html += "<td>%s</td></tr>\n"%(element.attrib.get('status'))
    html += "<tr><td>Start Time</td>"
    html += "<td>%s</td></tr>\n"%(element.attrib.get('timeStart'))
    html += "<tr><td>Stop Time</td>"
    html += "<td>%s</td></tr>\n"%(element.attrib.get('timeStop'))
    html += "<tr><td>MD5</td>"
    html += "<td>%s</td></tr>\n"%(element.attrib.get('md5sum'))
    
    if element.attrib.has_key('uname'):
        if element.attrib.get('uname') != 'None':
            html += "<tr><td>uname</td>"
            html += "<td>%s<td></tr>\n"%(element.attrib.get('uname'))
    if element.attrib.has_key('uid'):
        html += "<tr><td>uid</td>"
        html += "<td>%s</td></tr>\n"%(element.attrib.get('uid'))
    if element.attrib.has_key('gid'):
        html += "<tr><td>gid</td>"
        html += "<td>%s</td></tr>\n"%(element.attrib.get('gid'))
    if element.attrib.has_key('timeoutTime'):
        html += "<tr><td>Timeout</td>\n"
        html += "<td>%s (%s)</td></tr>\n"% \
                (element.attrib.get('timeoutFlag'), element.attrib.get('timeoutTime'))
    html += "</table>\n\n"

    # dependency data (if it exists)
    depElts = element.findall('dep')
    if len(depElts)>0:
        html += "<BR>\n"
        html += "<table id='output'>\n"
        html += "<caption>Dependencies</caption>\n"
        html += "<tr>\n"
        html += "\t<th>Expected</th>\n"
        html += "\t<th>Actual</th>\n"
        html += "\t<th>Prerequisite (Dependency)</th>\n"
        html += "</tr>\n"
        for idep in depElts:
            actual = idep.attrib.get('actual','actual=unknown').upper()
            expect = idep.attrib.get('expect','expect=unknown').upper()
            parent = idep.attrib.get('parent','parent=unknown')
            html += "<tr>\n"
            html += "\t<td class='%s'>%s</td>\n"%(expect.lower(), expect)
            html += "\t<td class='%s'>%s</td>\n"%(actual.lower(), actual)
            if actual==expect:
                html += "\t<td>&nbsp;%s</td>\n"%(parent)
            else:
                html += "\t<td class='failed'>&nbsp;%s</td>\n"%(parent)
            html += "</tr>\n"
        html += "</table>\n\n"

    # print output elements if they exist.
    outputElts = element.findall('output')
    if len(outputElts)>0:
        for outputElt in outputElts:
            actual = outputElt.find('actual').text
            if actual == None:
                actual = ""
            actual = actual.replace('&','&amp;');
            actual = actual.replace('<','&lt;')
            actual = actual.replace('>','&gt;')

            expect = outputElt.find('expect').text
            if expect == None:
                expect = ""
            expect = expect.replace('&','&amp;')
            expect = expect.replace('<','&lt;')
            expect = expect.replace('>','&gt;')
            
            key = outputElt.get('name','noname')
            matched = outputElt.get('matched','unknown')
            
            html += "<BR>\n<table id='output'>\n"
            html += "\t<caption>Output [%s]  matched [%s]</caption>\n"%(key,matched)
            html += "\t<tr>\n"
            html += "\t\t<th>Expected</th>\n"
            html += "\t</tr>\n\t<tr>\n"
            html += "\t\t<td valign=top width=50%%><pre>%s</pre></td>\n"%(expect)
            html += "\t</tr>\n"
            html += "<tr>\n"
            html += "\t<th>Actual</th>\n"
            html += "\t</tr>\n\t<tr>\n"
            html += "\t\t<td valign=top width=50%%><pre>%s</pre></td>\n"%(actual)
            html += "\t</tr>\n"
            html += "</table>\n\n"
    return html

##
# get_short_description(filename)
#
def get_short_description(filename):
    """ Extract the shortDescription from test / batch files. """
    maxShortDescStringLength = 60
    parsedOk = False
    ret = None
    xml = None
    try:
        xml = ElementTree.parse(filename).getroot()
        parsedOk = True
    except:
        pass
    if xml:
        desc = xml.find("shortDescription")
        if desc != None:
            desc = desc.text
            if desc != None:
                desc = string.lstrip(desc)
                if desc != "":
                    ret = desc[:maxShortDescStringLength]
    return (ret,parsedOk)


#========================================================================
# http page classes
#========================================================================
class HTTProot(resource.Resource):
    def getChild(self, name, request):
        ## print name,request, ':->-:', self.__dict__
        if name == '': return self
        return resource.Resource.getChild(self,name,request)

    def render(self, request):
        return """<html>Hello!  I am located at %r.</html>"""%(request.prepath)



#========================================================================
# shutdown the Server
#========================================================================
class wwwShutdown(resource.Resource, libdebug.debuggable):
    """ handler for shutting down the server """
    def render(self, request):
        """
        render the HTML
        """
        turnedOff = False
        doTurnOff = True
        
        if request.args.has_key('status'):
            if request.args['status'][0] == 'off':
                turnedOff = True
                doTurnOff = False
        
        html = ""
        html += "<HTML>\n"
        html += "<HEAD>\n"
        if doTurnOff:
            html += '<META HTTP-EQUIV=refresh content="5; url=/shutdown?status=off">\n'
        html += "</HEAD>\n"
        html += "<BODY>\n"
        if doTurnOff:
            html += "<H1>Shutting down APItest Server</H1>\n"
        else:
            html += "<H1>APItest is shut down.</H1>\n"
        html += "</BODY>\n"
        html += "</HTML>\n"
        if doTurnOff:
            reactor.callLater(5.5, reactor.stop)
        return html



#========================================================================
# www_process_html
#========================================================================
class www_process_html(resource.Resource, libdebug.debuggable):
    """ Handler for process webpage """
    isLeaf  = True
    options = None
    wwwDisplayResultRef  = None

    # ----------------------
    def Initialize(self, options, db=None):
        """ Initialize the wwwProcessRequest class """
        self.options = options
        self.WB.clearTestData()
        self.nocss = self.options['nocss']==1
        self.db = db

    # ----------------------
    def render(self, request):
        """
        receives the user request and passes it into the worklist for the
        executor thread.  Then redirects the users' browser to the result
        viewing page.
        """

        target_url = "running"   #  "display" is orig
        self.printDebug("[->]\twwwProcessResult.render()")
        # if we're debugging, we need to delay for a bit here
        delay = 0
        if self.options['debug']: 
            delay = 10

        # clear the work list & reset running flag
        self.WB.clear()
        self.WB.running[0]=True
        runID = self.WB.TD.newRun()
        
        ##########
        #
        # MySQL Test Code HERE
        #
        if self.options and self.options.parent["sqldb"] and self.db.connected:
            from db_mysql import apitestdb
            db_runid = self.db.create_new_run()
        #
        # END MySQL
        #
        ##########
        
        
        fileList = []
        # Build list of files to execute.
        for k in request.args.keys():
            testFileRE = re.compile('.*(\.apt)$')
            if testFileRE.match(request.args[k][0]):
                self.WB.workList.put(request.args[k][0])
                
        for k in request.args.keys():
            testFileRE = re.compile('.*(\.apb)$')
            if testFileRE.match(request.args[k][0]):
                self.WB.workList.put(request.args[k][0])
                
        # Generate / Create output directories
        self.WB.currentORoot = [ self.options["oroot"] ]
        if( self.options["transient"]==0):
            if not libapitest.makeOutputDir(self.WB, runID):
                self.options["transient"] = 1
                if self.options.has_key("subOptions"):
                    self.options.subOptions["transient"] = 1
                    
        # Generate the HTML
        html  = "<html>\n"
        html += "<head>\n"
        html += "\t<title>APItest - Process</title>\n"
        html += '\t<meta http-equiv=refresh content="%d; url=%s"/>\n' % \
                    (delay,target_url) 
        header = stylesheets.html_css_header(self.nocss)
        html += "%s"%(header)
        html += """<script language="JavaScript1.2">
        <!--
        function refresh() { window.location.reload(false); }
        -->
        </script>
        """
        html += "</head>\n\n"
        html += "<body>\n"
        html += "<div id='wrapper'>\n"
        
        html += "<div id='header'>\n"
        html += "<h1>APItest</h1>\n\n"
        html += "<ul id=\"nav\">\n"
        html += "\t<li><a href='index.html'>Main</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='running' class='here'>Running</a>\n"
        html += "\t<ul>\n"
        html += "\t\t<li><a href='javascript:history.back()'>Back</a></li>\n"
        html += "\t\t<li><a href='javascript:refresh()'>Refresh</a></li>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='session'>Session</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='saved'>Saved</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='admin'>Admin</a>\n"
        html += "\t</ul>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='about'>About</a>\n"
        html += "\t</li>\n"
        html += "</ul>\n"
        html += "</div>\n\n"
        
        html += "<div id='main'>\n"
        html += "<a href='%s'>Click to continue</a>\n"%(target_url)
        html += "</div>\n\n"
        
        html += "</div>\n"
        html += "</body>\n"
        html += "</html>\n"
        self.printDebug("[<-]\twwwProcessRequest.render()")
        return html



# ====================================================================
# wwwShowXML
# showxml show result source
# ====================================================================
class wwwShowXML(resource.Resource,libdebug.debuggable):
    """ Displays the XML source of the result entry. """
    isLeaf = True
    options = None
    
    # ----------------------
    def Initialize(self,options):
        self.options = options
        self.turquoise = htmltools.genColor('turquoise')

    # ----------------------
    def render(self,request):
        self.printDebug("[->]\twwwShowXML.render()")
        html = "<HTML>\n<HEAD>\n"+\
               "</HEAD>\n<BODY>\n"
        html += genTitlebar("Result Source")
        html += "<HR COLOR=BLACK>\n"
        if request.args.has_key('testID'):
            testID = int(request.args['testID'][0])
            testXML = self.WB.TD.getTest(testID)
            xmlText = libapitest.xmlObjToString(testXML)
            xmlText = xmlText.replace('<','&lt;')
            xmlText = xmlText.replace('>','&gt;')
            html += "<PRE>%s\n</PRE>\n"%(xmlText)
        html += "<HR COLOR=BLACK>\n"
        html += "<A HREF='javascript:self.close()'>Close</A>\n"
        html+= "</BODY>\n</HTML>\n"
        return html



# ====================================================================
# wwwShowTestFileXML
# ====================================================================
class wwwShowTestFileXML(resource.Resource, libdebug.debuggable):
    """ Displays the XML source of a test file in a popup """
    # -------------------
    def Initialize(self,options):
        self.options = options

    def render(self,request):
        html = "<HTML>\n<HEAD>\n"
        html +="</HEAD>\n<BODY>\n"
        html += genTitlebar("Test Source")
        html += "<A HREF='javascript:history.back()'>Back</A>&nbsp;\n"
        html += "<A HREF='javascript:self.close()'>Close</A>\n"	
        html += "<HR COLOR=BLACK>\n"
        if request.args.has_key('fileName'):
            fileName = request.args['fileName'][0]
            html += "<H2>%s</H2>"%(fileName)
            if os.path.exists(fileName):
                try:
                    xmlTxt = libapitest.xmlObjToString( \
                        ElementTree.parse(fileName).getroot() )
                    xmlTxt = xmlTxt.replace('&','&amp;')
                    xmlTxt = xmlTxt.replace('<','&lt;')
                    xmlTxt = xmlTxt.replace('>','&gt;')
                    html  += "<PRE>\n%s\n</PRE>\n"%(xmlTxt)
                except ExpatError,e:
                    html += "<FONT COLOR=RED><B>Error parsing XML file</B></FONT><BR>\n"
                    html += "<PRE>%s%s</PRE>\n"%(5*"&nbsp;",e)
            else:
                html += "<FONT COLOR=RED><B>File does not exist!</B></FONT><BR>\n"
                html += "Could not find file [%s]<BR>\n"%(fileName)
        html += "<HR COLOR=BLACK>\n"
        html += "<A HREF='javascript:history.back()'>Back</A>&nbsp;\n"
        html += "<A HREF='javascript:self.close()'>Close</A>\n"
        html +="</BODY></HTML>\n"
        return html



# ====================================================================
# wwwShowTestResult
# ====================================================================
class wwwShowTestResult(resource.Resource, libdebug.debuggable):
    """ """
    def Initialize(self, options):
        self.options = options

    def render(self,request):
        html = ""
        return html



# ====================================================================
# wwwShowTestFileSummary
# ====================================================================
class wwwShowTestFileSummary(resource.Resource, libdebug.debuggable):
    """
    Display the summary of a test file.  If there is a problem, then
    display an appropriate message.
    """
    def Initialize(self,options):
        self.options = options

    def displayTestFileSummary(self, fileName, xmlroot):
        # get info
        element = xmlroot.find('info')
        info = None
        if element != None and element.text != None:
            info = element.text
            info = string.lstrip(info)
            info = string.rstrip(info)
            if info[0]=='\n': info = info[1:]
            info = string.replace(info,'\n','<BR>')
                    
        # get shortDescription
        element = xmlroot.find('shortDescription')
        shortDesc = None
        if element != None:
            shortDesc = element.text
            shortDesc = string.rstrip(string.lstrip(shortDesc))
            
        # get test type
        element = xmlroot.find('test')
        type = None
        if element != None:
            type = element.attrib.get('type','UNKNOWN')
            
        (path,file) = os.path.split(os.path.abspath(fileName))
        
        tblRowSep = "<TR><TD COLSPAN=2><HR COLOR=blue></TD></TR>\n"
        
        html  = genTitlebar("Test Summary")
        html += "<A HREF='javascript:self.close()'>Close</A>\n"
        html += "<HR COLOR=BLACK>\n"
        html += "<TABLE border=0>"
        html += "<TR>\n"
        html += "  <TD WIDTH=80>PATH</TD>\n"
        html += "  <TD>&nbsp;%s</TD>\n"%(path+os.path.sep)
        html += "</TR>\n"
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD>FILE</TD>\n"
        html += "  <TD>&nbsp;%s</TD>\n"%(file)
        html += "</TR>\n"
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD>DESC</TD>\n"
        html += "  <TD>%s</TD>\n"%(shortDesc)
        html += "</TR>\n"
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD valign=top>INFO</TD>\n"
        html += "  <TD>%s</TD>\n"%(info)
        html += "</TR>\n"
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD>TYPE</TD>\n"
        html += "  <TD>%s</TD>\n"%(type)
        html += "</TR>\n"
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD>SOURCE</TD>\n"
        html += "  <TD><A HREF='showtestxml?fileName=%s'>View Source</A></TD>\n"%(fileName)
        html += "</TR>\n"
        html += "</TABLE>"
        return html
        
    def displayBatchFileSummary(self, fileName, xmlroot):
        # get info
        element = xmlroot.find('info')
        info = None
        if element != None and element.text != None:
            info = element.text
            info = string.lstrip(info)
            info = string.rstrip(info)
            if info[0]=='\n': info = info[1:]
            info = string.replace(info,'\n','<BR>')
                    
        # get shortDescription
        element = xmlroot.find('shortDescription')
        shortDesc = None
        if element != None:
            shortDesc = element.text
            shortDesc = string.rstrip(string.lstrip(shortDesc))
            
        (path,file) = os.path.split(os.path.abspath(fileName))
        
        tblRowSep = "<TR><TD COLSPAN=2><HR COLOR=blue></TD></TR>\n"
        html  = genTitlebar("Batch Summary")
        html += "<A HREF='javascript:self.close()'>Close</A>\n"	
        html += "<HR COLOR=BLACK>\n"
        html += "<TABLE border=0>"
        html += "<TR>\n"
        html += "  <TD WIDTH=80>PATH</TD>\n"
        html += "  <TD>&nbsp;%s</TD>\n"%(path+os.path.sep)
        html += "</TR>\n"
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD>FILE</TD>\n"
        html += "  <TD>&nbsp;%s</TD>\n"%(file)
        html += "</TR>\n"
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD>DESC</TD>\n"
        html += "  <TD>%s</TD>\n"%(shortDesc)
        html += "</TR>\n"
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD valign=top>INFO</TD>\n"
        html += "  <TD>%s</TD>\n"%(info)
        html += "</TR>\n"

        for i in xmlroot.findall('parameter'):
            html += tblRowSep
            html += "<TR>\n"
            html += "  <TD VALIGN=TOP>PARAMETER</TD>\n"
            html += "  <TD>KEY='%s'<BR>VALUE='%s'</TD>\n"% \
                    (i.attrib.get('key'),i.attrib.get('value'))
            html += "</TR>\n"
            
        tests = xmlroot.findall('test')
        if tests != None and len(tests)>0:
            html += tblRowSep
        for i in tests:
            tname = None
            for k in i.attrib.keys():
                if string.lower(k) == 'name': 
                    tname=i.attrib[k]
            html += "<TR>\n"
            html += "  <TD>TEST</TD>\n"
            html += "  <TD>%s</TD>\n"%(tname)
            html += "</TR>\n"
        deps = xmlroot.findall('dep')
        for i in deps:
            pName = i.attrib.get('parent')
            cName = i.attrib.get('child')
            status= i.attrib.get('status','PASS')
            html += "<TR>\n"
            html += "  <TD VALIGN=TOP>DEP</TD>\n"
            html += "  <TD>parent = %s<BR>child = %s<BR>status = %s</TD>\n"% \
                 (pName,cName,status)
            html += "</TR>\n"
            
        html += tblRowSep
        html += "<TR>\n"
        html += "  <TD>SOURCE</TD>\n"
        html += "  <TD><A HREF='showtestxml?fileName=%s'>View Source</A></TD>\n"%(fileName)
        html += "</TR>\n"
        html += "</TABLE>\n"
        return html

    def render(self,request):
        html  = "<HTML>\n<HEAD>\n</HEAD>\n<BODY>\n"
        if request.args.has_key('fileName'):
            fileName = request.args['fileName'][0]
            if os.path.exists(fileName):
                try:
                    xmlroot = ElementTree.parse(fileName).getroot()
                    
                    if xmlroot.tag == "testDef":
                        html += self.displayTestFileSummary(fileName,xmlroot)
                    elif xmlroot.tag=="testBatch":
                        html += self.displayBatchFileSummary(fileName,xmlroot)
                        
                except ExpatError,e:
                    html += "<a href='javascript:self.close()'>Close</a><BR>\n"
                    html += "<FONT COLOR=RED><B>Error parsing XML file</B></FONT><BR>\n"
                    html += "<PRE>%s%s</PRE>\n"%(5*"&nbsp;",e)
                    html += "<HR COLOR=black>\n"
                    html += "<PRE>"
                    FP = open(fileName,'r')
                    lineno = 1
                    for line in FP:
                        line = line.replace('&','&amp;')
                        line = line.replace('<','&lt;')
                        html += "%8d %s"%(lineno,line)
                        if lineno == e.lineno:
                            html += "<FONT COLOR=RED>"
                            html += "=ERROR=="
                            for i in range(len(line)):
                                if i<(e.offset-1):
                                    if line[i] == "\t":
                                        html += 8*"="
                                    else:
                                        html += "="
                            html += "^</FONT>\n"
                        lineno += 1
                    html += "</PRE>\n"
                    FP.close()
                    
            else:
                html += "<FONT COLOR=RED><B>File does not exist!</B></FONT><BR>\n"
                html += "Could not find file [%s]<BR>\n"%(fileName)
                
        html += "<HR COLOR=BLACK>\n"
        html += "<A HREF='javascript:self.close()'>Close</A>\n"
        html += "</BODY>\n</HTML>\n"
        return html



#========================================================================
# www_offlineBrowser class
#========================================================================
#
# ###### ###### ###### ##     ## ##  ## ######
# ##  ## ##     ##     ##     ## ### ## ##
# ##  ## ####   ####   ##     ## ## ### ####
# ##  ## ##     ##     ##     ## ##  ## ##
# ###### ##     ##     ###### ## ##  ## ######
#
#========================================================================
class www_saved_html(resource.Resource,libdebug.debuggable):

    def Initialize(self,options):
        self.options = options
        self.turquoise = htmltools.genColor('turquoise')
        self.reset()
        self.nocss = self.options['nocss']==1

    def reset(self):
        pass

    def getRunlistDirlist(self):
        """ Return a dictionary of test run directories from within oroot """
        self.RLD = {}
        oroot = self.options['oroot']
        
        try:
            rl_raw = os.listdir(oroot)
        except:
            print "error in getRunlistDirlist(), could not list %s"%(oroot)
            return self.RLD
        
        for i in rl_raw:
            if re.match("run\.(\d){4}-\d\d-\d\d\.(\d\d-){2}\d\d",i):
                fp = os.path.normpath( os.path.abspath( oroot+os.path.sep+i))
                if os.path.exists(fp) and os.path.isdir(fp):
                    self.RLD[fp] = {}
        self.RLK = self.RLD.keys()
        self.RLK.sort( str_cmp_desc )
        return self.RLD


    def getTestsFromRun(self,rldir):
        """ """
        tl = {}
        tl_raw = os.listdir(rldir)
        for i in tl_raw:
            if re.match("^t\d+\..*\.out",i):
                key = re.search("^t\d+",i).group()
                tl[key] = i
            elif re.match("^b\d+\..*\.out",i):
                key = re.search("^b\d+",i).group()
                tl[key]=i
        return tl


    # ---------------------
    def viewList(self):
        self.getRunlistDirlist()
        basePath = os.path.dirname( os.path.commonprefix( self.RLD.keys() ) )
        html  = ""
        html += "<table id='listing'\n"
        html += "<tr>\n"
        html += "  <th>Date</th>"+\
                "  <th>Time</th>"+\
                "  <th>Link</th>\n"
        html += "</tr>\n"
        
        keyList = self.RLD.keys()
        keyList.sort(str_cmp_desc)
        for k in keyList:
            p1 = k[ len(basePath)+1: ]
            sz = len(self.RLD[k])
            html += "<tr>\n" +\
                    "  <td class='date'>%s</td>\n"%(p1[4:14]) +\
                    "  <td class='time'>%s</td>\n"%(p1[15:23].replace("-",":")) +\
                    "  <td>&nbsp;"+\
                    "<a href=\"saved?viewRun=%s&focus=root\">Details</a>"%(p1)+\
                    "</td>\n"+\
                    "</tr>\n" 
        html += "</table>\n"
        return html


    # ---------------------
    def viewRun(self,arg,focus=None):
        """ """
        fileListXML = {}
        theRun = arg
        oroot = self.options["oroot"]
        opath = os.path.normpath(os.path.abspath(oroot+os.path.sep+str(theRun)))
        fileList = self.getTestsFromRun( opath )
        fileListKeys = fileList.keys()
        fileListKeys.sort()
        self.getRunlistDirlist()
        html  = ""
        for i in fileListKeys:
            ifile = opath+os.path.sep+fileList[i]
            try:
                xml = ElementTree.parse(ifile).getroot()
            except ExpatError,e:
                print "Error parsing %s in www_offlineBroser.viewRun()"%(ifile)
                print "\tmsg:",e
            if xml.attrib.get("pBatchID",None)==focus:
                fileListXML[i] = xml
            elif "b"+str(xml.attrib.get("pBatchID",None))==focus:
                fileListXML[i] = xml
        del fileListKeys
        fileListKeys = fileListXML.keys()
        fileListKeys.sort()
        
        html += "<table id='results'>\n"
        html += "<tr>\n"
        html += "\t<caption>%s</td>\n"%(theRun)
        html += "</tr>\n"
        html += "<tr class='header'>\n"
        html += "\t<th class='status'>Status</th>\n"
        html += "\t<th class='type' colspan=3>Batch</th>\n"
        html += "\t<th class='directory'>Test Path</th>\n"
        html += "\t<th>Test File</th>\n"
        html += "</tr>\n"
        for i in fileListKeys:
            status   = fileListXML[i].attrib.get("status",None)
            status   = status.lower()
            filename = fileListXML[i].attrib.get("filename",None)
            (path,file) = os.path.split(filename)
            
            # Get shortDescription from the results
            desc = fileListXML[i].find("shortDescription")
            if desc != None:
                desc = string.lstrip(desc.text)
                desc = desc[:60]
            if desc == None or desc == "":
                desc = file	    
                
            fgColor = htmltools.genColor(status)
            bgColor = htmltools.genColor(status+"BG")
            if fileListXML[i].tag=="testResult":
                html += "<tr class='test'>\n"
                html += "\t<td class='%s'>%s</td>\n"%(status,status.upper())
                html += "\t<td colspan=3>&nbsp;</td>\n"
                html += "\t<td>&nbsp;%s</td>\n"%(path)
                html += "\t<td>&nbsp;"+\
                        "<a HREF=\"saved?viewRun=%s&focus=%s\">%s</a>\n"%(arg,i,desc) +\
                        "</td>\n"
            elif fileListXML[i].tag=="batchResult":
                html += "<tr class='batch'>\n"
                html += "  <td class='%s'>%s</td>\n"%(status,status.upper())
                (nP,nF) = self.r_sum_batch(opath,fileList,i)
                nP = int(nP)
                nF = int(nF)
                nT = nP+nF
                html += "\t<td class='bTotal'>%d</td>\n"%(nT)
                html += "\t<td class='bPass'>%d</td>\n"%(nP)
                html += "\t<td class='bFail'>%d</td>\n"%(nF)
                html += "\t<td>&nbsp;%s</td>\n"%(path)
                html += "\t<td>&nbsp;"+\
                        "<a href=\"saved?viewRun=%s&focus=%s\">%s</a></td>\n"%(arg,i,desc)
            html += "</tr>\n"
        html += "</table>\n\n"
        return html


    # ------------------
    def r_sum_batch(self,opath,fileList,k):
        nP = 0
        nF = 0
        xml = ElementTree.parse(opath+os.path.sep+fileList[k]).getroot()
        xmlSummary = xml.find('summary')
        nP = int(xmlSummary.attrib.get("nPass","0"))
        nF = int(xmlSummary.attrib.get("nFail","0"))
        for i in xml.findall("child"):
            bID = i.attrib.get("batchID",None)
            if bID != None:
                k = "b"+bID
                (tP,tF)=self.r_sum_batch(opath,fileList,k)
                nP += tP
                nF += tF
        return (nP,nF)
 
    
    # ------------------
    def viewBatch(self,arg,focus=None):
        """ Display the offline results for a specific batch file """
        html      = ""
        oroot     = self.options["oroot"]
        opath     = os.path.normpath(os.path.abspath(oroot+os.path.sep+str(arg)))
        fileList  = self.getTestsFromRun( opath )
        bFile     = opath+os.path.sep+fileList[focus]
        xml       = ElementTree.parse(bFile).getroot()
        bStatus   = xml.attrib.get('status','UNKNOWN')
        bStatus   = bStatus.lower()
        testList  = {}
        batchList = {}
        for i in xml.findall("child"):
            file  = i.attrib.get("file","")
            (p,f) = os.path.split(file)
            
            # get the short description out of the file
            (desc,descOk) = get_short_description(file)
            if descOk == False:
                desc = f
                
            if i.attrib.has_key("testID"):
                s = i.attrib.get("status","s")
                testList[ i.attrib.get("testID") ] = [p,f,s,desc]
            elif i.attrib.has_key("batchID"):
                bID = i.attrib.get("batchID","")
                s   = i.attrib.get("status","s")
                (nP,nF) = self.r_sum_batch(opath,fileList,"b"+bID)
                batchList[ i.attrib.get("batchID") ] = [p,f,nP,nF,s,desc]
            elif i.attrib.has_key("status") and i.attrib.has_key("ID"):
                id = i.attrib.get("ID","-99")
                s  = i.attrib.get("status","s")
                testList[ id ] = [p,f,s,desc]
                
        bgColor = htmltools.genColor(bStatus+"BG")
        fgColor = htmltools.genColor(bStatus)
        html += "<table id='results'>\n"
        html += "<tr>\n"
        html += "  <caption>%s</caption>\n"%(xml.attrib.get("filename",None))
        html += "</tr>\n"
        
        html += "<tr class='%s'>\n"%(bStatus)
        html += "\t<td colspan=6>%s</td>\n"%(bStatus.upper())
        html += "</tr>\n"
        
        html += "<tr class='header'>\n"
        html += "  <th colspan=1 class='status'>Status</th>\n"
        html += "  <th colspan=3 class='type'>Batch</th>\n"
        html += "  <th colspan=1 class='directory'>Path</th>\n"
        html += "  <th colspan=1>Test File</th>\n"
        html += "</tr>\n"
        batchListKeys = batchList.keys()
        batchListKeys.sort()
        for i in batchListKeys:
            nPass  = batchList[i][2]
            nFail  = batchList[i][3]
            nTotal = nPass+nFail
            status = batchList[i][4]
            desc   = batchList[i][5]
            status = status.lower()
            html += "<tr class='batch'>\n"
            html += "  <td class='%s'>%s</td>\n"%(status,status.upper())
            html += "  <td class='bTotal'>%s</td>\n"%(nTotal)
            html += "  <td class='bPass'>%s</td>\n"%(nPass)
            html += "  <td class='bFail'>%s</td>\n"%(nFail)
            html += "  <td>&nbsp;%s</td>\n"%(batchList[i][0])
            html += "  <td>&nbsp;<a HREF=\"saved?viewRun=%s&focus=%s\">%s</a></td>\n"% \
                       (arg,"b"+i,desc)
            html += "</tr>\n"
        testListKeys = testList.keys()
        testListKeys.sort()
        for i in testListKeys:
            status  = testList[i][2]
            status  = status.lower()
            desc    = testList[i][3]
            thePath = testList[i][0]
            html += "<tr class='test'>\n"
            html += "  <td class='%s'>%s</td>\n"%(status,status.upper())
            html += "  <td colspan=3>&nbsp;</td>\n"
            html += "  <td>&nbsp;%s</td>\n"%(thePath)
            html += "  <td>&nbsp;<A HREF=\"saved?viewRun=%s&focus=%s\">%s</a></td>\n"% \
                       (arg,"t"+i,desc)
            html += "</tr>\n"
        html += "</table>\n"
        return html


    # ----------------
    def viewTest(self,arg,focus=None):
        html = ""
        oroot = self.options["oroot"]
        opath = os.path.normpath(os.path.abspath(oroot+os.path.sep+str(arg)))
        fileList = self.getTestsFromRun( opath )
        if focus in fileList:
            fileName = fileList[focus]
            xml = ElementTree.parse(opath+os.path.sep+fileName).getroot()
            html += genTestResultTableFromElement(0,xml)
        else:
            pass
        return html

    # offline.render
    def render(self,request):
        self.printDebug("[**]\twww_offlineBrowser.render()")
        html  = "<html lang=\"en\">\n"
        html += "<head>\n"
        html += "<title>APItest - Saved</title>\n"
        header = stylesheets.html_css_header(self.nocss)
        html += "%s"%(header)
        html += """<script language="JavaScript1.2">
        <!--
        function refresh() { window.location.reload(false); }
        -->
        </script>
        """
        html += "</head>\n\n"
        
        # BODY
        html += "<body>\n"
        html += "<div id='wrapper'>\n"
        html += "<div id='header'>\n"
        html += "<h1>APItest</h1>\n"
        html += "<ul id=\"nav\">\n"
        html += "\t<li><a href='index.html'>Main</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='running'>Running</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='session'>Session</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='saved' class='here'>Saved</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='admin'>Admin</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='about'>About</a>\n"
        html += "\t<ul>\n"
        html += "\t\t<li><a href='javascript:history.back()'>Back</a></li>\n"
        html += "\t\t<li><a href='javascript:refresh()'>Refresh</a></li>\n"
        html += "\t</ul>\n"
        html += "\t</li>\n"
        html += "</ul>\n"
        html += "</div>\n\n"	
        
        # MAIN
        html += "<div id='main'>\n"
        if request.args.has_key("viewRun") and request.args.has_key("focus"):
            run_arg = request.args["viewRun"][0]
            foc_arg = request.args["focus"][0]
            if foc_arg == "root":
                html += self.viewRun(run_arg)
            elif foc_arg[0] == "b":
                html += self.viewBatch(run_arg,foc_arg)
            elif foc_arg[0] == "t":
                html += self.viewTest(run_arg,foc_arg)
        else:
            html += self.viewList()
        
        html += "</div>\n\n"
        
        # END
        html += "</div>\n"
        html += "</body>\n"
        html += "</html>\n"
        return html


#========================================================================
# www_main_html class
#========================================================================
class www_main_html(resource.Resource,libdebug.debuggable):
    """ Handler for rendering the index.html page """
    fileHash = {}
    options = None

    ##
    # www_main_html.Initialize()
    #
    def Initialize(self,options):
        self.printDebug("[->]\twww_main_html.Initialize()")
        self.options = options
        self.reset()
        self.nocss = self.options['nocss']==1

    ##
    # www_main_html.reset()
    #
    def reset(self):
        self.printDebug("[  ]\twww_main_html.reset()")
        self.fileHash.clear()
        self.fileHash = {}

    ##
    # www_main_html.f_detectFiles()
    #
    def f_detectFiles(self,arg,dirPath,nameList):
        self.printDebug("[  ]\twww_main_html.f_detectFiles()")
        relPath = dirPath[len(getcwd())+1:]
        for file in nameList:
            fullFile = dirPath +"/"+file
            if os.path.isfile(fullFile):
                if re.match(".*\.((apt)|(apb))$",file):	        
                    if not arg.has_key(dirPath):
                        arg[dirPath]=[]
                    arg[dirPath].append(file)

    ##
    # www_main_html.scan()
    #
    def scan(self):
        self.printDebug("[->]\twww_main_html.scan()")
        if self.options.has_key('iroot'): 
            os.path.walk(self.options['iroot'],self.f_detectFiles,self.fileHash)
        else:
            print "ERROR! 'iroot' not defined in self.options.subOptions\n" \
                  "\tIn file httptools.py :: scan()"
            exit(1)
            os.path.walk('./',self.f_detectFiles,self.fileHash)
        self.printDebug("[<-]\twww_main_html.scan()")
        return self.fileHash

    ##
    # www_main_html.genJScript()
    #
    def genJScript(self):
        self.printDebug("[  ]\twww_main_html.genJScript()")
        self.jscript = "<script language=JavaScript>\n"
        i = 1
        js1 = ""
        js2 = ""
        js3 = "function chkAll() {\n"
        js4 = "function unchkAll() {\n"
        dirList = self.fileHash.keys()
        dirList.sort()
        for dir in dirList:
            j = 1
            js1  = "function chkDir%s() {\n"%(i)
            js1 += " document.dir.chkbox%d.checked=true;\n"%(i)
            js2  = "function unchkDir%s() {\n"%(i)
            js2 += " document.dir.chkbox%d.checked=false;\n"%(i)
            js3 += " chkDir%s();\n"%(i)
            js4 += " unchkDir%s();\n"%(i)
            for test in self.fileHash[dir]:
                js1 += " document.dir.chkbox%d_%d.checked=true;\n"%(i,j)
                js2 += " document.dir.chkbox%d_%d.checked=false;\n"%(i,j)
                j += 1
            i += 1
            js1 += "};\n"
            js2 += "};\n"
            self.jscript += js1+js2
        js3 += "};\n"
        js4 += "};\n"
        self.jscript += js3+js4;
        self.jscript += "</script>\n"
        return self.jscript


    ##
    # www_main_html.genHTML()
    #
    def genHTML(self):
        html  = "<html lang=\"en\">\n"
        html += "<head>\n"
        html += "<title>APItest - Main</title>\n"
        header = stylesheets.html_css_header(self.nocss)
        html += "%s"%(header)
        html += """<script language="JavaScript1.2">
        <!--
        function refresh() { window.location.reload(false); }
        -->
        </script>
        """
        html += "</head>\n"
        
        html += self.genJScript()
        
        html += "<script language='JavaScript' type='text/javascript'>\n"
        html += "function f_submit( type )\n"
        html += "{\n"
        html += "\tdocument.supportform.supporttype.value = type;\n"
        html += "\tdocument.supportform.submit();\n"
        html += "}\n"
        html += "</script>\n"
        
        html += "<body>\n"
        html += "<div id=\"wrapper\">\n"
        
        # HEADER
        html += "<div id=\"header\">\n"
        html += "<h1>APItest</h1>\n\n"
        html += "<FORM NAME='dir' METHOD=POST "
        html += "ACTION='http://%s:%s/process'>\n"% \
                (self.options['host'],self.options['port'])
        html += "<ul id=\"nav\">\n"
        html += "\t<li><a href='index.html' class='here'>Main</a>\n"
        html += "\t<ul>\n"
        html += "\t\t<div id='subbutton'>\n"
        html += "\t\t\t<li><span>\n"
        html += "\t\t\t\t<input type='submit' name='btnExecute' value='Submit'></input>\n"
        html += "\t\t\t\t<input type='reset'  name='btnReset' value='Reset'></input>\n"
        html += "\t\t\t</span></li>\n"
        html += "\t\t\t\t<li><a href='javascript:refresh()'>Refresh</a></li>\n"
        html += "\t\t</div>\n"
        html += "\t</ul>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='running'>Running</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='session'>Session</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='saved'>Saved</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='admin'>Admin</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='about'>About</a>\n"
        html += "\t</li>\n"
        html += "</ul>\n"
        html += "</div>\n\n"
        
        # MAIN BODY
        html += "<div id=\"main\">\n"
        html += "<table id='results'>\n"
        html += "<tr class='select_all'>\n"
        html += "\t<td colspan=4>"
        opts = 'onClick="if(this.checked){chkAll();} else {unchkAll();}"'
        html += genCheckBox('ex_all','all',opts)
        html += "Select All</tr>\n"
        html += "</tr>\n"
        i=1
        dirList = self.fileHash.keys()
        dirList.sort()
        for dir in dirList:
            # build up 'opts' field for checkbox
            opts = 'onClick="if(this.checked){chkDir%d();} else{unchkDir%d();}"'%(i,i)
            html += "\n<!-- ================================================ -->\n"
            html += "<tr class='directory'>\n\t<td colspan=4>\n"
            html += genCheckBox('chkbox%s'%(i),dir,opts)
            html += "&nbsp;%s</td>\n"%(dir)
            html += "</tr>\n"
            j=1
            for file in self.fileHash[dir]:
                opts = 'onClick="if(!this.checked){document.dir.chkbox%d.checked=false;'%(i)
                opts += 'document.dir.ex_all.checked=false;}"'
                (base,ext) = os.path.splitext(file)
                absFile = os.path.normpath(dir+"/"+file)
                parsedOk  = False
                shortName = ""
                
                if ext == ".apt" or ext==".apb":
                    (shortName,parsedOk) = get_short_description(absFile)
                    
                # Display a TEST file
                if ext == ".apt":
                    html += "\n<!-- ======================================= -->\n"
                    if parsedOk:
                        html += "<tr class='test'>\n"
                    else:
                        html += "<tr class='xmlerror'>\n"
                    html += "\t<td class='box' width=40>"
                    if shortName != None:
                        name = shortName
                    else:
                        name = file
                    if parsedOk == False:
                        name += " <FONT COLOR=%s>[FILE DID NOT PARSE]</FONT>"%("#ee4444")
                    html += genCheckBox('chkbox%d_%d'%(i,j),absFile,opts)
                    html += "\t</td>\n"
                    html += "\t<td class='type'>TEST</td>\n"
                    html += "\t<td>&nbsp;%s</td>\n"%(name)
                elif ext == ".apb":
                    html += "\n<!-- ======================================= -->\n"
                    if shortName != None:
                        name = shortName
                    else:
                        name = file
                        
                    if parsedOk == True:
                        html += "<tr class='batch'>\n"
                    elif parsedOk == False:
                        html += "<tr class='xmlerror'>\n"
                        name += " <FONT COLOR=%s>[FILE DID NOT PARSE]</FONT>"%("#ee4444")
                    html +="\t<td class='box' width=40>\n"
                    html += genCheckBox('chkbox%d_%d'%(i,j),absFile,opts)
                    html += "\t</td>\n"
                    html += "\t<td class='type'>BATCH</td>\n"
                    html += "\t<td>&nbsp;%s</td>\n"%(name)
                html += "\t<td class='button'>"
                html += genShowTestButton(absFile)
                html += "\t</td>\n"
                html += "</tr>\n"
                j+=1
            i+=1
        html += "</table>\n"
        html += "</form>\n"
        html += "</div>\n\n"
        
        # FOOTER
        #html += "<div id=\"footer\">\n"
        #html += "this is the footer<BR>isn't it cool!\n"
        #html += "</div>\n"
        
        html += "</div>\n"
        html += "</body>\n"
        html += "</html>\n"
        return html


    ##
    # www_main_html.render()
    #
    def render(self,request):
        self.printDebug("[**]\twww_main_html.render()")
        self.reset()
        self.scan()
        html = self.genHTML()
        return html


# ====================================================================
# www_about_html
# ====================================================================
class www_about_html(resource.Resource, libdebug.debuggable):
    """ Menu Style Sheet """
    # -------------------
    def Initialize(self,options):
        self.options = options
        self.nocss = self.options['nocss']==1

    def render(self,request):
        html  = "<html lang=\"en\">\n"
        html += "<head>\n"
        html += "<title>APItest - About</title>\n"
        header = stylesheets.html_css_header(self.nocss) 
        html += "%s"%(header)
        html += """<script language="JavaScript1.2">
        <!--
        function refresh() { window.location.reload(false); }
        -->
        </script>
        """
        html += "</head>\n"
        
        # BODY :: TAB BAR
        html += "<body>\n"
        html += "<div id='wrapper'>\n"
        
        html += "<div id='header'>\n"
        html += "<h1>APItest</h1>\n\n"
        html += "<ul id=\"nav\">\n"
        html += "\t<li><a href='index.html'>Main</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='running'>Running</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='session'>Session</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='saved'>Saved</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='admin'>Admin</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='about' class='here'>About</a>\n"
        html += "\t<ul>\n"
        html += "\t\t<li><a href='javascript:history.back()'>Back</a></li>\n"
        html += "\t\t<li><a href='javascript:refresh()'>Refresh</a></li>\n"
        html += "\t</ul>\n"
        html += "\t</li>\n"
        html += "</ul>\n"
        html += "</div>\n\n"

        html += "<div id='main'>\n"
        html += "<h3>APItest version</h3>\n"
        html += "<div id='nest'>\n"
        html += "1.0\n"
        html += "</div>\n"
        html += "<h3>Date</h3>\n"
        html += "<div id='nest'>\n2005-25-03\n</div>\n"
        html += "<h3>Contact</h3>\n"
        html += "<div id='nest'>"
        html += "<a href='mailto:wcmclen@sandia.gov'>e-mail author</a></div>\n"
        html += """
<h3>Open Source License</h3>
<div id='nest'>
This Cplant(TM) source code is the property of Sandia National Laboratories.<BR>
<BR>
This Cplant(TM) source code is copyrighted by Sandia National
Laboratories.<BR>
<BR>
The redistribution of this Cplant(TM) source code is subject to the
terms of the GNU Lesser General Public License
(see cit/LGPL or <a href='http://www.gnu.org/licenses/lgpl.html'>
 http://www.gnu.org/licenses/lgpl.html</a>)<BR>
<BR>
Cplant(TM) Copyright 1998, 1999, 2000, 2001, 2002 Sandia Corporation.>
Under the terms of Contract DE-AC04-94AL85000, there is a non-exclusive
license for use of this work by or on behalf of the US Government.  
Export of this program may require a license from the United States Government.
</div>
        """
        
        html += "</div>\n\n"
        #html += "<div id='footer'>\nfooter text\n"
        #html += "</div>\n\n"
        html += "</body>\n"
        html += "</html>\n"
        return html

# ====================================================================
# www_admin_html
# ====================================================================
class www_admin_html(resource.Resource, libdebug.debuggable):
    """ Admin Functions """
    # -------------------
    def Initialize(self,options):
        self.options = options
        self.nocss = self.options['nocss']==1

    def render(self,request):
        html  = "<html lang=\"en\">\n"
        html += "<head>\n"
        html += "<title>APItest - Admin</title>\n"
        header = stylesheets.html_css_header(self.nocss)
        html += "%s"%(header)
        html += """<script language="JavaScript1.2">
        <!--
        function refresh() { window.location.reload(false); }
        -->
        </script>
        """	
        html += "</head>\n"
        
        # BODY :: TAB BAR
        html += "<body>\n"
        html += "<div id='wrapper'>\n"
        
        html += "<div id='header'>\n"
        html += "<h1>APItest</h1>\n\n"
        html += "<ul id=\"nav\">\n"
        html += "\t<li><a href='index.html'>Main</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='running'>Running</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='session'>Session</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='saved'>Saved</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='admin' class='here'>Admin</a>\n"
        html += "\t<ul>\n"
        html += "\t\t<li><a href='javascript:history.back()'>Back</a></li>\n"
        html += "\t\t<li><a href='javascript:refresh()'>Refresh</a></li>\n"
        html += "\t</ul>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='about'>About</a>\n"
        html += "\t</li>\n"
        html += "</ul>\n"
        html += "</div>\n\n"        
        html += "<div id='main'>\n"
        html += genShutdownButton()
        html += "</div>\n\n"
        #html += "<div id='footer'>\nfooter text\n"
        #html += "</div>\n\n"
        html += "</body>\n"
        html += "</html>\n"
        return html

# ====================================================================
# www_running_html
# ====================================================================
class www_running_html(resource.Resource, libdebug.debuggable):
    """ Render pages of currently running test """
    # -------------------
    def Initialize(self,options):
        self.options = options
        self.nocss = self.options['nocss']==1

    def genRunTable(self, runID):
        try:
            timeStamp = self.WB.TD.getRun(runID)[2].split("T")
        except:
            return ""
            
        # build fname->ID mapping
        testFileMap = {}
        testList = self.WB.TD.getTestsByRun(runID)
        for testID in testList:
            fullname = self.WB.TD.getTest(testID).get('filename', \
                                                      'ERROR: NO FILENAME EXISTS')
            path = os.path.split(fullname)[0]
            fname= os.path.split(fullname)[1]
            if not testFileMap.has_key(path):
                testFileMap[path] = []
            testFileMap[path].append((fname,testID))
        # append batch info to the list here as well
        batchList= self.WB.TD.getBatchesByRun(runID)
        for batchID in batchList:
            fullname = self.WB.TD.getBatch(batchID)[3].get('filename', \
                    "ERROR: NO FILENAME ATTRIBUTE!")
            path = os.path.split(fullname)[0]
            fname= os.path.split(fullname)[1]
            if not testFileMap.has_key(path):
                testFileMap[path]=[]
            testFileMap[path].append((fname,batchID))

        ## BUILD HTML
        html  = "<table id='results'>\n"
        html += "<caption>%s&nbsp;%s</caption>\n"%(timeStamp[0],timeStamp[1])
        # Header row.
        html += "<tr class='header'>\n"
        html += "\t<th colspan=1 class='status'>Status</th>\n"
        html += "\t<th colspan=3 class='type'>Batch</th>\n"
        html += "\t<th colspan=1 >Test</th>\n"
        html += "</tr>\n"
        
        # fill in rows.
        dirList = testFileMap.keys()
        dirList.sort()
        for idir in dirList:
            # print out directory line.
            html += "<tr class='directory'>\n"
            html += "\t<td colspan=5>%s</td>\n"%(idir)
            html += "</tr>\n"
            
            fileList = testFileMap[idir]
            html += self.genResultRows(fileList)
        html += "</table>\n"
        return html

    # ========================
    def genResultRows(self,fileList):
        html = ""
        fileList.sort()
        for ifile in fileList:
            if re.match(".*\.apt$", ifile[0]):
                testData = self.WB.TD.getTest(ifile[1])
                status = testData.get('status','UNKNOWN')
                desc   = testData.get('shortDescription')
                if desc != None:
                    desc = string.lstrip(desc.text)
                    desc = desc[:60]
                if desc == None or desc == "":
                    desc = ifile[0]
                testID = ifile[1]
                html += "<tr class='test'>\n"
                html += "\t<td colspan=1 class='%s'>%s</td>\n"%(status.lower(), status)
                html += "\t<td colspan=3>&nbsp;</td>\n"
                html += "\t<td colspan=1>"
                html += "<a href='running?testID=%d'>%s</a></td>\n"%(testID,desc)
                html += "</tr>\n\n"
            elif re.match(".*\.apb$", ifile[0]):
                batchID = ifile[1]
                (nT,nP,nF) = self.WB.TD.sumBatchTree(batchID)
                status = self.WB.TD.getBatch(ifile[1])[3].get('status','BATCH')
                if status== '': status = 'RUNNING'
                desc = self.WB.TD.getBatch(ifile[1])[3].find("shortDescription")
                if desc != None:
                    desc = string.lstrip(desc.text)
                    desc = desc[:60]
                if desc == None or desc == "":
                    desc = ifile[0]
                html += "<tr class='batch'>\n"
                html += "\t<td colspan=1 class='%s'>%s</td>\n"%(status.lower(),status)
                html += "\t<td colspan=1 class='bTotal'>%s</td>\n"%(nT)
                html += "\t<td colspan=1 class='bPass'>%s</td>\n"%(nP)
                html += "\t<td colspan=1 class='bFail'>%s</td>\n"%(nF)
                html += "\t<td colspan=1>"
                html += "<a href='running?batchID=%d'>%s</a>"%(batchID,desc)
                html += "</td>\n"
                html += "</tr>\n\n"
        return html
        

    # ========================
    def genBatchTable(self,batchID):
        runID = self.WB.TD.getRunIDByBatch(batchID)
        batchFileName = self.WB.TD.getBatch(batchID)[3].get('filename', \
                                                            "ERROR: NO FILENAME ATTRIBUTE!")
        batchFileStatus = self.WB.TD.getBatch(batchID)[3].get('status','BATCH')
        
        ## BUILD HTML
        html  = "<table id='results'>\n"
        
        # add caption, batch file name
        html += "<caption>%s</caption>\n"%(batchFileName)
        
        # add pass/fail row for batch 
        html += "<tr class='%s'>\n"%(batchFileStatus.lower())
        html += "\t<td colspan=5>%s</td>\n"%(batchFileStatus)
        html += "</tr>\n"
        
        # Header row.
        html += "<tr class='header'>\n"
        html += "\t<th colspan=1 class='status'>Status</th>\n"
        html += "\t<th colspan=3 class='type'>Batch</th>\n"
        html += "\t<th colspan=1 >Test</th>\n"
        html += "</tr>\n"
        
        testFileMap = {}
        testList = self.WB.TD.getTestsByBatch(batchID)
        for testID in testList:
            fullName = self.WB.TD.getTest(testID).get('filename',\
                                                      'ERROR: NO FILENAME EXISTS');
            (path,fname) = os.path.split(fullName)
            if not testFileMap.has_key(path):
                testFileMap[path] = []
            testFileMap[path].append((fname,testID))
        batchList = self.WB.TD.getSubBatchesByBatch(batchID)
        for batchID in batchList:
            fullname = self.WB.TD.getBatch(batchID)[3].get('filename',\
                                                           "ERROR: NO FILENAME ATTRIB!")
            (path,fname) = os.path.split(fullname)
            if not testFileMap.has_key(path):
                testFileMap[path]=[]
            testFileMap[path].append((fname,batchID))
        dirList = testFileMap.keys()
        dirList.sort()
        for idir in dirList:
            # print out directory line.
            html += "<tr class='directory'>\n"
            html += "\t<td colspan=5>%s</td>\n"%(idir)
            html += "</tr>\n"
            fileList = testFileMap[idir]
            html += self.genResultRows(fileList)
        
        # close table
        html += "</table>\n"
        return html


    # ========================
    def render(self,request):
        uri = request.uri
        html  = "<html lang=\"en\">\n"
        html += "<head>\n"
        html += "<title>APItest - Running</title>\n"
        if self.WB.running[0]:
           html += "<META HTTP-EQUIV=refresh CONTENT=\"4; url=%s\"\>\n"%(uri)
        header = stylesheets.html_css_header(self.nocss)
        html += "%s"%(header)
        html += """<script language="JavaScript1.2">
        <!--
        function refresh() { window.location.reload(false); }
        -->
        </script>
        """
        html += "</head>\n"
        html += "<body>\n"
        html += "<div id=\"wrapper\">\n"
        
        # HEADER ===
        html += "<div id=\"header\">\n"
        html += "<h1>APItest</h1>\n\n"
        html += "<ul id=\"nav\">\n"
        html += "\t<li><a href='index.html'>Main</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='running' class='here'>Running</a>\n"
        html += "\t<ul>\n"
        html += "\t\t<li><a href='javascript:history.back()'>Back</a></li>\n"
        html += "\t\t<li><a href='javascript:refresh()'>Refresh</a></li>\n"
        html += "\t</ul>\n"	
        html += "\t</li>\n"
        html += "\t<li><a href='session'>Session</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='saved'>Saved</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='admin'>Admin</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='about'>About</a>\n"
        html += "\t</li>\n"
        html += "</ul>\n"
        html += "</div>\n\n"
        
        # BODY :: CONTENTS
        html += "<div id=\"main\">\n"
        if request.args.has_key('batchID'):
            batchID = int(request.args['batchID'][0])
            html += self.genBatchTable(batchID)
        elif request.args.has_key('testID'):
            testID  = int(request.args['testID'][0])
            html += genTestResultTableFromElement(testID, self.WB.TD.getTest(testID))
        else:
            currentID = self.WB.TD.R.currentID
            html += self.genRunTable(currentID)
        html += "</div>\n\n"
        
        # FOOTER
        #html += "<div id=\"footer\">\n"
        #html += "running.currentID = %s<BR>\n"%(self.WB.TD.R.currentID)
        #html += "</div></div>\n\n"
        
        html += "</body>\n"
        html += "</html>\n"
        return html


# ====================================================================
# www_session_html
# ====================================================================
class www_session_html(resource.Resource, libdebug.debuggable):
    """ Render pages of currently running test """
    # -------------------
    def Initialize(self,options):
        self.options = options
        self.nocss = self.options['nocss']==1

    def genRunTable(self, runID):
        try:
            timeStamp = self.WB.TD.getRun(runID)[2].split("T")
        except:
            return ""
            
        # build fname->ID mapping
        testFileMap = {}
        testList = self.WB.TD.getTestsByRun(runID)
        for testID in testList:
            fullname = self.WB.TD.getTest(testID).get('filename', \
                                'ERROR: NO FILENAME EXISTS')
            path = os.path.split(fullname)[0]
            fname= os.path.split(fullname)[1]
            if not testFileMap.has_key(path):
                testFileMap[path] = []
            testFileMap[path].append((fname,testID))
        # append batch info to the list here as well
        batchList= self.WB.TD.getBatchesByRun(runID)
        for batchID in batchList:
            fullname = self.WB.TD.getBatch(batchID)[3].get('filename', \
                    "ERROR: NO FILENAME ATTRIBUTE!")
            path = os.path.split(fullname)[0]
            fname= os.path.split(fullname)[1]
            if not testFileMap.has_key(path):
                testFileMap[path]=[]
            testFileMap[path].append((fname,batchID))
            
        ## BUILD HTML
        html  = "<table id='results'>\n"
        html += "<caption>%s&nbsp;%s</caption>\n"%(timeStamp[0],timeStamp[1])
        # Header row.
        html += "<tr class='header'>\n"
        html += "\t<th colspan=1 class='status'>Status</th>\n"
        html += "\t<th colspan=3 class='type'>Batch</th>\n"
        html += "\t<th colspan=1 >Test</th>\n"
        html += "</tr>\n"
        
        # fill in rows.
        dirList = testFileMap.keys()
        dirList.sort()
        for idir in dirList:
            # print out directory line.
            html += "<tr class='directory'>\n"
            html += "\t<td colspan=5>%s</td>\n"%(idir)
            html += "</tr>\n"
            fileList = testFileMap[idir]
            html += self.genResultRows(fileList)
        html += "</table>\n"
        return html

    # ========================
    def genResultRows(self,fileList):
        html = ""
        fileList.sort()
        for ifile in fileList:
            if re.match(".*\.apt$", ifile[0]):
                testData = self.WB.TD.getTest(ifile[1])
                status = testData.get('status','UNKNOWN')
                desc   = testData.get('shortDescription')
                if desc != None:
                    desc = string.lstrip(desc.text)
                    desc = desc[:60]
                if desc == None or desc == "":
                    desc = ifile[0]
                testID = ifile[1]
                html += "<tr class='test'>\n"
                html += "\t<td colspan=1 class='%s'>%s</td>\n"%(status.lower(), status)
                html += "\t<td colspan=3>&nbsp;</td>\n"
                html += "\t<td colspan=1>"
                html += "<a href='session?testID=%d'>%s</a></td>\n"%(testID,desc)
                html += "</tr>\n\n"
            elif re.match(".*\.apb$", ifile[0]):
                batchID = ifile[1]
                (nT,nP,nF) = self.WB.TD.sumBatchTree(batchID)
                status = self.WB.TD.getBatch(ifile[1])[3].get('status','BATCH')
                if status== '': status = 'RUNNING'
                desc = self.WB.TD.getBatch(ifile[1])[3].find("shortDescription")
                if desc != None:
                    desc = string.lstrip(desc.text)
                    desc = desc[:60]
                if desc == None or desc == "":
                    desc = ifile[0]
                html += "<tr class='batch'>\n"
                html += "\t<td colspan=1 class='%s'>%s</td>\n"%(status.lower(),status)
                html += "\t<td colspan=1 class='bTotal'>%s</td>\n"%(nT)
                html += "\t<td colspan=1 class='bPass'>%s</td>\n"%(nP)
                html += "\t<td colspan=1 class='bFail'>%s</td>\n"%(nF)
                html += "\t<td colspan=1>"
                html += "<a href='session?batchID=%d'>%s</a>"%(batchID,desc)
                html += "</td>\n"
                html += "</tr>\n\n"
        return html
        

    # ========================
    def genBatchTable(self,batchID):
    
        runID = self.WB.TD.getRunIDByBatch(batchID)
        batchFileName = self.WB.TD.getBatch(batchID)[3].get('filename',\
                                                            "ERROR: NO FILENAME ATTRIBUTE!")
        batchFileStatus = self.WB.TD.getBatch(batchID)[3].get('status','BATCH')
        
        ## BUILD HTML
        html  = "<table id='results'>\n"
        
        # add caption, batch file name
        html += "<caption>%s</caption>\n"%(batchFileName)
        
        # add pass/fail row for batch 
        html += "<tr class='%s'>\n"%(batchFileStatus.lower())
        html += "\t<td colspan=5>%s</td>\n"%(batchFileStatus)
        html += "</tr>\n"
        
        # Header row.
        html += "<tr class='header'>\n"
        html += "\t<th colspan=1 class='status'>Status</th>\n"
        html += "\t<th colspan=3 class='type'>Batch</th>\n"
        html += "\t<th colspan=1 >Test</th>\n"
        html += "</tr>\n"
        
        testFileMap = {}
        testList = self.WB.TD.getTestsByBatch(batchID)
        for testID in testList:
            fullName = self.WB.TD.getTest(testID).get('filename',\
                                                      'ERROR: NO FILENAME EXISTS');
            (path,fname) = os.path.split(fullName)
            if not testFileMap.has_key(path):
                testFileMap[path] = []
            testFileMap[path].append((fname,testID))
        batchList = self.WB.TD.getSubBatchesByBatch(batchID)
        for batchID in batchList:
            fullname = self.WB.TD.getBatch(batchID)[3].get('filename', \
                                                    "ERROR: NO FILENAME ATTRIB!")
            (path,fname) = os.path.split(fullname)
            if not testFileMap.has_key(path):
                testFileMap[path]=[]
            testFileMap[path].append((fname,batchID))
        dirList = testFileMap.keys()
        dirList.sort()
        for idir in dirList:
            # print out directory line.
            html += "<tr class='directory'>\n"
            html += "\t<td colspan=5>%s</td>\n"%(idir)
            html += "</tr>\n"
            fileList = testFileMap[idir]
            html += self.genResultRows(fileList)
        
        # close table
        html += "</table>\n"
        return html


    # ========================
    def genRunList(self):
        """ Generate list of runs. """
        html  = ""
        html += "<table id='listing'>\n"
        html += ""
        
        runIDs = self.WB.TD.getRunIDs()
        html += "<tr>\n"
        html += "\t<th>Date</th>\n"
        html += "\t<th>Time</th>\n"
        html += "\t<th></th>\n"
        html += "</tr>\n"
        if len(runIDs)>0:
            runid = len(runIDs)-1
            while runid >= 0:
                s = string.split(self.WB.TD.getRun(runid)[2],"T",1)
                html += "<tr>\n"
                html += "\t<td class='date'>%s</td>\n"%(s[0])    # date
                html += "\t<td class='time'>%s</td>\n"%(s[1])    # time
                html += "\t<td><a href='session?runID=%d'>"%(runid)+ \
                        "click for details</a></td>\n"
                html += "</tr>\n"
                runid -= 1
        html += "</table>\n"
        return html


    # ========================
    def render(self,request):
        """ render main page for s session """ 
        html  = "<html lang=\"en\">\n"
        html += "<head>\n"
        html += "<title>APItest - Session</title>\n"
        header = stylesheets.html_css_header(self.nocss)
        html += "%s"%(header)
        html += """<script language="JavaScript1.2">
        <!--
        function refresh() { window.location.reload(false); }
        -->
        </script>
        """
        html += "</head>\n"
        html += "<body>\n"
        html += "<div id=\"wrapper\">\n"
        
        # HEADER ===
        html += "<div id=\"header\">\n"
        html += "<h1>APItest</h1>\n\n"
        html += "<ul id=\"nav\">\n"
        html += "\t<li><a href='index.html'>Main</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='running'>Running</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='session' class='here'>Session</a>\n"
        html += "\t<ul>\n"
        html += "\t\t<li><a href='javascript:history.back()'>Back</a></li>\n"
        html += "\t\t<li><a href='javascript:refresh()'>Refresh</a></li>\n"
        html += "\t</ul>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='saved'>Saved</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='admin'>Admin</a>\n"
        html += "\t</li>\n"
        html += "\t<li><a href='about'>About</a>\n"
        html += "\t</li>\n"
        html += "</ul>\n"
        html += "</div>\n\n"
        
        # BODY :: CONTENTS
        html += "<div id=\"main\">\n"
        if request.args.has_key('batchID'):
            batchID = int(request.args['batchID'][0])
            html += self.genBatchTable(batchID)
        elif request.args.has_key('testID'):
            testID  = int(request.args['testID'][0])
            html += genTestResultTableFromElement(testID, self.WB.TD.getTest(testID))
        elif request.args.has_key('runID'):
            runID = int(request.args['runID'][0])
            html += self.genRunTable(runID)
        else:
            html += self.genRunList()
        html += "</div>\n\n"
        
        # FOOTER
        #html += "<div id=\"footer\">\n"
        #html += "running.currentID = %s<BR>\n"%(self.WB.TD.R.currentID)
        #html += "</div></div>\n\n"
        
        html += "</body>\n"
        html += "</html>\n"
        return html


# EOF
