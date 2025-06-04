import struct
from PIL import Image
import os
import logging
import math

class RAWNot16BitError(Exception):
    pass

def reverse_converter(input_path, output_path, json_data):
    required_fields = ['Min', 'Max', 'Delta']
    for field in required_fields:
        if field not in json_data:
            raise ValueError(f"Missing required field in JSON: {field}")

    _min = float(json_data['Min'])
    _max = float(json_data['Max'])
    _del = float(json_data['Delta'])

    def is_zero(x, epsilon=1e-7):
        return abs(x) < epsilon

    if math.isnan(_min) or math.isnan(_max) or math.isnan(_del):
        raise ValueError("Invalid values detected: Min, Max or Delta is NaN.")

    if is_zero(_min) and is_zero(_max) and is_zero(_del):
        raise ValueError("Invalid values detected: Min and Max is zero.")
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()

    if ext == '.raw':
        with open(input_path, 'rb') as f:
            data_bytes = f.read()
            if not data_bytes:
                raise ValueError("Input .raw file contains no data.")

            if len(data_bytes) % 2 != 0:
                raise RAWNot16BitError("Input .raw file has incomplete 16-bit data.")
            
            normalized_data = list(struct.unpack(f'{len(data_bytes)//2}H', data_bytes))

    elif ext == '.png':
        image = Image.open(input_path)
        if image.mode != 'I;16':
            raise ValueError("Input PNG must be 16-bit integer grayscale")
        normalized_data = list(image.getdata())
    else:
        raise ValueError("Unsupported input format. Use .raw or .png")
    
    if _del == 0.0:
        logging.warning("Delta is zero. Restoring flat value of min.")
        raw_values = [_min] * len(normalized_data)
    else:
        raw_values = [(_val / 0xFFFF) * _del + _min for _val in normalized_data]

    with open(output_path, 'wb') as f:
        f.write(struct.pack(f'{len(raw_values)}f', *raw_values))

    return _min, _max, _del