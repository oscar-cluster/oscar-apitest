# APItest README

## Installing APItest

Please refer to [INSTALL.html](INSTALL.html) for installation
instructions.

## Running APItest

This code is currently in development, but we do have the shell and
command tests working.  
  
To run apitest type the following:  
  
`**$ apitest httpd**`
  
This will start apitest as an HTTP daemon on your local machine.  
To use apitest, direct a web browser to:  
  
<http://localhost:2112/index.html>

## Installation

APItest can be installed using the Python setup script that is
provided.  
  
`$ python setup.py install`
  
should be sufficient to install APItest onto a unix machine.  
We also have an RPM distribution available.

## Command Line Help

Examples of how to get command-line help.

Prints out a list of command line options:
`$ apitest --help`


Prints out a list of httpd command line options:
`$ apitest httpd --help`


## Directories

The destination directories of the default APItest installation are:

-   **/usr/bin** - location of the *apitest* execution script.
-   **/usr/share/doc/apitest** - Documentation & example scripts.
-   **/usr/lib/python{py_vers}/site-packages/libapitest** - libapitest
-   [User Guide
    (PDF)](file:///usr/share/doc/apitest/APItest-userguide-1_0.pdf)

  

------------------------------------------------------------------------

## Questions & Comments

Help make APItest better... please send questions and comments to
[William McLendon](=%22mailto::wcmclen@sandia.gov%22)
