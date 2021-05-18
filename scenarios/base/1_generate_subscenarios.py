import numpy as np
import os
import shutil
import sys

sys.path.append('../../')
import distributions


def create_subscenarios(n, output_folder='inputs/'):
    for i in range(n):
        # Create folder for subscenario
        sub_folder = os.path.join(output_folder, '%d' % i)
        if not os.path.isdir(sub_folder):
            os.makedirs(sub_folder)
        
        # Copy in the config and profile file
        shutil.copyfile('config.yaml', os.path.join(sub_folder, 'config.yaml'))
        shutil.copyfile('profiles.yaml', os.path.join(sub_folder, 'profiles.yaml'))
        

def generate_parameters(n, n_modes, support, centers_range, spreads_range, output_folder='inputs/'):
    for i in range(n):
        # Create folder for subscenario
        sub_folder = os.path.join(output_folder, '%d' % i)
        if not os.path.isdir(sub_folder):
            os.makedirs(sub_folder)
        
        # Generate PMF
        centers = np.random.randint(centers_range[0], centers_range[1] + 1, n_modes)
        spreads = np.random.randint(spreads_range[0], spreads_range[1] + 1, n_modes)
        pmf = distributions.normal_sum_pmf(support[0], support[1], centers, spreads)
        
        # Save PMF
        np.save(os.path.join(sub_folder, 'distrib'), pmf)


if __name__ == '__main__':
    """
    Subscenario parameters
    """
    num_subscenarios = 1000
    n_modes = 2
    
    # Create subscenarios and populate them with parameters
    create_subscenarios(num_subscenarios)
    generate_parameters(num_subscenarios, n_modes, [1, 80], [1, 80], [10, 50])