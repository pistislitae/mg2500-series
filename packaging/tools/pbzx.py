#!/usr/bin/env python3
"""
pbzx stream parser (Python 3) — mengekstrak aliran cpio dari payload .pkg macOS.

Format (pudquick/parse_pbzx2):
  'pbzx' + [8B flags awal] + per-chunk: [8B flags][8B length][length byte konten]
  Konten chunk biasanya stream XZ (magic FD 37 7A 58 5A 00), sesekanti raw cpio.
Output: cpio bersih ke stdout.  Pemakaian: pbzx.py Payload | cpio -idmu
Berdasarkan gist pudquick ff412bcb29c9c1fa4b8d (domain publik).
"""
import struct
import sys
import lzma

def main():
    if len(sys.argv) < 2:
        sys.exit("pemakaian: pbzx.py <Payload>  (output cpio ke stdout)")
    with open(sys.argv[1], "rb") as f:
        if f.read(4) != b"pbzx":
            sys.exit("bukan file pbzx")
        out = sys.stdout.buffer
        (flags,) = struct.unpack(">Q", f.read(8))
        n = 0
        while flags & (1 << 24):
            (flags,) = struct.unpack(">Q", f.read(8))
            (length,) = struct.unpack(">Q", f.read(8))
            content = f.read(length)
            if content[:6] == b"\xfd7zXZ\x00":
                out.write(lzma.decompress(content))
            else:
                out.write(content)  # chunk cpio mentah
            n += 1
        sys.stderr.write(f"pbzx: {n} chunk diekstrak\n")

if __name__ == "__main__":
    main()
