%define name apitest
%define version 1.0.2
%define release 2
#define _unpackaged_files_terminate_build 0

#{expand:%%define py_ver %(python -V 2>&1| awk '{print $2}')}
#{expand:%%define py_libver %(python -V 2>&1| awk '{print $2}'|cut -d. -f1-2)}

Summary: A test driver application. 
Name: %{name}
Version: %{version}
Release: %{release}
License: LGPL
Group: Development/Libraries
Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root

# Architecture
BuildArch: noarch

Requires: python-twisted >= 1.3
BuildRequires: python-twisted >= 1.3

#%if 0%(echo %{?python_version}|tr '.' '0') < 206
#Requires: python-elementtree
#BuildRequires: python-elementtree
#%endif

Requires: python >= 2.6
BuildRequires: python >= 2.6


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
echo "python%{python_version}"
echo "buildroot=%{buildroot}"
#define sitepackages %{_prefix}/%{_lib}/python%{py_libver}/site-packages
#python%{py_libver} setup.py build


%install
echo "==========[ INSTALL ]=================================="
echo %{buildroot}
#define doc_prefix /usr/share/doc/apitest
%{__python} setup.py install --no-compile --prefix=%{buildroot}%{_prefix}/ --install-lib=%{buildroot}%{python_sitelib}
###--install-data=%{buildroot}/%{doc_prefix}


%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog doc/COPYING.LGPLv2.1
%{python_sitelib}/*
%{_docdir}/*
%{_bindir}/*


%clean
echo "cleaning $RPM_BUILD_ROOT"
rm -rf $RPM_BUILD_ROOT

%changelog
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
