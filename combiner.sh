#!/bin/bash
#SBATCH --job-name combiner
#SBATCH -e ./combiner.err
#SBATCH -o ./combiner.out
#SBATCH --mail-type None
#SBATCH -N 1
#SBATCH -n 24 
#SBATCH -p xeon24el8_test
#SBATCH -t 00:30:00

module purge

ml Python

module use /home/modules/energy/modules/all

python combiner.py
 
