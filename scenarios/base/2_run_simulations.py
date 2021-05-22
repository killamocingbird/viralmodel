import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from multiprocessing import Process
import os
import sys
from tqdm import tqdm
sys.path.append('../../')
import run_scenario
import util


# Single threaded run without parallelization
def run_subscenarios_single(subscenarios_path='inputs/', queue=None, tqdm_pos=0):
    # Get list of all subfolders
    dirs = queue if queue else os.listdir(subscenarios_path)
    dirs.sort()
    # Prime working directory
    os.chdir(os.path.join(subscenarios_path, dirs[0]))
    for target_dir in tqdm(dirs, position=tqdm_pos):
        # Switch working directory
        os.chdir(os.path.join('../', target_dir))
        SIR = run_scenario.run('config.yaml')
        
        # Plot final SIR
        util.plot_SIR(SIR)
        plt.savefig('SIR.pdf')
        plt.close()
        
# Multithreaded run with parallelization
def run_subscenarios_multi(num_workers, subscenarios_path='inputs/'):
    workers = []
    subscenarios = os.listdir(subscenarios_path)
    queue_size = len(subscenarios) // num_workers
    
    for worker_idx in range(num_workers):
        queue = subscenarios[worker_idx*queue_size:(worker_idx+1)*queue_size]
        p = RunProcess(subscenarios_path, queue, worker_idx)
        p.start()
        workers.append(p)

# Multithread process
class RunProcess(Process):
    def __init__(self, subscenarios_path, queue, pos):
        super().__init__()
        
        # Aggregation variables
        self.subscenarios_path = subscenarios_path
        
        # MultiProcesses variables
        self.queue = queue
        self.pos = pos
        
    def run(self):
        run_subscenarios_single(subscenarios_path=self.subscenarios_path,
                                queue=self.queue,
                                tqdm_pos=self.pos)
    

if __name__ == '__main__':
    run_subscenarios_multi(8)
    
    
    
    


