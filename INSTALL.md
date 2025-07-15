# APItest Installation Instructions

## Required Prerequisites for APItest

APItest depends on a few freely available Python packages and utilities
to run. The following table provides the list and links for
downloading.  

*Required packages for APItest*

- Python 3.6 or higher [http://www.python.org](http://www.python.org)
- Twisted >= 18.9.0 [http://www.twistedmatrix.com](http://www.twistedmatrix.com/products/download)
- TwistedWeb [http://www.twistedmatrix.com](http://www.twistedmatrix.com/products/download)
- zope.interface >= 5.0 [https://pypi.org/project/zope.interface/] (https://pypi.org/project/zope.interface/)
- ElementTree [http://www.effbot.org](http://www.effbot.org)

## Building and Installing
`$ python3 -m build --wheel; python3 -m pip install --prefix=<installation path>`

## Building rpm package (package check included):
`$ python3 -m build --sdist ; rpmbuild -tb dist/apitest-*.tar.gz`

## Building deb package (with package check):
`$ dpkg-buildpackage -us -uc`
`$ autopkgtest ../apitest_*.deb -- null`

## Executing APItest

After installation, you should make sure that the installation directory
is in your search path. Then you can run:  
  

`$ apitest httpd`

 
From anywhere and APItest will start up a web-server listening to: [http://localhost:2112/](http://localhost:2112/).
A full listing of allowable commands is listed in the APItest userguide, is also
available by typing **--help** into the command line.
