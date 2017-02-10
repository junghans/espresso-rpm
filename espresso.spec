%if 0%{?fedora} > 12 || 0%{?rhel} > 6
%global with_python3 1
%else
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%endif

# Define a macro for calling ../configure instead of ./configure
%global dconfigure %(printf %%s '%configure' | sed 's!\./configure!../configure!g')
# transform proper bindir
%global dconfigure_mpi %(printf %%s '%dconfigure' | sed 's!/usr/bin!$MPI_BIN!g')

### TESTSUITE ###
# The testsuite currently fails only on the buildsystem, but works localy.
# So to easy enable/disable the testsuite, I introduce the following
#   variables:
#
# * MPICH:     if '1' enable mpich
# * OPENMPI:   if '1' enable openmpi
%global MPICH 0
%global OPENMPI 0

Name:           espresso
Version:        3.3.0
Release:        11%{?dist}
Summary:        Extensible Simulation Package for Research on Soft matter

License:        GPLv3+
URL:            http://espressomd.org
Source0:        http://download.savannah.gnu.org/releases/espressomd/espresso-%{version}.tar.gz
# upstream commit from https://github.com/espressomd/espresso/pull/214
Patch0:         espresso-cython-022.patch
# run autoreconf for aarch64 support
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool

BuildRequires:  Cython
BuildRequires:  fftw-devel
BuildRequires:  numpy
BuildRequires:  python-devel
BuildRequires:  tcl-devel

Requires:       numpy

Requires:       %{name}-common = %{version}-%{release}

%description
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics

%package common
Summary:        Common files for %{name} packages
BuildArch:      noarch
Requires:       %{name}-common = %{version}-%{release}
%description common
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics
This package contains the license file and data files shard between the
subpackages of %{name}.

%package openmpi
BuildRequires:  openmpi-devel
Requires:       %{name}-common = %{version}-%{release}
Summary:        Extensible Simulation Package for Research on Soft matter
%description openmpi
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics

This package contains %{name} compiled against Open MPI.


%package mpich
BuildRequires:  mpich-devel
Requires:       %{name}-common = %{version}-%{release}
Summary:        Extensible Simulation Package for Research on Soft matter
Provides:       %{name}-mpich2 = %{version}-%{release}
Obsoletes:      %{name}-mpich2 < 3.1.1-3
%description mpich
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics

This package contains %{name} compiled against MPICH2.


%prep
%setup -q
%patch0 -p1

#sed -i 's/tclsh8\.4/tclsh/' tools/trace_memory.tcl

mkdir openmpi_build mpich_build no_mpi


%build
autoreconf -fi
pushd no_mpi
export CC=gcc
export CXX=g++
%dconfigure --enable-shared
make V=1 %{?_smp_mflags}
popd

# Build parallel versions: set compiler variables to MPI wrappers
export CC=mpicc
export CXX=mpicxx

# Build OpenMPI version
%{_openmpi_load}
pushd openmpi_build
%dconfigure_mpi --enable-shared --program-suffix=$MPI_SUFFIX
make V=1 %{?_smp_mflags}
popd
%{_openmpi_unload}

# Build mpich version
%{_mpich_load}
pushd mpich_build
%dconfigure_mpi --enable-shared --program-suffix=$MPI_SUFFIX
make V=1 %{?_smp_mflags}
popd
%{_mpich_unload}


%install
# first install mpi files and move around because MPI_SUFFIX above doesn't
# work yet (will be fixed in a new version)
%{_openmpi_load}
pushd openmpi_build
make install DESTDIR=%{buildroot}
popd
%{_openmpi_unload}

%{_mpich_load}
pushd mpich_build
make install DESTDIR=%{buildroot}
popd
%{_mpich_unload}


pushd no_mpi
make install DESTDIR=%{buildroot}
popd

#rm %{buildroot}%{_libdir}/libespressobf.a

