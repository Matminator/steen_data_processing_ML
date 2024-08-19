import multiprocessing
from ase.io.trajectory import Trajectory
from collections import Counter
from scipy import sparse
from ase.neighborlist import NeighborList
import numpy as np
from ase.io import Trajectory
from collections import Counter
import json
import os

from concurrent import futures
import argparse
import sqlite3
import psutil


def get_memory_info():
    return psutil.virtual_memory().available * 100 / psutil.virtual_memory().total

class Detect(object):
    def __init__(self, traj, cutoff_dict,
                 saved_components_file='components.npz'):
        atoms = traj[0]
        self.traj = traj
        self.atoms = atoms
        self.cutoffs = [cutoff_dict[s.symbol] for s in atoms]
        self.save_file = saved_components_file
        self.syms = atoms.get_chemical_symbols()
        self.Cl_indices = np.array(
            [a.index for a in atoms if a.symbol == 'Cl'])
        self.Al_indices = np.array(
            [a.index for a in atoms if a.symbol == 'Al'])
        self.nl = NeighborList(self.cutoffs, skin=0,
                               self_interaction=False, bothways=False)
        self.create_database()
        self.parse_trajectory()

    def create_database(self):
        # Connect to SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(f'{self.save_file}.db')
        cursor = conn.cursor()

        # Create the table with an additional column for the reference ID
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chemical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT
        )
        ''')

        conn.commit()
        conn.close()
        
    def insert_data(self, data):
        # Connect to SQLite database
        conn = sqlite3.connect(f'{self.save_file}.db')
        cursor = conn.cursor()
        data_json = json.dumps(data)

        cursor.execute('''
        INSERT INTO chemical_data (data)
        VALUES (?)
        ''', (data_json,))

        conn.commit()
        conn.close()       
    
    def parse_trajectory(self):
        chunk_size = 1000
        total_items = len(self.traj)
        print(f'Read trajectory with {get_memory_info()}% memory available')
        for start_idx in range(0, total_items, chunk_size):
            end_idx = min(start_idx + chunk_size, total_items)
            # Define a new pool for every chunk
            with futures.ThreadPoolExecutor() as executor:
                traj = [a for a in self.traj[start_idx:end_idx]]
                for idx, ret in enumerate(executor.map(self.get_component_list, traj, chunksize=200)):
                    self.insert_data(ret)
                    # Check memory usage and optionally restart the loop if needed
                    avail_mem = get_memory_info()
                    print(f"Memory available after processing index {idx}: {avail_mem}", flush=True)
 
    def get_formula(self, fragment):
        return self.atoms[fragment].get_chemical_formula()

    def get_component_list(self, atoms):
        self.nl.update(atoms)
        mat = self.nl.get_connectivity_matrix(sparse=False)

        for i in self.Cl_indices:
            for j in range(len(atoms)):
                if self.syms[j] != 'Al':
                    mat[i, j] = 0
                    mat[j, i] = 0

        return self.get_mol_count(sparse.csgraph.connected_components(mat)[1])

    def get_mol_count(self, component):
        molecule_formula = []
        for idx in range(max(component) + 1):
            molecule_formula.append(self.get_formula(component == idx))
        molecule_count = dict(Counter(molecule_formula))
        
        return molecule_count
    
def save_components_file(fname, components, matrices):
    np.savez_compressed(fname, components=components, matrices=matrices)

def main():
    
    # ------------------------------------------------------------------------------------------
    # Create the parser
    parser = argparse.ArgumentParser(description="A script that takes command-line arguments")

    # print('Entered main function')
    # # # Add arguments
    parser.add_argument('--N', type=str, required=True)
    parser.add_argument('--start_index', type=int,  required=True)
    parser.add_argument('--end_index', type=int, required=True)
    parser.add_argument('--offset_index', type=int, required=True)

    # # Parse the arguments
    args = parser.parse_args()
    # # ------------------------------------------------------------------------------------------
    N = args.N
    XXX = args.start_index
    YYY = args.end_index
    traj_file = os.environ['traj_name']
    output_filename = os.environ['output_file']
    traj = Trajectory(traj_file)[XXX:YYY]

    # Specify the file where components are saved and loaded
    # from. Mind that if this file exists the results will be loaded
    # from it so no new detection takes place.
    
    components_file = f'concentrations_INDEX_{N}'

    cutoff_dict = {'Al': 1, 'Cl': 1.7, 'H': .37, 'O': 1, 'N': 1, 'C': 1}
    # components_file = 'component'
    Detect(traj, cutoff_dict, saved_components_file=components_file)

if __name__ == "__main__":
    main()
