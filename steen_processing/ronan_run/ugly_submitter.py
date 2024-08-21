
# --- Inpus -------------
num_divides = 20
input_traj_name = '/home/scratch3/rogle/first_alcl3_acetamidine_1_5.traj' # <------------------------------------------------------------------- CHANGE THIS
output_filename= 'first'
# -----------------------

# *** Imports: ***
import os
import math
from ase.io import Trajectory

traj = Trajectory(input_traj_name)
len_traj = len(traj)
os.environ['output_file'] = output_filename
os.environ['traj_name'] = input_traj_name

batch_size = math.ceil(len_traj / num_divides)

print('\n-- UGLY SUBMITTER :-P --')
print('batches_size:', batch_size)
print('trajectory length:', len_traj)
print('--------------------------------\n')

cwd = os.getcwd()

end_index = 0
for com_id in range(num_divides):
    os.environ['com_id'] = str(com_id)
    start_index = end_index
    end_index += batch_size
    if end_index > len_traj:
        end_index = len_traj
    print('start_index:', start_index)
    print('end_index:', end_index)

    # ---- Job file ------------
    with open('job.sh', 'r') as file:

        red_file = file.read()

        red_file = red_file.replace('#SBATCH --job-name US_',
                                    '#SBATCH --job-name US_' + str(com_id))
        
        red_file = red_file.replace('-NNN-', str(com_id))
        red_file = red_file.replace('-START_INDEX-', str(start_index))
        red_file = red_file.replace('-END_INDEX-', str(end_index))
        red_file = red_file.replace('-OFFSET_INDEX-', str(start_index))
        red_file = red_file.replace('-TRAJ-', input_traj_name)
        
        job_name = 'job_' + str(com_id) + '.sh'
        with open('TEMP_job_file.sh', 'w') as file:
            file.write(red_file)

    os.system('sbatch ' + 'TEMP_job_file.sh')

os.remove('TEMP_job_file.sh')

print('\n-- UGLY SUBMITTER :-P --')
print('---> Submitted successfully !!!')
print('--------------------------------\n')