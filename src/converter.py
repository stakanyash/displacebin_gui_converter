import struct
from PIL import Image
import json
import logging
from pathlib import Path

DGCVER = b'DisplaceGUI_2.0.1'

def process_raw(input_path, output_path, size, save_metadata=True):
    with open(input_path, 'rb') as stream:
        raw = struct.unpack(f'{size ** 2}f', stream.read())

    _min = min(raw)
    _max = max(raw)
    _del = _max - _min

    if _del == 0.0:
        logging.warning("All values are identical. Writing flat white map (0xFFFF).")
        normalized_data = [0xFFFF for _ in range(size ** 2)]
    else:
        def mut(v):
            rel = v - _min
            rel /= _del
            rel *= 0xFFFF
            return int(rel)
        
        normalized_data = list(map(mut, raw))

    with open(output_path, 'wb') as stream:
        data = struct.pack(f'{size ** 2}H', *normalized_data)
        stream.write(data)

    json_path = _write_metadata(output_path, _min, _max, _del) if save_metadata else None

    return _min, _max, _del, json_path

def process_png(input_path, output_path, size, save_metadata=True):
    with open(input_path, 'rb') as stream:
        raw = struct.unpack(f'{size ** 2}f', stream.read())

    _min = min(raw)
    _max = max(raw)
    _del = _max - _min

    if _del == 0.0:
        logging.warning("All values are identical. Writing flat white image.")
        normalized_data = [0xFFFF for _ in range(size ** 2)]
    else:
        def mut(v):
            rel = v - _min
            rel /= _del
            rel *= 0xFFFF
            return int(rel)

        normalized_data = list(map(mut, raw))

    image = Image.new('I;16', (size, size))
    image.putdata(normalized_data)
    image.save(output_path, format="png")

    json_path = _write_metadata(output_path, _min, _max, _del) if save_metadata else None

    return _min, _max, _del, json_path

def _write_metadata(base_path, _min, _max, _del):
    output_dir = Path(base_path).parent

    mapname = output_dir.name

    json_filename = f"displace_{mapname}_metadata.json"
    json_path = output_dir / json_filename

    meta = {
        'Min': _min,
        'Max': _max,
        'Delta': _del,
        'DGCVer': DGCVER.decode('utf-8', errors='ignore')
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    logging.info(f"Metadata saved to: {json_path}")

    return str(json_path)