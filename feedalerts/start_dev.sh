#!/bin/bash

docker-compose down

docker-compose up -d

WEB_CONTAINER_ID=`docker ps --filter="ancestor=feedalerts_web" -q`

echo "Web container ID: $WEB_CONTAINER_ID$"

docker exec -it $WEB_CONTAINER_ID /bin/bash 
