# RPM spec: Canon PIXMA MG2500 series (MG2570S) untuk Fedora / Bazzite (rpm-ostree)
#
# Isi paket:
#  - Driver printer CUPS resmi Canon "IJ Printer Driver Ver. 4.00 for Linux"
#    (binary resmi dari packagearchive RPM Canon, lihat Source0)
#  - Preset cetak (kualitas tinggi & hemat tinta, termasuk preset "realtone")
#  - UI pemindai (scan) GTK3: mg2500-scan (via SANE sane-pixma)
#  - Helper setup printer: mg2500-setup
#
# Binari Canon direpakaging tanpa modifikasi (kecuali patch soname libusb
# untuk cnijlgmon2 oleh packaging/build.sh). Lisensi: modul GPL Canon +
# modul EULA Canon; teks lisensi ikut dipaketkan.

%global canondoc     cnijfilter-mg2500series-4.00
%global queue_name   MG2500S

Name:           mg2500-series
Version:        1.0.0
Release:        1%{?dist}
Summary:        Canon PIXMA MG2500 series (MG2570S) CUPS driver + scan UI + ink-smart presets

License:        GPL+ and Canon-EULA
URL:            https://github.com/pistislitae/mg2500-series
Source0:        %{name}-%{version}.tar.gz
ExclusiveArch:  x86_64

Requires:       cups
Requires:       cups-filters
Requires:       ghostscript
Requires:       popt
Requires:       libxml2
Requires:       libusb1
Requires:       sane-backends
Requires:       sane-backends-libs
Requires:       python3
Requires:       python3-gobject
Requires:       gtk3
Recommends:     python3-pillow
Recommends:     simple-scan

%description
Paket lengkap Canon PIXMA MG2500 series (termasuk MG2570S) untuk Fedora,
Bazzite, dan distro berbasis rpm-ostree lainnya:

* Driver printer CUPS resmi Canon (IJ Printer Driver Ver. 4.00 for Linux),
  filter cmdtocanonij/pstocanonij + backend cnij USB, PPD canonmg2500.ppd.
* Preset cetak pintar tinta:
    - text-draft      : draf hemat tinta (plain, quality 4, hitam-putih)
    - text-standard   : dokumen sehari-hari
    - photo-realtone  : foto kualitas maksimal (glossygold, quality 1)
                        dengan tone warna natural (realtone)
    - photo-inksave   : foto di kertas biasa, tinta hemat
* mg2500-scan: aplikasi GUI GTK3 untuk memindai dokumen/foto
  (PNG/JPEG/PDF), memakai backend SANE pixma bawaan kernel-distro.
* mg2500-setup: registrasi antrean printer + monitor level tinta
  (cnijlgmon2, dipatch agar kompatibel libusb Fedora).

Dirakit ulang dari packagearchive resmi Canon:
  cnijfilter-mg2500series-4.00-1-rpm.tar.gz ( Fedora 18 x86_64, binary )
Lisensi modul Canon mengikuti EULA Canon (ikut dipaketkan); modul GPL
mengikuti GPL+. Lihat docs/audit di repo proyek untuk hasil audit.

%prep
%autosetup -c -n %{name}-%{version}

%install
# ---------- driver CUPS (filter & backend) ----------
mkdir -p %{buildroot}%{_prefix}/lib/cups/filter
mkdir -p %{buildroot}%{_prefix}/lib/cups/backend
install -pm0755 canon-common/usr/lib/cups/filter/cmdtocanonij  %{buildroot}%{_prefix}/lib/cups/filter/
install -pm0755 canon-common/usr/lib/cups/filter/pstocanonij   %{buildroot}%{_prefix}/lib/cups/filter/
install -pm0755 canon-common/usr/lib/cups/backend/cnijbe       %{buildroot}%{_prefix}/lib/cups/backend/
install -pm0755 canon-common/usr/lib/cups/backend/cnijnet      %{buildroot}%{_prefix}/lib/cups/backend/
install -pm0755 canon-common/usr/lib/cups/backend/cnijusb      %{buildroot}%{_prefix}/lib/cups/backend/

# ---------- binari utilitas ----------
mkdir -p %{buildroot}%{_bindir}
install -pm0755 canon-common/usr/bin/cngpij       %{buildroot}%{_bindir}/
install -pm0755 canon-common/usr/bin/cngpijmnt    %{buildroot}%{_bindir}/
install -pm0755 canon-common/usr/bin/cnijlgmon2   %{buildroot}%{_bindir}/
install -pm0755 canon-common/usr/bin/cnijnetprn   %{buildroot}%{_bindir}/
install -pm0755 canon-common/usr/bin/cnijnpr      %{buildroot}%{_bindir}/
install -pm0755 canon-model/usr/bin/cifmg2500     %{buildroot}%{_bindir}/

