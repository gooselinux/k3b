
## distro/release specific support
%if 0%{?fedora} > 4 || 0%{?rhel} > 4
%define _with_hal --with-hal
%endif

%if 0%{?fedora} > 6 || 0%{?rhel} >= 6
%define kdelibs3 kdelibs3
%else
%define kdelibs3 kdelibs
BuildRequires: libutempter-devel
%endif

# include sub pkgs
%if 0%{?fedora} > 9 || 0%{?rhel} > 5
%define common 1
%endif
%define devel 1
%define i18n 1

Name:    k3b
Summary: CD/DVD burning application
Epoch:   1
Version: 1.0.5
Release: 13%{?dist}

Group:   Applications/Archiving
License: GPLv2+
URL:     http://www.k3b.org
Source0: http://downloads.sf.net/k3b/k3b-%{version}.tar.bz2
%{?i18n:Source1: http://downloads.sf.net/k3b/k3b-i18n-%{version}.tar.bz2}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
# TODO: bugzilla/document
ExcludeArch: s390 s390x

Source2: k3brc

Patch2: k3b-1.0.3-umount.patch
# manual bufsize (upstream?)
Patch4: k3b-1.0.4-manualbufsize.patch

# upstream patches
# http://bugs.kde.org/151816 , k3b can't reload media for verification
#Patch100: k3b-1.0.4-kde#151816.patch
# http://bugs.kde.org/156684 , alternative to patch100
#Patch101: k3b-1.0.5-kde#156684.patch
# 3rd time is a charm, https://bugs.kde.org/show_bug.cgi?id=156684#c30 
Patch102: reload-for-verification.diff
# put k3b-(iso,cue).desktop to xdg_apps_DATA , see http://bugzilla.redhat.com/419681
# upstreamed 2008-08-27
Patch105: k3b-1.0.5-hidden.patch
# 
Patch106: k3b-1.0.5-desktopfile.patch

BuildRequires: %{kdelibs3}-devel
BuildRequires: desktop-file-utils
BuildRequires: alsa-lib-devel
BuildRequires: audiofile-devel
%{?_with_hal:BuildRequires: dbus-qt-devel hal-devel}
BuildRequires: flac-devel
BuildRequires: gettext
BuildRequires: libdvdread-devel
BuildRequires: libmpcdec-devel
BuildRequires: libmusicbrainz-devel
BuildRequires: libsamplerate-devel
BuildRequires: libsndfile-devel
BuildRequires: libvorbis-devel
BuildRequires: taglib-devel
BuildRequires: zlib-devel

Obsoletes: k3b-extras < 0:1.0-1
Provides:  k3b-extras = %{epoch}:%{version}-%{release} 

%if 0%{?i18n}
# imo, should be packaged separately, tis a shame to duplicate all 
# this noarch build/data on *every* arch.  -- Rex
Obsoletes: %{name}-i18n < %{epoch}:%{version}-%{release}
Provides: %{name}-i18n = %{epoch}:%{version}-%{release}
%endif

%if ! 0%{?devel}
Obsoletes: %{name}-devel < %{epoch}:%{version}-%{release}
%endif

Requires(post): coreutils
Requires(postun): coreutils

Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}
%if 0%{?common}
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%else
Obsoletes: %{name}-common < %{epoch}:%{version}-%{release}
Provides:  %{name}-common = %{epoch}:%{version}-%{release}
%endif

Requires: cdrecord mkisofs
%if 0%{?fedora} > 3 || 0%{?rhel} >= 5
Requires(hint): cdrdao
Requires(hint): dvd+rw-tools
#Requires(hint): gnome-mount
%endif

%description
K3b provides a comfortable user interface to perform most CD/DVD
burning tasks. While the experienced user can take influence in all
steps of the burning process the beginner may find comfort in the
automatic settings and the reasonable k3b defaults which allow a quick
start.

%package common
Summary:  Common files of %{name}
Group:    Applications/Archiving
Requires: %{name} = %{epoch}:%{version}-%{release}
BuildArch: noarch
%description common
%{summary}.

%package libs
Summary: Runtime libraries for %{name}
Group:   System Environment/Libraries
Requires: %{name} = %{epoch}:%{version}-%{release}
%description libs
%{summary}.

%package devel
Summary: Files for the development of applications which will use %{name} 
Group: Development/Libraries
Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}
%description devel
%{summary}.


%prep
%setup -q %{?i18n:-a 1} -n %{name}-%{version}

%patch2 -p1 -b .umount
# set in k3brc too 
%patch4 -p1 -b .manualbufsize

