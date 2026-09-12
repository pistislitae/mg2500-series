# Preset cetak & Media Settings — Canon MG2500 series (MG2570S)

## Ringkas
| Preset | Media | Quality | Warna/Tinta | Kapan dipakai |
|---|---|---|---|---|
| `text-draft` | plain | 4 (Draft) | B/W, catridge hitam | cetak cepat hemat: draf, tugas, struk |
| `text-standard` | plain | 3 (Std) | warna | dokumen harian |
| `text-bw` | plain | 3 (Std) | B/W, catridge hitam | dokumen final hitam-putih |
| `photo-realtone` | glossygold (Photo Paper Plus Glossy II) | 1 (High) | warna, tone natural | foto kenangan — hasil maksimal |
| `photo-standard` | glossypaper (Glossy Photo Paper) | 2 | warna | foto rutin |
| `photo-inksave` | plain | 2 | warna, density −10 | foto di kertas biasa, irit |

## Pemakaian
```bash
mg2500-presets list             # bantuan
mg2500-presets photo-realtone   # terapkan preset (ganti kertas sesuai preset!)
mg2500-presets text-draft
mg2500-presets show             # lihat opsi aktif
mg2500-presets reset            # kembali ke default Canon
```
Sebagai root → tersimpan sebagai default sistem; sebagai user → default user.

## Aturan emas hemat tinta
1. **MediaType harus sesuai kertas** — memilih `glossygold` saat kertas biasa = buang tinta; memilih `plain` saat kertas foto = warna pucat.
2. **Quality 1 hanya sah untuk `glossygold`** (matriks resmi Canon); kombinasi lain bisa berakhir quality default.
3. Dokumen teks → `text-draft`/`text-bw` memakai catridge hitam saja, tinta warna aman.
4. Foto → jangan naikkan `CNDensity` (menambah tinta); preset realtone justru menurunkannya tipis (−3) sambil menaikkan kontras (+5) supaya warna tampak pekat & natural.
5. Selalu cetak foto dari file resolusi cukup (≥300 dpi pada ukuran cetak).

Panduan lengkap semua distro: `docs/media-settings-guide.md` di repo.
