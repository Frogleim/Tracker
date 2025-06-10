#!/bin/bash

ICON="assets/my_icon.png"
OUT_DIR="iconset"

rm -rf "$OUT_DIR"
mkdir "$OUT_DIR"

sizes=(16 32 128 256 512)

for size in "${sizes[@]}"; do
    sips -s format png -s formatOptions best -z $size $size "$ICON" --out "$OUT_DIR/icon_${size}x${size}.png"
    sips -s format png -s formatOptions best -z $((size * 2)) $((size * 2)) "$ICON" --out "$OUT_DIR/icon_${size}x${size}@2x.png"
done
