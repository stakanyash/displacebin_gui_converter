import struct
from PIL import Image
import logging
from pathlib import Path
from config import DGCVER
from metadata import write_metadata

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
    meta_filename = f"displace_{mapname}_metadata.dgc"
    meta_path = output_dir / meta_filename

    meta = {
        'Min': _min,
        'Max': _max,
        'Delta': _del,
        'DGCVer': DGCVER.decode('utf-8', errors='ignore'),
    }

    if raw_values is not None:
        meta['OriginalMin'] = _min
        meta['OriginalMax'] = _max
        meta['OriginalDelta'] = _del
        meta['OriginalValues'] = raw_values
        logging.info(f"OriginalValues included: {len(raw_values)} floats")

    write_metadata(str(meta_path), meta)
    logging.info(f"Metadata saved to: {meta_path}")
    return str(meta_path)