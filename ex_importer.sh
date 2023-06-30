#!/bin/bash

# Start Importer that imports factory data into SurrealDB

source common.sh

docker compose -f ./docker-compose-importer.yml up
