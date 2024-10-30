"""This example demonstrates the usage of Optuna with Ray Tune for
multi-objective optimization.

Please note that schedulers may not work correctly with multi-objective
optimization.

Requires the Optuna library to be installed (`pip install optuna`).
"""
import time

import ray
from ray import train, tune
from ray.tune.search import ConcurrencyLimiter
from ray.tune.search.optuna import OptunaSearch
import optuna
from datetime import datetime
import os
from typing import Optional
from DGRePlAce import Worker
from analyze import getCandidateSolutions

def simple_trial_name_creator(trial):
    return f"trial_{trial.trial_id}"  # Simple trial name without hyperparameters

# Define the hyperparameter class
class Params:
    def __init__(self, 
                 design: str = "", 
                 design_dir: str = "", 
                 openroad_exe: str = "", 
                 num_samples: int = 0, 
                 num_cores: int = 0, 
                 seed: int = 0, 
                 virtual_iter: int = 0, 
                 num_hops: int = 0, 
                 init_bloat_factor: float = 0.0, 
                 target_density: float = 0.0, 
                 density_penalty_coef: float = 0.0, 
                 halo_width: float = 0.0, 
                 coarsening_ratio: int = 0, 
                 max_num_level: int = 0, 
                 run_dir: str = ""):
        self._design = design
        self._design_dir = design_dir
        self._openroad_exe = openroad_exe
        self._num_samples = num_samples
        self._num_cores = num_cores
        self._seed = seed
        self._virtual_iter = virtual_iter
        self._num_hops = num_hops
        self._init_bloat_factor = init_bloat_factor
        self._target_density = target_density
        self._density_penalty_coef = density_penalty_coef
        self._halo_width = halo_width
        self._coarsening_ratio = coarsening_ratio
        self._max_num_level = max_num_level
        self._run_dir = run_dir


    # Example of basic validation
    @property
    def num_samples(self) -> int:
        return self._num_samples

    @num_samples.setter
    def num_samples(self, value: int):
        if value < 0:
            raise ValueError("num_samples must be non-negative")
        self._num_samples = value

    @property
    def num_cores(self) -> int:
        return self._num_cores

    @num_cores.setter
    def num_cores(self, value: int):
        if value < 0:
            raise ValueError("num_cores must be non-negative")
        self._num_cores = value

    @property
    def seed(self) -> int:
        return self._seed

    @seed.setter
    def seed(self, value: int):
        if value < 0:
            raise ValueError("seed must be non-negative")
        self._seed = value

    @property
    def virtual_iter(self) -> int:
        return self._virtual_iter
    
    @virtual_iter.setter
    def virtual_iter(self, value: int):
        if value < 0:
            raise ValueError("virtual_iter must be non-negative")
        self._virtual_iter = value

    @property
    def num_hops(self) -> int:
        return self._num_hops
    
    @num_hops.setter
    def num_hops(self, value: int):
        if value < 0:
            raise ValueError("num_hops must be non-negative")
        self._num_hops = value
    
    @property
    def init_bloat_factor(self) -> float:
        return self._init_bloat_factor
    
    @init_bloat_factor.setter
    def init_bloat_factor(self, value: float):
        if value < 0:
            raise ValueError("init_bloat_factor must be non-negative")
        self._init_bloat_factor = value

    @property
    def target_density(self) -> float:
        return self._target_density
    
    @target_density.setter
    def target_density(self, value: float):
        if value < 0:
            raise ValueError("target_density must be non-negative")
        self._target_density = value

    @property
    def density_penalty_coef(self) -> float:
        return self._density_penalty_coef
    
    @density_penalty_coef.setter
    def density_penalty_coef(self, value: float):
        if value < 0:
            raise ValueError("density_penalty_coef must be non-negative")
        self._density_penalty_coef = value
    
    @property
    def halo_width(self) -> float:
        return self._halo_width
    
    @halo_width.setter
    def halo_width(self, value: float):
        if value < 0:
            raise ValueError("halo_width must be non-negative")
        self._halo_width = value

    @property
    def coarsening_ratio(self) -> int:
        return self._coarsening_ratio
    
    @coarsening_ratio.setter
    def coarsening_ratio(self, value: int):
        if value < 0:
            raise ValueError("coarsening_ratio must be non-negative")
        self._coarsening_ratio = value

    @property
    def max_num_level(self) -> int:
        return self._max_num_level
    
    @max_num_level.setter
    def max_num_level(self, value: int):
        if value < 0:
            raise ValueError("max_num_level must be non-negative")
        self._max_num_level = value

    @property
    def run_dir(self) -> str:
        return self._run_dir
    
    @run_dir.setter
    def run_dir(self, value: str):
        if not value:
            raise ValueError("run_dir must be non-empty")
        self._run_dir = value

    
