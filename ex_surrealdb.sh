#!/bin/bash

# Start SurrealDB

source common.sh

docker compose -f ./docker-compose-surrealdb-file.yml up -d
