#!/bin/bash
set -u

# --------------------------------------------------
# Configuration
# --------------------------------------------------
obsdir="/scratch4/NCEPDEV/fv3-cam/Hongli.Wang/WoFS/test/frdd-wofs-obs-satellite/wofs_satellite/data"
targetdir="/scratch4/NCEPDEV/stmp/Hongli.Wang/wofs_wrf/wrf/obs_hw/WOFSRun20261010-131148d1"

#start_time="202607270845"
#end_time="202607272345"
start_time="202610101500"
end_time="202610110600"

interval_minutes=15

# --------------------------------------------------
# Validate directories
# --------------------------------------------------
if [[ ! -d "$obsdir" ]]; then
    echo "ERROR: Observation directory does not exist: $obsdir"
    exit 1
fi

mkdir -p "$targetdir" || {
    echo "ERROR: Cannot create target directory: $targetdir"
    exit 1
}

# --------------------------------------------------
# Link observation files
# --------------------------------------------------
current="$start_time"
linked=0
missing=0

while [[ "$current" -le "$end_time" ]]; do

    date="${current:0:8}"
    hhmm="${current:8:4}"
#data/202607270845/19_1/202607270845_GOES19_CWP_OBS.nc
    input="$obsdir/${date}${hhmm}/19_1/${date}${hhmm}_GOES19_CWP_OBS.nc"
    outdir="$targetdir/${current}"
    output="$outdir/${hhmm}-cwpobs.nc"

    if [[ -f "$input" ]]; then
        mkdir -p "$outdir" || {
            echo "ERROR: Cannot create directory: $outdir"
            exit 1
        }

        ln -sfn "$input" "$output" || {
            echo "ERROR: Cannot create link: $output"
            exit 1
        }

        echo "LINK: $input -> $output"
        ((linked += 1))
    else
        echo "MISSING: $input"
        ((missing += 1))
    fi

    # Advance by the specified number of minutes.
    current=$(date -u -d \
        "${current:0:8} ${hhmm:0:2}:${hhmm:2:2} UTC + ${interval_minutes} minutes" \
        +"%Y%m%d%H%M")

    if [[ -z "$current" ]]; then
        echo "ERROR: Failed to advance timestamp"
        exit 1
    fi

done

echo "----------------------------------------"
echo "Linking completed."
echo "Links created/updated: $linked"
echo "Missing input files:   $missing"
echo "----------------------------------------"
