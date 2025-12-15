#!/bin/bash

shopt -s nullglob

for f in *.mkv; do
    out="audio/${f%.mkv}.opus"

    # Skip if output exists
    if [[ -f "$out" ]]; then
        echo "Skipping '$f' (already converted)"
        continue
    fi

    echo "Normalising & converting: $f → $out"

    #
    # ==== FIRST PASS (no output; capture loudness stats) ====
    #
    # -14 is the upper safe bound, -16 is the recommended
    #

    stats=$(ffmpeg -i "$f" \
        -filter_complex "[0:a]loudnorm=I=-14:TP=-1:LRA=11:print_format=json" \
        -f null - 2>&1)

    # Extract required measured parameters
    input_i=$(echo "$stats"  | grep 'input_i'  | sed 's/.*: "\(.*\)".*/\1/')
    input_tp=$(echo "$stats" | grep 'input_tp' | sed 's/.*: "\(.*\)".*/\1/')
    input_lra=$(echo "$stats"| grep 'input_lra'| sed 's/.*: "\(.*\)".*/\1/')
    input_thresh=$(echo "$stats"| grep 'input_thresh'| sed 's/.*: "\(.*\)".*/\1/')
    target_offset=$(echo "$stats"| grep 'target_offset'| sed 's/.*: "\(.*\)".*/\1/')

    #
    # ==== SECOND PASS (actual output) ====
    #
    ffmpeg -i "$f" \
        -filter_complex "[0:a:0]loudnorm=I=-14:TP=-1:LRA=11:linear=false:measured_I=$input_i:measured_TP=$input_tp:measured_LRA=$input_lra:measured_thresh=$input_thresh:offset=$target_offset:print_format=none [ln]" \
        -map "[ln]" \
        -c:a libopus -b:a 128k -vbr on "$out"
done
