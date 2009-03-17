
%define lib_major	2
%define lib_name_orig	%{package_prefix}%mklibname binutils
%define lib_name	%{lib_name_orig}%{lib_major}

# Allow SPU support for native PowerPC arches, not cross env packages
%define spu_arches	ppc ppc64

# Define if building a cross-binutils
%define build_cross	0
%{expand: %{?cross:	%%global build_cross 1}}

%if %{build_cross}
%define target_cpu	%{cross}
%define target_platform	%{target_cpu}-linux
%if "%{target_cpu}" == "spu"
%define target_platform	%{target_cpu}-unknown-elf
%endif
%define program_prefix	%{target_platform}-
%define package_prefix	cross-%{target_cpu}-
%else
%define target_cpu	%{_target_cpu}
%define target_platform	%{_target_platform}
%define program_prefix	%{nil}
%define package_prefix	%{nil}
%endif

%define arch		%(echo %{target_cpu}|sed -e "s/\(i.86\|athlon\)/i386/" -e "s/amd64/x86_64/" -e "s/\(sun4.*\|sparcv[89]\)/sparc/")
%define isarch()	%(case %{arch} in (%1) echo 1;; (*) echo 0;; esac)

Summary:	GNU Binary Utility Development Utilities
Name:		%{package_prefix}binutils
Version:	2.19.51.0.2
Release:	%manbo_mkrel 1
License:	GPLv3+
Group:		Development/Other
URL:		http://sources.redhat.com/binutils/
Source0:	http://ftp.kernel.org/pub/linux/devel/binutils/binutils-%{version}.tar.bz2
Source1:	build_cross_binutils.sh
Source2:	spu_ovl.o
Source3:	embedspu.sh
Buildroot:	%{_tmppath}/%{name}-%{version}-root
%if "%{name}" == "binutils"
Requires:	%{lib_name} = %{version}-%{release}
Requires(post):	info-install
Requires(preun):info-install
%endif
Conflicts:	gcc-c++ < 3.2.3-1mdk
BuildRequires:	autoconf automake bison flex gcc gettext texinfo
BuildRequires:	dejagnu zlib-devel
# make check'ing requires libdl.a
BuildRequires:	glibc-static-devel

# Fedora patches:
Patch01:	binutils-2.19.50.0.1-libtool-lib64.patch
Patch02:	binutils-2.19.50.0.1-ppc64-pie.patch
Patch03:	binutils-2.19.50.0.1-ia64-lib64.patch
Patch04:	binutils-2.19.51.0.2-symbolic-envvar-revert.patch
# We don't want this one!
#Patch05:	binutils-2.19.50.0.1-version.patch
Patch06:	binutils-2.19.50.0.1-set-long-long.patch
Patch07:	binutils-2.19.50.0.1-build-id.patch

# Mandriva patches
Patch21:	binutils-2.19.50.0.1-linux32.patch
Patch22:	binutils-2.19.50.0.1-mips-string_literal-fixes.patch
Patch23:	binutils-2.19.51.0.2-mips-gas.patch
Patch24:	binutils-2.19.51.0.2-mips-ihex.patch
Patch25:	binutils-2.19.51.0.2-mips-ls2f_fetch_fix.patch

%description
Binutils is a collection of binary utilities, including:

   * ar: creating modifying and extracting from archives
   * nm: for listing symbols from object files
   * objcopy: for copying and translating object files
   * objdump: for displaying information from object files
   * ranlib: for generating an index for the contents of an archive
   * size: for listing the section sizes of an object or archive file
   * strings: for listing printable strings from files
   * strip: for discarding symbols (a filter for demangling encoded C++ symbols
   * addr2line: for converting addresses to file and line
   * nlmconv: for converting object code into an NLM

Install binutils if you need to perform any of these types of actions on
binary files.  Most programmers will want to install binutils.

%ifarch %{spu_arches}
%package -n	spu-binutils
Summary:	GNU Binary Utility Development Utilities for Cell SPU
Group:		Development/Other
Requires:	%{lib_name} = %{version}-%{release}

%description -n	spu-binutils
This package contains the binutils with Cell SPU support.
%endif

%package -n	%{lib_name}
Summary:	Main library for %{name}
Group:		Development/Other
Provides:	%{lib_name_orig}

%description -n	%{lib_name}
This package contains the library needed to run programs dynamically
linked with binutils.

%package -n	%{lib_name}-devel
Summary:	Main library for %{name}
Group:		Development/Other
Requires:	%{lib_name} = %{version}-%{release}
Provides:	%{lib_name_orig}-devel, %{name}-devel

%description -n	%{lib_name}-devel
This package contains the library needed to run programs dynamically
linked with binutils.

This is the development headers for %{lib_name}

%prep
%setup -q -n binutils-%{version}
%patch01 -p0 -b .libtool-lib64~
%patch02 -p0 -b .ppc64-pie~
%ifarch ia64
%if "%{_lib}" == "lib64"
%patch03 -p0 -b .ia64-lib64~
%endif
%endif
%patch04 -p1 -b .symbolic-envvar-revert~
#%patch05 -p0 -b .version~
%patch06 -p0 -b .set-long-long~
%patch07 -p0 -b .build-id~

%patch21 -p1 -b .linux32~
%patch22 -p1 -b .string_literal~
%patch23 -p1 -b .mips_gas~
%patch24 -p1 -b .mips_ihex~
%patch25 -p1 -b .mips_l2sf_fetch_fix~

# for boostrapping, can be rebuilt afterwards in --enable-maintainer-mode
cp %{SOURCE2} ld/emultempl/

%build
# Additional targets
ADDITIONAL_TARGETS=""
case %{target_cpu} in
ppc | powerpc)
  ADDITIONAL_TARGETS="powerpc64-%{_target_vendor}-%{_target_os}"
  ;;
