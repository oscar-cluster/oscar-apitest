%define name apitest
%define version 1.0.5
%define release 1
#define _unpackaged_files_terminate_build 0
%define is_suse %(grep -E "(suse)" /etc/os-release > /dev/null 2>&1 && echo 1 || echo 0)


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

%if 0%{?is_suse}
BuildRequires: python3-Twisted >= 18.9.0
BuildRequires: python3-zope.interface >= 5.0
Requires: python3-Twisted >= 18.9.0
Requires: python3-zope.interface >= 5.0
%else
BuildRequires: python3-twisted >= 18.9.0
BuildRequires: python3-zope-interface >= 5.0
Requires: python3-twisted >= 18.9.0
Requires: python3-zope-interface >= 5.0
%endif

Requires:       python3 >= 3.4
Requires:       python3-zope-interface
BuildRequires:  python3 >= 3.4
BuildRequires:  python3-wheel
BuildRequires:  python3-setuptools >= 61.0
BuildRequires:  python3-setuptools-wheel >= 61.0


%description
APItest version %{version}.
A test driver application.

%prep
%autosetup -n %{name}-%{version}

%build
%{__python3} -m build --wheel

%install
%{__python3} -m pip install \
  --no-compile \
  --prefix=%{buildroot}%{_prefix} \
  --no-deps \
  dist/apitest-%{version}-*.whl

%files
%doc AUTHORS COPYING ChangeLog doc/*
%doc samples
%{python3_sitelib}/*
%{_bindir}/*

%clean
echo "cleaning $RPM_BUILD_ROOT"
rm -rf $RPM_BUILD_ROOT

%changelog
* Tue Jul 15 2025    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.5-1
- don't use deprecated setup.py build.

* Mon Nov 08 2021    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.4-1
- Fix python3 port (2to3 forgot to replace the file() builtin).

* Thu May 21 2020    Olivier Lahaye <olivier.lahaye@cea.fr> 1.0.3-2
- Add support for SuSE and openSuSE Leap.

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