#patch100 -p1 -b .kde#151816
#patch101 -p1 -b .kde#156684
%patch102 -p0 -b .kde#156684
%patch105 -p1 -b .hidden
%patch106 -p1 -b .desktopfile


%build
unset QTDIR || : ; . /etc/profile.d/qt.sh

CFLAGS="%optflags -fno-strict-aliasing" \
CXXFLAGS="%optflags -fno-strict-aliasing" \
%configure \
  --includedir=%{_includedir}/k3b \
  --disable-rpath \
  --enable-new-ldflags \
  --disable-debug --disable-warnings \
  --disable-dependency-tracking --enable-final \
  --with-k3bsetup=no \
  --without-cdrecord-suid-root \
  --with-oggvorbis \
  --with-flac \
  --with-external-libsamplerate \
  --with-libdvdread \
  --with-musicbrainz \
  --with-sndfile \
  --without-ffmpeg --without-lame --without-libmad \
  --with-musepack \
  %{?_with_hal} %{!?_with_hal:--without-hal} 

make %{?_smp_mflags}

%if 0%{?i18n}
# Build for i18n tarball
pushd %{name}-i18n-%{version}
%configure
make %{?_smp_mflags}
popd
%endif


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

%if 0%{?i18n}
make install DESTDIR=%{buildroot} -C %{name}-i18n-%{version}
%endif

%{__install} -D -m 644 -p %{SOURCE2} %{buildroot}%{_datadir}/config/k3brc

# remove the .la files
rm -f %{buildroot}%{_libdir}/libk3b*.la 

# remove i18n for Plattdeutsch (Low Saxon)
rm -fr %{buildroot}%{_datadir}/locale/nds

%if 0%{?i18n}
%find_lang k3b --with-kde
%find_lang k3bsetup 
%find_lang libk3b
%find_lang libk3bdevice
cat k3b.lang k3bsetup.lang libk3b.lang libk3bdevice.lang >> all.lang
%endif

# unpackaged files
%if ! 0%{?devel}
rm -rf %{buildroot}%{_includedir}/k3b/
rm -f  %{buildroot}%{_libdir}/libk3b*.so
%endif


%check
desktop-file-validate %{buildroot}%{_datadir}/applications/kde/k3b-cue.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/kde/k3b-iso.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/kde/k3b.desktop


%clean
rm -rf %{buildroot}


%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post %{?common:common}
touch --no-create %{_datadir}/icons/hicolor ||:

%postun %{?common:common}
if [ $1 -eq 0 ] ; then
touch --no-create %{_datadir}/icons/hicolor &> /dev/null
gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :
update-desktop-database -q &> /dev/null
fi

%posttrans %{?common:common}
gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :
update-desktop-database -q &> /dev/null


