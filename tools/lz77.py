"""GBA BIOS LZ77 (type 0x10) decompress, compress, and whole-ROM block scan."""


def decompress(d, off=0, vram_safe=False):
    """Return (data, end_offset) or raise ValueError on a malformed block. end_offset is unaligned."""
    if d[off] != 0x10:
        raise ValueError("not lz10")
    size = d[off + 1] | d[off + 2] << 8 | d[off + 3] << 16
    out = bytearray()
    i = off + 4
    n = len(d)
    while len(out) < size:
        if i >= n:
            raise ValueError("ran off end")
        flags = d[i]
        i += 1
        for b in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> b):
                if i + 1 >= n:
                    raise ValueError("ran off end")
                a, c = d[i], d[i + 1]
                i += 2
                ln = (a >> 4) + 3
                disp = ((a & 15) << 8 | c) + 1
                if disp > len(out) or (vram_safe and disp == 1):
                    raise ValueError("bad disp")
                if len(out) + ln > size:
                    raise ValueError("overruns declared size")
                for _ in range(ln):
                    out.append(out[-disp])
            else:
                if i >= n:
                    raise ValueError("ran off end")
                out.append(d[i])
                i += 1
    return bytes(out), i


def compress(data, min_disp=1):
    """Greedy LZ10. min_disp=2 keeps the block safe for BIOS VRAM decompression."""
    out = bytearray(b"\x10" + len(data).to_bytes(3, "little"))
    i = 0
    n = len(data)
    head = {}
    while i < n:
        flag_at = len(out)
        out.append(0)
        flags = 0
        for b in range(8):
            if i >= n:
                break
            best = 0
            best_d = 0
            key = data[i:i + 3]
            if len(key) == 3:
                for p in reversed(head.get(key, ())):
                    d = i - p
                    if d > 0x1000:
                        break
                    if d < min_disp:
                        continue
                    ln = 3
                    while ln < 18 and i + ln < n and data[p + ln] == data[i + ln]:
                        ln += 1
                    if ln > best:
                        best, best_d = ln, d
                        if ln == 18:
                            break
            step = 1
            if best >= 3:
                flags |= 0x80 >> b
                v = (best - 3) << 12 | (best_d - 1)
                out += v.to_bytes(2, "big")
                step = best
            else:
                out.append(data[i])
            for k in range(i, i + step):
                head.setdefault(data[k:k + 3], []).append(k)
            i += step
        out[flag_at] = flags
    return bytes(out)


def scan(rom, align=4, min_size=16, max_size=0x80000):
    """Yield (offset, data, end) for every well-formed LZ10 block that does not overlap the previous hit."""
    i = 0
    n = len(rom)
    while i < n - 4:
        if rom[i] == 0x10:
            size = rom[i + 1] | rom[i + 2] << 8 | rom[i + 3] << 16
            if min_size <= size <= max_size:
                try:
                    data, end = decompress(rom, i)
                except ValueError:
                    data = None
                # a real block is smaller than its payload unless it is mostly literals
                if data is not None and end - i <= size * 9 // 8 + 8:
                    yield i, data, end
                    i = (end + align - 1) & ~(align - 1)
                    continue
        i += align


if __name__ == "__main__":
    blob = bytes(range(64)) * 20 + b"abcabcabc" * 50
    for md in (1, 2):
        packed = compress(blob, md)
        got, end = decompress(packed)
        assert got == blob and end == len(packed), md
    print("ok")
