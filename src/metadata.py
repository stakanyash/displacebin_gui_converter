import base64
import json
import logging
import os
import struct
import zlib

MAGIC = b"DGCB"
FORMAT_VERSION = 1
FLAG_HAS_ORIGINAL_RANGE = 0x01
FLAG_HAS_ORIGINAL_VALUES = 0x02

class MetadataError(Exception):
    pass

def _read_exact(f, n):
    buf = f.read(n)
    if len(buf) != n:
        raise MetadataError(f"Unexpected EOF: wanted {n} bytes, got {len(buf)}")
    return buf

def read_metadata(path):
    with open(path, "rb") as f:
        head = f.read(4)
        f.seek(0)
        if head == MAGIC:
            logging.debug(f"Reading binary metadata: {path}")
            return _read_binary(f)
        logging.debug(f"Reading legacy JSON metadata: {path}")
        try:
            return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise MetadataError(f"File is neither DGCB nor valid JSON: {e}")

def _read_binary(f):
    magic = _read_exact(f, 4)
    if magic != MAGIC:
        raise MetadataError("Bad magic")

    fmt_ver, flags = struct.unpack("<HH", _read_exact(f, 4))
    if fmt_ver != FORMAT_VERSION:
        raise MetadataError(f"Unsupported format version: {fmt_ver}")

    mn, mx, dl, omn, omx, odl = struct.unpack("<6d", _read_exact(f, 48))

    dgcver_len, = struct.unpack("<H", _read_exact(f, 2))
    dgcver_bytes = _read_exact(f, dgcver_len) if dgcver_len else b""
    dgcver = dgcver_bytes.decode("utf-8", errors="replace") if dgcver_bytes else ""

    ov_len, = struct.unpack("<I", _read_exact(f, 4))
    ov_bytes = _read_exact(f, ov_len) if ov_len else b""

    meta = {
        "Min": mn,
        "Max": mx,
        "Delta": dl,
    }
    if dgcver:
        meta["DGCVer"] = dgcver
    if flags & FLAG_HAS_ORIGINAL_RANGE:
        meta["OriginalMin"] = omn
        meta["OriginalMax"] = omx
        meta["OriginalDelta"] = odl
    if flags & FLAG_HAS_ORIGINAL_VALUES:
        meta["OriginalValues"] = ov_bytes

    return meta

def write_metadata(path, data):
    flags = 0

    omn = omx = odl = 0.0
    if "OriginalMin" in data and "OriginalMax" in data and "OriginalDelta" in data:
        flags |= FLAG_HAS_ORIGINAL_RANGE
        omn = float(data["OriginalMin"])
        omx = float(data["OriginalMax"])
        odl = float(data["OriginalDelta"])

    ov_bytes = b""
    if "OriginalValues" in data and data["OriginalValues"] is not None:
        ov = data["OriginalValues"]
        if isinstance(ov, (bytes, bytearray)):
            ov_bytes = bytes(ov)
        elif isinstance(ov, str):
            ov_bytes = base64.b64decode(ov)
        elif isinstance(ov, (list, tuple)):
            packed = struct.pack(f"{len(ov)}f", *ov)
            ov_bytes = zlib.compress(packed, level=9)
        else:
            raise MetadataError(f"Unsupported OriginalValues type: {type(ov)}")
        flags |= FLAG_HAS_ORIGINAL_VALUES

    dgcver = data.get("DGCVer", "")
    if isinstance(dgcver, (bytes, bytearray)):
        dgcver = bytes(dgcver).decode("utf-8", errors="ignore")
    dgcver_bytes = (dgcver or "").encode("utf-8")

    tmp_path = str(path) + ".tmp"
    try:
        with open(tmp_path, "wb") as f:
            f.write(MAGIC)
            f.write(struct.pack("<HH", FORMAT_VERSION, flags))
            f.write(struct.pack(
                "<6d",
                float(data["Min"]),
                float(data["Max"]),
                float(data["Delta"]),
                omn, omx, odl,
            ))
            f.write(struct.pack("<H", len(dgcver_bytes)))
            if dgcver_bytes:
                f.write(dgcver_bytes)
            f.write(struct.pack("<I", len(ov_bytes)))
            if ov_bytes:
                f.write(ov_bytes)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise