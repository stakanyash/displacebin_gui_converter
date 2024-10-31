import struct
from PIL import Image

def process_raw(input_path, output_path, size):
    with open(input_path, 'rb') as stream:
        raw = struct.unpack(f'{size ** 2}f', stream.read())

    _min = min(raw)
    _max = max(raw)
    _del = _max - _min

    def mut(v):
        rel = v
        rel -= _min
        rel /= _del
        rel *= 0xFFFF
        rel = int(rel)
        return rel

    with open(output_path, 'wb') as stream:
        data = struct.pack(f'{size ** 2}H', *map(mut, raw))
        stream.write(data)

    return _min, _max, _del

def process_png(input_path, output_path, size):
    with open(input_path, 'rb') as stream:
        raw = struct.unpack(f'{size ** 2}f', stream.read())

    _min = min(raw)
    _max = max(raw)
    _del = _max - _min

    def mut(v):
        rel = v
        rel -= _min
        rel /= _del
        rel *= 0xFFFF
        rel = int(rel)
        return rel

    normalized_data = list(map(mut, raw))

    image = Image.new('I', (size, size))
    image.putdata(normalized_data)
    image.save(output_path)

    return _min, _max, _del
