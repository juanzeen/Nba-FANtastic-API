#!/bin/bash
echo "Restaurando dados e índices..."
mongorestore --uri="mongodb://user:password@localhost:27017/?authSource=admin" --nsInclude=nba_fantastic* ./dump/
