%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

%global upstream_name Sphinx

Name:       python-sphinx
Version:    1.0.8
Release:    3%{?dist}
Summary:    Python documentation generator

Group:      Development/Tools

# Unless otherwise noted, the license for code is BSD
# sphinx/util/stemmer.py Public Domain
# sphinx/pycode/pgen2 Python
# jquery (MIT or GPLv2)
License:    BSD and Public Domain and Python and (MIT or GPLv2)
URL:        http://sphinx.pocoo.org/
Source0:    http://pypi.python.org/packages/source/S/%{upstream_name}/%{upstream_name}-%{version}.tar.gz
# on RHEL6, one of the HTML warnings is slightly different
Patch0:     %{upstream_name}-1.0.8-el6-htmltest-fixwarning.patch

BuildArch:     noarch
BuildRequires: python2-devel >= 2.4
BuildRequires: python-setuptools
BuildRequires: python-docutils
BuildRequires: python-jinja2
BuildRequires: python-nose
# Test dependencies
BuildRequires: texlive-latex
Requires:      python-docutils
Requires:      python-jinja2
Requires:      python-pygments


%description
Sphinx is a tool that makes it easy to create intelligent and
beautiful documentation for Python projects (or other documents
consisting of multiple reStructuredText sources), written by Georg
Brandl. It was originally created to translate the new Python
documentation, but has now been cleaned up in the hope that it will be
useful to many other projects.

Sphinx uses reStructuredText as its markup language, and many of its
strengths come from the power and straightforwardness of
reStructuredText and its parsing and translating suite, the Docutils.

Although it is still under constant development, the following
features are already present, work fine and can be seen "in action" in
the Python docs:

    * Output formats: HTML (including Windows HTML Help) and LaTeX,
      for printable PDF versions
    * Extensive cross-references: semantic markup and automatic links
      for functions, classes, glossary terms and similar pieces of
      information
    * Hierarchical structure: easy definition of a document tree, with
      automatic links to siblings, parents and children
    * Automatic indices: general index as well as a module index
    * Code handling: automatic highlighting using the Pygments highlighter
    * Various extensions are available, e.g. for automatic testing of
      snippets and inclusion of appropriately formatted docstrings.


%package doc
Summary:    Documentation for %{name}
Group:      Documentation
License:    BSD
Requires:   %{name} = %{version}-%{release}


%description doc
Sphinx is a tool that makes it easy to create intelligent and
beautiful documentation for Python projects (or other documents
consisting of multiple reStructuredText sources), written by Georg
Brandl. It was originally created to translate the new Python
documentation, but has now been cleaned up in the hope that it will be
useful to many other projects.

This package contains documentation in reST and HTML formats.


%prep
%setup -q -n %{upstream_name}-%{version}%{?prerel}
%if 0%{?el6}
%patch0 -p1 -b .el6-htmltest-fixwarning
%endif
sed '1d' -i sphinx/pycode/pgen2/token.py

%build
%{__python} setup.py build
pushd doc
make html
make man
rm -rf _build/html/.buildinfo
mv _build/html ..
popd


%install
rm -rf %{buildroot}

%{__python} setup.py install --skip-build --root %{buildroot}


pushd doc
# Deliver man pages
install -d %{buildroot}%{_mandir}/man1
mv _build/man/sphinx-*.1 %{buildroot}%{_mandir}/man1/
popd

# Deliver rst files
rm -rf doc/_build
sed -i 's|python ../sphinx-build.py|/usr/bin/sphinx-build|' doc/Makefile
mv doc reST

# Move language files to /usr/share;
# patch to support this incorporated in 0.6.6
pushd %{buildroot}%{python_sitelib}

for lang in `find sphinx/locale -maxdepth 1 -mindepth 1 -type d -printf "%f "`;
do
  install -d %{buildroot}%{_datadir}/sphinx/locale/$lang
  install -d %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES
  mv sphinx/locale/$lang/LC_MESSAGES/sphinx.js \
     %{buildroot}%{_datadir}/sphinx/locale/$lang/
  mv sphinx/locale/$lang/LC_MESSAGES/sphinx.mo \
    %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/
  rm -rf sphinx/locale/$lang
done
popd
%find_lang sphinx

# Language files; Since these are javascript, it's not immediately obvious to
# find_lang that they need to be marked with a language.
(cd %{buildroot} && find . -name 'sphinx.js') | sed -e 's|^.||' | sed -e \
  's:\(.*/locale/\)\([^/_]\+\)\(.*\.js$\):%lang(\2) \1\2\3:' \
  >> sphinx.lang


%check
make test


