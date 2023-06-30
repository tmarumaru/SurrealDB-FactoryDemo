#!/bin/bash

if test -f ".env"; then
# load .env file
  set -o allexport
  source .env set
  set +o allexport
fi

# Factory-demo image
export IMAGE="factory-demo"

# SurrealDB hostname (Do not change)
export SERVER="surrealdb"

# SurrealDB settings (Can be changed)
export PORT="8000"
export USER="root"
export PW="root"
export DATABASE="test"
export NAMESPACE="test"

# SurrealDB database directory  (Can be changed)
export DATABASE_DIR="/tmp/surrealdb"

# json file name (Can be changed)
FACTORY_DATA_JSON_FILE="factory_data.json"

# Specifies the directory where json files are stored on the docker host. (Can be changed)
export SOURCE_DIR="/tmp/data"

# Specify the docker container mount point for the json-file. (Do not change)
export MOUNT_POINT="/app/data"
export FACTORY_DATA_JSON_FILE_PATH="${MOUNT_POINT}/${FACTORY_DATA_JSON_FILE}"
