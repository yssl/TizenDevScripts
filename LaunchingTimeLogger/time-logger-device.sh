#!/bin/bash

printf "# Command: %s\n\n" "$*"
echo "# Milliseconds since UNIX epoch & all stdout"
invoke=$(date +%s%3N)
printf "(time-logger)Invoking command: %d\n" $invoke
eval "$*"
