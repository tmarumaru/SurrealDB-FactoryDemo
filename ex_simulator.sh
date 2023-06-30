#!/bin/bash

# Start Simulator that simulates the production process in a factory.

source common.sh

# Clock for factory simulator
export CLOCK=500

docker compose -f ./docker-compose-simulator.yml up
