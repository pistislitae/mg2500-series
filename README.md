# mg2500-series — Canon PIXMA MG2500 series (MG2570S) untuk Linux

Paket **siap pakai** untuk **Bazzite / Fedora Atomic (rpm-ostree)** berisi:

* 🖨️ **Driver printer CUPS resmi Canon** — *IJ Printer Driver Ver. 4.00 for Linux*
  (binary resmi dari packagearchive RPM Canon, direpakaging + patch kompatibilitas
  Fedora modern), lengkap dengan PPD `canonmg2500.ppd`, filter
  `cmdtocanonij`/`pstocanonij`, backend USB Canon, monitor level tinta `cnijlgmon2`,
  dan utilitas maintenance (`cif`, cleaning, nozzle check).
* 🎚️ **Preset cetak pintar tinta** (`mg2500-presets`) — hemat tinta untuk dokumen,
  kualitas maksimal + warna **realtone** untuk foto.
* 🔍 **UI pemindai** (`mg2500-scan`, GTK3) — scan PNG/JPEG & PDF multi halaman
  via backend **SANE pixma** (MG2500 series didukung penuh, deteksi otomatis).
* ⚙️ **Setup otomatis** (`mg2500-setup`) — registrasi antrean printer ke CUPS
  dalam satu perintah.

> 📋 Audit **DMG driver Mac** (PPD, CUPS filter, raster processing, capability
> table) dan perbandingannya dengan driver Linux ada di [`docs/audit/`](docs/audit/).

---

## Pasang di Bazzite (rpm-ostree)

```bash
# 1) Pasang paket (langsung dari GitHub Release) + reboot
rpm-ostree install https://github.com/pistislitae/mg2500-series/releases/download/v1.0.0/mg2500-series-1.0.0-1.x86_64.rpm
systemctl reboot

# 2) Setelah restart — nyalakan printer & colok USB, lalu:
sudo mg2500-setup --scan
```

`mg2500-setup` menyalakan `cups`, mendeteksi printer, membuat antrean **MG2500S**
dengan PPD resmi, dan mengecek scanner. Selesai — printer muncul di
*Pengaturan → Cetak* dan aplikasi **MG2500 Scan** ada di menu.

Alternatif (unduh manual dulu):

```bash
curl -LO https://github.com/pistislitae/mg2500-series/releases/download/v1.0.0/mg2500-series-1.0.0-1.x86_64.rpm
rpm-ostree install ./mg2500-series-1.0.0-1.x86_64.rpm
systemctl reboot
```

Rollback kapan saja: `rpm-ostree uninstall mg2500-series && systemctl reboot`.

## Fedora non-Atomic (Workstation/Server)

```bash
sudo dnf install https://github.com/pistislitae/mg2500-series/releases/download/v1.0.0/mg2500-series-1.0.0-1.x86_64.rpm
sudo mg2500-setup --scan
```

## Preset cetak (kualitas vs hemat tinta)

```bash
mg2500-presets list              # lihat semua preset
mg2500-presets text-draft        # dokumen: paling hemat (B/W, draft)
mg2500-presets photo-realtone    # FOTO: kualitas maksimal + warna natural
```

| Preset | Media | Quality | Catatan |
|---|---|---|---|
| `text-draft` | Kertas biasa | Draft | B/W — tinta warna tidak terpakai |
| `text-standard` | Kertas biasa | Standard | dokumen harian |
| `text-bw` | Kertas biasa | Standard | final hitam-putih, hemat warna |
| `photo-realtone` | **Photo Paper Plus Glossy II** | **High (1)** | tone natural, kontras halus |
| `photo-standard` | Glossy Photo Paper | 2 | foto rutin |
| `photo-inksave` | Kertas biasa | 2 | density −10, foto di kertas biasa |

⚠️ Saat memakai preset foto, **ganti kertas sesuai preset** — kecocokan
`MediaType` adalah kunci utama kualitas warna sekaligus efisiensi tinta
(panduan lengkap: [`docs/media-settings-guide.md`](docs/media-settings-guide.md)).

## Scan

* GUI: buka **MG2500 Scan** dari menu aplikasi (atau `mg2500-scan`).
* CLI cepat: `mg2500-scan --cli --res 300` → PNG di `~/Pictures/MG2500-Scan/`.
* Multi halaman → tombol **Gabung jadi PDF** (butuh `python3-pillow`, ikut
  terpasang sebagai rekomendasi).
* Bisa juga pakai *Document Scanner* (simple-scan) — scanner MG2500 series
  didukung backend `sane-pixma` bawaan `sane-backends`.

## Catatan build & lisensi

* Binari driver = **rilis resmi Canon** `cnijfilter-mg2500series-4.00-1-rpm`
  (Fedora 18 x86_64), diverifikasi MD5, direpakaging tanpa mengubah binary —
  hanya `cnijlgmon2` dipatch `DT_NEEDED` (`libusb-1.0.so.0` → `libusb-1.0.so.1`)
  agar jalan di Fedora modern. Hasil audit & verifikasi ada di `docs/audit/`.
* Modul GPL Canon mengikuti **GPL+**; modul ber-EULA Canon mengikuti **EULA
  Canon** (teks lisensi resmi ikut dipaketkan di `/usr/share/doc/mg2500-series/`).
* Dibangun otomatis oleh GitHub Actions di container Fedora — reproducible dari
  `packaging/build.sh`.

## Peta repo

```
packaging/            RPM spec + build.sh + tools
src/                  glue: mg2500-presets, mg2500-setup, mg2500-scan (UI)
docs/
  media-settings-guide.md   ← memaksimalkan Media Settings di SEMUA Linux
  bazzite-guide.md          ← spesifik Bazzite/rpm-ostree
  audit/                    ← audit DMG Mac + perbandingan driver Mac vs Linux
.github/workflows/    CI: audit-dmg.yml, build.yml
```
