#!/bin/bash
magick \
    -size 410x80 xc:white -font Noto-Sans-Italic \
    -fill '#E6E7E8' \
    -draw "rectangle 80,60 380,70" -draw "rectangle 80,20 380,30" \
    -fill '#31373D' \
    -draw "line  80,15  80,20" -draw "text  80,13 '1'" \
    -draw "line 180,15 180,20" -draw "text 180,13 '10'" \
    -draw "line 280,15 280,20" -draw "text 280,13 '100'" \
    -draw "line 380,15 380,20" -draw "text 380,13 '1000'" \
    -draw "line  80,55  80,60" -draw "text  80,53 '0'" \
    -draw "line 155,55 155,60" -draw "text 155,53 '¼'" \
    -draw "line 230,55 230,60" -draw "text 230,53 '½'" \
    -draw "line 305,55 305,60" -draw "text 305,53 '¾'" \
    -draw "line 380,55 380,60" -draw "text 380,53 '1'" \
    -pointsize 13 -draw "text 0,30 'Guesses'" \
    -draw "text 0,70 'Accuracy'" \
    ${1-redactle-base.png}