def evaluation_fn(params: Params):
    worker = Worker()
    worker.set_design_dir(params._design_dir)
    worker.set_exe(params._openroad_exe)
    worker.set_target_density(params._target_density)
    worker.set_density_penalty_coef(params._density_penalty_coef)
    worker.set_halo_width(params._halo_width)
    worker.set_coarsening_ratio(params._coarsening_ratio)
    worker.set_max_num_level(params._max_num_level)
    worker.set_virtual_iter(params._virtual_iter)
    worker.set_num_hops(params._num_hops)
    worker.set_init_bloat_factor(params._init_bloat_factor)
    
    run_dir = params.run_dir        
    template_file = run_dir + "/run_openroad.tcl"
    worker.set_template_file(template_file)
    Wirelength, Congestion, Density = worker.run(run_dir)

    print("run_dir: ", run_dir)
    return Congestion, Wirelength, Density

    
def easy_objective(config):
    design = config["design"]
    design_dir = config["design_dir"]
    openroad_exe = config["openroad_exe"]
    num_samples = config["num_samples"]
    num_cores = config["num_cores"]
    seed = config["seed"]
    virtual_iter = config["virtual_iter"]
    num_hops = config["num_hops"]
    init_bloat_factor = config["init_bloat_factor"]
    target_density = config["target_density"]
    density_penalty_coef = config["density_penalty_coef"]
    halo_width = config["halo_width"]
    coarsening_ratio = config["coarsening_ratio"]
    max_num_level = config["max_num_level"]
    run_dir = os.getcwd()  # Note that this is not the current directory.
    config["trial_dir"] = run_dir  

    template_file = design_dir + "/run_openroad_template.tcl"
    run_file = run_dir + "/run_openroad.tcl"
    os.system(f"cp {template_file} {run_file}")

    # Create an instance of the Params class
    params = Params(design=design, 
                    design_dir=design_dir, 
                    openroad_exe=openroad_exe, 
                    num_samples=num_samples, 
                    num_cores=num_cores, 
                    seed=seed, 
                    virtual_iter=virtual_iter, 
                    num_hops=num_hops, 
                    init_bloat_factor=init_bloat_factor, 
                    target_density=target_density, 
                    density_penalty_coef=density_penalty_coef, 
                    halo_width=halo_width, 
                    coarsening_ratio=coarsening_ratio, 
                    max_num_level=max_num_level, 
                    run_dir=run_dir)
    
    Congestion, Wirelength, Density = evaluation_fn(params)

    # Train the model
    train.report({"Congestion": Congestion, "Wirelength": Wirelength, "Density": Density})
    time.sleep(0.1)

def tune_func(config):
    tune.utils.wait_for_gpu()
    easy_objective(config)


