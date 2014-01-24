""" 
Interface methods to MySQL database
"""
##########################################################################
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
#     Under the terms of Contract DE-AC04-94AL85000, there is a 
#     non-exclusive license for use of this work by or on behalf of 
#     the US Government.
#     Export of this program may require a license from the United States
#     Government.
#
##########################################################################

#
# $Id: db_mysql.py,v 1.4 2005/04/07 21:12:09 wcmclen Exp $
#

import libdebug
import MySQLdb

# ========================================================================
class sqldb(libdebug.debuggable):
    """ 
    Generic functions to wrap some common mysql interface functions 
    """
 
    # --------------------------
    def __init__(self):
        self.Initialize()

    # --------------------------
    def Initialize(self, 
                   host="localhost",
                   user="apitest",
                   db="apitest"):
        """ Initialize the data structure """
        self.printDebug("sqldb::Initialize()")
        self.cursor = None
        self.dbname = db
        self.host   = host
        self.user   = user
        self.db	    = None
        self.dbOk   = False
        self.connected = False


    # --------------------------
    def printErrorMsg(self,e):
        """ Prints out MySQL error message when debug mode is on."""
        self.printDebug("MySQLdb Error %s: %s" % (e.args[0],e.args[1]))

        
    # --------------------------
    def deleteDB(self):
        """ Delete the database... USE WITH CAUTION!!! """
        self.execute("""DROP DATABASE %s""" % self.dbname)


    # --------------------------
    def deleteTBL(self, table):
        """ Delete a table from the database. """
        self.execute("""DROP TABLE %s""" % (table) )

        
    # --------------------------
    def CreateDB(self):
        """ Create a blank database. """
        self.deleteDB(self)
        self.execute("""CREATE DATABASE %s""" % self.dbname)


    # --------------------------
    def BackupDB(self):
        """ Invoke MySQL to save a backup. """
        pass

        
    # --------------------------
    def Connect(self, passwd=""):
        """ Connect to DB """
        # try to connect to the database...
        if not self.connected:
            self.connected = False
            try:
                self.db = MySQLdb.connect(host=self.host,
                                          user=self.user,
                                          passwd=passwd,
                                          db=self.dbname)
                self.connected = True
            except MySQLdb.Error, e:
                self.printErrorMsg(e)
                return False
        return True

    
    # --------------------------
    def getCursor(self):
        if self.connected:
            try:
                self.cursor = self.db.cursor()
            except MySQLdb.Error, e:
                self.printErrorMsg(e)
                self.cursor = None
                return None
        return self.cursor


    # --------------------------
    def closeCursor(self):
        """ close the current cursor """
        # Close the cursor.
        try:
            self.cursor.close()
            self.cursor = None
        except MySQLdb.Error, e:
            self.printErrorMsg(e)
            return False
        return True


    # ----------------------------
    def close(self):
        """ disconnect from the database """

        self.closeCursor()
        #  Close the DB.
        try:
            self.db.close()
            self.db = None
        except MySQLdb.Error, e:
            self.printErrorMsg(e)
            return False
        self.connected = False
        return True


    # ----------------------------
    def execute(self, query):
        self.printDebug("Executing QUERY: [%s]"%(query))
        if not self.connected:
            self.printDebug("ERROR: Not connected to %s!"%(self.dbname))
            return None
        cursor = self.getCursor()
        try:
            cursor.execute(query)
        except MySQLdb.Error, e:
            self.printErrorMsg(e)
            return None
        return cursor


    # ----------------------------
    def getMaxID(self,table, ID="ID"):
        c = self.execute("""
                SELECT %s from %s, ( SELECT MAX(%s) as MAXID FROM %s) S
                WHERE %s = S.MAXID""" % (ID, table, ID, table, ID) )
        if c == None:
            return None
        return c.fetchone()[0]
            



