#!/bin/bash

docker run -it --rm --network redis-net valkey/valkey:8-alpine \
  redis-cli --cluster create \
  redis-node-0:6000 redis-node-1:6001 redis-node-2:6002 \
  redis-node-3:6003 redis-node-4:6004 redis-node-5:6005 \
  --cluster-replicas 1