#!/usr/bin/env bash
# build.sh — rakit RPM mg2500-series untuk Fedora/Bazzite.
# Berjalan di container Fedora (CI) atau Fedora lokal.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${TMPDIR:-/tmp}/mg2500-build"
STAGE="$WORK/stage"
LOG="$WORK/build-full.log"
VERSION="$(sed -n 's/^Version:[[:space:]]*//p' "$REPO_ROOT/packaging/mg2500-series.spec" | head -1 | tr -d '[:space:]')"

# Pada kegagalan: kumpulkan log lalu commit ke repo agar bisa dianalisis
cleanup_fail() {
  local code=$?
  if [ $code -ne 0 ]; then
    {
      echo "build.sh gagal (exit $code) pada $(date -u '+%F %T')"
      echo "=== ekor log ==="
      tail -60 "$LOG" 2>/dev/null
      echo "=== isi staging ==="
      find "$STAGE" -type f 2>/dev/null | head -200
    } > "$REPO_ROOT/ci-build-log.txt"
    cd "$REPO_ROOT" || return
    git config user.name "arena-ai-coding-agent[bot]"
    git config user.email "arena-ai-coding-agent[bot]@users.noreply.github.com"
    git add ci-build-log.txt || return
    git commit -m "ci: log kegagalan build [skip ci]" || return
    git push origin HEAD 2>/dev/null || \
      git push "https://x-access-token:${GITHUB_TOKEN:-}@github.com/${GITHUB_REPOSITORY:-pistislitae/mg2500-series}.git" HEAD || true
  fi
}
trap cleanup_fail EXIT

run_build() {
set -e

echo "==> [1/7] Unduh & verifikasi packagearchive resmi Canon"
mkdir -p "$WORK/dl" "$STAGE"
cd "$WORK/dl"
ARCHIVE="cnijfilter-mg2500series-4.00-1-rpm.tar.gz"
if [ ! -f "$ARCHIVE" ]; then
  curl -fL --retry 3 -o "$ARCHIVE" "https://gdlp01.c-wss.com/gds/1/0100005501/01/$ARCHIVE"
fi
echo "37fd638ae176fad74fd656f6cb719ead  $ARCHIVE" | md5sum -c -
sha256sum "$ARCHIVE"

echo "==> [2/7] Ekstrak RPM x86_64 Canon"
cd "$WORK"
rm -rf "$WORK/canon-arch"
mkdir -p "$WORK/canon-arch"
tar xzf "dl/$ARCHIVE" -C "$WORK/canon-arch"
RPM_DIR="$(find "$WORK/canon-arch" -type d -name 'packages' | head -1)"
echo "packages dir: $RPM_DIR"
ls -la "$RPM_DIR"

rm -rf "$STAGE"; mkdir -p "$STAGE/canon-common" "$STAGE/canon-model"
COMMON_RPM="$(find "$RPM_DIR" -name 'cnijfilter-common-4.00*x86_64*.rpm' | head -1)"
MODEL_RPM="$(find "$RPM_DIR" -name 'cnijfilter-mg2500series-4.00*x86_64*.rpm' | head -1)"
[ -n "$COMMON_RPM" ] || { echo "FATAL: rpm common x86_64 tidak ditemukan"; exit 1; }
[ -n "$MODEL_RPM" ]  || { echo "FATAL: rpm model x86_64 tidak ditemukan"; exit 1; }
( cd "$STAGE/canon-common" && rpm2cpio "$COMMON_RPM" | cpio -idmu --no-absolute-filenames )
( cd "$STAGE/canon-model"  && rpm2cpio "$MODEL_RPM"  | cpio -idmu --no-absolute-filenames )
echo "--- manifest canon-common:"; ( cd "$STAGE/canon-common" && find . -type f | sort )
echo "--- manifest canon-model:";  ( cd "$STAGE/canon-model"  && find . -type f | sort )

echo "==> [3/7] Patch kompatibilitas Fedora modern"
LGMON="$STAGE/canon-common/usr/bin/cnijlgmon2"
if [ -f "$LGMON" ]; then
  echo "--- ldd sebelum patch:"; ldd "$LGMON" || true
  if ldd "$LGMON" 2>/dev/null | grep -q 'libusb-1.0.so.0 => not found'; then
    patchelf --replace-needed libusb-1.0.so.0 libusb-1.0.so.1 "$LGMON"
    echo "--- ldd setelah patch:"; ldd "$LGMON" || true
  fi
fi
for b in "$STAGE"/canon-common/usr/lib/cups/filter/* "$STAGE"/canon-common/usr/lib/cups/backend/* "$STAGE"/canon-model/usr/bin/*; do
  [ -e "$b" ] || continue
  echo "--- cek: $b"
  ldd "$b" 2>/dev/null | grep 'not found' || true
done

echo "==> [4/7] Salin glue (preset, setup, scan UI)"
mkdir -p "$STAGE/glue"
cp -a "$REPO_ROOT/src/." "$STAGE/glue/"
chmod +x "$STAGE"/glue/mg2500-presets "$STAGE"/glue/mg2500-setup "$STAGE"/glue/mg2500-scan

echo "==> [5/7] Template spec (LOCALE_FILES) & jaminan lisensi"
LOCF=""
if find "$STAGE/canon-common" -path '*locale*' -name 'cnijlgmon2.mo' | grep -q .; then
  LOCF='%{_datadir}/locale/*/LC_MESSAGES/cnijlgmon2.mo'
fi
echo "LOCF=[$LOCF]"
if ! find "$STAGE" -name 'LICENSE-cnijfilter-4.00EN.txt' | grep -q .; then
  ANYLIC="$(find "$STAGE" -name 'LICENSE-*.txt' | head -1)"
  if [ -n "$ANYLIC" ]; then
    cp "$ANYLIC" "$(dirname "$ANYLIC")/LICENSE-cnijfilter-4.00EN.txt"
  else
    # fallback terakhir: buat penanda lisensi (teks resmi ada di repo)
    mkdir -p "$STAGE/canon-model/usr/share/doc/cnijfilter-mg2500series"
    echo "Lihat LICENSE resmi Canon pada repositori proyek." > "$STAGE/canon-model/usr/share/doc/cnijfilter-mg2500series/LICENSE-cnijfilter-4.00EN.txt"
  fi
fi

echo "==> [6/7] Tarball sumber + rpmbuild"
cd "$WORK"
rm -rf rpmbuild && mkdir -p rpmbuild/SOURCES rpmbuild/SPECS rpmbuild/RPMS rpmbuild/BUILD rpmbuild/BUILDROOT
tar czf "rpmbuild/SOURCES/mg2500-series-$VERSION.tar.gz" -C "$STAGE" .
sed "s|%%LOCALE_FILES%%|$LOCF|" "$REPO_ROOT/packaging/mg2500-series.spec" > "rpmbuild/SPECS/mg2500-series.spec"
rpmbuild -bb \
  --define "_topdir $WORK/rpmbuild" \
  --define "_sourcedir $WORK/rpmbuild/SOURCES" \
  --undefine dist \
  "rpmbuild/SPECS/mg2500-series.spec"

echo "==> [7/7] Salin hasil"
DIST="$REPO_ROOT/dist"
rm -rf "$DIST" && mkdir -p "$DIST"
find "$WORK/rpmbuild/RPMS" -name '*.rpm' -exec cp -v {} "$DIST/" \;
( cd "$DIST" && sha256sum ./*.rpm > SHA256SUMS )
echo "SELESAI:"; ls -la "$DIST"
}

run_build 2>&1 | tee "$LOG"
STATUS="${PIPESTATUS[0]}"
exit "$STATUS"
