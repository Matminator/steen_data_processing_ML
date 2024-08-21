#!/bin/bash
#SBATCH --job-name US_
#SBATCH --mail-type None
#SBATCH -e ./slurm-%j.err
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -p xeon24el8
#SBATCH --time=06:00:00

module purge

# ml Python

module use /home/modules/energy/modules/all

python detect_molecules_ugly_extension.py --N -NNN- --start_index -START_INDEX- --end_index -END_INDEX- --offset_index -OFFSET_INDEX-
