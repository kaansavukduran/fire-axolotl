# SPDX-License-Identifier: MPL-2.0
"""Register generated whole-character frames; never draw or rig a character.

Input: existing Aion Pet PNG and three generated green-matte 3x4 sheets.
Only chroma removal, complete-pose extraction, shared scaling and encoding occur.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / 'browser/extension/characters'


def bands(values, minimum=3, gap=8):
    result = []
    for index, value in enumerate(values):
        if value < minimum:
            continue
        if result and index - result[-1][1] <= gap:
            result[-1][1] = index + 1
        else:
            result.append([index, index + 1])
    return result


def register(path, destination):
    source = Image.open(path).convert('RGB')
    key_green = source.getpixel((0, 0))[1]
    pixels = []
    for red, green, blue in source.getdata():
        dominance = green - max(red, blue)
        if green > 100 and dominance > 18:
            alpha = max(0, min(255, round(255 * (1 - dominance / key_green))))
            if alpha < 8:
                pixels.append((0, 0, 0, 0))
            else:
                opacity = alpha / 255
                final_red, final_blue = min(255, round(red / opacity)), min(255, round(blue / opacity))
                final_green = max(0, min(255, round((green - (1 - opacity) * key_green) / opacity)))
                pixels.append((final_red, min(final_green, max(final_red, final_blue)), final_blue, alpha))
        else:
            pixels.append((red, min(green, max(red, blue)), blue, 255))
    clean = Image.new('RGBA', source.size)
    clean.putdata(pixels)
    alpha = clean.getchannel('A')
    rows = bands([sum(value > 80 for value in alpha.crop((0, y, source.width, y + 1)).getdata()) for y in range(source.height)], minimum=8)
    if len(rows) != 3:
        raise ValueError(f'Expected three separated activity rows, found {rows}')
    poses = []
    for top, bottom in rows:
        columns = bands([sum(value > 80 for value in alpha.crop((x, top, x + 1, bottom)).getdata()) for x in range(source.width)])
        if len(columns) != 4:
            raise ValueError(f'Expected four complete poses in row {(top, bottom)}, found {columns}')
        for left, right in columns:
            if left < 3 or right > source.width - 3 or top < 3 or bottom > source.height - 3:
                raise ValueError('Generated pose touches the source boundary; regenerate it')
            poses.append((left, top, right, bottom))
    scale = min(240 / max(r - l for l, t, r, b in poses), 264 / max(b - t for l, t, r, b in poses))
    output = Image.new('RGBA', (1024, 864))
    for index, bounds in enumerate(poses):
        pose = clean.crop(bounds)
        pose = pose.resize((round(pose.width * scale), round(pose.height * scale)), Image.Resampling.LANCZOS)
        x = index % 4 * 256 + (256 - pose.width) // 2
        y = index // 4 * 288 + 276 - pose.height
        output.alpha_composite(pose, (x, y))
    output.save(destination, optimize=True)
    return {'source_size': list(source.size), 'source_rectangles': [list(p) for p in poses], 'shared_scale': scale, 'cell_size': [256, 288], 'processing': 'green-matte removal, complete-pose registration, one shared scale, PNG encoding'}


def prepare(args):
    DESTINATION.mkdir(exist_ok=True)
    shutil.copyfile(args.aion, DESTINATION / 'aion.png')
    catalog = []
    provenance = {'date': '2026-11-09', 'pillow': PIL.__version__, 'identity': 'User-authorized AI-generated Aion/lamb/wolf/owl references; no built-in ChatGPT pet artwork copied.', 'sources': {}}
    names = {'aion': {'tr': 'Aion', 'en': 'Aion'}, 'sheep': {'tr': 'Kuzu', 'en': 'Lamb'}, 'wolf': {'tr': 'Kurt', 'en': 'Wolf'}, 'owl': {'tr': 'Baykuş Ömer', 'en': 'Ömer the Owl'}}
    for name in names:
        source = Path(getattr(args, name))
        record = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
        if name == 'aion':
            record.update({'pet_id': 'pet_6aad786b91808191b25c0836c76cbaa1', 'processing': 'Unmodified existing user-owned custom Pet PNG'})
            width, height, w, h = 1536, 2288, 192, 208
            clips = {key: [[i * w, row * h, w, h] for i in range(count)] for key, row, count in [('idle', 0, 6), ('read', 8, 6), ('work', 7, 6), ('wave', 3, 4)]}
        else:
            record.update(register(source, DESTINATION / f'{name}.png'))
            width, height, w, h = 1024, 864, 256, 288
            clips = {key: [[i * w, row * h, w, h] for i in range(4)] for row, key in enumerate(['idle', 'read', 'work'])}
        record['packaged_sha256'] = hashlib.sha256((DESTINATION / f'{name}.png').read_bytes()).hexdigest()
        provenance['sources'][name + '.png'] = record
        catalog.append({'id': name, 'name': names[name], 'path': f'characters/{name}.png', 'width': width, 'height': height, 'fps': 4, 'clips': clips})
    (DESTINATION / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    (DESTINATION / 'PROVENANCE.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    print('Registered all four whole-character companions and recorded source hashes')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['aion', 'sheep', 'wolf', 'owl']:
        parser.add_argument('--' + name, type=Path, required=True)
    prepare(parser.parse_args())
