#!/bin/bash

# the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

TGT_DIR=$1
GOES_SAT=$2
start=$3
end=$4

echo "wofs-obs-sat directory: $DIR"
echo "target directory: $TGT_DIR"
echo "GOES satellite: $GOES_SAT"

if [ ! -e "$TGT_DIR/geo_em.d01.nc" ]; then
    echo "Error: geo_em.d01.nc does not exist in the target directory: $TGT_DIR"
    exit 1
fi

cd $DIR

runsat() {

    echo "Running for time: $1"

    TEMPD=`mktemp -d -p "$DIR"`

    cd $2

    source create.sh $1 $TGT_DIR/geo_em.d01.nc $TEMPD $GOES_SAT

    mkdir -p "$TGT_DIR/$1"

    mv $TEMPD/*.nc $TGT_DIR/$1
    mv $TEMPD/*.png $TGT_DIR/$1

    # Iterate over each file in the directory
    for FILE in "$TGT_DIR/$1"/*.nc; do
        FILENAME=$(basename "$FILE")
        HOURMINUTE=${FILENAME:8:4}

        if [[ ! $FILENAME =~ ^[0-9] ]]; then
            echo "Skipping: $FILENAME"
            continue
        fi

        if [[ "$FILENAME" == *"CWP"* ]]; then
            mv "$FILE" "$TGT_DIR/$1/$HOURMINUTE-cwpobs.nc"
        elif [[ "$FILENAME" == *"GOES"* ]]; then
            mv "$FILE" "$TGT_DIR/$1/$HOURMINUTE-goes.nc"
        fi
    done

}

start_date=`echo $start | cut -b 1-8`

echo "Start time: $start"
echo "End time: $end"

current_time=$start

while [ $current_time != $end ]
do
    yr=`echo $current_time | cut -b 1-4`
    mon=`echo $current_time | cut -b 5-6`
    day=`echo $current_time | cut -b 7-8`
    hr=`echo $current_time | cut -b 9-10`
    min=`echo $current_time | cut -b 11-12`

    runsat $current_time $DIR

    current_time=$(date -u --date "$yr-$mon-${day}T${hr}:${min}:00 UTC +15 minutes" +%Y%m%d%H%M)

    sleep 1
done

runsat $end $DIR

echo "Removing temporary directories"

rm -r $DIR/tmp.*

echo "Finished running satellite obs for time range $start - $end"