%files -f sphinx.lang
%defattr(-,root,root,-)
%doc AUTHORS CHANGES EXAMPLES LICENSE README TODO
%{_bindir}/sphinx-*
%{python_sitelib}/*
%dir %{_datadir}/sphinx/
%dir %{_datadir}/sphinx/locale
%dir %{_datadir}/sphinx/locale/*
%{_mandir}/man1/*

%files doc
%defattr(-,root,root,-)
%doc html reST


%changelog
* Tue Jun 04 2013 James Slagle <jslagle@redhat.com> 1.0.8-3
- new package built with tito

* Thu Oct 25 2012 James Slagle <jslagle@redhat.com> 1.0.8-2
- Add missing tito.props, fix version number (jslagle@redhat.com)

* Thu Oct 25 2012 James Slagle <jslagle@redhat.com> 1.0.9-1
- new package built with tito

* Sat Dec 17 2011 Michel Salim <salimma@fedoraproject.org> - 1.0.8-1
- Update to upstream 1.0.8
- BR on texlive-latex for LaTeX tests

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 18 2011 Toshio Kuratomi <toshio@fedoraproject.org> - 1.0.7-1
- Update to upstream 1.0.7

* Mon Jan 17 2011 Toshio Kuratomi <toshio@fedoraproject.org> - 1.0.6-1
- Update to upstream 1.0.6

* Mon Nov  1 2010 Michel Salim <salimma@fedoraproject.org> - 1.0.4-3
- Fix -doc Makefile to allow regeneration of .rst files

* Mon Nov  1 2010 Michel Salim <salimma@fedoraproject.org> - 1.0.4-2
- Actually include *.js locale files
- Generate manpages

* Fri Sep 17 2010 Michel Salim <salimma@fedoraproject.org> - 1.0.4-1
- Update to 1.0.4
- Remove BuildRoot and %%clean declarations

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 1.0-0.1.b2.1
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Mon May 31 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 1.0-0.2.b2
- Update to 1.0 beta 2
- Fixes problem building html documentation in non-English locales

* Wed May 26 2010 Michel Salim <salimma@fedoraproject.org> - 1.0-0.1.b1
- Update to 1.0 beta 1

* Tue May 25 2010 Michel Salim <salimma@fedoraproject.org> - 0.6.6-1
- Update to 0.6.6

* Fri May 21 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 0.6.5-2
- Few minor tweaks to Gareth's spec file update

* Mon May 10 2010 Gareth Armstrong <gareth.armstrong@hp.com> - 0.6.5-1.hp
- Update to 0.6.5
- Initial import of python-sphinx from Fedora Rawhide for use in HP CMS
- Enforce that Sphinx requires Python 2.4 or later via an explicit BR
- Minor tweaks to spec file
- Move language files to %%{_datadir}, idea borrowed from Debian's sphinx
  package
- Deliver man pages for sphinx-build & sphinx-quickstart
- Deliver rst documentation files to reST directory in doc sub-package
- Add %%check section for Python2 and add BR on python-nose

* Wed Jan 13 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 0.6.4-1
- Update to 0.6.4
- Fixes a problem using autodoc with pylons projects.

* Fri Sep  4 2009 Michel Salim <salimma@fedoraproject.org> - 0.6.3-1
- Update to 0.6.3

* Mon Aug 17 2009 Toshio Kuratomi <toshio@fedoraproject.org> - 0.6.2-1
- Update to 0.6.2 -- upstream bugfix requested inside bz#512438

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jun 05 2009 Luke Macken <lmacken@redhat.com> - 0.6.1-2
- Add a patch to use our own setuptools package

* Fri Apr 17 2009 Michel Salim <salimma@fedoraproject.org> - 0.6.1-1
- Update to 0.6.1

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan  2 2009 Michel Salim <salimma@fedoraproject.org> - 0.5.1-1
- Update to 0.5.1

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.5-2
- Rebuild for Python 2.6

* Mon Nov 24 2008 Michel Salim <salimma@fedoraproject.org> - 0.5-1
- Update to 0.5

* Fri Oct 10 2008 Michel Salim <salimma@fedoraproject.org> - 0.4.3-1
- Update to 0.4.3

* Wed Aug 27 2008 Toshio Kuratomi <toshio@fedoraproject.org> - 0.4.2-1.1
- Fix for EL-5 build.

* Mon Aug 25 2008 Michel Salim <salimma@fedoraproject.org> - 0.4.2-1
- Update to 0.4.2

* Mon May 26 2008 Michel Salim <salimma@fedoraproject.org> - 0.3-1
- Update to 0.3

* Fri May  2 2008 Michel Salim <salimma@fedoraproject.org> - 0.1.61950-3
- Split documentation into subpackage
- Exclude C files (not built by default anyway)

* Wed Apr 16 2008 José Matos <jamatos@fc.up.pt> - 0.1.61950-2
- Build html documentation, include it and include the rst
  documentation.

* Thu Mar 27 2008 Michel Salim <michel.sylvan@gmail.com> 0.1.61950-1
- Initial package
