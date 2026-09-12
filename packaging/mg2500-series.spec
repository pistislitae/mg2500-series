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
# Layout upstream RPM (Fedora-era) memakai /usr/local/bin, /usr/lib64/bjlib,
# dan /usr/local/share — dinormalkan ke FHS (/usr/bin, /usr/share, /usr/lib64)
# dan diberi symlink kompatibilitas di /usr/local (beberapa binary Canon
# meng-hardcode path lama).

Name:           mg2500-series
Version:        1.0.1
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
# rpm >= 4.20 (Fedora 41+) otomatis mengekstrak Source0 ke builddir — kosongkan.
# Untuk rpm lama, %install di bawah yang menangani ekstraksi.

%install
# posisikan dir kerja ke sumber (kompatibel rpm 4.20 baru & rpm lama)
if [ -d canon-common ]; then :;
elif [ -d %{name}-%{version}/canon-common ]; then cd %{name}-%{version};
else
  mkdir -p %{name}-%{version}
  tar -xzf %{SOURCE0} -C %{name}-%{version}
  cd %{name}-%{version}
fi
BR=%{buildroot}

# ---------- 1. Salin pohon usr/ Canon apa adanya ----------
mkdir -p "$BR/usr"
cp -a canon-common/usr/. "$BR/usr/"
cp -a canon-model/usr/.  "$BR/usr/"
if [ -d canon-common/etc/udev/rules.d ]; then
  mkdir -p "$BR%{_prefix}/lib/udev/rules.d"
  cp -a canon-common/etc/udev/rules.d/. "$BR%{_prefix}/lib/udev/rules.d/"
fi

