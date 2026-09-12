# Memaksimalkan Media Settings pada "Configure Printer" — semua Linux
### Canon PIXMA MG2500 series (MG2570S) · PPD canonmg2500.ppd

Panduan ini berlaku untuk **semua distro Linux** (Fedora/Bazzite, Ubuntu, Arch,
openSUSE, Debian) karena semuanya memakai **CUPS + PPD** yang sama. Yang
berbeda hanya *di mana* kotak dialognya berada.

---

## 1. Peta pengaturan (dari capability table driver)

Capability table resmi Canon (dokumen `lproptions-mg2500-4.00EN.txt` + PPD):

| Opsi | Nilai | Keterangan |
|---|---|---|
| **MediaType** (Media Type) | `plain` · `glossygold` (Photo Paper Plus Glossy II) · `glossypaper` (Glossy Photo Paper) · `envelope` | penentu #1 hasil & tinta |
| **InputSlot** | `asf` (Rear Tray) | satu-satunya sumber kertas |
| **CNQuality** | `1` High · `2` · `3` Standar · `4` Draft | makin kecil = makin halus |
| **CNGrayscale** | True/False | cetak hitam-putih |
| **CNInkCartridgeSettings** | `bk` · `color` · `bkcolor` | catridge yang dipakai |
| **CNBalanceC/M/Y** | −50…50 | keseimbangan warna |
| **CNDensity** (Intensity) | −50…50 | makin positif = makin banyak tinta |
| **CNContrast** | −50…50 | kontras |
| **CNGamma** (Brightness) | 1.4 Terang · 1.8 Normal · 2.2 Gelap | |
| **PageSize** | Letter, Legal, A5, A4, B5, 4"×6", 5"×7", Com10, DL, Custom | |
| **CNCopies / natural-scaling / scaling / position** | 1–999 / % / fit-to-page | |

### Matriks kombinasi SAH (resmi Canon) — quality × media
| Media | Quality yang sah |
|---|---|
| plain | 2, 3, 4 |
| envelope | 2, 3 |
| glossypaper | 2, 3 |
| **glossygold** | **1 (High)**, 2, 3 |

> Quality 1 (High) **hanya tersedia untuk Photo Paper Plus Glossy II**.
> Kombinasi di luar matriks ini akan jatuh ke quality default oleh firmware driver.

---

## 2. Cara #1 — CUPS Web UI (universal, paling lengkap) ✅

1. Pastikan CUPS jalan: `sudo systemctl enable --now cups`
2. Buka **http://localhost:631** di browser → tab **Printers** → klik
   **MG2500S** → menu *Maintenance/Administration* → **Set Default Options**
   (di beberapa versi: *Configure Printer*).
3. Atur **default** yang menempel permanen ke antrean:

   | Halaman | Setelan | Nilai yang disarankan |
   |---|---|---|
   | *Media Type* | sesuai kertas terpasang | Kertas biasa = `Plain Paper`; foto = `Photo Paper Plus Glossy II` |
   | *Print Quality* | sesuai kebutuhan | dokumen `3`; foto `1` (hanya dgn PP-301) |
   | *Paper Source* | `Rear Tray` | |
   | *Page Size* | A4 (atau 4"×6" untuk foto) | |
   | *Grayscale Printing* | OFF kecuali dokumen B/W | |
   | *Ink Cartridge Settings* | `Both Black and Color` | pakai `Black Only` utk teks |
   | *Cyan/Magenta/Yellow, Intensity, Contrast, Brightness* | 0 / 0 / 0 / 1.8 | kalibrasi visual opsional |

4. **Submit** → setelan ini jadi default **semua aplikasi**.

> Di dialog print aplikasi (LibreOffice, browser dsb.), nilai-nilai ini juga
> muncul sebagai pilihan per-cetakan — default dari CUPS UI menjadi nilai
> awalnya.

