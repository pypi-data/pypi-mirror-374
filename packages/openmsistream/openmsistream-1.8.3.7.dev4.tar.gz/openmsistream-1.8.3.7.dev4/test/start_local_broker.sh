#!/bin/bash

set -euxo pipefail

docker compose -f local-kafka-broker-docker-compose.yml up -d