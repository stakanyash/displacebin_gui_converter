import struct
from PIL import Image
import os
import logging
import math
import base64
import zlib

class RAWNot16BitError(Exception):
    pass

def _decode_original_values(json_data, expected_length):
    if 'OriginalValues' not in json_data:
        return None
    try:
        encoded = json_data['OriginalValues']
        compressed = base64.b64decode(encoded)
        packed = zlib.decompress(compressed)
        if len(packed) % 4 != 0:
            logging.warning("OriginalValues: decompressed size is not multiple of 4")
            return None
        floats = list(struct.unpack(f'{len(packed)//4}f', packed))
        if len(floats) != expected_length:
            logging.warning(
                f"OriginalValues length mismatch: {len(floats)} vs {expected_length}. "
                f"Falling back to full remap."
            )
            return None
        logging.info(f"OriginalValues decoded: {len(floats)} floats")
        return floats
    except Exception as e:
        logging.warning(f"Failed to decode OriginalValues: {e}")
        return None

def reverse_converter(input_path, output_path, json_data, custom_range=None):
    required_fields = ['Min', 'Max', 'Delta']
    for field in required_fields:
        if field not in json_data:
            raise ValueError(f"Missing required field in JSON: {field}")

    def is_zero(x, epsilon=1e-7):
        return abs(x) < epsilon

    if custom_range is not None:
        try:
            new_min = float(custom_range[0])
            new_max = float(custom_range[1])
        except (TypeError, ValueError, IndexError):
            raise ValueError("Invalid custom_range values")

        if math.isnan(new_min) or math.isnan(new_max):
            raise ValueError("Invalid custom range: NaN detected.")
        if new_max < new_min:
            raise ValueError("Invalid custom range: Max must be >= Min.")
        new_del = new_max - new_min
        if new_del == 0.0:
            logging.warning("Custom range has Min == Max. Terrain will be flat.")
    else:
        new_min = float(json_data['Min'])
        new_max = float(json_data['Max'])
        new_del = float(json_data['Delta'])

        if math.isnan(new_min) or math.isnan(new_max) or math.isnan(new_del):
            raise ValueError("Invalid values detected: Min, Max or Delta is NaN.")
        if is_zero(new_min) and is_zero(new_max) and is_zero(new_del):
            raise ValueError("Invalid values detected: Min and Max is zero.")

    if custom_range is None:
        logging.info(f"REVERSE MODE: original range ({new_min:.2f} – {new_max:.2f}), no extension")
    else:
        logging.info(f"REVERSE MODE: custom range ({new_min:.2f} – {new_max:.2f}), extension active")

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

    orig_floats = None
    if custom_range is not None:
        orig_floats = _decode_original_values(json_data, len(normalized_data))

    if orig_floats is not None:
        old_min = float(json_data['Min'])
        old_del = float(json_data['Delta'])

        orig_pxs = []
        for orig_float in orig_floats:
            if old_del > 0:
                opx = int(round((orig_float - old_min) / old_del * 0xFFFF))
                orig_pxs.append(max(0, min(0xFFFF, opx)))
            else:
                orig_pxs.append(0)

        raw_values = []
        changed_count = 0
        threshold = 1

        for i, (px, orig_px) in enumerate(zip(normalized_data, orig_pxs)):
            new_8bit = px >> 8
            orig_8bit = orig_px >> 8
            if abs(new_8bit - orig_8bit) <= threshold:
                raw_values.append(orig_floats[i])
            else:
                if new_del == 0.0:
                    raw_values.append(new_min)
                else:
                    raw_values.append((px / 0xFFFF) * new_del + new_min)
                changed_count += 1

        preserved = len(normalized_data) - changed_count
        logging.info(
            f"SMART RESTORE (8-bit comparison): "
            f"{changed_count}/{len(normalized_data)} pixels changed, "
            f"{preserved} preserved"
        )
    else:
        if custom_range is not None:
            logging.warning(
                "FALLBACK: custom range set, but OriginalValues unavailable. "
                "ENTIRE MAP will be rescaled."
            )
        if new_del == 0.0:
            logging.warning("Delta is zero. Restoring flat value of min.")
            raw_values = [new_min] * len(normalized_data)
        else:
            raw_values = [(px / 0xFFFF) * new_del + new_min for px in normalized_data]

    with open(output_path, 'wb') as f:
        f.write(struct.pack(f'{len(raw_values)}f', *raw_values))

    return new_min, new_max, new_del