# ========================================================================
class apitestdb(sqldb):
    """ Database specific commands for APItest Database(s)"""

    # --------------------------
    def __init__(self):
        self.debug_off()
        sqldb.__init__(self)

    # --------------------------
    def deleteTables(self):
        """ Delete the tables. """
        self.deleteTBL("results")

    # --------------------------
    def createTables(self):
        """ Create the tables for the APItest database. """
        pass

    # ----------------------------
    def tblCreate_runs(self):
        """ Create a 'runs' table """
        query = \
        """
        CREATE TABLE `runs` (
                `ID` int(11) NOT NULL auto_increment,
                `TSTART` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                `TFINISH` TIMESTAMP NULL,
                PRIMARY KEY(`ID`)
                )
        """
        return self.execute(query)

    # ----------------------------
    def create_new_run(self):
        """ Create a new entry for a new run. """
        query = """INSERT INTO runs (`TFINISH`) VALUES (Null) """
        self.execute(query)
        id = self.getMaxID('runs')
        return id

    # ----------------------------
    def tblDrop_runs(self):
        """ Delete the 'runs' table. """
        return self.execute(""" DROP TABLE `runs` """)

    # ----------------------------
    def tblRuns_setTFINISH(self,id):
        """ Set the TFINISH Timestamp """
        query = """
        UPDATE `runs` SET `TFINISH`=CURRENT_TIMESTAMP WHERE ID=%s
        """%(id)
        return self.execute(query)


    # ----------------------------
    def tblCreate_results(self):
        """
        Create the 'results' table """
        query = \
        """
        CREATE TABLE `results` (
                `ID` int(11) NOT NULL auto_increment,
                `RUNID` int(11),
                `PID` int(11) NULL,
                `FNAME` VARCHAR(200) NOT NULL,
                `MD5` CHAR(32),
                `TYPE` ENUM('BATCH','TEST','OTHER') NOT NULL DEFAULT 'OTHER',
                `TSTART` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                `TFINISH` TIMESTAMP NULL,
                `STATUS` ENUM('PASS','FAIL','TIMEDOUT','FAILDEP',
                              'RUNNING','UNKNOWN')
                    default 'UNKNOWN',
                `TIMEOUT` double,
                PRIMARY KEY(`ID`)
                )
        """
        return self.execute(query)


    # ----------------------------
    def tblCreate_deps(self):
        """
        Create the 'dependencies' table.
        """
        query = """
        CREATE TABLE `dependencies` (
                `ID` int(11) NOT NULL auto_increment,
                `RESULTID` int(11),
                `EXPECT` ENUM('PASS','FAIL','ANY'),
                `ACTUAL` ENUM('PASS','FAIL'),
                `PARENT_FILE` VARCHAR(60),
                PRIMARY KEY(`ID`)
                )
        """
        #      `PARENT_RESULT_ID` int(11),
        return self.execute(query)


    # ----------------------------
    def tblDrop_deps(self):
        """
        Drop dependencies table.
        """
        return self.execute("""DROP TABLE `dependencies` """)


    # ----------------------------
    def tblCreate_userdata(self):
        query = """
        CREATE TABLE `userdata` (
                `ID` int(11) NOT NULL auto_increment,
                `RESULTID` int(11),
                `TEXT` TEXT,
                PRIMARY KEY(`ID`)
                )
        """
        return self.execute(query)


    # ----------------------------
    def tblDrop_userdata(self):
        return self.execute("""DROP TABLE `userdata`""")


    # ----------------------------
    def tblCreate_resultdata(self):
        query = """
        CREATE TABLE `resultdata` (
                `ID` int(11) NOT NULL auto_increment,
                `RESULTID` int(11),
                `TYPE` VARCHAR(20),
                `FORMAT` VARCHAR(20),
                `EXPECT` TEXT,
                `ACTUAL` TEXT,
                `MATCH` BOOL,
                PRIMARY KEY(`ID`)
                )
        """
        return self.execute(query)


    # ----------------------------
    def tblDrop_resultdata(self):
        return self.execute("""DROP TABLE `resultdata`""")


    # ----------------------------
    def tblDrop_results(self):
        """
        Delete the `results` table from the database.
        """
        return self.execute(""" DROP TABLE `results` """)
    
        
    # ----------------------------
    def TestDB(self):
        """ Test the database for correct structure. """
        pass
            






# ========================================================================
# MY SQL NOTES ...
#
"""
To get the latest row with an autoincrement ID...

SELECT * from <TBL>,
    ( SELECT MAX(ID) AS MAXID FROM <TBL>) S
WHERE
    ID = S.MAXID


"""
        


###############
#   # EOF #   #
###############
