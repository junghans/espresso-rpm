%global git 0
%global commit f74064d62090da45a28225881008b05798703d1c
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           espresso
Version:        4.0.1
Release:        1%{?dist}
Summary:        Extensible Simulation Package for Research on Soft matter

License:        GPLv3+
URL:            http://espressomd.org
%if %{git}
Source0:        https://github.com/%{name}md/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz
%else
Source0:       https://github.com/%{name}md/%{name}/releases/download/%{version}/%{name}-%{version}.tar.gz
%endif


BuildRequires:  gcc-c++
%if 0%{?rhel}
BuildRequires:  cmake3 >= 3.0
BuildRequires:  python%{python3_pkgversion}-Cython
BuildRequires:  python%{python3_pkgversion}-setuptools
%global cython /usr/bin/cython%{python3_version}
# no boost-mpi* for ppc64le on epel7
ExcludeArch:   ppc64le
%else
BuildRequires:  cmake >= 3.0
%global cmake3 %{cmake}
BuildRequires:  /usr/bin/cython
%global cython /usr/bin/cython
%endif
BuildRequires:  fftw-devel
BuildRequires:  python%{python3_pkgversion}-numpy
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  boost-devel
BuildRequires:  hdf5-devel
BuildRequires:  gsl-devel
BuildRequires:  boost-devel
BuildRequires:  mpich-devel
BuildRequires:  boost-mpich-devel
BuildRequires:  openmpi-devel
BuildRequires:  boost-openmpi-devel

Requires:       python%{python3_pkgversion}-numpy
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
This package contains the license file and data files shared between the
sub-packages of %{name}.

%package devel
Summary:        Development package for  %{name} packages
Requires:       python%{python3_pkgversion}-%{name}-openmpi = %{version}-%{release}
Requires:       python%{python3_pkgversion}-%{name}-mpich = %{version}-%{release}
%description devel
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics
This package contains the development libraries of %{name}.

%package -n python%{python3_pkgversion}-%{name}-openmpi
Requires:       %{name}-common = %{version}-%{release}
Summary:        Extensible Simulation Package for Research on Soft matter
Provides:       %{name}-openmpi = %{version}-%{release}
Obsoletes:      %{name}-openmpi < 3.3.0-12
%description -n python%{python3_pkgversion}-%{name}-openmpi
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics

This package contains %{name} compiled against Open MPI.


%package -n python%{python3_pkgversion}-%{name}-mpich
Requires:       %{name}-common = %{version}-%{release}
Summary:        Extensible Simulation Package for Research on Soft matter
Provides:       %{name}-mpich2 = %{version}-%{release}
Obsoletes:      %{name}-mpich2 < 3.1.1-3
Provides:       %{name}-mpich = %{version}-%{release}
Obsoletes:      %{name}-mpich < 3.3.0-12
%description -n python%{python3_pkgversion}-%{name}-mpich
ESPResSo can perform Molecular Dynamics simulations of bead-spring models
in various ensembles ((N,V,E), (N,V,T), and (N,p,T)).
ESPResSo contains a number of advanced algorithms, e.g.
    * DPD thermostat (for hydrodynamics)
    * P3M, MMM2D, MMM1D, ELC for electrostatic interactions
    * Lattice-Boltzmann for hydrodynamics

This package contains %{name} compiled against MPICH2.


%prep
%if %{git}
%setup -q -n espresso-%{commit}
%else
%setup -q
%endif
mkdir openmpi_build mpich_build
sed -i 's/1.67/1.66/' CMakeLists.txt

%build
%global defopts \\\
 -DWITH_PYTHON=ON \\\
 -DPYTHON_EXECUTABLE=%{__python3} \\\
 -DWITH_TESTS=ON \\\
 -DCMAKE_SKIP_RPATH=ON \\\
 -DINSTALL_PYPRESSO=OFF \\\
 -DCYTHON_EXECUTABLE=%{cython}

#save some memory using -j1
%define _smp_mflags -j1

# Build OpenMPI version
%{_openmpi_load}
pushd openmpi_build
%{cmake3} \
  %{defopts} \
  -DLIBDIR=${MPI_LIB} \
  -DPYTHON_INSTDIR=%{python3_sitearch}/openmpi \
  ..
%make_build
popd
%{_openmpi_unload}

