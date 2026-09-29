#!/bin/bash
cd /roms/ports/meujogo

# Diz ao Linux do R36S que este é um terminal padrão de tela cheia
export TERM=linux
export PYTHONUNBUFFERED=1

python3 main.py > log.txt 2>&1
