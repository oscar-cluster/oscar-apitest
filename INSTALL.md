# APItest Installation Instructions

## Required Prerequisites for APItest

APItest depends on a few freely available Python packages and utilities
to run. The following table provides the list and links for
downloading.  

*Required packages for APItest*

- Python 3.2 or higher [http://www.python.org](http://www.python.org)
- Twisted 2.0 [http://www.twistedmatrix.com](http://www.twistedmatrix.com/products/download)
- TwistedWeb [http://www.twistedmatrix.com](http://www.twistedmatrix.com/products/download)
- ElementTree [http://www.effbot.org](http://www.effbot.org)

## Building and Installing

`$ setup.py install --prefix=installation path[ --install-lib=lib installation path]`

## Executing APItest

After installation, you should make sure that the installation directory
is in your search path. Then you can run:  
  

`$ apitest httpd`

 
From anywhere and APItest will start up a web-server listening to: [http://localhost:2112/](http://localhost:2112/).
A full listing of allowable commands is listed in the APItest userguide, is also
available by typing **--help** into the command line.
