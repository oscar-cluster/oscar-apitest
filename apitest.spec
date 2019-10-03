%define name apitest
%define version 1.0.3
%define release 1
#define _unpackaged_files_terminate_build 0

#{expand:%%define py_ver %(python -V 2>&1| awk '{print $2}')}
#{expand:%%define py_libver %(python -V 2>&1| awk '{print $2}'|cut -d. -f1-2)}

Summary: A test driver application. 
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
License: LGPL
Group: Development/Libraries
Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root

# Architecture
BuildArch: noarch

Requires: python3-twisted
BuildRequires: python3-twisted

Requires: python3 >= 3.4
BuildRequires: python3 >= 3.4


%description
APItest version %{version}.
A test driver application. 


##########
# PREP
##########
%prep
%setup -q -n %{name}-%{version}

%build
echo "==========[ BUILD ]===================================="
echo "python%{python3_version}"
echo "buildroot=%{buildroot}"


%install
echo "==========[ INSTALL ]=================================="
echo %{buildroot}
#define doc_prefix /usr/share/doc/apitest
%{__python3} setup.py install --no-compile --prefix=%{buildroot}%{_prefix}/ --install-lib=%{buildroot}%{python3_sitelib}
###--install-data=#{buildroot}/#{doc_prefix}


%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog doc/COPYING.LGPLv2.1
%{python3_sitelib}/*
%{_docdir}/*
%{_bindir}/*


%clean
echo "cleaning $RPM_BUILD_ROOT"
rm -rf $RPM_BUILD_ROOT

%changelog
* Thu Oct  3 2019    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.3-1
- Port to python3.

* Tue Jul  1 2014    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.2-3
- Finegrained Requirements regarding python-twisted (now only core and web are required).
  This is needed to CentOS7-beta which has incomplete python-twisted.

* Thu Nov 28 2013    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.2-2
- New upstream version that fix deprecated md5 module warning.
- Now requires python >= 2.6 (apitest-1.0.1+ doesn't work anymore with old python-elementtreee-1.2.6)

* Thu Nov 28 2013    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.2-1
- New upstream version that fix ElementTreee on python > 2.6 (included in xml.etree)
- spec cleanup (removed unused libvers variable)

* Wed Oct 02 2013    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.1-2
- Removed %dir files directives when they point to system dirs (conflict with filesystem package).

* Fri May 04 2012    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.1-1
- Made BuildRequires: python-elementtree conditional (included in python >= 2.6)

* Thu Jan 12 2006    Thomas Naughton  <naughtont@ornl.gov> 1.0.0-12
- (1.0.0-12) Removed unused profile.d portions.
- Changed to use (what appears) more standard 'python-twisted', doesn't
  cover case where it is v2.0 and twisted-web is seperate, but should be ok. 
