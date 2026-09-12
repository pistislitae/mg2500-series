#!/usr/bin/env bash
# build.sh — rakit RPM mg2500-series untuk Fedora/Bazzite.
# Berjalan di container Fedora (CI) atau Fedora lokal.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${TMPDIR:-/tmp}/mg2500-build"
STAGE="$WORK/stage"
VERSION="$(sed -n 's/^Version:[[:space:]]*//p' "$REPO_ROOT/packaging/mg2500-series.spec" | head -1)"

# Sumber resmi Canon (packagearchive RPM; mirror id: asia.canon support 0100550101)
CANON_URL="https://gdlp01.c-wss.com/gds/1/0100005501/01/cnijfilter-mg2500series-4.00-1-rpm.tar.gz"
CANON_MD5="37fd638ae176fad74fd656f6cb719ead"

echo "==> [1/6] Unduh & verifikasi packagearchive resmi Canon"
mkdir -p "$WORK/dl"
cd "$WORK/dl"
ARCHIVE="cnijfilter-mg2500series-4.00-1-rpm.tar.gz"
if [[ ! -f "$ARCHIVE" ]]; then
  curl -fL --retry 3 -o "$ARCHIVE" "$CANON_URL"
fi
echo "$CANON_MD5  $ARCHIVE" | md5sum -c -

echo "==> [2/6] Ekstrak RPM x86_64 Canon"
cd "$WORK"
tar xzf "dl/$ARCHIVE"
RPM_DIR="$(find "$WORK" -maxdepth 2 -type d -name 'packages' | head -1)"
echo "packages dir: $RPM_DIR"
ls -la "$RPM_DIR"

mkdir -p "$STAGE/canon-common" "$STAGE/canon-model"
extract_rpm() {
  local rpmfile="$1" dest="$2"
  rpm2cpio "$rpmfile" | cpio -idmu --no-absolute-filenames -D "$dest"
}
COMMON_RPM="$(find "$RPM_DIR" -name 'cnijfilter-common-4.00*x86_64.rpm' | head -1)"
MODEL_RPM="$(find "$RPM_DIR" -name 'cnijfilter-mg2500series-4.00*x86_64.rpm' | head -1)"
[[ -n "$COMMON_RPM" && -n "$MODEL_RPM" ]] || { echo "FATAL: rpm x86_64 tidak ditemukan"; ls "$RPM_DIR"; exit 1; }
extract_rpm "$COMMON_RPM" "$STAGE/canon-common"
extract_rpm "$MODEL_RPM"  "$STAGE/canon-model"

echo "==> [3/6] Patch kompatibilitas Fedora modern"
# cnijlgmon2 menautkan libusb-1.0.so.0 (soname Debian lama); Fedora memakai libusb-1.0.so.1
if ldd "$STAGE/canon-common/usr/bin/cnijlgmon2" 2>/dev/null | grep -q 'not found'; then
  ldd "$STAGE/canon-common/usr/bin/cnijlgmon2" || true
  patchelf --replace-needed libusb-1.0.so.0 libusb-1.0.so.1 "$STAGE/canon-common/usr/bin/cnijlgmon2" \
    || patchelf --replace-needed libusb-1.0.so.0 libusb-1.0.so.1 "$STAGE/canon-common/usr/bin/cnijlgmon2"
fi
ldd "$STAGE/canon-common/usr/bin/cnijlgmon2" || true
ldd "$STAGE/canon-model/usr/bin/cifmg2500" || true
ldd "$STAGE/canon-common/usr/lib/cups/filter/cmdtocanonij" || true

echo "==> [4/6] Salin glue (preset, setup, scan UI)"
mkdir -p "$STAGE/glue"
cp -a "$REPO_ROOT/src/." "$STAGE/glue/"

echo "==> [5/6] Rakit source tarball & jalankan rpmbuild"
cd "$WORK"
tar czf "mg2500-series-$VERSION.tar.gz" -C "$STAGE" .
mkdir -p "$WORK/rpmbuild/SOURCES" "$WORK/rpmbuild/SPECS" "$WORK/rpmbuild/RPMS" "$WORK/rpmbuild/BUILD"
mv "mg2500-series-$VERSION.tar.gz" "$WORK/rpmbuild/SOURCES/"
cp "$REPO_ROOT/packaging/mg2500-series.spec" "$WORK/rpmbuild/SPECS/"
rpmbuild -bb \
  --define "_topdir $WORK/rpmbuild" \
  --define "_sourcedir $WORK/rpmbuild/SOURCES" \
  "$WORK/rpmbuild/SPECS/mg2500-series.spec"

echo "==> [6/6] Salin hasil"
DIST="$REPO_ROOT/dist"
mkdir -p "$DIST"
find "$WORK/rpmbuild/RPMS" -name '*.rpm' -exec cp -v {} "$DIST/" \;
( cd "$DIST" && sha256sum ./*.rpm > SHA256SUMS )
echo "SELESAI:"; ls -la "$DIST"
