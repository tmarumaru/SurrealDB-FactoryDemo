#!/bin/bash

# Start the production process dashboard

source common.sh

# port number for streamlit
export STREAMLIT_PORT="8080"

docker compose -f ./docker-compose-dashboard.yml up -d