# ---------- 2. Normalisasi binari /usr/local/bin -> /usr/bin ----------
mkdir -p "$BR%{_bindir}"
if [ -d "$BR/usr/local/bin" ]; then
  for f in "$BR"/usr/local/bin/*; do
    [ -e "$f" ] || continue
    b=$(basename "$f")
    mv "$f" "$BR%{_bindir}/$b"
  done
  rm -rf "$BR/usr/local/bin"
fi

# ---------- 3. Normalisasi share /usr/local/share -> /usr/share ----------
mkdir -p "$BR%{_datadir}"
for d in cmdtocanonij cnijlgmon2 locale; do
  if [ -d "$BR/usr/local/share/$d" ] && [ ! -e "$BR%{_datadir}/$d" ]; then
    mv "$BR/usr/local/share/$d" "$BR%{_datadir}/$d"
  fi
  rm -rf "$BR/usr/local/share/$d"
done

# ---------- 4. Shared lib: pastikan semua di %%{_libdir} + symlink soname ----------
mkdir -p "$BR%{_libdir}"
for f in "$BR%{_prefix}/lib"/lib*.so.*; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  mv "$f" "$BR%{_libdir}/$base"
done
for f in "$BR%{_libdir}"/lib*.so.*; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  son="${base%%.so.*}"
  [ -e "$BR%{_libdir}/${son}.so" ] || ln -s "$base" "$BR%{_libdir}/${son}.so"
done

# ---------- 5. bjlib: real di %%{_libdir}/bjlib + duplikat /usr/lib/bjlib ----------
# binary Canon era RPM membaca /usr/lib64/bjlib; era DEB membaca /usr/lib/bjlib.
if [ -d "$BR%{_libdir}/bjlib" ] && [ ! -d "$BR%{_prefix}/lib/bjlib" ]; then
  mkdir -p "$BR%{_prefix}/lib"
  cp -a "$BR%{_libdir}/bjlib" "$BR%{_prefix}/lib/bjlib"
fi
if [ -d "$BR%{_prefix}/lib/bjlib" ] && [ ! -d "$BR%{_libdir}/bjlib" ]; then
  cp -a "$BR%{_prefix}/lib/bjlib" "$BR%{_libdir}/bjlib"
fi

# ---------- 6. Symlink kompatibilitas /usr/local (path hardcoded) ----------
mkdir -p "$BR/usr/local/bin" "$BR/usr/local/share"
for b in cngpij cngpijmnt cnijlgmon2 cnijnetprn cnijnpr cifmg2500; do
  [ -e "$BR%{_bindir}/$b" ] && ln -sf "%{_bindir}/$b" "$BR/usr/local/bin/$b"
done
for d in cmdtocanonij cnijlgmon2 locale; do
  if [ -d "$BR%{_datadir}/$d" ]; then
    ln -sfn "../../%{_datadir#/usr/}/$d" "$BR/usr/local/share/$d"
  fi
done

# ---------- 6b. bersihkan duplikat/sisa upstream (Fedora: unpackaged = fatal) ----------
rm -rf "$BR%{_libdir}/cups"
rm -rf "$BR%{_datadir}/doc/cnijfilter-common-4.00" "$BR%{_datadir}/doc/cnijfilter-mg2500series-4.00"
rm -rf "$BR/usr/local/share/ppd"

# ---------- 7. PPD ke direktori CUPS model ----------
PPDSRC="$(find "$BR%{_datadir}" "$BR/usr/local/share" -name 'canonmg2500*.ppd*' 2>/dev/null | head -1)"
if [ -n "$PPDSRC" ]; then
  mkdir -p "$BR%{_datadir}/cups/model/canon"
  case "$PPDSRC" in
    *.gz) cp "$PPDSRC" "$BR%{_datadir}/cups/model/canon/canonmg2500.ppd.gz" ;;
    *)    gzip -9c "$PPDSRC" > "$BR%{_datadir}/cups/model/canon/canonmg2500.ppd.gz" ;;
  esac
  rm -f "$PPDSRC"
  rmdir --ignore-fail-on-non-empty "$(dirname "$PPDSRC")" 2>/dev/null || true
else
  echo "PERINGATAN: PPD canonmg2500 tidak ditemukan di paket upstream" >&2
fi

# ---------- 8. Glue kami (preset, setup, scan UI) ----------
install -pm0755 glue/mg2500-presets "$BR%{_bindir}/"
install -pm0755 glue/mg2500-setup   "$BR%{_bindir}/"
install -pm0755 glue/mg2500-scan    "$BR%{_bindir}/"
mkdir -p "$BR%{_datadir}/applications"
install -pm0644 glue/mg2500-scan.desktop "$BR%{_datadir}/applications/"
mkdir -p "$BR%{_datadir}/icons/hicolor/scalable/apps"
install -pm0644 glue/mg2500-scan.svg "$BR%{_datadir}/icons/hicolor/scalable/apps/"

# ---------- 9. Dokumentasi & lisensi ----------
mkdir -p "$BR%{_defaultdocdir}/%{name}-%{version}"
find canon-common canon-model -name 'LICENSE-*.txt' -exec install -pm0644 {} "$BR%{_defaultdocdir}/%{name}-%{version}/" \;
find canon-model -name 'lproptions-*.txt' -exec install -pm0644 {} "$BR%{_defaultdocdir}/%{name}-%{version}/" \;
install -pm0644 glue/README-presets.md "$BR%{_defaultdocdir}/%{name}-%{version}/"

%post
if systemctl is-active -q cups 2>/dev/null; then systemctl reload cups 2>/dev/null || true; fi
udevadm control --reload 2>/dev/null || true
udevadm trigger 2>/dev/null || true
exit 0

%files
%license %{_defaultdocdir}/%{name}-%{version}/LICENSE-*.txt
%doc %{_defaultdocdir}/%{name}-%{version}/README-presets.md
%doc %{_defaultdocdir}/%{name}-%{version}/lproptions-*.txt

%{_prefix}/lib/cups/filter/*
%{_prefix}/lib/cups/backend/*
%{_prefix}/lib/udev/rules.d/81-canonij_prn.rules
%{_prefix}/lib/bjlib/*
%{_libdir}/bjlib/*
%{_datadir}/cmdtocanonij/*
%{_datadir}/cnijlgmon2/*
%{_datadir}/cups/model/canon/*
%{_datadir}/applications/mg2500-scan.desktop
%{_datadir}/icons/hicolor/scalable/apps/mg2500-scan.svg
%%LOCALE_FILES%%
%{_libdir}/libcn*.so.*
%{_libdir}/libcn*.so
%{_bindir}/cifmg2500
%{_bindir}/cnijlgmon2
%{_bindir}/cnijnetprn
%{_bindir}/cnijnpr
%{_bindir}/cngpij
%{_bindir}/cngpijmnt
%{_bindir}/mg2500-presets
%{_bindir}/mg2500-setup
%{_bindir}/mg2500-scan
/usr/local/bin/cngpij
/usr/local/bin/cngpijmnt
/usr/local/bin/cnijlgmon2
/usr/local/bin/cnijnetprn
/usr/local/bin/cnijnpr
/usr/local/bin/cifmg2500
/usr/local/share/cmdtocanonij
/usr/local/share/cnijlgmon2
/usr/local/share/locale

%changelog
* Sat Sep 12 2026 pistislitae <56380429+pistislitae@users.noreply.github.com> - 1.0.1-1
- Perbaikan: patch soname libusb (1.0.0 -> 1.0.1) kini menjangkau cnijlgmon2
  yang di RPM upstream berada di /usr/local/bin; dependency kini resolvable
  di Fedora/Bazzite.
- Bersih berkas PPD asli upstream (unpackaged)
- Repackage resmi Canon IJ driver 4.00 (MG2500 series) untuk Fedora/Bazzite
- Preset pintar tinta + realtone, UI scan GTK3 (SANE pixma), patch libusb