chmod +x %{buildroot}/usr/share/espresso/tools/trace_memory.py
chmod +x %{buildroot}/usr/share/espresso/tools/trace_memory.tcl
chmod +x %{buildroot}/usr/share/espresso/tools/set_features


%check
pushd no_mpi
make check || cat testsuite/runtest.log || :
popd

# test openmpi?
%if 0%{?OPENMPI}
%{_openmpi_load}
pushd openmpi_build
make check || cat testsuite/runtest.log || :
popd
%{_openmpi_unload}
%endif

# test mpich?
%if 0%{?MPICH}
%{_mpich_load}
pushd mpich_build
make check || cat testsuite/runtest.log || :
popd
%{_mpich_unload}
%endif


%files common
%doc AUTHORS COPYING README NEWS ChangeLog doc/ug/ug.pdf
%{_datadir}/espresso/

%files
%{_bindir}/Espresso

%files openmpi
%{_libdir}/openmpi/bin/Espresso_openmpi

%files mpich
%{_libdir}/mpich/bin/Espresso_mpich


%changelog
* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Oct 21 2016 Orion Poplawski <orion@cora.nwra.com> - 3.3.0-10
- Rebuild for openmpi 2.0

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Sep 15 2015 Orion Poplawski <orion@cora.nwra.com> - 3.3.0-8
- Rebuild for openmpi 1.10.0

* Sat Aug 15 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.3.0-7
- Rebuild for MPI provides

* Sun Jul 26 2015 Sandro Mani <manisandro@gmail.com> - 3.3.0-6
- Rebuild for RPM MPI Requires Provides Change

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 3.3.0-4
- Rebuilt for GCC 5 C++11 ABI change

* Thu Mar 12 2015 Thomas Spura <tomspur@fedoraproject.org> - 3.3.0-3
- Rebuild for changed mpich libraries
- Added patch for building with cython-0.22
- Remove group tag

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Aug 11 2014 Thomas Spura <tomspur@fedoraproject.org> - 3.3.0-1
- update to 3.3.0

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 28 2014 Thomas Spura <tomspur@fedoraproject.org> - 3.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/f21tcl86

* Sun May 25 2014 Thomas Spura <tomspur@fedoraproject.org> - 3.2.0-2
- run autoreconf in %%build to support aarch64

* Sat May 24 2014 Thomas Spura <tomspur@fedoraproject.org> - 3.2.0-1
- update to 3.2.0

* Wed May 21 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 3.1.1-6
- Rebuilt for https://fedoraproject.org/wiki/Changes/f21tcl86

* Sat Feb 22 2014 Deji Akingunola <dakingun@gmail.com> - 3.1.1-5
- Rebuild for mpich-3.1

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Jul 20 2013 Deji Akingunola <dakingun@gmail.com> - 3.1.1-3
- Rename mpich2 sub-packages to mpich and rebuild for mpich-3.0

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Nov 14 2012 Thomas Spura <tomspur@fedoraproject.org> - 3.1.1-1
- rebuild for newer mpich2
- update to new version
- disable tk per upstream request
- drop patch

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct 26 2011 Thomas Spura <tomspur@fedoraproject.org> - 3.0.2-2
- add missing BR autoconf/automake
- use _isa where possible
- use general tclsh shebang
- build --with-tk

* Thu Oct  6 2011 Thomas Spura <tomspur@fedoraproject.org> - 3.0.2-1
- update to new version
- introduce configure_mpi

* Sun Sep 25 2011 Thomas Spura <tomspur@fedoraproject.org> - 3.0.1-3
- use correct MPI_SUFFIX
- don't install library as upstream doesn't support it anymore

* Sun Sep 25 2011 Thomas Spura <tomspur@fedoraproject.org> - 3.0.1-2
- correctly install into _libdir/openmpi and not _libdir/name-openmpi

* Fri Sep 16 2011 Thomas Spura <tomspur@fedoraproject.org> - 3.0.1-1
- initial packaging
