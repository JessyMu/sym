#!/usr/bin/env bash

# export PYTHONPATH=./
GPUS=1
workdir=/home/jesse/Project/SymPoint
OMP_NUM_THREADS=$GPUS torchrun --nproc_per_node=$GPUS --master_port=$((RANDOM + 10000)) test.py \
	 $workdir/svg_pointT.yaml  $workdir/best.pth --dist
