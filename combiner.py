import numpy as np
import os
import re

def get_sorted_filenames(folder_path):
    # Regex pattern to match files ending with INDEX_XX.npz where XX is a number between 0 and 799
    pattern = r'INDEX_(\d{1,3})\.npz'

    # List to store tuples of (number, filename)
    matching_files = []


    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        match = re.search(pattern, filename)
        if match:
            # Extract the number XX from the filename
            number = int(match.group(1))
            if 0 <= number <= 10000:
                matching_files.append((number, filename))
            else:
                '\n--- An CRITICAL ERROR occurred ---\n'
        

    # Sort the list of tuples by the number (XX)
    matching_files.sort()

    # Return only the filenames in sorted order
    sorted_filenames = [filename for _, filename in matching_files]
    return sorted_filenames


def load_and_combine_data(folder_path = 'steen_processing'):
    
    sorted_filenames = get_sorted_filenames(folder_path)

    # loading data:
    all_data = []
    for i, filename in enumerate(sorted_filenames):
        data =  np.load(folder_path + '/' + filename)
        components = data['components']
        all_data.append(components)
        if i%30 == 0:
            print(np.round(100 * i/len(sorted_filenames), 1), '% loaded', flush = True)
    print('Data Loaded!', flush = True)

    combined_components = np.vstack(all_data)

    return combined_components
