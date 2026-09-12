# RPM spec: Canon PIXMA MG2500 series (MG2570S) untuk Fedora / Bazzite (rpm-ostree)
#
# Isi paket:
#  - Driver printer CUPS resmi Canon "IJ Printer Driver Ver. 4.00 for Linux"
#    (binary resmi dari packagearchive RPM Canon — diunduh & diverifikasi md5
#    oleh packaging/build.sh)
#  - Preset cetak (kualitas tinggi & hemat tinta, termasuk preset "realtone")
#  - UI pemindai (scan) GTK3: mg2500-scan (via SANE sane-pixma)
#  - Helper setup printer: mg2500-setup
#
# Catatan: %install memindahkan seluruh pohon usr/ Canon ke buildroot lalu
# merapikan (relokasi shared lib ke %%{_libdir}, symlink soname, PPD ke
# cups/model). %%LOCALE_FILES%% adalah placeholder yang diisi build.sh.

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

* Driver printer CUPS resmi Canon (IJ Printer Driver Ver. 4.00 for Linux):
  filter cmdtocanonij/pstocanonij + backend cnij USB, PPD canonmg2500.ppd,
  monitor level tinta cnijlgmon2, utilitas maintenance (cif, cleaning,
  nozzle check).
* Preset cetak pintar tinta (mg2500-presets):
    - text-draft      : draf hemat tinta (plain, quality 4, hitam-putih)
    - text-standard   : dokumen sehari-hari
    - photo-realtone  : foto kualitas maksimal (glossygold, quality 1)
                        dengan tone warna natural
    - photo-inksave   : foto di kertas biasa, tinta hemat
* mg2500-scan: aplikasi GUI GTK3 untuk memindai dokumen/foto
  (PNG/JPEG/PDF), memakai backend SANE pixma.
* mg2500-setup: registrasi antrean printer otomatis.

Dirakit ulang dari packagearchive resmi Canon:
  cnijfilter-mg2500series-4.00-1-rpm.tar.gz (binary x86_64)
Teks lisensi Canon ikut dipaketkan; hasil audit ada di docs/audit repo.

%prep
# ekstraksi manual (tanpa keajaiban %autosetup)
rm -rf %{name}-%{version}
mkdir %{name}-%{version}
tar -xzf %{SOURCE0} -C %{name}-%{version}
ls -laR . | head -50

%install
# ---------- 1. Salin pohon usr/ Canon apa adanya ke buildroot ----------
mkdir -p %{buildroot}/usr
cp -a canon-common/usr/. %{buildroot}/usr/
cp -a canon-model/usr/.  %{buildroot}/usr/

# aturan udev bila upstream taruh di /etc
if [ -d canon-common/etc/udev/rules.d ]; then
  mkdir -p %{buildroot}%{_prefix}/lib/udev/rules.d
  cp -a canon-common/etc/udev/rules.d/. %{buildroot}%{_prefix}/lib/udev/rules.d/
fi

# ---------- 2. Relokasi shared library privat ke %%{_libdir} + symlink ----------
mkdir -p %{buildroot}%{_libdir}
for f in %{buildroot}%{_prefix}/lib/lib*.so.*; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  son="${base%%.so.*}"
  mv "$f" %{buildroot}%{_libdir}/
  ln -s "$base" "%{buildroot}%{_libdir}/${son}.so"
done

# ---------- 3. PPD ke direktori CUPS model ----------
PPDSRC="$(find %{buildroot}%{_datadir} -name 'canonmg2500*.ppd*' 2>/dev/null | head -1)"
if [ -n "$PPDSRC" ]; then
  mkdir -p %{buildroot}%{_datadir}/cups/model/canon
  case "$PPDSRC" in
    *.gz) mv "$PPDSRC" %{buildroot}%{_datadir}/cups/model/canon/canonmg2500.ppd.gz ;;
    *)    gzip -9c "$PPDSRC" > %{buildroot}%{_datadir}/cups/model/canon/canonmg2500.ppd.gz; rm -f "$PPDSRC" ;;
  esac
  rmdir --ignore-fail-on-non-empty -p "$(dirname "$PPDSRC")" 2>/dev/null || true
else
  echo "PERINGATAN: PPD canonmg2500 tidak ditemukan di paket upstream" >&2
fi

# ---------- 4. Glue kami (preset, setup, scan UI) ----------
install -pm0755 glue/mg2500-presets %{buildroot}%{_bindir}/
install -pm0755 glue/mg2500-setup   %{buildroot}%{_bindir}/
install -pm0755 glue/mg2500-scan    %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_datadir}/applications
install -pm0644 glue/mg2500-scan.desktop %{buildroot}%{_datadir}/applications/
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -pm0644 glue/mg2500-scan.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/

# ---------- 5. Dokumentasi & lisensi ----------
mkdir -p %{buildroot}%{_defaultdocdir}/%{name}-%{version}
find canon-common canon-model -name 'LICENSE-*.txt' -exec install -pm0644 {} %{buildroot}%{_defaultdocdir}/%{name}-%{version}/ \;
find canon-model -name 'lproptions-*.txt' -exec install -pm0644 {} %{buildroot}%{_defaultdocdir}/%{name}-%{version}/ \;
install -pm0644 glue/README-presets.md %{buildroot}%{_defaultdocdir}/%{name}-%{version}/

%post
if systemctl is-active -q cups 2>/dev/null; then systemctl reload cups 2>/dev/null || true; fi
udevadm control --reload 2>/dev/null || true
udevadm trigger 2>/dev/null || true
exit 0

%files
%license %{_defaultdocdir}/%{name}-%{version}/LICENSE-cnijfilter-4.00EN.txt
%doc %{_defaultdocdir}/%{name}-%{version}/*

%{_prefix}/lib/cups/filter/*
%{_prefix}/lib/cups/backend/*
%{_prefix}/lib/bjlib/*
%{_prefix}/lib/udev/rules.d/81-canonij_prn.rules
%{_datadir}/cmdtocanonij/*
%{_datadir}/cnijlgmon2/*
%{_datadir}/cups/model/canon/*
%{_datadir}/applications/mg2500-scan.desktop
%{_datadir}/icons/hicolor/scalable/apps/mg2500-scan.svg
%%LOCALE_FILES%%
%{_libdir}/libcn*
%{_bindir}/cifmg2500
%{_bindir}/cnijlgmon2
%{_bindir}/cnijnetprn
%{_bindir}/cnijnpr
%{_bindir}/cngpij
%{_bindir}/cngpijmnt
%{_bindir}/mg2500-presets
%{_bindir}/mg2500-setup
%{_bindir}/mg2500-scan

%changelog
* Fri Sep 12 2026 Arena Agent <arena-agent@arena.ai> - 1.0.0-1
- Repackage resmi Canon IJ driver 4.00 (MG2500 series) untuk Fedora/Bazzite
- Preset pintar tinta + realtone, UI scan GTK3 (SANE pixma), patch libusb
