# steen_data_processing_ML

## Instructions 

Clone the repository to the location where you want to work with the data:
```
git clone https://github.com/Matminator/steen_data_processing_ML.git
```

Go to the file steen_processing/ugly_submitter.py and set the number of data divisions (800 should work well) and specify the path to your data:
```python
# --- Inpus -------------
num_divides = 800
input_traj_name = '../md_run.traj'
# -----------------------
```

# Specify the trajectory file
traj_file = 'TEMP' # <------------------------------ Change this path to your .traj file
traj = Trajectory(traj_file)[XXX:YYY]


# Specify the file where components are saved and loaded
# from. Mind that if this file exists the results will be loaded
# from it so no new detection takes place.
components_file = 'TEMP' #<-------------------------- Change the name of your output file. Important that the format is .npz!

Run the ugly_submitter.py script:
```
ml ASE
python ugly_submitter.py
```
This will submit #num_divides jobs to Niflheim.

How to load the data:
```python
from combiner import load_and_combine_data
frame = load_and_combine_data()
```
This will load the 'components' part of Steen's data processing as a numpy array (np.array).

NOTE: If you are not loading the data from the same location as the combiner.py file, you will need to provide the location of the steen_processing folder.


