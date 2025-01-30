#!/bin/bash

SECRET=$(cat ./secret/secret.txt)

curl -X POST -H "Content-Type: application/json" -d "{\"secret\":\"$SECRET\",\"data\":\"hej!\"}" localhost/report/1/1