def run_optuna_tune(design, openroad_exe, design_dir, num_samples, num_cores, seed):
    sampler = optuna.samplers.NSGAIISampler()   
    
    if (num_samples <= 50):
        sampler = optuna.samplers.NSGAIISampler(
            population_size=10,
            crossover_prob=0.8,
            swapping_prob=0.4,
            mutation_prob=0.3,
            seed = seed)
    else:
        sampler = optuna.samplers.NSGAIISampler(
            population_size=40,
            crossover_prob=0.9,
            swapping_prob=0.5,
            mutation_prob=0.2,
            seed = seed)   

    # Congestion is calculated based on RUDY
    # Density is the maximum bin density
    # Wirelength is the total wirelength
   
   
    param_space = {
        # ------- general parameters ------------*
        "design" : design,
        "design_dir" : design_dir,
        "openroad_exe" : openroad_exe,
        "num_samples" : num_samples,
        "num_cores" : num_cores,
        "seed" : seed, 
        "trial_dir" : os.getcwd(), # to store the trial directory in the results
        # -------- Hyperparameters ------------*  
        "virtual_iter": 4, # use default value
        "num_hops": 4,  # use default value
        "init_bloat_factor": 1.00, # use default value
        "target_density": tune.uniform(0.6, 0.8),
        "density_penalty_coef": tune.uniform(0.98, 1.013),
        "halo_width": tune.uniform(1.0, 3.0),
        "coarsening_ratio": tune.randint(10, 30), # integer between [5, 20]
        "max_num_level": tune.randint(1, 3), # integer between [1, 2]
    }

    # Queue default trial as initial trials for the search algorithm
    initial_configs = [{
        "target_density": 0.7,  # Example default value
        "density_penalty_coef": 0.99,  # Example default value
        "halo_width": 2.0,  # Example default value
        "coarsening_ratio": 20,  # Example default value
        "max_num_level": 2  # Example default value
    }]

    algo = OptunaSearch(points_to_evaluate=initial_configs, sampler=sampler, metric=["Congestion", "Wirelength", "Density"], mode=["min", "min", "min"])  
    algo = ConcurrencyLimiter(algo, max_concurrent=num_cores)

    tuner = tune.Tuner(
        #easy_objective,
        tune.with_resources(
            tune_func,
            resources={"cpu": 1, "gpu": 0.2}
        ),
        #tune_func,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=num_samples,
            trial_name_creator=lambda trial: f"{trial.trainable_name}_{trial.trial_id}",
            trial_dirname_creator=lambda trial: f"{trial.trainable_name}_{trial.trial_id}",
        ),
        param_space=param_space,
    )
       
    results = tuner.fit()

    print(
        "Best hyperparameters for Congestion found were: ",
        results.get_best_result("Congestion", "min").config,
    )
   
    print(
        "Best hyperparameters for Density found were: ",
        results.get_best_result("Density", "min").config,
    )
    
    print(
        "Best hyperparameters for Wirelength found were: ",
        results.get_best_result("Wirelength", "min").config,
    )

    # Get a dataframe with the last results for each trial
    df_results = results.get_dataframe()
    print(df_results)

    best_dir = results.get_best_result("Wirelength", mode="min").config["trial_dir"]
    base_dir = ""
    items = best_dir.split("/") 
    for i in range(len(items) - 1):
        base_dir += items[i] + "/"

    print("base_dir : ", base_dir)

    old_dir_list = df_results[:]["trial_id"].tolist()
    updated_dir_list = []
    for i in range(len(old_dir_list)):
        updated_dir_list.append(base_dir + "tune_func_" + old_dir_list[i])

    print("updated_dir_list : ", updated_dir_list)

    df_results["trial_id"] = updated_dir_list

    # Get a dataframe of results for a specific score or mode
    #df = results.get_dataframe(filter_metric="score", filter_mode="max")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') 
    filename = f'results_{timestamp}.csv'
    df_results.to_csv(filename, index=False)
    print(f'File saved as: {filename}')

    top_n = 5
    num_clusters = 5
    random_seed = 0
    weight_params = [1.0, 1.0, 1.0]

    # Pareto optimal points
    getCandidateSolutions(filename, top_n, num_clusters, random_seed, weight_params)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing"
    )
    args, _ = parser.parse_known_args()

    pwd = os.getcwd()

    design = "swerv_wrapper" 
    openroad_exe = pwd + "/../OpenROAD-tool/build/src/openroad"
    design_dir = pwd + "/../test/swerv_wrapper"
    num_samples = 500
    num_cores = 6
    seed = 0

    # Shorter symbolic link path
    # You may need to update this based on your system settings
    link_path = "/tmp/short_ray_dir"
    result_path = "/home/memzfs_projects/DG_RePlAce_autoDMP/ray_results"

    # Create the symbolic link
    try:
        os.symlink(design_dir, link_path)
        print(f"Symbolic link created: {link_path} -> {result_path}")
    except FileExistsError:
        print(f"Symbolic link already exists: {link_path}")
    except OSError as e:
        print(f"Error creating symbolic link: {e}")

    # Set an environment variable
    os.environ['TMPDIR'] = link_path
    # Optionally, create the directory if it doesn't exist
    os.makedirs(os.environ['TMPDIR'], exist_ok=True)
    run_optuna_tune(design, openroad_exe, design_dir, num_samples, num_cores, seed)




