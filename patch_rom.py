#!/usr/bin/env python3
"""Patch YGOWCT06 USA to use uncensored card art and fix Huge Revolution."""

import argparse
import hashlib
import struct
from pathlib import Path


EXPECTED_SHA1 = "9689337d6aac1ce9699ab60aac73fc2cfdccad9b"
EXPECTED_SIZE = 0x2000000

CARD_ART_INDEX_OFFSET = 0x15B5C00
CARD_ART_PAIR_COUNT = 800
EXPECTED_DIFFERING_ART_PAIRS = 90

HUGE_REVOLUTION_OFFSET = 0x20FC2
HUGE_REVOLUTION_OLD_VALUE = 0x4D
HUGE_REVOLUTION_NEW_VALUE = 0x8B


def sha1(data: bytes | bytearray) -> str:
    return hashlib.sha1(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Clean USA .gba ROM")
    parser.add_argument("output", type=Path, nargs="?", help="Patched .gba path")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file")
    args = parser.parse_args()

    input_path = args.input.resolve()
    output_path = (
        args.output.resolve()
        if args.output
        else input_path.with_name(
            f"{input_path.stem} (Uncensored + Huge Revolution Fix){input_path.suffix}"
        )
    )

    if input_path == output_path:
        raise SystemExit("Input and output paths must be different; the clean ROM is preserved.")
    if output_path.exists() and not args.force:
        raise SystemExit(f"Output already exists: {output_path}\nUse --force to replace it.")

    original = input_path.read_bytes()
    input_sha1 = sha1(original)
    if len(original) != EXPECTED_SIZE:
        raise SystemExit(
            f"Unexpected ROM size: 0x{len(original):X}; expected 0x{EXPECTED_SIZE:X}."
        )
    if input_sha1 != EXPECTED_SHA1:
        raise SystemExit(
            f"Unexpected ROM SHA-1: {input_sha1}\nExpected: {EXPECTED_SHA1}"
        )
    if original[HUGE_REVOLUTION_OFFSET] != HUGE_REVOLUTION_OLD_VALUE:
        raise SystemExit(
            f"Unexpected byte at 0x{HUGE_REVOLUTION_OFFSET:X}: "
            f"0x{original[HUGE_REVOLUTION_OFFSET]:02X}; "
            f"expected 0x{HUGE_REVOLUTION_OLD_VALUE:02X}."
        )

    patched = bytearray(original)
    differing_pairs = 0
    for card_index in range(CARD_ART_PAIR_COUNT):
        japanese_offset = CARD_ART_INDEX_OFFSET + card_index * 4
        international_offset = japanese_offset + 2
        japanese_art = struct.unpack_from("<H", original, japanese_offset)[0]
        international_art = struct.unpack_from("<H", original, international_offset)[0]

        if japanese_art != international_art:
            differing_pairs += 1
            struct.pack_into("<H", patched, international_offset, japanese_art)

    if differing_pairs != EXPECTED_DIFFERING_ART_PAIRS:
        raise SystemExit(
            f"Unexpected differing artwork pair count: {differing_pairs}; "
            f"expected {EXPECTED_DIFFERING_ART_PAIRS}."
        )

    patched[HUGE_REVOLUTION_OFFSET] = HUGE_REVOLUTION_NEW_VALUE

    for card_index in range(CARD_ART_PAIR_COUNT):
        pair_offset = CARD_ART_INDEX_OFFSET + card_index * 4
        japanese_art, international_art = struct.unpack_from("<HH", patched, pair_offset)
        if japanese_art != international_art:
            raise SystemExit(f"Artwork pair {card_index} was not patched correctly.")
    if patched[HUGE_REVOLUTION_OFFSET] != HUGE_REVOLUTION_NEW_VALUE:
        raise SystemExit("Huge Revolution patch verification failed.")

    output_path.write_bytes(patched)
    print(f"Input SHA-1:  {input_sha1}")
    print(f"Output SHA-1: {sha1(patched)}")
    print(f"Artwork mappings changed: {differing_pairs}")
    print(
        f"Huge Revolution: 0x{HUGE_REVOLUTION_OLD_VALUE:02X} -> "
        f"0x{HUGE_REVOLUTION_NEW_VALUE:02X} at 0x{HUGE_REVOLUTION_OFFSET:08X}"
    )
    print(f"Patched ROM: {output_path}")


if __name__ == "__main__":
    main()
