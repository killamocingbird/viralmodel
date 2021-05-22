import os
import sys
from tqdm import tqdm
sys.path.append('../../')
import aggregate_data as data

def aggregate_all(subscenarios_path='inputs/', dump_folder='out_agg/'):
    folders = [os.path.join(subscenarios_path, folder, 'out') for folder in os.listdir(subscenarios_path)]
    # Make aggregated dump path
    if not os.path.exists(dump_folder):
        os.mkdirs(dump_folder)
    
    for folder in tqdm(folders):
        data.aggregate_proj(folder, dump_folder)
        data.aggregate_deltas(folder, dump_folder)
    

if __name__ == '__main__':
    aggregate_all()
    
        
    