# ---------- library privat Canon (nama unik: aman di %{_libdir}) ----------
mkdir -p %{buildroot}%{_libdir}
install -pm0755 canon-common/usr/lib/libcnbpcnclapicom.so.4.0.0 %{buildroot}%{_libdir}/
install -pm0755 canon-common/usr/lib/libcnnet.so.1.2.2          %{buildroot}%{_libdir}/
install -pm0755 canon-model/usr/lib/libcnbpcmcm429.so.8.20.1    %{buildroot}%{_libdir}/
install -pm0755 canon-model/usr/lib/libcnbpcnclapi429.so.4.0.0  %{buildroot}%{_libdir}/
install -pm0755 canon-model/usr/lib/libcnbpcnclbjcmd429.so.3.3.0 %{buildroot}%{_libdir}/
install -pm0755 canon-model/usr/lib/libcnbpcnclui429.so.4.0.0   %{buildroot}%{_libdir}/
install -pm0755 canon-model/usr/lib/libcnbpess429.so.4.3.1      %{buildroot}%{_libdir}/
install -pm0755 canon-model/usr/lib/libcnbpo429.so.1.0.1        %{buildroot}%{_libdir}/
# symlink soname yang diminta DT_NEEDED (tanpa ldconfig)
ln -s libcnbpcnclapicom.so.4.0.0  %{buildroot}%{_libdir}/libcnbpcnclapicom.so
ln -s libcnnet.so.1.2.2           %{buildroot}%{_libdir}/libcnnet.so
ln -s libcnbpcmcm429.so.8.20.1    %{buildroot}%{_libdir}/libcnbpcmcm429.so
ln -s libcnbpcnclapi429.so.4.0.0  %{buildroot}%{_libdir}/libcnbpcnclapi429.so
ln -s libcnbpcnclbjcmd429.so.3.3.0 %{buildroot}%{_libdir}/libcnbpcnclbjcmd429.so
ln -s libcnbpcnclui429.so.4.0.0   %{buildroot}%{_libdir}/libcnbpcnclui429.so
ln -s libcnbpess429.so.4.3.1      %{buildroot}%{_libdir}/libcnbpess429.so
ln -s libcnbpo429.so.1.0.1        %{buildroot}%{_libdir}/libcnbpo429.so

# ---------- tabel & konfigurasi (path hardcoded binari Canon) ----------
mkdir -p %{buildroot}%{_prefix}/lib/bjlib
install -pm0644 canon-common/usr/lib/bjlib/cnnet.ini           %{buildroot}%{_prefix}/lib/bjlib/
install -pm0644 canon-model/usr/lib/bjlib/cifmg2500.conf       %{buildroot}%{_prefix}/lib/bjlib/
install -pm0644 canon-model/usr/lib/bjlib/cnb_4290.tbl         %{buildroot}%{_prefix}/lib/bjlib/
install -pm0644 canon-model/usr/lib/bjlib/cnbpname429.tbl      %{buildroot}%{_prefix}/lib/bjlib/

mkdir -p %{buildroot}%{_datadir}/cmdtocanonij
install -pm0644 canon-common/usr/share/cmdtocanonij/autoalign.utl   %{buildroot}%{_datadir}/cmdtocanonij/
install -pm0644 canon-common/usr/share/cmdtocanonij/cleaning.utl    %{buildroot}%{_datadir}/cmdtocanonij/
install -pm0644 canon-common/usr/share/cmdtocanonij/nozzlecheck.utl %{buildroot}%{_datadir}/cmdtocanonij/

mkdir -p %{buildroot}%{_datadir}/cnijlgmon2
install -pm0644 canon-common/usr/share/cnijlgmon2/cnb_cnijlgmon2.res %{buildroot}%{_datadir}/cnijlgmon2/

# locale cnijlgmon2
for l in de fr ja zh; do
  mkdir -p %{buildroot}%{_datadir}/locale/$l/LC_MESSAGES
  install -pm0644 canon-common/usr/share/locale/$l/LC_MESSAGES/cnijlgmon2.mo \
    %{buildroot}%{_datadir}/locale/$l/LC_MESSAGES/
done

# ---------- PPD ----------
mkdir -p %{buildroot}%{_datadir}/cups/model/canon
install -pm0644 canon-model/usr/share/ppd/canonmg2500.ppd %{buildroot}%{_datadir}/cups/model/canon/
gzip -9f %{buildroot}%{_datadir}/cups/model/canon/canonmg2500.ppd

# ---------- udev ----------
mkdir -p %{buildroot}%{_prefix}/lib/udev/rules.d
install -pm0644 canon-common/etc/udev/rules.d/81-canonij_prn.rules %{buildroot}%{_prefix}/lib/udev/rules.d/

