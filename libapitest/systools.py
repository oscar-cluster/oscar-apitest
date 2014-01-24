"""
Useful system tools and commands
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
import pwd
import stat
import re
import os
import os.path

# KLUDGE FOR PATH SETTING
if not os.path.__dict__.has_key('sep'):
    os.path.sep = "/"
if not os.path.__dict__.has_key('pathsep'):
    os.path.pathsep = ":"

#-------------------------------------------------------------
# user / group ID stuff
#-------------------------------------------------------------

# ------------------------------------------------------------
def str_unique(l):
   dict = {}
   for s in l:
      dict[s] = 1
   return dict.keys()


# ------------------------------------------------------------
def getUNAMEfromUID(uid):
    """
    Retrieve the username given the userid
    """
    uname  = None
    if re.match("\d+",str(uid)):
        uid = int(uid)
        try:
            (uname,junk1,uid,gid,longname,homedir,shell) = pwd.getpwuid(uid)
        except:
            pass
    return uname


# ------------------------------------------------------------
def getUIDfromUNAME(uname):
    """
    Retrieve the UID given the username
    """
    uid = None
    try:
        (uname,junk1,uid,gid,longname,homedir,shell) = pwd.getpwnam(uname)
    except:
        pass
    return uid


# ------------------------------------------------------------
def getGIDfromUNAME(uname):
    """
    Retrieve the GID given a username
    """
    gid = None
    try:
        (uname,junk1,uid,gid,longname,homedir,shell) = pwd.getpwnam(uname)
    except:
        pass
    return(gid)


# ------------------------------------------------------------
def searchPathForExecutable(prog):
    """
    Search the path for an executable.
    """
    pathList = "./"
    F_found  = False
    F_exec   = False
    F_search = True

    nfo = None
    try:
        testPath = os.path.normpath(prog)
        nfo = os.stat( prog ); 
        if nfo:
            F_found = True
            if nfo[stat.ST_MODE] & stat.S_IEXEC:
                F_exec = True
    except: 
        if os.environ.has_key("PATH"):
            pathList = os.environ["PATH"]
            pathList = pathList.split( os.path.pathsep )  # (ie. break on the ':' of the path listing
            #pathList = dict.fromkeys(pathList).keys()  # make unique!
            pathList = str_unique(pathList)  # make unique list of keys
            for iPath in pathList:
                testPath = os.path.abspath(os.path.normpath(iPath+os.path.sep+prog))
                basePath = os.path.abspath(os.path.normpath(iPath))
                nfo = None
                try: 
                    nfo = os.stat( testPath )
                    if nfo: 
                        F_found = True
                        if nfo[stat.ST_MODE] & stat.S_IEXEC:
                            F_exec = True
                except: 
                    pass
                if F_found: break
    return (F_found, F_exec, testPath)
                

# ------------------------------------------------------------
if __name__ == "__main__":
    ##print "uid = %s\tuname = %s"%("501",getUNAMEfromUID(501))
    print searchPathForExecutable('ls')
    print searchPathForExecutable('systools.py')
    print searchPathForExecutable('whoozahamuttet')
    print searchPathForExecutable('/home/wcmclen/ls')
    print searchPathForExecutable('../setup.py')
    pass

# EOF #
