import glob
import numpy as np
import os

def aggregate_proj(source_folder, dump_folder, pattern='proj_*.npy'):
    files = glob.glob(os.path.join(source_folder, pattern))
    files.sort()
    ret = [np.load(file) for file in files]
    ret = np.stack(ret, 0)
    
    np.save(os.path.join(dump_folder, 'agg_deltas'), ret)
    
    return ret


def aggregate_deltas(source_folder, dump_folder, bins=4, normalize=True, pattern='deltas_*.npy', combos=None):
    if combos is None:
        combos = np.array(np.meshgrid(np.arange(bins), np.arange(bins)), dtype=np.long).T.reshape(-1,2)
    
    files = glob.glob(os.path.join(source_folder, pattern))
    files.sort()
    deltas = []
    # Convert to bin index form [bin_1, bin_2, 0, delta_bin_2]
    for i in range(len(files)):
        delta = np.load(files[i])
        deltas.append(np.concatenate((
            combos.astype(np.float) / (bins if normalize else 1.),
            np.zeros((len(combos), 1), dtype=np.long),
            delta[combos[:,0], combos[:,1]][:,None]), 1))
    deltas = np.stack(deltas, 0)
    
    np.save(os.path.join(dump_folder, 'agg_deltas'), deltas)
    
    return deltas
    
    
    
