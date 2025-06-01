import struct
from PIL import Image
import logging

def process_raw(input_path, output_path, size):
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

    return _min, _max, _del


def process_png(input_path, output_path, size):
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
    image.save(output_path)

    return _min, _max, _del