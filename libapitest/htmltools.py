"""
Generic HTML widgets for making buttons, horizontal lines, colors, etc.
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

import string

def genButton(name,value,opts):
    return '<input type=BUTTON name="%s" value="%s" %s>'%(name,value,opts)

def genCheckBox(name,value,opts):
    return '<input type=CHECKBOX name="%s" value="%s" %s>'%(name,value,opts)

def genRadioButton(name,value,opts):
    return '<input type=RADIO name="%s" value="%s" %s>'%(name,value,opts)

def genResetButton():
    return '<input type=RESET>'

def genSubmitButton(name,value,opts):
    return '<input type=SUBMIT name="%s" value="%s" %s>'%(name,value,opts)

def genSubmitTextButton(name,value,opts):
    return '<input type=IMAGE src="none.gif" onmouseover="this.img=\'img/tab.gif\'" value="submit" name="%s" alt="%s" %s></input>'%(name,value,opts);

def genHRuleTable(width,height,color):
    html  = "<!-- HRULE TABLE -->"
    html += "<TABLE BORDER=0 CELLSPACING=0 WIDTH='%s'>\n"%(width)
    html += "  <TR BGCOLOR='%s'><TD HEIGHT=%s></TD></TR>\n"%(color,height)
    html += "</TABLE>\n\n"
    return html

def genColor(colorName):
    """ Generates an HTML color code according to the name given """
    colorName = string.upper(colorName)
    if   colorName == 'BLACK'     : return '#000000'
    elif colorName == "TURQUOISE" : return '#0099CC'
    elif colorName == 'PASS'      : return '#008000'
    elif colorName == 'PASSBG'    : return '#98FB98'
    elif colorName == 'FAIL'      : return '#B22222'
    elif colorName == 'FAILBG'    : return '#F08080'
    elif colorName == 'RUNNING'   : return '#4B0082'  # Indigo
    elif colorName == 'RUNNINGBG' : return '#CD5CDC'  # Indianred
    elif colorName == 'BATCH'     : return '#333366'
    elif colorName == 'BATCHBG'   : return '#FFFFFF'
    elif colorName == 'FAILDEP'   : return '#B22222'
    elif colorName == 'FAILDEPBG' : return '#FFA500'
    elif colorName == 'TIMEDOUT'  : return '#B22222'
    elif colorName == 'TIMEDOUTBG': return '#FFFF00'
    elif colorName == 'DNE'       : return '#0000FF'
    elif colorName == 'DNEBG'     : return '#B22222'
    elif colorName == 'RED'       : return '#FF0000'
    elif colorName == 'GREEN'     : return '#00FF00'
    elif colorName == 'BLUE'      : return '#0000FF'
    elif colorName == "YELLOW"    : return '#FFFF00'
    elif colorName == "ORANGE"    : return '#FFA500'
    elif colorName == 'FIREBRICK' : return '#B22222'
    elif colorName == "LIGHTCORAL": return '#F08080'
    elif colorName == "PALEGREEN" : return '#98FB98'
    elif colorName == "INDIANRED" : return '#CD5CDC'
    elif colorName == "INDIGO"    : return '#4B0082'
    else:
        return "#000000"

def genTitlebar(titleText):
    """ Generate HTML for a title bar for APItest """
    html = ""
    html += "<TABLE WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=0>\n"
    html += "<TR>\n"
    html += "  <TD VALIGN=bottom><FONT SIZE=+3>%s</FONT></TD>\n"%(titleText)
    html += "  <TD WIDTH=52>\n"
    ##html += "    <A HREF='http://www.sandia.gov/'><IMG SRC='img/snlbird_50.gif' HEIGHT=50 BORDER=0></A>"
    html += "  </TD>\n"
    html += "</TR>\n"
    html += "</TABLE>\n<BR>\n"
    return html
    

    

    
#-----------------------------------------------------------------------
# internal testing routines
#-----------------------------------------------------------------------
def test(label,control,test):
    """ Nothing to see here... move along... move along """
    failed=0
    if control == test:
        print "%-24s\tPASS"%(label)
    else:
        print "%-24s\tFAIL"%(label)
        failed = 1
    return failed


def testme():
    """ Pay no mind to the man behind the curtain... """
    print "Testing module: htmltools.py"
    test("genCheckBox", \
         '<input type=CHECKBOX name="nme" value="val" >\n', \
         genCheckBox('nme','val','') )
    
    test("genRadioButton", \
         '<input type=RADIO name="nme" value="val" >\n', \
         genRadioButton('nme','val','') )
    
    test("genButton", \
         '<input type=BUTTON name="nme" value="val" >\n', \
         genButton('nme','val','') )
    
    test("genResetButton", \
         '<input type=RESET>\n', genResetButton() )
    
    test("genSubmitButton", \
         '<input type=SUBMIT name="nme" value="val" >\n',
         genSubmitButton('nme','val','') )
        

#-----------------------------------------------------------------------
# main()
#-----------------------------------------------------------------------
if __name__ == '__main__':
    """ For testing htmltools.py internally """
    testme()

# EOF
