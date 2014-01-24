#!/usr/bin/env python
"""
  ###################################################################
  #
  #     This Cplant(TM) source code is the property of Sandia
  #     National Laboratories.
  #
  #     This Cplant(TM) source code is copyrighted by Sandia
  #     National Laboratories.
  #
  #     The redistribution of this Cplant(TM) source code is
  #     subject to the terms of the GNU Lesser General Public
  #     License.
  #     (see cit/LGPL or http://www.gnu.org/licenses/lgpl.html)
  #
  #     Cplant(TM) Copyright 1998, 1999, 2000, 2001, 2002 Sandia
  #     Corporation.  Under the terms of Contract DE-AC04-94AL85000,
  #     there is a non-exclusive license for use of this work by or
  #     on behalf of the US Government.  Export of this program may
  #     require a license from the United States Government.
  #
  ###################################################################
"""
import distutils
from distutils.core import setup
from os.path import normpath
from string import replace
import sys, os, re, os.path,getopt

# Kludge fix for python2.2 that doesn't have os.path.sep
if not os.path.__dict__.has_key('sep'):
    os.path.sep = "/"


#####
#
# Default variables
#
#####
__author__   = "William McLendon"
__version__  = "1.0.2"

#####
#
# Process Command Line
#
#####



######
## Config values that are dependent on the install_root
######
#install_root = os.path.normpath(os.path.abspath(install_root))
#docs_dir = os.path.normpath(os.path.abspath(install_root+os.path.sep+"docs"))


#####
def getDirtreeFileList(rootDir):
    L = []
    for i in os.walk(rootDir):
        theDir = i[0]
        if not re.match(".*/CVS$", theDir):
            theEntry = ( theDir,[])
            for j in i[2]:
                theEntry[1].append(normpath(theDir+'/'+j))
            L.append( theEntry )
    return L

prefix = ""

scripts_list = ['apitest']

data_file_list = []

doc_dir = ""
doc_dir = "share/doc/apitest/"
#doc_dir = "/usr/share/doc/apitest/"

data_file_list.append( (doc_dir, ['README.html', 'doc/APItest-userguide-1_0.pdf']))

data_file_list.append( (doc_dir+"examples",
                        ['samples/apitest_test.apb',
                        'samples/install_test.apt']))

data_file_list.append( (doc_dir+"examples/batch",
                        ['samples/batch/bTest_1.apb',
                         'samples/batch/bTest_2.apb',
                         'samples/batch/bTest_3.apb',
                         'samples/batch/bTest_4.apb',
                         'samples/batch/bTest_5.apb',
                         'samples/batch/bTest_6.apb',
                         'samples/batch/bTest_7.apb',
                         'samples/batch/bTest_8.apb',
                         'samples/batch/bTest_seq.apb',
                         'samples/batch/batch.apb',
                         'samples/batch/bTest_conditional.apb',
                         'samples/batch/bTest_conditional_FAIL.apb',
                         'samples/batch/bTest_conditional_PASS.apb',
                         'samples/batch/bTest_subTestCheck.apb',
                         'samples/batch/bTest_faildep.apb']))

data_file_list.append( (doc_dir+"examples/cmd",
                        ['samples/cmd/cmd.apb',
                        'samples/cmd/cmd_filediff.apt',
                        'samples/cmd/cmd_notfound_1.apt',
                        'samples/cmd/cmd_notfound_2.apt',
                        'samples/cmd/cmd_test_1.apt',
                        'samples/cmd/cmd_test_2.apt',
                        'samples/cmd/cmd_test_3.apt',
                        'samples/cmd/cmd_test_4.apt',
                        'samples/cmd/cmd_nomatch.apt']) )

data_file_list.append( (doc_dir+"examples/daemon",
                        ['samples/daemon/daemonize.apt']))

data_file_list.append( (doc_dir+"examples/envvar",
                        ['samples/envvar/envvar.apb',
                        'samples/envvar/envvar_cmd.apt',
                         'samples/envvar/envvar_cmd_suid.apt',
                         'samples/envvar/envvar_script.apt',
                         'samples/envvar/envvar_script_suid.apt']) )

data_file_list.append( (doc_dir+"examples/io",
                        ['samples/io/io.apb',
                         'samples/io/io_large_matchall.apt',
                         'samples/io/io_large_miss_stderr.apt',
                         'samples/io/io_large_miss_stdout.apt']))

data_file_list.append( (doc_dir+"examples/scidac_sss",[]) )

data_file_list.append( (doc_dir+"examples/scidac_sss/sd",
                         ['samples/scidac_sss/sd/sss_01.apt',
                          'samples/scidac_sss/sd/sss_02.apt',
                          'samples/scidac_sss/sd/sss_sd_inittest.apb',
                          'samples/scidac_sss/sd/sss_sd_inittest_cleanup.apt',
                          'samples/scidac_sss/sd/sss_sd_inittest_prep.apt',
                          'samples/scidac_sss/sd/sss_sd_remove_emng.apt',
                          'samples/scidac_sss/sd/sss_sdstat_sdoff.apt',
                          'samples/scidac_sss/sd/sss_sdstat_sdon.apt',
                          'samples/scidac_sss/sd/sss_start.apt',
                          'samples/scidac_sss/sd/sss_stop.apt']) )

data_file_list.append( (doc_dir+"examples/script",
                        ['samples/script/script.apb',
                         'samples/script/script_test_1.apt',
                         'samples/script/script_test_2.apt',
                         'samples/script/timestamp.apt',
                         'samples/script/script_test_badamp.apt',
                         'samples/script/script_foo.apt',
                         'samples/script/script_envvar.apt']) )

data_file_list.append( (doc_dir+"examples/suid",
                        ['samples/suid/suid_cmd_uid.apt',
                         'samples/suid/suid_cmd_uname.apt',
                         'samples/suid/suid_cmd_uname_notfound.apt',
                         'samples/suid/suid_cmd_uname_wdir_1.apt',
                         'samples/suid/suid_cmd_uname_wdir_2.apt',
                         'samples/suid/suid_script_uid.apt',
                         'samples/suid/suid_script_uname.apt',
                         'samples/suid/suid_script_uname_notfound.apt',
                         'samples/suid/suid_script_uname_status.apt']) )

data_file_list.append( (doc_dir+"examples/timeout",
                        ['samples/timeout/timeout.apb',
                        'samples/timeout/timeout.apt']) )

_classifiers_ = [
    'Development Status :: 1.0',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Intended Audience :: Software Testers',
    'Intended Audience :: Managers',
    'License :: LGPL',
    'Operating System :: MacOS X',
    'Operating System :: Unix',
    'Operating System :: Linux',
    'Programming Language :: Python',
    'Topic :: Software Development :: Software Testing',
    ]


#####
print 70*"-"
#print "\tInstalling apitest v%s into '%s'"%(__version__,install_root)
#print 70*"-"


# Patch for python releases prior to 2.2.3 to ignore the classifiers 
# and download_url
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers  = None
    DistributionMetadata.download_url = None


setup(name        = "apitest",
      description = "APItest Testing Framework",
      version     = __version__,
      author      = __author__,
      author_email= "wcmclen@sandia.gov",
      data_files  = data_file_list,
      scripts     = scripts_list,
      packages    = ["libapitest"],
     )

# EOF
