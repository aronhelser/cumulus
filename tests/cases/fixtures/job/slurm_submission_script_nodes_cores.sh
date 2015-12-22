#!/bin/sh
#                             _
#                            | |
#   ___ _   _ _ __ ___  _   _| |_   _ ___
#  / __| | | | '_ ` _ \| | | | | | | / __|
# | (__| |_| | | | | | | |_| | | |_| \__ \
#  \___|\__,_|_| |_| |_|\__,_|_|\__,_|___/
#
#
#SBATCH --job-name=dummy-123432423
#SBATCH --nodes=12312312
#SBATCH --cpus-per-task=8

ls
sleep 20
mpirun -n 1000000 parallel
