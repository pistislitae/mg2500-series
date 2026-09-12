# Panduan Bazzite / Fedora Atomic (rpm-ostree)

Bazzite adalah *image-based* Fedora Atomic: paket tidak dipasang langsung ke
sistem, melainkan **di-layering** ke image boot berikutnya lewat `rpm-ostree`.
Paket `mg2500-series` dibangun kompatibel dengan alur ini.

## 1. Pasang

```bash
# A. Langsung dari URL GitHub Release (tidak perlu unduh manual)
rpm-ostree install https://github.com/pistislitae/mg2500-series/releases/download/v1.0.0/mg2500-series-1.0.0-1.x86_64.rpm

# B. Atau unduh dulu lalu pasang file lokal
curl -LO https://github.com/pistislitae/mg2500-series/releases/download/v1.0.0/mg2500-series-1.0.0-1.x86_64.rpm
rpm-ostree install ./mg2500-series-1.0.0-1.x86_64.rpm

# Terapkan layer (butuh reboot; pekerjaan lain aman disimpan)
systemctl reboot
```

> rpm-ostree otomatis men-layer dependensi yang belum ada di image Bazzite
> (`cups`, `cups-filters`, `sane-backends`, `gtk3`, dll.) — tidak perlu
> pasang manual.

## 2. Daftarkan printer (sekali saja)

```bash
sudo mg2500-setup --scan
```
Skrip ini: mengaktifkan `cups.service` → mendeteksi URI USB `usb://Canon/MG2500...`
→ membuat antrean `MG2500S` dengan PPD resmi Canon → mengecek scanner SANE.

## 3. Pemakaian harian

```bash
mg2500-presets list          # preset cetak (hemat tinta / realtone)
mg2500-scan                  # UI pemindai (juga ada di menu aplikasi)
mg2500-scan --cli            # scan cepat tanpa GUI
```
Pengaturan media (Media Type, Quality, Grayscale, dsb.):
* KDE: *System Settings → Printers → MG2500S → Configure Printer*
* GNOME: *Settings → Printers* (terbatas) atau lengkap via http://localhost:631
* Detail: [`media-settings-guide.md`](media-settings-guide.md)

## 4. Update & maintenance

* `ujust update` / `rpm-ostree upgrade` biasa — layer `mg2500-series` ikut
  terbawa ke image baru.
* Cek status layer: `rpm-ostree status`
* Copot: `rpm-ostree uninstall mg2500-series && systemctl reboot`
* Darurat: boot ke deployment sebelumnya dari menu GRUB (rollback instan).

## 5. Catatan khusus Bazzite

* **CUPS sudah tersedia** di image Bazzite; `mg2500-setup` memastikan service
  aktif. (Bila image Anda minim print, paket tetap men-layer `cups` otomatis.)
* **Scanner**: MG2500 series didukung backend `sane-pixma` (paket
  `sane-backends`, otomatis ter-layer). Aplikasi *Document Scanner / Skanpage*
  juga bisa dipakai selain `mg2500-scan`.
* **Gaming mode / session switch**: antrean CUPS bersifat system-wide, jadi
  preset `mg2500-presets` tetap berlaku di session apa pun.
* File hasil scan default: `~/Pictures/MG2500-Scan/`.
