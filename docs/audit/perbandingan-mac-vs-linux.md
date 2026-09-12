# Perbandingan: driver Mac (DMG 16.91) vs driver Linux (cnijfilter-mg2500series 4.00)

## 1. Tabel perbandingan arsitektur

| Lapisan | macOS (mcpd 16.91.1.0) | Linux (cnijfilter-mg2500series 4.00) | Catatan |
|---|---|---|---|
| Format paket | DMG → pkg (xar+pbzx) → /Library/Printers | RPM/DEB packagearchive → /usr | Kami repackage → RPM Fedora-native |
| Capability table | `CIJMG2500series.db` (plist) + PDE `.nib` | PPD statis `canonmg2500.ppd` (897 baris) | Linux: semua opsi terekspos ke CUPS |
| PPD | **Dibangkitkan** saat setup antrean (template di CIJAutoSetupToolS) | Statis, dipakai langsung | Paritas kendali tercapai via PPD Linux |
| Filter raster | `Raster2CanonIJS.bundle` (Mach-O, 658 KB) | `pstocanonij` (ELF; PS→raster Canon) + lib model `libcnbpcmcm429` | Input CUPS raster/PS, output aliran proprietary Canon sama |
| Filter maintenance | `Command2CanonIJ.bundle` | `cmdtocanonij` + `*.utl` (cleaning/nozzlecheck/autoalign) | Sumber perintah head-cleaning identik fungsinya |
| Output module model | `cnbao428.plugin` | `libcnbpcmcm429.so` + `cnb_4290.tbl` + `cnbpname429.tbl` | Kode model 428/429 = saudara (MG2400/MG2500) |
| Monitor tinta/status | `BJStatus2.framework` + `.sts` | `cnijlgmon2` + `cnb_cnijlgmon2.res` | Kami patch soname libusb agar jalan di Fedora modern |
| Utilitas | `CanonIJPrinterUtility.app` | `cifmg2500`, `cngpij`, `cngpijmnt` | head cleaning, nozzle check, alignment |
| Akses USB | `BJUSBLoad.kext` (IOKit, khusus macOS) | kernel + backend CUPS `usb` / `cnijusb` | Linux tidak butuh kext |
| Setup antrean | `CIJAutoSetupToolS.app` | `install.sh` Canon / **`mg2500-setup` kami** | satu perintah di Bazzite |
| UI dialog cetak | PDE "Quality & Media" (nib) | GTK/Qt print dialog membaca PPD + CUPS Web UI | Panduan: docs/media-settings-guide.md |

## 2. Capability table — persamaan & perbedaan

Kendali yang tersedia di **kedua** platform:
* Media type: Plain / Glossy Photo / Photo Paper Plus Glossy II / Envelope
* Print quality (mac: popup "Print Quality"; Linux: `CNQuality` 1–5)
* Grayscale printing
* Color balance C/M/Y, Intensity/Density, Contrast, Brightness/Gamma
* Ukuran kertas (A4/Letter/Legal/B5/A5/4"×6"/5"×7"/envelope/custom)

Kendali **hanya terekspos jelas di Linux PPD** (kami dokumentasikan agar semua
bisa dipakai):
* `CNInkCartridgeSettings` (pakai catridge hitam saja / warna saja / keduanya)
* `CNCopies` driver-side (1–999)
* Skala cetak `natural-scaling`/`scaling` & posisi `position`
* Matriks kombinasi sah media×quality (quality 1 = hanya Photo Paper Plus Glossy II)

Kendali **khusus Mac** (tidak direplikasi driver Linux): preset cepat di PDE dan
integrasi ColorSync — di Linux kami menggantinya dengan preset `mg2500-presets`
(termasuk **photo-realtone**).

## 3. Raster processing (jalur tinta)

```
macOS:  app → CGPSConverter/CUPS → cgpdftoraster(CUPS) → CUPS Raster
        → Raster2CanonIJS (media/quality/dither: CNIJDitherPattern)
        → cnbao428.plugin → BJ command stream → CIJUSBClassDriver → printer

Linux:  app → CUPS (cups-filters: pdftopdf, ghostscript)
        → application/vnd.cups-postscript → pstocanonij (halftone:
          keyHalftoneMethod_Int / AutoHalftone / MonochromeTone)
        → libcnbpcmcm429 + cnb_4290.tbl → BJ command stream
        → backend usb/cnijusb → printer
```

Titik temu: **keduanya berakhir di protokol printer Canon yang sama** (BJ
command + raster banding proprietary). Itulah mengapa driver Linux resmi 4.00
tetap valid untuk MG2570S modern, dan mengapa audit ini relevan: tidak ada
fitur rastersasi Mac yang hilang di Linux — hanya *penyajian setelan* yang
berbeda (plist+PDE vs PPD), dan PPD Linux justru lebih transparan.

## 4. Implikasi untuk paket `mg2500-series` (Bazzite)

1. Driver Linux 4.00 = padanan fungsional penuh DMG Mac 16.91 → kami pakai
   binary resmi Canon Linux (terverifikasi MD5) tanpa modifikasi kode.
2. Dua patch integrasi modern: soname `libusb-1.0.so.0→.1` (cnijlgmon2) dan
   penempatan PPD ke `/usr/share/cups/model/canon/`.
3. Setelan mac-style yang hilang dikompensasi `mg2500-presets`:
   `text-draft`, `text-standard`, `text-bw`, `photo-realtone`,
   `photo-standard`, `photo-inksave` — termasuk strategi hemat tinta dan
   warna natural yang di Mac harus diatur manual per-slider.
4. Scan: DMG Mac memuat stack scan tersendiri; di Linux MG2500 series sudah
   didukung `sane-pixma` → UI `mg2500-scan` GTK3 kami memakai jalur SANE
   (lebih terintegrasi daripada ScanGear MP 2.20 lama yang GTK2).

## 5. Bukti verifikasi (lihat `dmg/`)

* `dmg/filelist.txt` — 1.455 file terekstrak penuh.
* `dmg/plists/` — Info.plist setiap bundle/framework (versi, signature).
* `dmg/grep-hits.txt` — pencarian marker (realtone: **0 hit**, mediatype:
  banyak, dither/halftone: ada di filter).
* `dmg/strings__Raster2CanonIJS.txt`, `strings__cnbao428.txt`,
  `strings__CIJAutoSetupToolS.txt` (template PPD), dst.
