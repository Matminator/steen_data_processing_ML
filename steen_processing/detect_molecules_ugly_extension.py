from ase.db import connect
import re
import os
import itertools
import sys
import multiprocessing
from ase.io.trajectory import Trajectory
from collections import defaultdict
from collections import Counter
import collections
from scipy import sparse
from ase.neighborlist import NeighborList
from ase.io import read
from ase.visualize import view
import numpy as np
import time # added by Lotte

import argparse


class Detect(object):
    def __init__(self, traj, cutoff_dict,
                 saved_components_file='components.npz'):
        atoms = traj[0]
        self.cutoffs = [cutoff_dict[s.symbol] for s in atoms]
        self.save_file = saved_components_file
        self.syms = atoms.get_chemical_symbols()
        self.Cl_indices = np.array(
            [a.index for a in atoms if a.symbol == 'Cl'])
        self.Al_indices = np.array(
            [a.index for a in atoms if a.symbol == 'Al'])

        self.nl = NeighborList(self.cutoffs, skin=0,
                               self_interaction=False, bothways=False)

        self.initial_components = None
        self.traj = [a for a in traj]
        self.atoms = atoms
        self.molecule_information = {}
        self.open_reactions = {}
        self.closed_reactions = []
        self.reaction_indices = []

        self._initialize(atoms)
        self.parse_trajectory()

    def _initialize(self, atoms):
        cl = self.get_component_list(atoms)[0]
        self.initial_components = cl

        for Al_idx in self.Al_indices:
            fragment = self.get_fragment(Al_idx, cl)
            self.molecule_information[Al_idx] = [
                (0, self.get_formula(fragment))]
            
    def print_initial_components(self):
        print('Initial molecules:')
        for idx in range(max(self.initial_components) + 1):
            print(f'Fragment {idx}:', self.get_formula(self.initial_components == idx))

    def parse_trajectory(self):
        if os.path.isfile(self.save_file) and os.stat(self.save_file).st_size > 0:
            components, matrices = load_components_file(self.save_file)
            self.traj_components = components
            self.connectivity_matrices = matrices
        else:
            pool = multiprocessing.Pool()
            pm = pool.map(self.get_component_list, self.traj)
            pool.close()
            pool.join()

            components, matrices = zip(*pm)

            self.traj_components = components
            self.connectivity_matrices = matrices
            save_components_file(self.save_file, components, matrices)

    def get_fragment(self, idx, component_list):
        return np.where(component_list == component_list[idx])[0]

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

        return sparse.csgraph.connected_components(mat)[1], mat

    def follow(self):
        previous_components = self.initial_components
        for count, component_list in enumerate(self.traj_components):
            diff = component_list - previous_components
            if any(diff):
                print('Reaction took place at', count)

                reactant_dict = {}
                for Al_idx in self.Al_indices:
                    fragment = self.get_fragment(
                        Al_idx, previous_components)
                    reactant_dict[Al_idx] = (
                        self.get_formula(fragment), fragment)

                product_dict = {}
                for Al_idx in self.Al_indices:
                    fragment = self.get_fragment(Al_idx, component_list)
                    product_dict[Al_idx] = (
                        self.get_formula(fragment), fragment)

                reacted_idx = []
                reactants = []
                products = []
                all_indices_of_reaction = set()
                for Al_idx in self.Al_indices:
                    reac = reactant_dict[Al_idx][0]
                    prod = product_dict[Al_idx][0]
                    if reac != prod:
                        print(Al_idx, f'changed from {reac} to {prod}')
                        self.molecule_information[Al_idx].append((count, prod))
                        reactants.append(reac)
                        products.append(prod)
                        reacted_idx.append(Al_idx)
                        # Add the indices from the fragment belonging
                        # to this Al index to all the indices of all
                        # the fragments in this reaction
                        all_indices_of_reaction |= set(
                            reactant_dict[Al_idx][1])
                        all_indices_of_reaction |= set(product_dict[Al_idx][1])
                all_reaction_idx = sorted(all_indices_of_reaction)
                print('All indices of this reaction: ',
                      all_reaction_idx)

                cm = self.connectivity_matrices
                broken_indices = np.ravel(
                    np.nonzero(cm[count] - cm[count - 1]))
                print('The bond between the following indices broke: ',
                      broken_indices)

                # Save the time of reaction, all indices and broken
                # indices to easier process the specific reaction
                # later
                self.reaction_indices.append((count, all_reaction_idx,
                                              broken_indices))

                reactant_str = ', '.join(sorted(list(set(reactants))))
                product_str = ', '.join(sorted(list(set(products))))
                reaction_str = f'{reactant_str} -> {product_str}'
                opposite_reaction = f'{product_str} -> {reactant_str}'
                # A reaction should be identified by both Aluminium
                # indices and reaction species.
                reacts = tuple(reacted_idx + [opposite_reaction])
                if reacts in self.open_reactions.keys():
                    # It is now a closed reaction!?!
                    lifetime = count - self.open_reactions[reacts]
                    tot_reaction_str = opposite_reaction + ' -> ' + \
                        reaction_str.split(' -> ')[-1]
                    self.closed_reactions.append(
                        (reacts[:-1], f'{tot_reaction_str} :: lifetime: {lifetime} (from {self.open_reactions[reacts]} to {count})'))
                    self.open_reactions.pop(reacts)
                else:
                    # key is Al_idx and forward reaction
                    # when checking for a closed reaction we need to
                    # use the backward/opposite reaction
                    self.open_reactions[tuple(
                        reacted_idx + [reaction_str])] = count

            previous_components = component_list


def save_components_file(fname, components, matrices):
    np.savez_compressed(fname, components=components, matrices=matrices)


def load_components_file(fname):
    data = np.load(fname)
    return data['components'], data['matrices']


def main():
    
    # ------------------------------------------------------------------------------------------
    # Create the parser
    parser = argparse.ArgumentParser(description="A script that takes command-line arguments")

    # Add arguments
    parser.add_argument('--N', type=int, required=True)
    parser.add_argument('--start_index', type=int,  required=True)
    parser.add_argument('--end_index', type=int, required=True)

    # Parse the arguments
    args = parser.parse_args()
    # ------------------------------------------------------------------------------------------
    N = args.N
    XXX = args.start_index
    YYY = args.end_index


    # Specify the trajectory file
    traj_file = 'TEMP' # <------------------------------ Change this path to your .traj file
    traj = Trajectory(traj_file)[XXX:YYY]


    # Specify the file where components are saved and loaded
    # from. Mind that if this file exists the results will be loaded
    # from it so no new detection takes place.
    components_file = 'TEMP' #<-------------------------- Change the name of your output file. Important that the format is .npz!
    
    components_file += '_INDEX_' + str(N) + '.npz'

    cutoff_dict = {'Al': 1, 'Cl': 1.7, 'H': .37, 'O': 1, 'N': 1, 'C': 1}
    detect = Detect(traj, cutoff_dict, saved_components_file=components_file)
    # detect.print_initial_components()
    # detect.follow()
    # print('-' * 80)
    # for idx, reactions in detect.molecule_information.items():
    #     print(idx, reactions)
    # print('-' * 80)
    # print('Closed reactions:')
    # for i in detect.closed_reactions:
    #     print(i)
    # print('-' * 80)
    # print('Open reactions:')
    # for i in detect.open_reactions.items():
    #     print(i)

if __name__ == "__main__":
    main()
