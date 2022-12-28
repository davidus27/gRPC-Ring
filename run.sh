#!/bin/bash -e

# this script will iterate over "topologies.txt"
# each line will be an argument to the python script
# the python script will run the topology and log the output
# each file will be named with number of lines in the file

line_num=0
while read -r line; do
    line_num=$((line_num+1))
    echo "Running topology $line_num"
    python main.py "$line" 1&> "logs/$line_num.log"
    # end if the line_num is bigger that 200
    if [ $line_num -gt 150 ]; then
        break
    fi
done < topologies.txt