# ---------- glue & UI kami ----------
install -pm0755 glue/mg2500-presets %{buildroot}%{_bindir}/
install -pm0755 glue/mg2500-setup   %{buildroot}%{_bindir}/
install -pm0755 glue/mg2500-scan    %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_datadir}/applications
install -pm0644 glue/mg2500-scan.desktop %{buildroot}%{_datadir}/applications/
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -pm0644 glue/mg2500-scan.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/

# ---------- dokumentasi & lisensi ----------
mkdir -p %{buildroot}%{_defaultdocdir}/%{name}-%{version}
for f in canon-common/usr/share/doc/cnijfilter-common/LICENSE-cnijfilter-*.txt \
         canon-model/usr/share/doc/cnijfilter-mg2500series/LICENSE-cnijfilter-*.txt \
         canon-model/usr/share/doc/cnijfilter-mg2500series/lproptions-mg2500-4.00EN.txt; do
  install -pm0644 "$f" %{buildroot}%{_defaultdocdir}/%{name}-%{version}/
done
install -pm0644 glue/README-presets.md %{buildroot}%{_defaultdocdir}/%{name}-%{version}/

%post
# muat ulang CUPS & udev bila berjalan (aman di image-based system)
if systemctl is-active -q cups 2>/dev/null; then systemctl reload cups 2>/dev/null || true; fi
udevadm control --reload 2>/dev/null || true
udevadm trigger 2>/dev/null || true
exit 0

%files
%license %{_defaultdocdir}/%{name}-%{version}/LICENSE-cnijfilter-4.00EN.txt
%doc %{_defaultdocdir}/%{name}-%{version}/README-presets.md
%doc %{_defaultdocdir}/%{name}-%{version}/lproptions-mg2500-4.00EN.txt

%{_prefix}/lib/cups/filter/cmdtocanonij
%{_prefix}/lib/cups/filter/pstocanonij
%{_prefix}/lib/cups/backend/cnijbe
%{_prefix}/lib/cups/backend/cnijnet
%{_prefix}/lib/cups/backend/cnijusb
%{_bindir}/cngpij
%{_bindir}/cngpijmnt
%{_bindir}/cnijlgmon2
%{_bindir}/cnijnetprn
%{_bindir}/cnijnpr
%{_bindir}/cifmg2500
%{_libdir}/libcnbpcnclapicom.so.4.0.0
%{_libdir}/libcnnet.so.1.2.2
%{_libdir}/libcnbpcmcm429.so.8.20.1
%{_libdir}/libcnbpcnclapi429.so.4.0.0
%{_libdir}/libcnbpcnclbjcmd429.so.3.3.0
%{_libdir}/libcnbpcnclui429.so.4.0.0
%{_libdir}/libcnbpess429.so.4.3.1
%{_libdir}/libcnbpo429.so.1.0.1
%{_libdir}/libcnbpcnclapicom.so
%{_libdir}/libcnnet.so
%{_libdir}/libcnbpcmcm429.so
%{_libdir}/libcnbpcnclapi429.so
%{_libdir}/libcnbpcnclbjcmd429.so
%{_libdir}/libcnbpcnclui429.so
%{_libdir}/libcnbpess429.so
%{_libdir}/libcnbpo429.so
%{_prefix}/lib/bjlib/cnnet.ini
%{_prefix}/lib/bjlib/cifmg2500.conf
%{_prefix}/lib/bjlib/cnb_4290.tbl
%{_prefix}/lib/bjlib/cnbpname429.tbl
%{_datadir}/cmdtocanonij/autoalign.utl
%{_datadir}/cmdtocanonij/cleaning.utl
%{_datadir}/cmdtocanonij/nozzlecheck.utl
%{_datadir}/cnijlgmon2/cnb_cnijlgmon2.res
%{_datadir}/locale/de/LC_MESSAGES/cnijlgmon2.mo
%{_datadir}/locale/fr/LC_MESSAGES/cnijlgmon2.mo
%{_datadir}/locale/ja/LC_MESSAGES/cnijlgmon2.mo
%{_datadir}/locale/zh/LC_MESSAGES/cnijlgmon2.mo
%{_datadir}/cups/model/canon/canonmg2500.ppd.gz
%{_prefix}/lib/udev/rules.d/81-canonij_prn.rules
%{_bindir}/mg2500-presets
%{_bindir}/mg2500-setup
%{_bindir}/mg2500-scan
%{_datadir}/applications/mg2500-scan.desktop
%{_datadir}/icons/hicolor/scalable/apps/mg2500-scan.svg

%changelog
* Fri Sep 12 2026 Arena Agent <arena-agent@arena.ai> - 1.0.0-1
- Repackage resmi Canon IJ driver 4.00 (MG2500 series) untuk Fedora/Bazzite
- Preset pintar tinta + realtone, UI scan GTK3 (SANE pixma), patch libusb