## 3. Cara #2 — GNOME / KDE (Bazzite, Silverblue, Fedora Workstation)

* **GNOME**: *Pengaturan → Cetak (Printers) → MG2500S → Printing Options* —
  tampil terbatas (Paper size, Media Type/Quality tergantung versi GNOME).
  Untuk kontrol penuh tetap pakai CUPS Web UI (cara #1).
* **KDE Plasma (Bazzite KDE)**: *System Settings → Printers → MG2500S →
  Configure Printer* — dialog ini memunculkan SEMUA opsi PPD termasuk
  **Media Type, Print Quality, Grayscale, Ink Cartridge, warna**. Ini adalah
  "Configure Printer" paling lengkap di dunia GUI Linux; isinya sama persis
  dengan tabel di atas.

## 4. Cara #3 — baris perintah (per cetakan & default)

Per cetakan:
```bash
lp -d MG2500S -o MediaType=glossygold -o CNQuality=1 foto.pdf     # realtone photo HQ
lp -d MG2500S -o MediaType=plain -o CNQuality=4 -o CNGrayscale dokumen.pdf
lpoptions -p MG2500S -l                                           # lihat semua opsi
```

Default permanen — pakai preset bawaan paket (sama untuk semua distro yang
menginstal mg2500-series):
```bash
mg2500-presets text-draft       # hemat maksimal (B/W, draft, hitam saja)
mg2500-presets text-standard    # dokumen harian
mg2500-presets text-bw          # final B/W hemat warna
mg2500-presets photo-realtone   # foto kualitas maksimal + warna natural
mg2500-presets photo-standard   # foto rutin glossy
mg2500-presets photo-inksave    # foto di kertas biasa, irit
mg2500-presets reset            # default Canon
```
Jalankan sebagai **root** → default sistem (`/etc/cups/lpoptions`), sebagai
**user** → default per-user. Semua dialog (GNOME/KDE/aplikasi) langsung ikut.

## 5. Strategi kualitas maksimal TANPA boros tinta

1. **Kecocokan MediaType = 80% hasil.** Kertas foto harus `glossygold`/
   `glossypaper`; memilih `plain` saat memakai kertas foto membuat driver
   menaburkan tinta dengan profil kertas biasa → warna pucat + cepat habis.
2. **Foto kenangan**: `photo-realtone` (glossygold + quality 1). Preset ini
   menurunkan Intensity −3 (hemat tinta) dan menaikkan Contrast +5 sehingga
   warna tetap pekat & natural (skin tone tidak terbakar) — pendekatan
   "digital photo color" ala Canon.
3. **Dokumen**: `text-draft` untuk harian (hanya catridge hitam → tinta warna
   sangat irit), `text-bw` untuk final.
4. **Jangan pernah** menaikkan `CNDensity` di atas 0 untuk hemat; density
   positif = tinta bertambah tanpa keuntungan warna.
5. Foto dari sumber kecil: skala turun (`natural-scaling`) lebih baik daripada
   memaksa full page — driver tak akan interpolasi berlebihan.
6. Maintenance rutin (`cifmg2500` / `lpr -P MG2500S
   /usr/share/cmdtocanonij/cleaning.utl`) hanya saat nozzle tersumbat — head
   cleaning mengonsumsi tinta paling boros.

## 6. Troubleshooting cepat

| Gejala | Solusi |
|---|---|
| Warna pucat di kertas foto | MediaType belum `glossygold`/`glossypaper` |
| Tinta cepat habis | default masih quality tinggi; `mg2500-presets text-draft` |
| Cetak bergaris | nozzle check + cleaning (via `cifmg2500`) |
| Dialog tidak muncul opsi Media Type | pastikan antrean memakai PPD `/usr/share/cups/model/canon/canonmg2500.ppd.gz` (`lpoptions -p MG2500S -l`) |
| Printer tidak terdeteksi | `sudo mg2500-setup` (deteksi USB otomatis) |
