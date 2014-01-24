"""
Cascading stylesheet classes.
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
# $Id: stylesheets.py,v 1.6 2005/05/12 20:22:50 wcmclen Exp $
#############################################################################
from twisted.web import resource
from twisted.internet import reactor
import string
import libdebug

class html_css_header:
    """ loads the correct CSS stylesheets """
    def __init__(self,compatibility=None):
        self.compat = False
        if compatibility:
            self.compat = True

    def __str__(self):
        html  = "<style text=\"text/css\" media=\"all\">\n"
        if self.compat == False:
            html += "@import \"page.css\";\n"
            html += "@import \"nav.css\";\n"
        html += "@import \"tbl_output.css\";\n"
        html += "@import \"tbl_listing.css\";\n"
        html += "@import \"tbl_results.css\";\n"
        html += "</style>\n"
        return html


class www_css_page(resource.Resource, libdebug.debuggable):
    """ css stylesheets for the webpage sections """
    def Initialize(self,options):
        self.options = options
    def render(self,request):
        html = """
body {
    color: #333; 
    background-color: #fff;
    margin-top: 10px;
    margin-left: 10px;
    font: normal 12px verdana,arial,sans-serif;
}
div#wrapper {
    background-color: #ffd;
    border: thin solid #000000;
    width: 640px;
}
div#header {
    float: top;
    background-color: #ffd;
    height: 80px;
}
div#main {
    /*    position: relative; */
    z-index: 102;
    top: 0px;
    padding-top: 25px;
    padding-left: 5px;
    padding-right: 5px;
    padding-bottom: 10px;
    background-color: #ffd;
    margin-top: 5px;
}
div#footer {
    z-index: 104;
    position: relative;
    float: bottom;
    margin-top: 0px;
    padding-left: 5px;
    padding-right: 5px;
    background-color: #cd5c5c;
    border-top: 0px solid #000;
}
div#nest {
position: relative;
    padding-left: 40px;
}
h1 { 
    padding: 0 0 0 20px;
    font-size:2em; 
    font-weight:normal; 
}
h2 {
    padding: 0 0 0 40px;
    font-size: 1.5em;
    font-weight: normal;
}
#subbutton {
    line-height: normal;
    white-space: nowrap;
}
#subbutton span {
    padding-left: 5px;
    text-decoration: none;
}
#subbutton input {
    width: auto;
}
#subbutton span input {
    color: #bbb;
    background: transparent;
    background-image: none;
    border-left: 0px;
    border-right: 0px;
    border-top: 0px;
    border-bottom: 0px;
    margin-top: -5px;
}
#subbutton span input:hover {
    color: #555;
    background: #aac;
}
#subber span input {
    float: none;
}
"""
        return html


# =====================================
class www_css_tbl_results(resource.Resource, libdebug.debuggable):
    """ css stylesheet for results tables. """
    def Initialize(self,options):
        self.options = options
    def render(self,request):
        html = """
table#results {
    top: 0px;
    left: 1px;
    z-index: 101;
    width: 630px;
    margin-top: 0px;
    background: transparent;
    border-top: 1px solid #000;
    border-left: 1px solid #000;
    border-right: 1px solid #000;
    border-bottom: 1px solid #000;
    border-spacing: 1px;
    empty-cells: show;
    font: normal 12px verdana,arial,sans-serif;
}
#results caption { 
    width: 630px;
    background: #b0c4de;  /* #9370d8*/
    font-weight: normal;
    padding-top: 2px;
}
#results tr.header {
    background: #999;
}
#results th { 
    padding-top: 5px;
    background: #778899;
}
#results th.status {
    width: 80px;
}
#results th.type {
    width: 90px;
}
#results th.directory {
    width: 150px;
}
#results td.type {
    text-align: center;
    width: 90px;
}
#results td {
    border: 0px solid #000;
}
#results tr.pass {
    text-align: center;
    color: #006600;
    background: #00ff99;
}
#results tr.fail {
    text-align: center;
    color: #990000;
    background: #ff9999;
}
#results tr.faildep {
    text-align: center;
    color: #b22222;
    background: #ffa500;
}
#results td.pass { 
    text-align: center; 
    width: 80px; 
    background: #00FF99; 
    color: #006600; 
    padding-top: 4px;
}
#results td.bTotal {
    text-align: center;
    width: 30px;
}
#results td.bPass {
    text-align: center;
    color: #006600;
    background: #00ff99;
    width: 30px;
}
#results td.bFail {
    text-align: center;
    color: #990000;
    background: #ff9999;
    width: 30px;
}
#results td.fail { 
    text-align: center; 
    width: 80px; 
    background: #ff9999; 
    color: #990000; 
    padding-top: 4px;
}
#results td.running {
    text-align: center;
    width: 80px;
    background: #cd5cdc;
    color: #4b0082;
    padding-top: 4px;
}
#results td.faildep {
    text-align: center;
    width: 80px;
    background: #ffa500;
    color: #b22222;
    padding-top: 4px;
}
#results td.timedout {
    text-align: center;
    width: 80px;
    background: #ffff00;
    color: #b22222;
    padding-top: 2px;
}
#results td.box { 
    width: 40px; 
    text-align: left;
}
#results td.button     { width: 30px; text-align: center; }
#results tr.select_all { background: #20b2dd; 2px;}
#results tr.directory  { background: #b0c4de; color: #000; }
#results td.directory  { padding-top: 2px; }
#results tr.test       { background: #d3d3d3; }
#results tr.batch      { background: lavender; }
/* color: #900; */
#results tr.xmlerror   { background: #fdd; }
"""
        return html


# ==============================
class www_css_tbl_listing(resource.Resource, libdebug.debuggable):
    """ css stylesheet for a listing table.  (tbl_listing) """
    def Initialize(self,options):
        self.options = options
    def render(self,request):
        html = """