ppc64)
  ADDITIONAL_TARGETS=""
  ;;
ia64)
  ADDITIONAL_TARGETS="i586-%{_target_vendor}-%{_target_os}"
  ;;
i*86 | athlon*)
  ADDITIONAL_TARGETS="x86_64-%{_target_vendor}-%{_target_os}"
  ;;
sparc*)
  ADDITIONAL_TARGETS="sparc64-%{_target_vendor}-%{_target_os}"
  ;;
mipsel)
  ADDITIONAL_TARGETS="mips64el-%{_target_vendor}-%{_target_os}"
  ;;
mips)
  ADDITIONAL_TARGETS="mips64-%{_target_vendor}-%{_target_os}"
  ;;
esac
%ifarch %{spu_arches}
if [[ -n "$ADDITIONAL_TARGETS" ]]; then
  ADDITIONAL_TARGETS="$ADDITIONAL_TARGETS,spu-unknown-elf"
else
  ADDITIONAL_TARGETS="spu-unknown-elf"
fi
%endif
if [[ -n "$ADDITIONAL_TARGETS" ]]; then
  TARGET_CONFIG="$TARGET_CONFIG --enable-targets=$ADDITIONAL_TARGETS"
fi

case %{target_cpu} in
ppc | powerpc | i*86 | athlon* | sparc* | mips*)
  TARGET_CONFIG="$TARGET_CONFIG --enable-64-bit-bfd"
  ;;
esac

%if "%{name}" != "binutils"
%define _program_prefix %{program_prefix}
TARGET_CONFIG="$TARGET_CONFIG --target=%{target_platform}"
%endif

# Don't build shared libraries in cross binutils
%if "%{name}" == "binutils"
TARGET_CONFIG="$TARGET_CONFIG --enable-shared"
%endif

# Binutils comes with its own custom libtool
# [gb] FIXME: but system libtool also works and has relink fix
%define __libtoolize /bin/true

# Build with -Wno-error
export CFLAGS="$RPM_OPT_FLAGS -Wno-error"

# Build main binaries
rm -rf objs
mkdir objs
pushd objs
CONFIGURE_TOP=.. %configure $TARGET_CONFIG
%make tooldir=%{_prefix}
popd

# Build alternate binaries (spu-gas in particular)
case "$ADDITIONAL_TARGETS," in
%ifarch %{spu_arches}
*spu-*-elf,*)
  ALTERNATE_TARGETS="spu-unknown-elf"
  ;;
%endif
*)
  ;;
esac
if [[ -n "$ALTERNATE_TARGETS" ]]; then
  for target in $ALTERNATE_TARGETS; do
    cpu=`echo "$target" | sed -e "s/-.*//"`
    rm -rf objs-$cpu
    mkdir objs-$cpu
    pushd objs-$cpu
    CONFIGURE_TOP=.. %configure --enable-shared --target=$target --program-prefix=$cpu-
    # make sure we use the fully built libbfd & libopcodes libs
    # XXX could have been simpler to just pass $ADDITIONAL_TARGETS
    # again to configure and rebuild all of those though...
    for dso in bfd opcodes; do
    %make all-$dso
    rm -f $dso/.libs/lib$dso-%{version}.so
    ln -s ../../../objs/$dso/.libs/lib$dso-%{version}.so $dso/.libs/
    done
    %make all-binutils all-gas all-ld
    popd
  done
fi

%check
# All Tests must pass on x86 and x86_64
echo ====================TESTING=========================
%if %isarch i386|x86_64|ppc|ppc64|spu
%make -C objs check
[[ -d objs-spu ]] && \
%make -C objs-spu check-gas
%else
%make -C objs -k check || echo make check failed
%endif
echo ====================TESTING END=====================

logfile="%{name}-%{version}-%{release}.log"
rm -f $logfile; find . -name "*.sum" | xargs cat >> $logfile

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_prefix}
%makeinstall_std -C objs

