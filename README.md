# steen_data_processing_ML

## Instructions 

clone the repository to where you whant to work with the data:
```
git clone https://github.com/Matminator/steen_data_processing_ML.git
```

Go to the file steen_processing/ugly_submitter.py and select the number of divides (800 should be fine) of the data and put the path to your data:
```python
# --- Inpus -------------
num_divides = 800
input_traj_name = '../md_run.traj'
# -----------------------
```
Then run the ugly_submitter.py script i.e.:
```
ml ASE
python ugly_submitter.py
```
This will submit #num_divides jobs to Nifelhime

How to load the data:
```python
from combiner import load_and_combine_data
frame = load_and_combine_data()
```

This loads the 'components' part of steens data processing as an np.array
