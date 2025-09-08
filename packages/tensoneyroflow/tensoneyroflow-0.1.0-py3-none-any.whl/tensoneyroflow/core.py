import os
import struct

def get_file_type(file_path):
    """Определяет тип файла по сигнатуре"""
    signatures = {
        b"\xff\xd8\xff": "JPEG",
        b"\x89PNG\r\n\x1a\n": "PNG",
        b"BM": "BMP",
        b"GIF87a": "GIF87a",
        b"GIF89a": "GIF89a",
        b"II*\x00": "TIFF",
        b"MM\x00*": "TIFF",
        b"RIFF": "WEBP",
    }

    try:
        with open(file_path, "rb") as f:
            header = f.read(12)

        for sig, ftype in signatures.items():
            if header.startswith(sig):
                return ftype
        return "Unknown"
    except:
        return "Error"