table#listing {
    position: relative;
    top: 0px;
    left: 0px;
    z-index: 101;
    padding: 0px 0px 4px 0px;
    width: 630px;
    background: transparent;
    border-spacing: 1px;
    empty-cells: show;
    font: normal 12px verdana,arial,sans-serif;
}
#listing tr       { background: #d3d3d3; }
#listing th       { background: #789;  }
#listing td.time  { width: 80px; text-align: center; }
#listing td.date  { width: 80px; text-align: center; }
"""
        return html


# ==============================
class www_css_tbl_output(resource.Resource, libdebug.debuggable):
    """ tbl_output.css """
    def Initialize(self,options):
        self.options = options
    def render(self,request):
        html = """
table#output {
    position: relative;
    top: 0px;
    left: 0px;
    z-index: 101;
    padding: 0px 0px 4px 0px;
    width: 630px;
    background: transparent;
    border-spacing: 1px;
    empty-cells: show;
    border: 1px solid #000;
    font: normal 12px verdana,arial,sans-serif;
}
#output caption {
    width: 630px;
    background: #9370d8;
    border-top: 1px solid #000;
    border-right: 1px solid #000;
    border-left: 1px solid #000;
    padding-top: 3px;
    padding-bottom: 2px;
}
#output th {
    background: #b0c4de;
    font-weight: normal;
}
#output td {
    padding-top: 3px;
    vertical-align: top;
    background: #f0f8ff;
}
#output td.pass { 
    text-align: center; 
    width: 80px; 
    background: #00FF99; 
    color: #006600; 
}
#output td.fail { 
    text-align: center; 
    width: 80px; 
    background: #ff9999; 
    color: #990000; 
}
#output td.failed {
    color: #990000;
    background: #ff9999;
}
"""
        return html


# =====================================================================
#  NAV BAR PURE CSS
# =====================================================================
class www_css_nav(resource.Resource, libdebug.debuggable):
    """ nav.css """
    def Initialize(self,options):
        self.options = options
    def render(self,request):
        html = """
/* ========== navigation css ========== */
#nav {
    position: relative;
    float: left;
    width: 620px;
    padding: 0 0 1.75em 1em;
    margin: 0;
    list-style: none;
    list-style-type: none;
    line-height: 1em;
    font: normal 12px verdana,arial,sans-serif;
}
#nav li {
    display:block;
    float: left;
    margin: 0;
    padding: 0;
}
#nav a {
    display: block;
    float: left;
    color #559;
    background: #cdc;
    text-decoration: none;
    font-weight: normal;
    padding: 0.25em 1em;
    border-left: 1px solid #fff;
    border-top: 1px sollid #fff;
    border-right: 1px solid #aaa;
}
#nav a:hover {
    z-index: 102;
    color: #fff;
    background: #9a9;
}
#nav a:active,
#nav a.here:link,
#nav a.here:visited {
    z-index: 102;
    color: #bbb;
    background: #559;
}

/* ========== subnav ========== */
#nav ul {
    position: absolute;
    z-index: 103;
    left: 0;
    top: 1.85em;
    float: left;
    background: #559;
    width: 619px;
    margin: 0;
    height: 2.2em;
    padding-top: 0.25em;
    padding-left: 1.5em;
    padding-right: 0.25em;
    padding-bottom: 4px;
    list-style: none;
    border-top: 0px solid #fff;
    margin-top: 0px;
    margin-bottom: 5px;
}
#nav ul li {
    float: left;
    display: block;
    margin-top: 5px;
}
#nav ul a {
    background: transparent;
    color: #bbb;
    display: inline;
    margin: 0;
    border: 0px solid #fff;
    padding: 0px 0.1em;  
    padding-top: 0px;	    /* line up buttons and links */
    padding-bottom: 1px;
    padding-left: 10px;
    padding-right: 10px;
}
#nav ul a:hover {
    color: #555;
    background: #aac;
}
#nav ul a:active,
#nav ul a.here:link,
#nav ul a.here:visited {
    color #444;
}
"""
        return html

#   #-#-#-#   #
#   | EOF |   #
#   #-#-#-#   #