%if "%{name}" == "binutils"
make -C objs prefix=$RPM_BUILD_ROOT%{_prefix} infodir=$RPM_BUILD_ROOT%{_infodir} install-info
install -m 644 include/libiberty.h $RPM_BUILD_ROOT%{_includedir}/
%if %isarch mips|mipsel|mips64|mips64el
install -m 644 objs/libiberty/libiberty.a $RPM_BUILD_ROOT%{_libdir}/
# Ship with the PIC libiberty
%else
install -m 644 objs/libiberty/pic/libiberty.a $RPM_BUILD_ROOT%{_libdir}/
%endif
rm -rf $RPM_BUILD_ROOT%{_prefix}/%{_target_platform}/
%else
rm -f  $RPM_BUILD_ROOT%{_libdir}/libiberty.a
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -rf $RPM_BUILD_ROOT%{_prefix}/%{target_platform}/lib/ldscripts/
rm -f  $RPM_BUILD_ROOT%{_prefix}/%{_target_platform}/%{target_cpu}-linux/lib/*.la
%endif

rm -f $RPM_BUILD_ROOT%{_mandir}/man1/{dlltool,nlmconv,windres}*
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
%if "%{name}" != "binutils"
rm -rf $RPM_BUILD_ROOT%{_datadir}/locale/
%endif

%find_lang binutils
%find_lang gas
%find_lang ld
%find_lang gprof
cat gas.lang >> binutils.lang
cat ld.lang >> binutils.lang
cat gprof.lang >> binutils.lang

%find_lang opcodes
%find_lang bfd
cat opcodes.lang >> libbinutils.lang
cat bfd.lang >> libbinutils.lang

# Alternate binaries
[[ -d objs-spu ]] && {
destdir=`mktemp -d`
make -C objs-spu DESTDIR=$destdir install-binutils install-gas install-ld
mv $destdir%{_bindir}/spu-* $RPM_BUILD_ROOT%{_bindir}/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/spu/bin
mv $destdir%{_prefix}/spu-unknown-elf/bin/* $RPM_BUILD_ROOT%{_prefix}/spu/bin/
rm -rf $destdir
cat > $RPM_BUILD_ROOT%{_bindir}/ppu-as << EOF
#!/bin/sh
exec %{_bindir}/as -mcell -maltivec \${1+"\$@"}
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/ppu-as
install -m 755 %{SOURCE3} $RPM_BUILD_ROOT%{_bindir}/embedspu
}

%clean
rm -rf $RPM_BUILD_ROOT

%if "%{name}" == "binutils"
%post
%_install_info as.info
%_install_info bfd.info
%_install_info binutils.info
%_install_info gasp.info
%_install_info gprof.info
%_install_info ld.info
%_install_info standards.info
%endif

%if "%{name}" == "binutils"
%preun
%_remove_install_info as.info
%_remove_install_info bfd.info
%_remove_install_info binutils.info
%_remove_install_info gasp.info
%_remove_install_info gprof.info
%_remove_install_info ld.info
%_remove_install_info standards.info
%endif

%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%files -f binutils.lang
%defattr(-,root,root)
%doc README
%{_bindir}/%{program_prefix}addr2line
%{_bindir}/%{program_prefix}ar
%{_bindir}/%{program_prefix}as
%{_bindir}/%{program_prefix}c++filt
%{_bindir}/%{program_prefix}gprof
%{_bindir}/%{program_prefix}ld
%{_bindir}/%{program_prefix}nm
%{_bindir}/%{program_prefix}objcopy
%{_bindir}/%{program_prefix}objdump
%{_bindir}/%{program_prefix}ranlib
%{_bindir}/%{program_prefix}readelf
%{_bindir}/%{program_prefix}size
%{_bindir}/%{program_prefix}strings
%{_bindir}/%{program_prefix}strip
%ifarch %{spu_arches}
%{_bindir}/ppu-as
%endif
%{_mandir}/man1/*
%if "%{name}" == "binutils"
%{_infodir}/*info*
%else
%{_prefix}/%{target_platform}/bin/*
%endif

%ifarch %{spu_arches}
%files -n spu-binutils
%defattr(-,root,root)
%doc README
%{_bindir}/spu-*
%{_bindir}/embedspu
%dir %{_prefix}/spu/bin
%{_prefix}/spu/bin
%endif

%if "%{name}" == "binutils"
%files -n %{lib_name} -f libbinutils.lang
%defattr(-,root,root)
%doc README
%{_libdir}/libbfd-%{version}*.so
%{_libdir}/libopcodes-%{version}*.so
%endif

%if "%{name}" == "binutils"
%files -n %{lib_name}-devel
%defattr(-,root,root)
%doc README
%{_includedir}/*
%{_libdir}/libbfd.a
%{_libdir}/libbfd.so
%{_libdir}/libopcodes.a
%{_libdir}/libopcodes.so
%{_libdir}/libiberty.a
%endif
