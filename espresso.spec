%global git 0
%global commit f74064d62090da45a28225881008b05798703d1c
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           espresso
Version:        4.1.2
Release:        4%{?dist}
Summary:        Extensible Simulation Package for Research on Soft matter
# segfault on s390x: https://github.com/espressomd/espresso/issues/3753
ExcludeArch:    s390x

License:        GPLv3+
URL:            http://espressomd.org
%if %{git}
Source0:        https://github.com/%{name}md/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz
%else
Source0:       https://github.com/%{name}md/%{name}/releases/download/%{version}/%{name}-%{version}.tar.gz
# https://github.com/espressomd/espresso/pull/3725.patch on boost-1.73
Patch0:        https://github.com/espressomd/espresso/pull/3725.patch
%endif


BuildRequires:  gcc-c++
BuildRequires:  cmake3 >= 3.4
BuildRequires:  /usr/bin/cython
%global cython /usr/bin/cython
BuildRequires:  fftw-devel
BuildRequires:  python%{python3_pkgversion}-numpy
BuildRequires:  python%{python3_pkgversion}-six
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  boost-devel
BuildRequires:  hdf5-devel
BuildRequires:  gsl-devel
BuildRequires:  boost-devel
BuildRequires:  mpich-devel
BuildRequires:  boost-mpich-devel
BuildRequires:  hdf5-mpich-devel
BuildRequires:  openmpi-devel
BuildRequires:  boost-openmpi-devel
BuildRequires:  hdf5-openmpi-devel
BuildRequires:  python%{python3_pkgversion}-h5py

Requires:       python%{python3_pkgversion}-numpy
Requires:       %{name}-common = %{version}-%{release}
Obsoletes:      %{name}-devel < %{version}-%{release}

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

%package -n python%{python3_pkgversion}-%{name}-openmpi
Requires:       %{name}-common = %{version}-%{release}
Requires:       python%{python3_pkgversion}-h5py
Suggests:       python%{python3_pkgversion}-MDAnalysis
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
Requires:       python%{python3_pkgversion}-h5py
Suggests:       python%{python3_pkgversion}-MDAnalysis
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
%setup -q -n %{name}
%patch0 -p1
%endif

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

for mpi in mpich openmpi ; do
   module load mpi/${mpi}-%{_arch}
   mkdir ${mpi}
   pushd ${mpi}
   old_LDFLAGS="${LDFLAGS}"
   export LDFLAGS="${LDFLAGS} -Wl,-rpath,${MPI_PYTHON3_SITEARCH}/%{name}md"
   %{cmake3} %{defopts} -DLIBDIR=${MPI_LIB} -DPYTHON_INSTDIR=${MPI_PYTHON3_SITEARCH} ..
   LD_LIBRARY_PATH=$PWD/src/config %make_build
   export LDFLAGS="${old_LDFLAGS}"
   popd
   module unload mpi/${mpi}-%{_arch}
done

%install
for mpi in mpich openmpi ; do
   module load mpi/${mpi}-%{_arch}
   %make_install -C "${mpi}"
   module unload mpi/${mpi}-%{_arch}
done

%check
for mpi in mpich openmpi ; do
   module load mpi/${mpi}-%{_arch}
   LD_LIBRARY_PATH=${MPI_LIB}:%{buildroot}${MPI_PYTHON3_SITEARCH}/%{name}md make -C "${mpi}" check CTEST_OUTPUT_ON_FAILURE=1 %{?testargs:%{testargs}}
   module unload mpi/${mpi}-%{_arch}
done

%files common
%doc AUTHORS README NEWS ChangeLog
%license COPYING

%files -n python%{python3_pkgversion}-%{name}-openmpi
%{python3_sitearch}/openmpi/%{name}md/

%files -n python%{python3_pkgversion}-%{name}-mpich
%{python3_sitearch}/mpich/%{name}md/

%changelog
* Thu Jun 11 2020 Christoph Junghans <junghans@votca.org> - 4.1.2-4
- fix build with boost-1.73

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 4.1.2-3
- Rebuilt for Python 3.9

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 4.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Dec 13 2019 Christoph Junghans <junghans@votca.org> - 4.1.2-1
- Version bump to v4.1.2 (bug #1783470)
- Drop 3312.patch got merge upstream

* Fri Nov 15 2019 Christoph Junghans <junghans@votca.org> - 4.1.1-2
- Remove rpath

* Wed Nov 13 2019 Christoph Junghans <junghans@votca.org> - 4.1.1-1
- Version bump to v4.1.1

* Tue Oct 01 2019 Christoph Junghans <junghans@votca.org> - 4.1.0-1
- Version bump to v4.1.0 (bug #1757509)
- updated 2946.patch to 3228.diff
- major spec clean up

* Wed Sep 11 2019 Christoph Junghans <junghans@votca.org> - 4.0.2-8
- MDAnalysis is optional

* Tue Sep 03 2019 Christoph Junghans <junghans@votca.org> - 4.0.2-7
- fix deps, h5py is needed at cmake time

* Tue Aug 20 2019 Susi Lehtola <jussilehtola@fedoraproject.org> - 4.0.2-6
- Rebuilt for GSL 2.6.

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 4.0.2-5
- Rebuilt for Python 3.8

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jun 26 2019 Christoph Junghans <junghans@votca.org> - 4.0.2-3
- add missing soversion to libH5mdCore

* Tue Jun 25 2019 Christoph Junghans <junghans@votca.org> - 4.0.2-2
- enable hdf5 support

* Wed Apr 24 2019 Christoph Junghans <junghans@votca.org> - 4.0.2-1
- Version bump to 4.0.2

* Thu Feb 14 2019 Orion Poplawski <orion@nwra.com> - 4.0.1-3
- Rebuild for openmpi 3.1.3

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild
- Rebuilt to change main python from 3.4 to 3.6 (on epel7)

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
