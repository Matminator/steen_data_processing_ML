# steen_data_processing_ML

## Instructions 

Clone the repository to the location where you want to work with the data:
```
git clone https://github.com/Matminator/steen_data_processing_ML.git
```

Go to the file steen_processing/ugly_submitter.py and set the number of data divisions (25 should work well as we need around 50000 images for each divide to work, so 12ns/25 = 50000 images) and specify the path to your data:
```python
# --- Inpus -------------
num_divides = 25
input_traj_name = '../md_run.traj'
# -----------------------
```
Run the ugly_submitter.py script:
```
ml ASE
python ugly_submitter.py
```
This will submit #num_divides jobs to Niflheim.
```
