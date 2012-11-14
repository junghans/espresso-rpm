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
# * MPD:       if '1' enable mpich2, which requires mpd to start
# * OPENMPI:   if '1' enable openmpi
%global MPD 0
%global OPENMPI 0

Name:           espresso
Version:        3.1.1
Release:        1%{?dist}
Summary:        Extensible Simulation Package for Research on Soft matter
Group:          System Environment/Libraries

License:        GPLv3+
URL:            http://espressomd.org
Source0:        http://download.savannah.gnu.org/releases/espressomd/espresso-%{version}.tar.gz
# BR autotools for patch0
#BuildRequires:  autoconf
#BuildRequires:  automake

BuildRequires:  tcl-devel
BuildRequires:  fftw-devel

Requires:       %{name}-common = %{version}-%{release}

# for the testsuite: 'pwgen' is needed to create a random password
BuildRequires:  pwgen

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
Requires:       openmpi%{?_isa}
Requires:       %{name}-common = %{version}-%{release}
Summary:        Extensible Simulation Package for Research on Soft matter
Group:          System Environment/Libraries 
%description openmpi
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics 

This package contains %{name} compiled against Open MPI.


%package mpich2
BuildRequires:  mpich2-devel
Requires:       mpich2%{?_isa}
Requires:       %{name}-common = %{version}-%{release}
Summary:        Extensible Simulation Package for Research on Soft matter
Group:          System Environment/Libraries 
%description mpich2
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics 

This package contains %{name} compiled against MPICH2.


%prep
%setup -q

#sed -i 's/tclsh8\.4/tclsh/' tools/trace_memory.tcl

mkdir openmpi_build mpich2_build no_mpi


%build
pushd no_mpi
export CC=gcc
export CXX=g++
%dconfigure --enable-shared
make %{?_smp_mflags}
popd

# Build parallel versions: set compiler variables to MPI wrappers
export CC=mpicc
export CXX=mpicxx

# Build OpenMPI version
%{_openmpi_load}
pushd openmpi_build
%dconfigure_mpi --enable-shared --program-suffix=$MPI_SUFFIX
make %{?_smp_mflags}
popd
%{_openmpi_unload}

# Build mpich2 version
%{_mpich2_load}
pushd mpich2_build
%dconfigure_mpi --enable-shared --program-suffix=$MPI_SUFFIX
make %{?_smp_mflags}
popd
%{_mpich2_unload}


%install
# first install mpi files and move around because MPI_SUFFIX above doesn't
# work yet (will be fixed in a new version)
%{_openmpi_load}
pushd openmpi_build
make install DESTDIR=%{buildroot}
popd
%{_openmpi_unload}

%{_mpich2_load}
pushd mpich2_build
make install DESTDIR=%{buildroot}
popd
%{_mpich2_unload}


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

# test mpd?
%if 0%{?MPD}
%{_mpich2_load}
# create mpd.conf
#export MPD_CONF_FILE=mpd.conf
#echo MPD_SECRETWORD=$(pwgen -s 50 1) > mpd.conf
#chmod 600 mpd.conf
#mpd --daemon

pushd mpich2_build
make check || cat testsuite/runtest.log || :
popd

#mpdallexit

# delete mpd.conf again
#rm mpd.conf
#unset MPD_CONF_FILE
%{_mpich2_unload}
%endif


%files common
%doc AUTHORS COPYING README NEWS ChangeLog doc/ug/ug.pdf
%{_datadir}/espresso/

%files
%{_bindir}/Espresso

%files openmpi
%{_libdir}/openmpi/bin/Espresso_openmpi

%files mpich2
%{_libdir}/mpich2/bin/Espresso_mpich2


%changelog
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
