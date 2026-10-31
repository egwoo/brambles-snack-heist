"""Compare two folders of screenshots and write an HTML report, biggest changes first.

Usage: python3 tests/compare.py OLD_DIR NEW_DIR REPORT.html

Uses only the standard library plus macOS `sips` (to turn PNGs into BMPs that are easy to read).
Pixels are compared at half resolution; a pixel counts as changed when any channel moves by more than 40.
"""
import os
import struct
import subprocess
import sys
import tempfile

THRESHOLD = 40


def read_bmp(png_path, tmp):
    bmp = os.path.join(tmp, os.path.basename(png_path) + '.bmp')
    subprocess.run(['sips', '-s', 'format', 'bmp', png_path, '--out', bmp], check=True, capture_output=True)
    with open(bmp, 'rb') as f:
        data = f.read()
    offset = struct.unpack_from('<I', data, 10)[0]
    width, height = struct.unpack_from('<ii', data, 18)
    bpp = struct.unpack_from('<H', data, 28)[0] // 8
    stride = (width * bpp + 3) & ~3
    top_down = height < 0
    height = abs(height)
    rows = []
    for y in range(0, height, 2):
        src = y if top_down else height - 1 - y
        start = offset + src * stride
        row = data[start:start + width * bpp]
        rows.append([(row[x + 2], row[x + 1], row[x]) for x in range(0, width * bpp, bpp * 2)])
    return rows


def write_png(rows, path, tmp):
    height, width = len(rows), len(rows[0])
    stride = (width * 3 + 3) & ~3
    body = bytearray()
    for row in reversed(rows):
        line = bytearray()
        for r, g, b in row:
            line += bytes((b, g, r))
        line += b'\0' * (stride - width * 3)
        body += line
    header = b'BM' + struct.pack('<IHHI', 54 + len(body), 0, 0, 54)
    info = struct.pack('<IiiHHIIiiII', 40, width, height, 1, 24, 0, len(body), 2835, 2835, 0, 0)
    bmp = os.path.join(tmp, os.path.basename(path) + '.bmp')
    with open(bmp, 'wb') as f:
        f.write(header + info + body)
    subprocess.run(['sips', '-s', 'format', 'png', bmp, '--out', path], check=True, capture_output=True)


def compare(old, new):
    changed = 0
    out = []
    for row_old, row_new in zip(old, new):
        line = []
        for (r0, g0, b0), (r1, g1, b1) in zip(row_old, row_new):
            grey = (r1 + g1 + b1) // 6 + 40
            if abs(r0 - r1) > THRESHOLD or abs(g0 - g1) > THRESHOLD or abs(b0 - b1) > THRESHOLD:
                changed += 1
                line.append((235, 40, 40))
            else:
                line.append((grey, grey, grey))
        out.append(line)
    total = sum(len(r) for r in new) or 1
    return changed / total * 100, out


def main():
    old_dir, new_dir, report = sys.argv[1:4]
    diff_dir = os.path.join(os.path.dirname(report), 'diff')
    os.makedirs(diff_dir, exist_ok=True)
    rel = lambda p: os.path.relpath(p, os.path.dirname(report))
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in sorted(os.listdir(new_dir)):
            if not name.endswith('.png'):
                continue
            new_png, old_png = os.path.join(new_dir, name), os.path.join(old_dir, name)
            if not os.path.exists(old_png):
                rows.append((101, name, None, new_png, None))
                continue
            pct, diff = compare(read_bmp(old_png, tmp), read_bmp(new_png, tmp))
            diff_png = os.path.join(diff_dir, name)
            write_png(diff, diff_png, tmp)
            rows.append((pct, name, old_png, new_png, diff_png))
    rows.sort(key=lambda r: -r[0])
    cells = []
    for pct, name, old_png, new_png, diff_png in rows:
        label = 'new shot' if pct > 100 else f'{pct:.1f}% changed'
        imgs = ''.join(f'<figure><img src="{rel(p)}" loading="lazy"><figcaption>{cap}</figcaption></figure>'
                       for p, cap in ((old_png, 'before'), (new_png, 'after'), (diff_png, 'changed pixels')) if p)
        cells.append(f'<section><h2>{name[:-4]} <small>{label}</small></h2><div class="row">{imgs}</div></section>')
    with open(report, 'w') as f:
        f.write('<!doctype html><meta charset="utf-8"><title>Shot comparison</title><style>'
                'body{font:14px system-ui;margin:16px;background:#f4f1ea;color:#222}h2{font-size:15px;margin:18px 0 6px}'
                'small{color:#a33;font-weight:400}.row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}'
                'figure{margin:0}img{width:100%;display:block;border:1px solid #ccc}figcaption{font-size:12px;color:#666}'
                '</style><h1>Shot comparison</h1>' + ''.join(cells))
    for pct, name, *_ in rows:
        print(f'{"new" if pct > 100 else f"{pct:5.1f}%"}  {name[:-4]}')
    print(f'Report: {report}')


if __name__ == '__main__':
    main()