%files %{?!common:-f all.lang}
%defattr(-,root,root,-)
%doc AUTHORS README COPYING TODO ChangeLog
%{_bindir}/k3b
%{_libdir}/kde3/*.so
%{_libdir}/kde3/*.la

%if 0%{?common}
%files common -f all.lang
%defattr(-,root,root,-)
%endif
%{_datadir}/applications/kde/k3b-cue.desktop
%{_datadir}/applications/kde/k3b-iso.desktop
%{_datadir}/applications/kde/k3b.desktop
%{_datadir}/apps/k3b/
%{_datadir}/apps/konqueror/servicemenus/*.desktop
%{_datadir}/apps/konqsidebartng/virtual_folders/services/videodvd.desktop
%{_datadir}/config/k3brc
%{_datadir}/mimelnk/application/x-k3b.desktop
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/services/kfile_k3b.desktop
%{_datadir}/services/videodvd.protocol
%{_datadir}/sounds/k3b_*.wav

%files libs
%defattr(-,root,root,-)
%{_libdir}/libk3b.so.3*
%{_libdir}/libk3bdevice.so.5*

%if 0%{?devel}
%files devel
%defattr(-,root,root,-)
%{_includedir}/k3b/
%{_libdir}/libk3b.so
%{_libdir}/libk3bdevice.so
%endif


%changelog
* Mon Jul 19 2010 Radek Novacek <rnovacek@redhat.com> 1:1.0.5-13
- Fixed overridden CFLAGS
- Resolves: #596179

* Tue Jun 15 2010 Radek Novacek <rnovacek@redhat.com> 1:1.0.5-12
- Added "-fno-strict-aliasing" flag
- Added missing %% to the summary of k3b-common
- Resolves: #596179

* Mon Feb 22 2010 Roman Rakus <rrakus@redhat.com> - 1:1.0.5-11
- Removed not needed patches.
- added defattr for common subpackage

* Fri Nov 13 2009 Dennis Gregorovic <dgregor@redhat.com> - 1:1.0.5-10.1
- Fix conditional for RHEL

* Sat Sep 26 2009 Rex Dieter <rdieter@fedoraproject.org> - 1:1.0.5-10
- Epoch: 1 (increment Release too, to minimize confusion)
- -common: noarch subpkg

* Sat Jun 13 2009 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.5-9
- another try at a reload patch that works (kde#156684#c30)
- optimize scriptlets

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.0.5-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jan 21 2009 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.5-7
- Summary: omit "for KDE"
- add rhel portability to .spec

* Wed Oct 01 2008 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.5-6
- revert libdvdread header changes, fix build (#465115)
- (re)enable -devel on f9

* Wed Aug 27 2008 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.5-5
- resurrect -devel (!=f9), grow -libs (f10+, #341651)
- avoid auto*foo
- fix build on rawhide (libdvdread header changes)
- conditionalize i18n bits

* Thu Jul 31 2008 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.5-4
- try alternative fix for tray eject/reload (kde#156684)

* Mon Jun 30 2008 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.5-3
- No association k3b with .iso files in gnome (#419681)
- scriptlet deps
- cleanup doc/HTML

* Sat May 31 2008 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.5-2
- (re)enable reload patch

* Tue May 27 2008 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.5-1
- k3b-1.0.5
- k3brc: set manual buffer size here
- omit reload patch (for now), to verify if still needed.

* Wed May  7 2008 Roman Rakus <rrakus@redhat.cz> - 0:1.0.4-9
- Fix doc dir (#238070), patch by Alain PORTAL (aportal@univ-montp2.fr)

* Tue Apr 22 2008 Roman Rakus <rrakus@redhat.cz> - 0:1.0.4-8
- Use manual buffer size by default (#220481)

* Tue Feb 19 2008 Rex Dieter <rdieter@fedoraproject.org> - 0:1.0.4-7
- f9+: Obsoletes: k3b-devel (#429613)

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.0.4-6
- Autorebuild for GCC 4.3

* Sat Dec 08 2007 Rex Dieter <rdieter[AT]fedoraproject.org> - 0:1.0.4-5
- patch for "k3b can't reload media for verification" (kde#151816)
- BR: kdelibs3-devel

* Wed Nov 21 2007 Adam Tkac <atkac redhat com> - 0:1.0.4-3
- rebuild against new libdvdread

* Mon Nov 05 2007 Rex Dieter <rdieter[AT]fedorproject.org> - 0:1.0.4-2
- k3b-1.0.4
- omit -devel subpkg (f9+), fixes multiarch conflicts (#341651)

* Fri Aug 17 2007 Harald Hoyer <harald@redhat.com> - 0:1.0.3-3
- changed license tag to GPLv2+

* Fri Aug  3 2007 Harald Hoyer <harald@redhat.com> - 0:1.0.3-2
- added gnome-umount options

* Fri Jul 27 2007 Harald Hoyer <harald@redhat.com> - 0:1.0.3-1
- version 1.0.3
- added gnome-umount patch

* Sat Jun 23 2007 Rex Dieter <rdieter[AT]fedoraproject.org> - 0:1.0.2-1
- k3b-1.0.2

* Sat Jun 16 2007 Rex Dieter <rdieter[AT]fedoraproject.org> - 0:1.0.1-4
- k3b-iso.desktop,k3b-cue.desktop: +NoDisplay=True (#244513)

* Wed Jun 13 2007 Rex Dieter <rdieter[AT]fedoraproject.org> - 0:1.0.1-3
- --without-cdrecord-suid-root

* Wed Jun 06 2007 Rex Dieter <rdieter[AT]fedoraproject.org> - 0:1.0.1-2
- respin (for libmpcdec)

* Wed May 30 2007 Rex Dieter <rdieter[AT]fedoraproject.org> - 0:1.0.1-1
- k3b-1.0.1
- include icon/mime scriptlets
- cleanup/simplify BR's
- optimize %%configure
- restore applnk/.hidden bits

* Wed Apr 11 2007 Harald Hoyer <harald@redhat.com> - 0:1.0-1
- version k3b-1.0
- provide/obsolete k3b-extras

* Thu Feb 15 2007 Harald Hoyer <harald@redhat.com> - 0:1.0.0-0.rc6.1
- version k3b-1.0rc6

* Wed Feb  7 2007 Harald Hoyer <harald@redhat.com> - 0:1.0.0-0.rc5.1
- version k3b-1.0rc5

* Wed Jan 17 2007 Harald Hoyer <harald@redhat.com> - 0:1.0.0-0.rc4.1
- version k3b-1.0rc4

* Thu Oct 26 2006 Harald Hoyer <harald@backslash.home> - 0:1.0.0-0.pre2.1
- version 1.0pre2

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0:0.12.15-3.1.1
- rebuild

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0:0.12.15-3.1
- rebuild

* Mon Jun 12 2006 Harald Hoyer <harald@redhat.com> - 0:0.12.15-3
- fixed symlinks

* Tue May 02 2006 Harald Hoyer <harald@redhat.com> 0:0.12.15-1
- version 0.12.15

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0:0.12.10-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0:0.12.10-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 24 2006 Harald Hoyer <harald@redhat.com> 0:0.12.10-2
- removed .la files (#172638)

* Tue Dec 20 2005 Harald Hoyer <harald@redhat.com> 0:0.12.10-1
- version 0.12.10

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Dec 06 2005 Harald Hoyer <harald@redhat.com> 0:0.12.8-1
- version 0.12.8

* Wed Sep 21 2005 Harald Hoyer <harald@redhat.com> 0:0.12.4-0.a.1
- version 0.12.4a

* Thu Jul 14 2005 Harald Hoyer <harald@redhat.com> 0:0.12.2-1
- version 0.12.2
- ported some patches

* Wed Jul 11 2005 Harald Hoyer <harald@redhat.com> 0:0.11.23-2
- added "dvd+rw-tools cdrdao" to Requires

* Thu Apr  7 2005 Petr Rockai <prockai@redhat.com> - 0:0.11.23-3
- fix statfs usage (as per issue 65935 from IT)

* Wed Mar 30 2005 Harald Hoyer <harald@redhat.com> 0:0.11.23-1
- update to 0.11.23

* Fri Mar 25 2005 David Hill <djh[at]ii.net> 0:0.11.22-1
- update to 0.11.22

* Tue Mar 08 2005 Than Ngo <than@redhat.com> 0:0.11.17-2
- rebuilt against gcc-4

* Tue Oct 05 2004 Harald Hoyer <harald@redhat.com> 0:0.11.17-1
- version 0.11.17
- revert the dao -> tao change
- add the suid feature to every app automatically

* Tue Oct 05 2004 Harald Hoyer <harald@redhat.com> 0:0.11.14-2
- fixed version string parsing, which fixes bug 134642

* Wed Sep 01 2004 Harald Hoyer <harald@redhat.com> 0:0.11.14-1
- added k3b-0.11.14-rdrw.patch for kernel >= 2.6.8
- update to 0.11.14

* Fri Jun 25 2004 Bill Nottingham <notting@redhat.com> 0:0.11.12-2
- update to 0.11.12

* Mon Jun 21 2004 Than Ngo <than@redhat.com> 0:0.11.11-1
- update to 0.11.11
- add prereq:/sbin/ldconfig

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon May 31 2004 Justin M. Forbes <64bit_fedora@comcast.net> - 0.11.10-1
- remove unnecesary [ -z "$QTDIR" ] check
- Update to 0.11.10 upstream 
- remove qt-devel BuildRequires, implied with kde-devel
- remove ldconfig Requires, implied
- remove i18n docbook patch, fixed upstream.

* Fri May 28 2004 Bill Nottingham <notting@redhat.com> - 0.11.9-5
- fix burning on SCSI CD-ROMS (#122096)

* Thu May 13 2004 Than Ngo <than@redhat.com> 0.11.9-4
- get rid of rpath

* Fri Apr 16 2004 Bill Nottingham <notting@redhat.com> - 0.11.9-3
- nuke k3bsetup
- use %%find_lang

* Thu Apr 15 2004 Justin M. Forbes <64bit_fedora@comcast.net> - 0.11.9-2
- Clean up i18n build to make improve maintainability

* Wed Apr 7 2004 Justin M. Forbes <64bit_fedora@comcast.net> - 0.11.9-1
- Update to 0.11.9 upstream
- Spec Cleanup for Fedora Core 2

* Wed Mar 18 2004 Justin M. Forbes <64bit_fedora@comcast.net> - 0.11.6-1
- Initial packaging of 0.11.6 for Fedora Core 2
- remove mp3 plugin build options
- add i18n package
- clean up for kde 3.2/FC2 target


