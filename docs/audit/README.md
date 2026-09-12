# Audit DMG driver Mac — Canon MG2500 series (mcpd-mac 16.91.1.0)

Sumber: `mcpd-mac-mg2500-16_91_1_0-ea21_3.dmg` (unduhan resmi Canon; SHA256
`83618ea9cef5954c09ed2a7db9a042799bce6f5058168bed22b9b4f829d4397f`).

Metode: DMG (UDIF/HFS+) diekstrak dengan 7-Zip 23.01 → `PrinterDriver_MG2500
series_169101.pkg` (xar) → `Payload` pbzx (56 MB, didekompresi per-chunk XZ →
cpio) → 1.455 file. Seluruh artefak audit teks ada di `dmg/`:

| File | Isi |
|---|---|
| `dmg/SUMMARY.md` | ringkasan ekstraksi |
| `dmg/filelist.txt` | daftar lengkap 1.455 file + ukuran |
| `dmg/plists/` | seluruh Info.plist & capability table (sudah dikonversi ke XML) |
| `dmg/grep-hits.txt` | jejak marker (mediatype, quality, realtone, dst.) |
| `dmg/ppds.txt` | PPD di dalam DMG (hasil: tidak ada — dibangkitkan dinamis) |
| `dmg/strings__*.txt` | string binary filter/framework kunci |

## Struktur yang ditemukan (instal ke `/Library/Printers/Canon/BJPrinter/`)

```
Filters/
  Command2CanonIJ.bundle   (727 KB)  — filter maintenance command  [≈ Linux cmdtocanonij]
  Raster2CanonIJ/
    Raster2CanonIJS.bundle (658 KB)  — filter CUPS raster → perintah printer
                                          [≈ Linux pstocanonij + lib model]
Frameworks/
  BJEssential2.framework   (1.46 MB) — inti rasterisasi/halftone
  BJCommand2, BJExtDDI, CIJExtDDI(2) — komunikasi & DDI printer
  BJStatus2 (+ .sts)                 — status printer [≈ lgmon]
  BJPDELocalizedString2              — teks PDE multibahasa
PDEs/CanonIJPDE.bundle               — panel dialog print macOS
  Resources/QualityMedia*.nib        — UI "Quality & Media" (media type+quality)
Utilities/
  CanonIJPrinterUtility.app          — maintenance & level tinta [≈ cngpij/cif+lgmon]
  CIJAutoSetupToolS.app              — pembuat antrean; memuat TEMPLATE PPD
                                        ("*PPD-Adobe: 4.3", @_IJUtilsCreatePPDPathWithPrinterID)
Resources/Database/CIJMG2500series.db (v1.0.10) — capability database model
Plugins/
  BJOutputModule/cnbao428.plugin     — output module khusus model
                                        [≈ Linux libcnbpcmcm429 + cnb_4290.tbl]
  CIJUtility/CIJUtilityCommand.bundle/Resources/*.utl (PDNZ_*/PDRG_*)
                                        [≈ Linux cleaning.utl/nozzlecheck.utl]
Library/Extensions/BJUSBLoad.kext (16.91.10) — driver USB kelas Canon (IOKit)
```

## Temuan kunci

1. **Arsitektur setara dengan Linux.** Pola "filter generik + output module
   per-model + tabel utilitas" identik: `Raster2CanonIJS` ↔ `pstocanonij`,
   `cnbao428.plugin` ↔ `libcnbpcmcm429`+`cnb_4290.tbl` (kode model bersebelahan
   428/429 = varian MG2400/MG2500), `*.utl` ↔ `cleaning.utl/nozzlecheck.utl`.
2. **PPD macOS dibangkitkan dinamis** oleh `CIJAutoSetupToolS` dari template
   + database `CIJMG2500series.db` saat antrean dibuat; sementara Linux memakai
   PPD statis `canonmg2500.ppd` yang memuat seluruh capability table
   (lihat `docs/media-settings-guide.md`). Makin lengkap data PPD Linux =
   semua kendali media yang dimiliki Mac tersedia juga di CUPS.
3. **Raster processing**: string pada `Raster2CanonIJS` menunjukkan jalur
   `CNIJMediaType` → `CNIJPrintQuality` → `CNIJDitherPattern` (halftone) —
   sama dengan jalur Linux di `cmdtocanonij` (`keyHalftoneMethod_Int`,
   `keyMonochromeTone_Int`, `AutoHalftone`). Keduanya menerima CUPS raster dan
   mengeluarkan aliran perintah proprietary Canon yang sama ke hardware.
4. **Tidak ada "RealTone"** — grep `realtone|real.?tone` nol hasil di seluruh
   isi DMG (dan juga di driver Linux). Fitur warna foto Canon resminya adalah
   *Canon Digital Photo Color* (driver matching). Karena itu paket kami
   menyediakan preset **photo-realtone** sebagai profil setelan
   (glossygold + quality 1 + Intensity −3 + Contrast +5) yang meniru hasil
   warna natural tanpa boros tinta.
5. **BJUSBLoad.kext 16.91.10** dibangun ulang dengan Xcode 14/macOS 12.3 SDK
   (hak cipta 2004–2026) — Canon merilis ulang driver ini agar kompatibel
   macOS modern; di Linux tidak diperlukan padanannya (kernel + libusb CUPS
   backend menangani USB).