# Build mpich version
%{_mpich_load}
pushd mpich_build
%{cmake3} \
  %{defopts} \
  -DLIBDIR=${MPI_LIB} \
  -DPYTHON_INSTDIR=%{python3_sitearch}/mpich \
  ..
%make_build
popd
%{_mpich_unload}

%install
# first install mpi files and move around because MPI_SUFFIX above doesn't
# work yet (will be fixed in a new version)
%{_openmpi_load}
pushd openmpi_build
%make_install
popd
%{_openmpi_unload}

%{_mpich_load}
pushd mpich_build
%make_install
popd
%{_mpich_unload}
find %{buildroot}%{_prefix} -name "*.so" -exec chmod +x {} \;
find %{buildroot}%{_prefix} -name "gen_pxiconfig" -exec chmod +x {} \;

%check
# https://github.com/espressomd/espresso/issues/2468
%if 0%{?fedora} <= 29
%ifarch ppc64 ppc64le aarch64 i686
%global testargs ARGS='-E npt'
%endif
%endif
%{_openmpi_load}
pushd openmpi_build
LD_LIBRARY_PATH=${MPI_LIB}:%{buildroot}${MPI_LIB} make check CTEST_OUTPUT_ON_FAILURE=1 %{?testargs:%{testargs}}
popd
%{_openmpi_unload}

%{_mpich_load}
pushd mpich_build
LD_LIBRARY_PATH=${MPI_LIB}:%{buildroot}${MPI_LIB} make check CTEST_OUTPUT_ON_FAILURE=1 %{?testargs:%{testargs}}
popd
%{_mpich_unload}

%files common
%doc AUTHORS README NEWS ChangeLog
%license COPYING

%files devel
%{_libdir}/*/lib/lib*.so

%files -n python%{python3_pkgversion}-%{name}-openmpi
%{_libdir}/openmpi/lib/lib*.so.*
%{python3_sitearch}/openmpi/%{name}md

%files -n python%{python3_pkgversion}-%{name}-mpich
%{_libdir}/mpich/lib/lib*.so.*
%{python3_sitearch}/mpich/%{name}md

%changelog
* Fri Jan 25 2019 Christoph Junghans <junghans@votca.org> - 4.0.1-1
- version bump to 4.0.1

* Fri Sep 07 2018 Christoph Junghans <junghans@votca.org> - 4.0.0-1
- version bump to 4.0.0 (bug #1625379)
- move to python3

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.0-0.12.20180203gitf74064d
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Feb 06 2018 Iryna Shcherbina <ishcherb@redhat.com> - 4.0-0.11.20180203gitf74064d
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Sun Feb 04 2018 Christoph Junghans <junghans@votca.org> - 4.0-0.10.20170220git7a9ac74
- added 1830.patch to fix install (missing libEspressoConfig)

* Sat Feb 03 2018 Christoph Junghans <junghans@votca.org> - 4.0-0.9.20170220git7a9ac74
- Bump to version 4.0 git version f74064d
- Drop 1056.patch, got merged upstream

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0-0.8.20170228git8a021f5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0-0.7.20170228git8a021f5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 19 2017 Jonathan Wakely <jwakely@redhat.com> - 4.0-0.6.20170228git8a021f5
- Rebuilt for s390x binutils bug

* Tue Jul 18 2017 Jonathan Wakely <jwakely@redhat.com> - 4.0-0.5.20170228git8a021f5
- Rebuilt for Boost 1.64

* Sun Mar 12 2017 Peter Robinson <pbrobinson@fedoraproject.org> 4.0-0.4.20170228git8a021f5
- Drop ExcludeArch as boost-mpi is now built on ppc64le

* Sun Mar 05 2017 Christoph Junghans <junghans@votca.org> - 4.0-0.3.20170228git8a021f5
- Dropped 1042.patch, merged upstream
- Add 1056.patch to fix install

* Sat Feb 25 2017 Christoph Junghans <junghans@votca.org> - 4.0-0.2.20170220git7a9ac74
- ExcludeArch: ppc64le due to missing boost-mpi

* Thu Feb 16 2017 Christoph Junghans <junghans@votca.org> - 4.0-0.1.20170220git7a9ac74
- Bump to version 4.0 git version
- Drop cypthon patch, incl. upstream
- Add 1042.patch from upstream

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
