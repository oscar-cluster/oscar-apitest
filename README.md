# APItest README

## Installing APItest

Please refer to [INSTALL.md](INSTALL.md) for installation
instructions.

## Running APItest

This code is currently in development, but we do have the shell and
command tests working.
  
To run apitest type the following:
  
`$ apitest httpd`
  
This will start apitest as an HTTP daemon on your local machine.
To use apitest, direct a web browser to:
  
<http://localhost:2112/index.html>

## Installation

APItest can be installed using the pyproject.toml that is
provided.
  
`$ python3 -m build --wheel; python3 -m pip install`

should be sufficient to install APItest onto a unix machine.
There is also have an RPM and DEB packages availables.
See [INSTALL.md](INSTALL.md) for package build instructions.

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
apitest [issues](https://github.com/oscar-cluster/oscar-apitest/issues)
Or [William McLendon](=%22mailto::wcmclen@sandia.gov%22)
