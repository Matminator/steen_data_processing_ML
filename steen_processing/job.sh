#!/bin/bash
#SBATCH --job-name US_
#SBATCH --mail-type None
#SBATCH -N 1
#SBATCH -n 96 
#SBATCH -p epyc96 
#SBATCH -t 01:00:00

module purge

ml Python

module use /home/modules/energy/modules/all

python detect_molecules_ugly_extension.py --N -NNN- --start_index -START_INDEX- --end_index -END_INDEX-
