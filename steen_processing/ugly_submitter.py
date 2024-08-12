"""
Instructions...
"""

# --- Inpus -------------
num_divides = 800
input_traj_name = '../md_run.traj'
# -----------------------

# *** Imports: ***
import os
import math
from ase.io import Trajectory

# *** Reading trajectory file: ***
traj = Trajectory(input_traj_name)
len_traj = len(traj)

batch_size = math.ceil(len_traj / num_divides)

print('\n-- UGLY SUBMITTER :-P --')
print('batches_size:', batch_size)
print('--------------------------------\n')

cwd = os.getcwd()

end_index = 0
for com_id in range(num_divides):

    start_index = end_index
    end_index += batch_size
    if end_index > len_traj:
        end_index = len_traj


    # ---- Job file ------------
    with open('job.sh', 'r') as file:

        red_file = file.read()

        red_file = red_file.replace('#SBATCH --job-name US_',
                                    '#SBATCH --job-name US_' + str(com_id))
        
        red_file = red_file.replace('-NNN-', str(com_id))
        red_file = red_file.replace('-START_INDEX-', str(start_index))
        red_file = red_file.replace('-END_INDEX-', str(end_index))
        
        job_name = 'job_' + str(com_id) + '.sh'
        with open('TEMP_job_file.sh', 'w') as file:
            file.write(red_file)

    os.system('sbatch ' + 'TEMP_job_file.sh')

os.remove('TEMP_job_file.sh')




















