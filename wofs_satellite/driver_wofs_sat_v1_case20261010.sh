#!/bin/bash

source ~/.bashrc

micromamba activate /scratch4/NCEPDEV/fv3-cam/Hongli.Wang/WoFS/conda/envs/wofs-satellite

START_STR="202610101415"
END_STR="202610110615"
#SAT_ID="18"
SAT_ID="19"
SKY_ID="1" # 0: allscky #1: clearsky

# Convert YYYYMMDDHHMM strings to Unix timestamps (Epoch seconds)
START=$(date -d "${START_STR:0:4}-${START_STR:4:2}-${START_STR:6:2} ${START_STR:8:2}:${START_STR:10:2}" +%s)
END=$(date -d "${END_STR:0:4}-${END_STR:4:2}-${END_STR:6:2} ${END_STR:8:2}:${END_STR:10:2}" +%s)

# 15 minutes = 900 seconds
STEP=900

while [[ "$START" -le "$END" ]]; do
    # Format the current epoch integer back into YYYYMMDDHHMM for your files/directories
    CURRENT_STR=$(date -d "@$START" +"%Y%m%d%H%M")

    OUTPUT_DIR="data/${CURRENT_STR}/${SAT_ID}_${SKY_ID}"
    mkdir -p ${OUTPUT_DIR}
    LOG_FILE="${OUTPUT_DIR}/log.wofs.sat.${CURRENT_STR}"

    echo "Running create.sh with timestamp: $CURRENT_STR"
    echo "Output directory: $OUTPUT_DIR"
    echo "Log file: $LOG_FILE"
     
    # Uncomment when ready to execute:
    rm -fr "$LOG_FILE"
    echo "bash create.sh "$CURRENT_STR" ./geo_em.d01.nc "$OUTPUT_DIR" ${SAT_ID} ${SKY_ID}  "
   
    # You can also choose use creat_cwp.sh or create_abi_rad.sh 
    bash create.sh "$CURRENT_STR" ./geo_em.d01.nc "$OUTPUT_DIR" ${SAT_ID} ${SKY_ID} >> "$LOG_FILE" 2>&1

    # Stop after the final timestamp is processed
    [[ "$START" -eq "$END" ]] && break

    # Advance cleanly by 15 minutes (900 seconds)
    START=$((START + STEP))

    # Wait 2 minutes
    # sleep 180 
done

