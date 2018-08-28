#!/bin/bash

for FILENAME in *.svg; do
	convert ${FILENAME%%.*}.svg -alpha off ${FILENAME%%.*}.png
done

for FILENAME in *.png; do
	convert $FILENAME -resize 50% converted/$FILENAME
done
