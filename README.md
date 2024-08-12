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

his will load the 'components' part of Steen's data processing as a numpy array (np.array).
