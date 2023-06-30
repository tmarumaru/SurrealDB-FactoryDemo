#!/bin/bash

# shellcheck disable=SC2046
docker stats $(docker ps|grep -v "NAMES"|awk '{ print $NF }'|tr "\n" " ") --no-stream
