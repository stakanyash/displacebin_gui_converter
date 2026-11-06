import struct
from PIL import Image
import json
import logging
import base64
import zlib
from pathlib import Path
from config import DGCVER

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

    json_path = _write_metadata(output_path, _min, _max, _del, raw_values=raw) if save_metadata else None

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

    json_path = _write_metadata(output_path, _min, _max, _del, raw_values=raw) if save_metadata else None

    return _min, _max, _del, json_path

def _write_metadata(base_path, _min, _max, _del, raw_values=None):
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

    if raw_values is not None:
        try:
            packed = struct.pack(f'{len(raw_values)}f', *raw_values)
            compressed = zlib.compress(packed, level=9)
            encoded = base64.b64encode(compressed).decode('ascii')
            meta['OriginalValues'] = encoded
            logging.info(
                f"OriginalValues saved: {len(raw_values)} floats, "
                f"{len(encoded)} bytes base64"
            )
        except Exception as e:
            logging.warning(f"Failed to encode OriginalValues: {e}")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    logging.info(f"Metadata saved to: {json_path}")

    return str(json_path)